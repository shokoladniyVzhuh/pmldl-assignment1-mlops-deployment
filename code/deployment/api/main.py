import os
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/model.pkl"))
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Penguins Classification API", version="1.0.0")


class PredictionRequest(BaseModel):
    island: Literal["Biscoe", "Dream", "Torgersen"]
    bill_length_mm: float = Field(gt=0)
    bill_depth_mm: float = Field(gt=0)
    flipper_length_mm: float = Field(gt=0)
    body_mass_g: float = Field(gt=0)
    sex: Literal["female", "male"]
    year: int = Field(ge=2007, le=2009)


class PredictionResponse(BaseModel):
    prediction: str
    probabilities: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    features = pd.DataFrame([payload.model_dump()])
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    classes = model.named_steps["classifier"].classes_
    return {
        "prediction": prediction,
        "probabilities": {
            label: float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        },
    }
