"""
Member 2 - Mandi price prediction adapter.

Loads the trained Gradient Boosting model and converts the
historical market-price data supplied by the backend into the
same features used during training.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.services.model_adapters.exceptions import ModelNotIntegratedError


# --------------------------------------------------
# Model path
# --------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()

# backend/app/services/model_adapters/
#        -> backend/
BACKEND_DIR = CURRENT_FILE.parents[3]

MODEL_PATH = (
    BACKEND_DIR
    / "ml"
    / "models"
    / "price_model.joblib"
)


# --------------------------------------------------
# Load model once
# --------------------------------------------------

_model_package = None


def _load_model():
    """Load the trained Member 2 model."""

    global _model_package

    if _model_package is None:

        if not MODEL_PATH.exists():
            raise ModelNotIntegratedError(
                f"Price model not found at: {MODEL_PATH}"
            )

        _model_package = joblib.load(MODEL_PATH)

    return _model_package


# --------------------------------------------------
# Date helper
# --------------------------------------------------

def _parse_date(value: Any) -> date:
    """Convert a date-like value to a Python date."""

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return pd.to_datetime(value).date()


# --------------------------------------------------
# Feature creation
# --------------------------------------------------

def _create_features(
    prices: list[float],
    forecast_date: date,
) -> dict[str, float]:
    """
    Create exactly the features used by the training script.

    The model uses:
        lag_1
        lag_2
        lag_3
        rolling_mean_3
        month
        day
        day_of_week
    """

    if len(prices) < 3:
        raise ModelNotIntegratedError(
            "At least 3 historical prices are required "
            "for price prediction."
        )

    lag_1 = prices[-1]
    lag_2 = prices[-2]
    lag_3 = prices[-3]

    rolling_mean_3 = (
        lag_1 + lag_2 + lag_3
    ) / 3.0

    return {
        "lag_1": float(lag_1),
        "lag_2": float(lag_2),
        "lag_3": float(lag_3),
        "rolling_mean_3": float(rolling_mean_3),
        "month": float(forecast_date.month),
        "day": float(forecast_date.day),
        "day_of_week": float(forecast_date.weekday()),
    }


# --------------------------------------------------
# Main prediction function
# --------------------------------------------------

async def predict_price(
    crop_id: int,
    market_id: int,
    days_ahead: int,
    historical_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Predict mandi prices for the requested number of future days.

    Parameters
    ----------
    crop_id:
        Backend crop ID.

    market_id:
        Backend market ID.

    days_ahead:
        Number of future days to predict.

    historical_data:
        Chronological historical market prices supplied by the
        existing backend orchestration layer.

    Returns
    -------
    list[dict[str, Any]]
        Example:
        [
            {
                "date": "2026-09-06",
                "predicted_price": 4500.25
            }
        ]
    """

    # These IDs are part of the existing backend contract.
    # The current global model is trained using price-history
    # features rather than crop_id/market_id.
    _ = (crop_id, market_id)

    if days_ahead < 1 or days_ahead > 30:
        raise ValueError(
            "days_ahead must be between 1 and 30."
        )

    if len(historical_data) < 3:
        raise ModelNotIntegratedError(
            "At least 3 historical market prices are required "
            "for price prediction."
        )

    package = _load_model()

    model = package["model"]
    feature_columns = package["features"]

    # --------------------------------------------------
    # Prepare historical prices
    # --------------------------------------------------

    history = []

    for item in historical_data:

        if "date" not in item:
            raise ModelNotIntegratedError(
                "Historical price record is missing 'date'."
            )

        if "modal_price" not in item:
            raise ModelNotIntegratedError(
                "Historical price record is missing 'modal_price'."
            )

        history.append(
            {
                "date": _parse_date(item["date"]),
                "modal_price": float(item["modal_price"]),
            }
        )

    # Sort chronologically
    history.sort(key=lambda item: item["date"])

    prices = [
        item["modal_price"]
        for item in history
    ]

    last_date = history[-1]["date"]

    predictions = []

    # --------------------------------------------------
    # Recursive forecasting
    # --------------------------------------------------

    for step in range(1, days_ahead + 1):

        forecast_date = last_date + timedelta(days=step)

        features = _create_features(
            prices=prices,
            forecast_date=forecast_date,
        )

        X = pd.DataFrame(
            [features],
            columns=feature_columns,
        )

        predicted_price = float(
            model.predict(X)[0]
        )

        # A market price cannot be negative.
        predicted_price = max(
            0.0,
            predicted_price,
        )

        predictions.append(
            {
                "date": forecast_date.isoformat(),
                "predicted_price": round(
                    predicted_price,
                    2,
                ),
            }
        )

        # Feed prediction into the next forecast.
        prices.append(predicted_price)

    return predictions