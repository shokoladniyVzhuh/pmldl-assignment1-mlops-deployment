from argparse import ArgumentParser
from json import dump
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET_COLUMN = "species"
NUMERIC_COLUMNS = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
    "year",
]
CATEGORICAL_COLUMNS = ["island", "sex"]
FEATURE_COLUMNS = [*CATEGORICAL_COLUMNS, *NUMERIC_COLUMNS]


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--train-data", type=Path, required=True)
    parser.add_argument("--test-data", type=Path, required=True)
    parser.add_argument("--model-output", type=Path, required=True)
    parser.add_argument("--metrics-output", type=Path, required=True)
    parser.add_argument("--mlflow-directory", type=Path, required=True)
    parser.add_argument("--mlflow-database", type=Path, required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--random-state", type=int, required=True)
    parser.add_argument("--max-iter", type=int, required=True)
    parser.add_argument("--c", type=float, required=True)
    return parser.parse_args()


def build_pipeline(random_state, max_iter, c):
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_COLUMNS),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_COLUMNS,
            ),
        ]
    )
    classifier = LogisticRegression(
        random_state=random_state,
        max_iter=max_iter,
        C=c,
    )
    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("classifier", classifier),
        ]
    )


def calculate_metrics(target, predictions):
    return {
        "accuracy": accuracy_score(target, predictions),
        "precision_macro": precision_score(
            target,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "recall_macro": recall_score(
            target,
            predictions,
            average="macro",
            zero_division=0,
        ),
        "f1_macro": f1_score(
            target,
            predictions,
            average="macro",
            zero_division=0,
        ),
    }


def main():
    args = parse_args()
    train_data = pd.read_csv(args.train_data)
    test_data = pd.read_csv(args.test_data)

    required_columns = set([TARGET_COLUMN, *FEATURE_COLUMNS])
    missing_train_columns = sorted(required_columns - set(train_data.columns))
    missing_test_columns = sorted(required_columns - set(test_data.columns))

    if missing_train_columns:
        raise ValueError(f"Missing train columns: {', '.join(missing_train_columns)}")
    if missing_test_columns:
        raise ValueError(f"Missing test columns: {', '.join(missing_test_columns)}")

    train_features = train_data[FEATURE_COLUMNS].copy()
    train_target = train_data[TARGET_COLUMN]
    test_features = test_data[FEATURE_COLUMNS].copy()
    test_target = test_data[TARGET_COLUMN]

    train_features[NUMERIC_COLUMNS] = train_features[NUMERIC_COLUMNS].astype(float)
    test_features[NUMERIC_COLUMNS] = test_features[NUMERIC_COLUMNS].astype(float)

    model = build_pipeline(args.random_state, args.max_iter, args.c)
    model.fit(train_features, train_target)
    predictions = model.predict(test_features)
    metrics = calculate_metrics(test_target, predictions)

    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
    args.mlflow_directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.model_output)

    with args.metrics_output.open("w", encoding="utf-8") as file:
        dump(metrics, file, indent=2, sort_keys=True)

    mlflow.set_tracking_uri(f"sqlite:///{args.mlflow_database.resolve()}")
    mlflow.set_experiment(args.experiment_name)

    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "model": "LogisticRegression",
                "random_state": args.random_state,
                "max_iter": args.max_iter,
                "C": args.c,
            }
        )
        mlflow.log_metrics(metrics)
        signature = infer_signature(test_features, predictions)
        mlflow.sklearn.log_model(
            model,
            name="model",
            signature=signature,
            input_example=test_features.head(3),
        )
        run_id = run.info.run_id

    for name, value in metrics.items():
        print(f"{name}: {value:.6f}")
    print(f"MLflow run: {run_id}")


if __name__ == "__main__":
    main()
