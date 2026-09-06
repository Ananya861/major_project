import joblib
import pandas as pd
import numpy as np
import os


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "karnataka_yield_model.pkl"
)

print("Loading trained crop yield model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_crop_yield(district, crop, season, year):

    input_data = pd.DataFrame([{
        "District_Name": district.upper(),
        "Crop": crop,
        "Season": season,
        "Crop_Year": year
    }])

    prediction = model.predict(input_data)

    predicted_yield = np.expm1(prediction[0])

    return round(float(predicted_yield), 2)


# ============================================================
# TEST PREDICTION
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("KARNATAKA CROP YIELD PREDICTION")
    print("=" * 60)

    district = "BELAGAVI"
    crop = "Maize"
    season = "Kharif"
    year = 2025

    result = predict_crop_yield(
        district=district,
        crop=crop,
        season=season,
        year=year
    )

    print("\nINPUT DETAILS")

    print("District :", district)
    print("Crop     :", crop)
    print("Season   :", season)
    print("Year     :", year)

    print("\nPREDICTION")

    print("Predicted Yield :", result)

    print("\nPrediction completed successfully.")