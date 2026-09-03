"""
Price prediction adapter — Member 2 integration point.

The rest of the backend (orchestration.py and API routes) must keep calling
`predict_price` from this module. When Member 2's trained model is ready,
change only this file.

Expected arguments:

    crop_id: int
    market_id: int
    days_ahead: int
    historical_data: list of dicts, chronological, e.g.
        [
            {
                "date": "2026-08-01",
                "min_price": 1800.0,
                "max_price": 2200.0,
                "modal_price": 2000.0,
            },
            ...
        ]

Expected return:

    [{"date": "YYYY-MM-DD", "predicted_price": 2500.0}, ...]

Do not train a model here. Do not return hardcoded price series.
"""

from __future__ import annotations

from typing import Any

from app.services.model_adapters.exceptions import ModelNotIntegratedError


async def predict_price(
    crop_id: int,
    market_id: int,
    days_ahead: int,
    historical_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Run Member 2's mandi price forecast model.

    MEMBER 2 — connect your model here, for example:

        from member2_price_package import PriceForecaster

        _model = PriceForecaster.load("path/or/artifact")

        async def predict_price(crop_id, market_id, days_ahead, historical_data):
            return _model.forecast(
                crop_id=crop_id,
                market_id=market_id,
                days_ahead=days_ahead,
                history=historical_data,
            )
    """
    _ = (crop_id, market_id, days_ahead, historical_data)
    raise ModelNotIntegratedError(
        "Price prediction ML model is not integrated yet. "
        "Member 2: load the trained model in "
        "app/services/model_adapters/price_model_adapter.py."
    )
