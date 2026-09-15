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

## Status

- [x] Initial directory structure
- [x] Dependency list
- [x] Dataset selection
- [x] Stage 1: data engineering
- [ ] Stage 2: model engineering
- [ ] Stage 3: deployment
- [ ] Pipeline automation
