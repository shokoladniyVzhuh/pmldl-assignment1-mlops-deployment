# PMLDL Assignment 1 — Deployment

An automated MLOps pipeline for multiclass penguin species classification. The project covers data preparation, model training and evaluation, experiment tracking, and deployment of a prediction API with a web interface.

The project uses the [Palmer Penguins dataset](https://github.com/allisonhorst/palmerpenguins). The target column is `species`.

## Pipeline

```text
data/raw/penguins.csv
        |
        v
DVC: cleaning, outlier removal, train/test split
        |
        v
DVC + MLflow: feature engineering, training, evaluation
        |
        v
models/model.pkl
        |
        v
Docker Compose: FastAPI <--- Streamlit
```

The project uses:

- DVC for the reproducible data and model pipeline;
- MLflow for parameters, metrics, and model logging;
- scikit-learn for preprocessing and logistic regression;
- FastAPI for the prediction API;
- Streamlit for the web application;
- Docker Compose for separate API and app containers;
- cron for automatic execution every five minutes.

## Requirements

- Linux;
- Python 3.12;
- Git;
- Docker Engine with the Docker Compose plugin;
- cron;
- `flock` from `util-linux`.

## Installation

Clone the public repository and enter its directory:

```bash
git clone https://github.com/shokoladniyVzhuh/pmldl-assignment1-mlops-deployment.git
cd pmldl-assignment1-mlops-deployment
```

Create a virtual environment and install the dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the local configuration:

```bash
cp .env.example .env
```

The default configuration exposes the API on port `8000` and Streamlit on port `8501`. Edit `.env` if either port is occupied.

## Project structure

```text
code/
├── datasets/              data loading, cleaning, and splitting
├── models/                feature engineering, training, and evaluation
└── deployment/
    ├── api/               FastAPI service and Dockerfile
    ├── app/               Streamlit application and Dockerfile
    └── docker-compose.yml
data/
├── raw/                   source dataset
└── processed/             generated train and test datasets
metrics/                   generated evaluation metrics
models/                    generated trained model
services/cron/             schedule installation scripts
dvc.yaml                   DVC pipeline definition
params.yaml                data and model parameters
run_pipeline.sh            complete automated pipeline
```

Generated data, model, metric, log, and MLflow files are excluded from Git. They are recreated by the pipeline from the committed raw dataset and source code.

## Stage 1: data engineering

The `prepare_data` DVC stage:

- loads `data/raw/penguins.csv`;
- selects and validates the required columns;
- removes duplicates and rows with missing values;
- removes numeric outliers with the IQR method;
- creates a reproducible stratified train/test split.

Outputs:

```text
data/processed/train.csv
data/processed/test.csv
```

## Stage 2: model engineering

The `train_model` DVC stage applies standard scaling to numeric features, one-hot encoding to categorical features, and trains a logistic regression classifier. The preprocessing and classifier are packaged in one scikit-learn pipeline.

Outputs:

```text
models/model.pkl
metrics/metrics.json
mlruns/
mlflow.db
```

Run both DVC stages and display the results:

```bash
dvc repro
dvc dag
dvc metrics show
```

Open the MLflow interface:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

MLflow is then available at [http://localhost:5000](http://localhost:5000).

## Stage 3: deployment

The FastAPI service loads the saved model and provides health and prediction endpoints. The Streamlit application collects feature values, sends them to FastAPI, and displays the predicted species and class probabilities. The services run in separate containers.

Build and start them after `dvc repro`:

```bash
docker compose -f code/deployment/docker-compose.yml up --build -d
```

Available services with the default `.env` configuration:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Streamlit: [http://localhost:8501](http://localhost:8501)

Check the API:

```bash
curl http://localhost:8000/health
```

Send a prediction request:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "island": "Biscoe",
    "bill_length_mm": 46.1,
    "bill_depth_mm": 13.2,
    "flipper_length_mm": 211,
    "body_mass_g": 4500,
    "sex": "female",
    "year": 2008
  }'
```

Inspect or stop the containers:

```bash
docker compose -f code/deployment/docker-compose.yml ps
docker compose -f code/deployment/docker-compose.yml down
```

## Complete pipeline and automation

Run the whole pipeline manually:

```bash
./run_pipeline.sh
```

The script activates `.venv`, runs `dvc repro`, rebuilds the Docker images, starts both containers, and appends output to `logs/pipeline.log`. A file lock prevents concurrent runs.

Install the required five-minute schedule:

```bash
./services/cron/install.sh
crontab -l
```

Follow automatic pipeline runs:

```bash
tail -f logs/pipeline.log
```

Remove the schedule when it is no longer needed:

```bash
./services/cron/uninstall.sh
```

## Troubleshooting

If ports `8000` or `8501` are occupied, change them in `.env`, for example:

```text
API_PORT=18000
APP_PORT=18501
COMPOSE_PROJECT_NAME=pmldl-assignment1
```

Use the configured ports in browser and `curl` commands. If Docker commands fail with a permissions error, make sure Docker is running and the current user is allowed to access its daemon.
