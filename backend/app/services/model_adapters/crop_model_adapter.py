"""
Member 1 crop-model adapter.

Keeps the rest of the Member 3 backend independent from the ML implementation.
"""

from __future__ import annotations

from typing import Any

from app.ml.crop_inference import CropModelNotAvailable, recommend_crops


async def predict_crop(soil_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run Member 1's trained crop recommendation model.

    The model is loaded from app/artifacts/crop_pipeline.joblib by
    app.ml.crop_inference.recommend_crops().
    """
    try:
        return recommend_crops(soil_data, top_k=3)
    except CropModelNotAvailable:
        raise
