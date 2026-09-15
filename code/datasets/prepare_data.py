from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


TARGET_COLUMN = "species"
FEATURE_COLUMNS = [
    "island",
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
    "sex",
    "year",
]
NUMERIC_COLUMNS = [
    "bill_length_mm",
    "bill_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]
REQUIRED_COLUMNS = [TARGET_COLUMN, *FEATURE_COLUMNS]


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--train-output", type=Path, required=True)
    parser.add_argument("--test-output", type=Path, required=True)
    parser.add_argument("--test-size", type=float, required=True)
    parser.add_argument("--random-state", type=int, required=True)
    parser.add_argument("--iqr-factor", type=float, required=True)
    return parser.parse_args()


def remove_outliers(data, columns, iqr_factor):
    mask = pd.Series(True, index=data.index)

    for column in columns:
        first_quartile = data[column].quantile(0.25)
        third_quartile = data[column].quantile(0.75)
        iqr = third_quartile - first_quartile
        lower_bound = first_quartile - iqr_factor * iqr
        upper_bound = third_quartile + iqr_factor * iqr
        mask &= data[column].between(lower_bound, upper_bound)

    return data.loc[mask]


def main():
    args = parse_args()
    data = pd.read_csv(args.input)

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

    initial_rows = len(data)
    data = data[REQUIRED_COLUMNS].drop_duplicates().dropna()
    rows_after_missing_values = len(data)
    data = remove_outliers(data, NUMERIC_COLUMNS, args.iqr_factor)
    rows_after_outliers = len(data)

    train_data, test_data = train_test_split(
        data,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=data[TARGET_COLUMN],
    )

    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.test_output.parent.mkdir(parents=True, exist_ok=True)
    train_data.reset_index(drop=True).to_csv(args.train_output, index=False)
    test_data.reset_index(drop=True).to_csv(args.test_output, index=False)

    print(f"Rows loaded: {initial_rows}")
    print(f"Rows after missing values and duplicates: {rows_after_missing_values}")
    print(f"Rows after outlier removal: {rows_after_outliers}")
    print(f"Train rows: {len(train_data)}")
    print(f"Test rows: {len(test_data)}")


if __name__ == "__main__":
    main()
