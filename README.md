# PMLDL Assignment 1 — Deployment

This project implements an automated MLOps pipeline with three stages:

1. data engineering;
2. model engineering;
3. deployment of an API and a web application.

## Initial project decision

The project uses the Palmer Penguins dataset and solves a multiclass classification problem. The target column is `species`.

Dataset source: [palmerpenguins](https://github.com/allisonhorst/palmerpenguins)

Planned tools:

- DVC for the data pipeline;
- MLflow for experiment and model logging;
- FastAPI for the prediction API;
- Streamlit for the web application;
- Docker Compose for separate API and app containers.

## Project structure

```text
code/datasets/       data preparation
code/models/         feature engineering and model training
code/deployment/api/ FastAPI service
code/deployment/app/ Streamlit application
data/raw/            raw input data
data/processed/      train/test data
models/              trained model artifacts
metrics/             evaluation metrics
```

## Stage 1: data engineering

The data preparation stage loads `data/raw/penguins.csv`, removes duplicates and rows with missing values, filters numeric outliers with the IQR method, and creates stratified train and test datasets.

Run the stage:

```bash
dvc repro
```

Outputs:

```text
data/processed/train.csv
data/processed/test.csv
```

## Stage 2: model engineering

The model training stage applies standard scaling to numeric features, one-hot encoding to categorical features, and trains a logistic regression classifier. The complete preprocessing and model pipeline is saved as a single artifact.

Run the complete pipeline:

```bash
dvc repro
```

Outputs:

```text
models/model.pkl
metrics/metrics.json
mlruns/
mlflow.db
```

Open the MLflow interface:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## Stage 3: deployment

The trained model is served by a FastAPI service. A separate Streamlit application sends prediction requests to the API. Both services run in separate Docker containers.

Create the model before building the containers:

```bash
dvc repro
```

Build and start the services:

```bash
docker compose -f code/deployment/docker-compose.yml up --build -d
```

Custom host ports can be used when the defaults are occupied:

```bash
API_PORT=18000 APP_PORT=18501 docker compose -f code/deployment/docker-compose.yml up --build -d
```

Available services:

```text
API: http://localhost:8000
Swagger: http://localhost:8000/docs
App: http://localhost:8501
```

Stop the services:

```bash
docker compose -f code/deployment/docker-compose.yml down
```

## Pipeline automation

Create the local configuration:

```bash
cp .env.example .env
```

Run the complete pipeline manually:

```bash
./run_pipeline.sh
```

The script prepares the data, trains the model when inputs change, rebuilds the Docker images, starts the API and application, and writes execution logs to `logs/pipeline.log`. Concurrent runs are prevented with a lock file.

Install the five-minute cron schedule:

```bash
./services/cron/install.sh
```

Check the installed schedule:

```bash
crontab -l
```

Remove the schedule:

```bash
./services/cron/uninstall.sh
```

## Status

- [x] Initial directory structure
- [x] Dependency list
- [x] Dataset selection
- [x] Stage 1: data engineering
- [x] Stage 2: model engineering
- [x] Stage 3: deployment
- [x] Pipeline automation
