from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "ml"
    / "models"
    / "price_model.joblib"
)

_model_bundle = None


def _load_model_bundle():
    global _model_bundle

    if _model_bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Price model not found: {MODEL_PATH}"
            )

        _model_bundle = joblib.load(MODEL_PATH)

    return _model_bundle


def _build_history_dataframe(
    historical_data: list[dict[str, Any]],
) -> pd.DataFrame:
    df = pd.DataFrame(historical_data)

    if df.empty:
        raise ValueError("Historical price data is empty")

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["modal_price"] = pd.to_numeric(
        df["modal_price"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["date", "modal_price"]
    )

    df = df.sort_values("date").reset_index(drop=True)

    if len(df) < 3:
        raise ValueError(
            "At least 3 historical price records are required"
        )

    return df


def _get_market_metadata(
    crop_id: int,
    market_id: int,
) -> tuple[str, str, str, str]:
    """
    Maps the existing application crop/market IDs to the
    categorical values used by the Pan-India model.

    The IDs below are the existing project database mappings.
    """

    crop_mapping = {
        1: "Wheat",
        2: "Rice",
        3: "Tomato",
        4: "Onion",
        5: "Cotton",
        16: "Maize",
        26: "Soyabean",
        27: "Groundnut",
        # Backward-compatibility aliases
        28: "Soyabean",
        29: "Groundnut",
    }

    market_mapping = {
        1: ("Azadpur", "Delhi", "North Delhi"),
        2: ("Pimpalgaon", "Maharashtra", "Nashik"),
        3: ("Kolar", "Karnataka", "Kolar"),
        4: ("Biaora", "Madhya Pradesh", "Rajgarh"),
        5: ("Khilchipur", "Madhya Pradesh", "Rajgarh"),
        6: ("Jaspur", "Chattisgarh", "Jashpur"),
        7: ("Sendhwa", "Madhya Pradesh", "Badwani"),
        # Backward-compatibility aliases
        8: ("Khilchipur", "Madhya Pradesh", "Rajgarh"),
        9: ("Jaspur", "Chattisgarh", "Jashpur"),
        10: ("Sendhwa", "Madhya Pradesh", "Badwani"),
    }

    commodity = crop_mapping.get(crop_id)

    if commodity is None:
        raise ValueError(
            f"Unsupported crop_id for price model: {crop_id}"
        )

    market_info = market_mapping.get(market_id)

    if market_info is None:
        raise ValueError(
            f"Unsupported market_id for price model: {market_id}"
        )

    market, state, district = market_info

    return commodity, state, district, market


def _create_feature_row(
    commodity: str,
    state: str,
    district: str,
    market: str,
    prediction_date,
    working_prices: list[float],
) -> pd.DataFrame:

    lag_1 = working_prices[-1]
    lag_2 = working_prices[-2]
    lag_3 = working_prices[-3]

    rolling_mean_3 = (
        lag_1 + lag_2 + lag_3
    ) / 3.0

    return pd.DataFrame(
        [
            {
                "lag_1": lag_1,
                "lag_2": lag_2,
                "lag_3": lag_3,
                "rolling_mean_3": rolling_mean_3,
                "month": prediction_date.month,
                "day": prediction_date.day,
                "day_of_week": prediction_date.weekday(),
                "Commodity": commodity,
                "State": state,
                "District": district,
                "Market": market,
            }
        ]
    )


async def predict_price(
    crop_id: int,
    market_id: int,
    days_ahead: int,
    historical_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    if not 1 <= days_ahead <= 30:
        raise ValueError(
            "days_ahead must be between 1 and 30"
        )

    if len(historical_data) < 3:
        raise ValueError(
            "At least 3 historical records are required"
        )

    bundle = _load_model_bundle()

    model = bundle["model"]
    preprocessor = bundle["preprocessor"]

    commodity, state, district, market = (
        _get_market_metadata(
            crop_id,
            market_id,
        )
    )

    df = _build_history_dataframe(
        historical_data
    )

    latest_date = df["date"].max().date()

    working_prices = list(
        df["modal_price"].astype(float)
    )

    predictions = []

    for step in range(1, days_ahead + 1):

        prediction_date = (
            latest_date
            + timedelta(days=step)
        )

        feature_row = _create_feature_row(
            commodity=commodity,
            state=state,
            district=district,
            market=market,
            prediction_date=prediction_date,
            working_prices=working_prices,
        )

        encoded_features = preprocessor.transform(
            feature_row
        )

        predicted_price = float(
            model.predict(encoded_features)[0]
        )

        predicted_price = max(
            0.0,
            predicted_price,
        )

        predictions.append(
            {
                "date": prediction_date.isoformat(),
                "predicted_price": round(
                    predicted_price,
                    2,
                ),
            }
        )

        working_prices.append(
            predicted_price
        )

    return predictions