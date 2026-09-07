"""
Member 1 crop-model adapter.

Keeps the rest of the Member 3 backend independent from the ML implementation.
"""

from __future__ import annotations

from typing import Any

from app.ml.crop_inference import CropModelNotAvailable, recommend_crops
from app.services.model_adapters.exceptions import ModelNotIntegratedError


async def predict_crop(soil_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run Member 1's trained crop recommendation model.

    The model is loaded from app/artifacts/crop_pipeline.joblib by
    app.ml.crop_inference.recommend_crops().
    """
    if "weather" in soil_data and isinstance(soil_data["weather"], dict):
        w = soil_data["weather"]
        soil_data.setdefault("temp", w.get("temp"))
        soil_data.setdefault("temperature", w.get("temp"))
        soil_data.setdefault("humidity", w.get("humidity"))
        soil_data.setdefault("rainfall", w.get("rainfall"))

    try:
        return recommend_crops(soil_data, top_k=3)
    except CropModelNotAvailable as exc:
        raise ModelNotIntegratedError(str(exc)) from exc

