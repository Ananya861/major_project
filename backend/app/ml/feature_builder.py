"""
Map the /recommend/crop soil+weather payload onto dataset columns.

Dataset columns: N, P, K, temperature, humidity, ph, rainfall.
API extras moisture and soil_type are not training features (see ml/data/raw/SOURCE.md).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.ml.schema import FEATURE_BOUNDS, NUMERIC_FEATURES


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clip(name: str, value: float | None) -> float | None:
    if value is None:
        return None
    low, high = FEATURE_BOUNDS[name]
    return float(min(high, max(low, value)))


def payload_to_frame(soil_data: dict) -> pd.DataFrame:
    """
    Build a one-row DataFrame with the training feature names.

    - humidity: relative atmospheric humidity from weather (0–100%).
    - moisture: soil moisture percentage (0–100%), kept distinct from atmospheric humidity.
    - rainfall: cumulative seasonal rainfall in mm (training mean ~103.5 mm).
      Instantaneous 1-hour precipitation from weather APIs (frequently 0.0 mm)
      is not seasonal rainfall. Missing/non-positive values stay as NaN so the
      fitted SimpleImputer can impute the training dataset median (~94.8 mm).
    - soil_type: ignored (not in the public training dataset).
    """
    nitrogen = _as_float(soil_data.get("nitrogen", soil_data.get("N")))
    phosphorus = _as_float(soil_data.get("phosphorus", soil_data.get("P")))
    potassium = _as_float(soil_data.get("potassium", soil_data.get("K")))
    ph = _as_float(soil_data.get("ph"))
    temperature = _as_float(soil_data.get("temperature", soil_data.get("temp")))
    humidity = _as_float(soil_data.get("humidity"))
    moisture = _as_float(soil_data.get("moisture"))

    # The crop recommendation model expects cumulative seasonal rainfall (mm).
    # 1-hour precipitation from weather APIs is typically 0.0 mm when it is not actively raining.
    # Passing 0.0 mm triggers an out-of-distribution drought state (minimum tree split is ~30 mm).
    # If seasonal rainfall is missing or non-positive, leave as None so SimpleImputer handles it.
    raw_rain = soil_data.get("seasonal_rainfall", soil_data.get("rainfall"))
    rainfall = _as_float(raw_rain)
    if rainfall is not None and rainfall <= 0.0:
        rainfall = None

    row = {
        "N": _clip("N", nitrogen),
        "P": _clip("P", phosphorus),
        "K": _clip("K", potassium),
        "temperature": _clip("temperature", temperature),
        "humidity": _clip("humidity", humidity),
        "ph": _clip("ph", ph),
        "rainfall": _clip("rainfall", rainfall),
    }
    if moisture is not None:
        row["moisture"] = moisture

    return pd.DataFrame([row])
