"""
Location-based crop yield prediction service.

Loads the trained Karnataka Random Forest model and provides
a reusable prediction function for FastAPI routes.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# MODEL PATH
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = (
    BACKEND_ROOT
    / "ml"
    / "models"
    / "karnataka_yield_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

_model = None


def get_model():
    """
    Load the trained ML model once and reuse it.
    """

    global _model

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Yield prediction model not found: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_crop_yield(
    district: str,
    crop: str,
    season: str,
    year: int,
) -> float:
    """
    Predict crop yield for a Karnataka district.

    Parameters:
        district: Karnataka district name
        crop: Crop name
        season: Kharif, Rabi, Summer, or Whole Year
        year: Prediction year

    Returns:
        Predicted yield on the original yield scale.
    """

    model = get_model()

    input_data = pd.DataFrame(
        [
            {
                "District_Name": district.strip().upper(),
                "Crop": crop.strip(),
                "Season": season.strip(),
                "Crop_Year": int(year),
            }
        ]
    )

    prediction = model.predict(input_data)

    # Model was trained using log1p(yield),
    # so convert prediction back to original scale.
    predicted_yield = np.expm1(prediction[0])

    return round(float(predicted_yield), 2)