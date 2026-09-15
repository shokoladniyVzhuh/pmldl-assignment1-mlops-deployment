# PMLDL Assignment 1 — Deployment

This project implements an automated MLOps pipeline with three stages:

1. data engineering;
2. model engineering;
3. deployment of an API and a web application.

## Initial project decision

The first implementation will use a small tabular classification dataset and a simple scikit-learn model. The exact dataset and target column will be documented here before Stage 1 implementation.

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

## Status

- [x] Initial directory structure
- [x] Dependency list
- [ ] Dataset selection
- [ ] Stage 1: data engineering
- [ ] Stage 2: model engineering
- [ ] Stage 3: deployment
- [ ] Pipeline automation

