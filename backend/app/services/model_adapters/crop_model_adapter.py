"""
Crop recommendation adapter — Member 1 integration point.

The rest of the backend (orchestration.py and API routes) must keep calling
`predict_crop` from this module. When Member 1's trained model is ready,
change only this file.

Expected input (`soil_data`) is a dict built by orchestration, typically:

    {
        "ph": float | None,
        "nitrogen": float | None,
        "phosphorus": float | None,
        "potassium": float | None,
        "moisture": float | None,
        "soil_type": str | None,
        "farm": {
            "farm_id": int,
            "latitude": float,
            "longitude": float,
            "area_acres": float,
        },
        "weather": {
            "temp": float | None,
            "humidity": float | None,
            "rainfall": float | None,
            "forecast": list | dict | None,
        } | None,
    }

Expected return:

    [{"crop": "Rice", "confidence": 0.87}, ...]

Do not train a model here. Do not return hardcoded crop rankings.
"""

from __future__ import annotations

from typing import Any

from app.services.model_adapters.exceptions import ModelNotIntegratedError


async def predict_crop(soil_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Run Member 1's crop recommendation model.

    MEMBER 1 — connect your model here, for example:

        from member1_crop_package import CropRecommender

        _model = CropRecommender.load("path/or/artifact")

        async def predict_crop(soil_data: dict) -> list[dict]:
            return _model.predict(soil_data)

    Sync `predict` functions are fine: orchestration will `await` this adapter;
    call your sync model inside this function (no need to change callers).
    """
    _ = soil_data  # reserved for Member 1's model input
    raise ModelNotIntegratedError(
        "Crop recommendation ML model is not integrated yet. "
        "Member 1: load the trained model in "
        "app/services/model_adapters/crop_model_adapter.py."
    )
