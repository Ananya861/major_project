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

    humidity: weather humidity if present, else soil moisture (0–100 proxy).
    soil_type: ignored (not in the public dataset).
    Missing values stay as NaN so the fitted SimpleImputer can fill them.
    """
    nitrogen = _as_float(soil_data.get("nitrogen", soil_data.get("N")))
    phosphorus = _as_float(soil_data.get("phosphorus", soil_data.get("P")))
    potassium = _as_float(soil_data.get("potassium", soil_data.get("K")))
    ph = _as_float(soil_data.get("ph"))
    temperature = _as_float(soil_data.get("temperature", soil_data.get("temp")))
    humidity = _as_float(soil_data.get("humidity"))
    if humidity is None:
        humidity = _as_float(soil_data.get("moisture"))
    rainfall = _as_float(soil_data.get("rainfall"))

    row = {
        "N": _clip("N", nitrogen),
        "P": _clip("P", phosphorus),
        "K": _clip("K", potassium),
        "temperature": _clip("temperature", temperature),
        "humidity": _clip("humidity", humidity),
        "ph": _clip("ph", ph),
        "rainfall": _clip("rainfall", rainfall),
    }
    return pd.DataFrame([row], columns=NUMERIC_FEATURES)
