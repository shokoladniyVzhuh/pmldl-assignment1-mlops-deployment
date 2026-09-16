import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Penguins Classifier", page_icon="🐧")
st.title("Penguins Classifier")
st.write("Enter penguin measurements to predict its species.")

with st.form("prediction_form"):
    island = st.selectbox("Island", ["Biscoe", "Dream", "Torgersen"])
    sex = st.selectbox("Sex", ["female", "male"])
    bill_length_mm = st.number_input(
        "Bill length (mm)",
        min_value=1.0,
        value=46.1,
        step=0.1,
    )
    bill_depth_mm = st.number_input(
        "Bill depth (mm)",
        min_value=1.0,
        value=13.2,
        step=0.1,
    )
    flipper_length_mm = st.number_input(
        "Flipper length (mm)",
        min_value=1.0,
        value=211.0,
        step=1.0,
    )
    body_mass_g = st.number_input(
        "Body mass (g)",
        min_value=1.0,
        value=4500.0,
        step=50.0,
    )
    year = st.selectbox("Year", [2007, 2008, 2009], index=1)
    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "island": island,
        "bill_length_mm": bill_length_mm,
        "bill_depth_mm": bill_depth_mm,
        "flipper_length_mm": flipper_length_mm,
        "body_mass_g": body_mass_g,
        "sex": sex,
        "year": year,
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        st.success(f"Predicted species: {result['prediction']}")
        st.subheader("Class probabilities")

        for label, probability in result["probabilities"].items():
            st.write(f"{label}: {probability:.2%}")
    except requests.RequestException as error:
        st.error(f"Prediction request failed: {error}")
