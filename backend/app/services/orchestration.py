"""
Central orchestration: farm/soil/weather + ML adapters + PostgreSQL.

Member 1 and Member 2 must not change this file. Connect models only in:

    app/services/model_adapters/crop_model_adapter.py
    app/services/model_adapters/price_model_adapter.py
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Crop, CropRecommendation, Farm, Market, MarketPrice, PricePrediction, SoilData
from app.services.model_adapters.crop_model_adapter import predict_crop as crop_adapter_predict
from app.services.model_adapters.exceptions import ModelNotIntegratedError
from app.services.model_adapters.price_model_adapter import predict_price as price_adapter_predict
from app.services.weather_service import get_weather

MIN_HISTORICAL_PRICES = 3
MAX_DAYS_AHEAD = 30
RECO_DEDUP_HOURS = 24


def _model_unavailable(exc: ModelNotIntegratedError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.detail)


def _soil_has_values(soil: SoilData) -> bool:
    return any(
        value is not None
        for value in (
            soil.ph,
            soil.nitrogen,
            soil.phosphorus,
            soil.potassium,
            soil.moisture,
            soil.soil_type,
        )
    )


def _normalize_crop_output(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Crop model returned no recommendations",
        )
    items: list[dict[str, Any]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("crop", "")).strip()
        if not name:
            continue
        try:
            confidence = float(entry.get("confidence", 0))
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Crop model returned an invalid confidence value",
            ) from exc
        if confidence > 1.0:
            confidence = confidence / 100.0
        if not 0.0 <= confidence <= 1.0:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Crop model confidence must be between 0 and 1",
            )
        items.append({"crop": name, "confidence": confidence})
    if not items:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Crop model returned no valid recommendations",
        )
    items.sort(key=lambda row: row["confidence"], reverse=True)
    return items


def _normalize_price_output(raw: Any, days_ahead: int) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Price model returned no predictions",
        )
    items: list[dict[str, Any]] = []
    seen_dates: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        date_str = str(entry.get("date", "")).strip()
        try:
            predicted_day = date.fromisoformat(date_str)
            price = float(entry["predicted_price"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Price model returned invalid date or predicted_price values",
            ) from exc
        if price < 0:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Price model returned a negative predicted_price",
            )
        iso = predicted_day.isoformat()
        if iso in seen_dates:
            continue
        seen_dates.add(iso)
        items.append({"date": iso, "predicted_price": round(price, 2)})
    if not items:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Price model returned no valid predictions",
        )
    items.sort(key=lambda row: row["date"])
    return items[:days_ahead]


async def _latest_soil(db: AsyncSession, farm_id: int) -> SoilData | None:
    result = await db.execute(
        select(SoilData)
        .where(SoilData.farm_id == farm_id)
        .order_by(SoilData.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _weather_for_farm(farm: Farm, db: AsyncSession) -> dict[str, Any] | None:
    try:
        weather = await get_weather(farm.latitude, farm.longitude, db)
    except HTTPException:
        return None
    return {
        "temp": weather.get("temp"),
        "humidity": weather.get("humidity"),
        "rainfall": weather.get("rainfall"),
        "forecast": weather.get("forecast"),
    }


async def get_crop_recommendations(farm_id: int, db: AsyncSession) -> dict[str, Any]:
    """
    Load farm + latest soil (+ weather when available), call Member 1's adapter,
    map crop names to the crop table, and persist crop_recommendation rows.
    """
    farm = (
        await db.execute(select(Farm).where(Farm.farm_id == farm_id))
    ).scalar_one_or_none()
    if farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    soil = await _latest_soil(db, farm.farm_id)
    if soil is None or not _soil_has_values(soil):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add a soil reading for this farm before requesting a recommendation",
        )

    weather = await _weather_for_farm(farm, db)
    model_input = {
        "ph": soil.ph,
        "nitrogen": soil.nitrogen,
        "phosphorus": soil.phosphorus,
        "potassium": soil.potassium,
        "moisture": soil.moisture,
        "soil_type": soil.soil_type,
        "farm": {
            "farm_id": farm.farm_id,
            "latitude": farm.latitude,
            "longitude": farm.longitude,
            "area_acres": farm.area_acres,
        },
        "weather": weather,
    }

    try:
        raw = await crop_adapter_predict(model_input)
    except ModelNotIntegratedError as exc:
        raise _model_unavailable(exc) from exc

    ranked = _normalize_crop_output(raw)
    generated_at = datetime.now(timezone.utc)
    dedup_after = generated_at - timedelta(hours=RECO_DEDUP_HOURS)
    recommendations: list[dict[str, Any]] = []

    for entry in ranked:
        crop_name = str(entry["crop"])
        confidence = float(entry["confidence"])
        crop = (
            await db.execute(select(Crop).where(func.lower(Crop.name) == crop_name.lower()))
        ).scalar_one_or_none()
        if crop is None:
            recommendations.append(
                {"crop_id": None, "crop": crop_name, "confidence": confidence}
            )
            continue

        existing = (
            await db.execute(
                select(CropRecommendation)
                .where(
                    CropRecommendation.farm_id == farm.farm_id,
                    CropRecommendation.crop_id == crop.crop_id,
                    CropRecommendation.generated_at >= dedup_after,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing is None:
            db.add(
                CropRecommendation(
                    farm_id=farm.farm_id,
                    crop_id=crop.crop_id,
                    confidence_score=confidence,
                    generated_at=generated_at,
                )
            )
        recommendations.append(
            {"crop_id": crop.crop_id, "crop": crop.name, "confidence": confidence}
        )

    await db.commit()
    return {
        "farm_id": farm.farm_id,
        "recommendations": recommendations,
        "generated_at": generated_at,
    }


async def get_price_predictions(
    crop_id: int,
    market_id: int,
    days_ahead: int,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    Load historical mandi prices, call Member 2's adapter, and persist
    price_prediction rows without duplicating crop/market/predicted_date.
    """
    if days_ahead < 1 or days_ahead > MAX_DAYS_AHEAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"days_ahead must be between 1 and {MAX_DAYS_AHEAD}",
        )

    crop = (
        await db.execute(select(Crop).where(Crop.crop_id == crop_id))
    ).scalar_one_or_none()
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")

    market = (
        await db.execute(select(Market).where(Market.market_id == market_id))
    ).scalar_one_or_none()
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")

    history_rows = (
        await db.execute(
            select(MarketPrice)
            .where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
            )
            .order_by(MarketPrice.date.asc())
        )
    ).scalars().all()
    if len(history_rows) < MIN_HISTORICAL_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Insufficient historical market data for this crop and market "
                f"(need at least {MIN_HISTORICAL_PRICES} records)"
            ),
        )

    historical_data = [
        {
            "date": row.date.isoformat(),
            "min_price": row.min_price,
            "max_price": row.max_price,
            "modal_price": row.modal_price,
        }
        for row in history_rows
    ]

    try:
        raw = await price_adapter_predict(
            crop_id=crop_id,
            market_id=market_id,
            days_ahead=days_ahead,
            historical_data=historical_data,
        )
    except ModelNotIntegratedError as exc:
        raise _model_unavailable(exc) from exc

    forecast = _normalize_price_output(raw, days_ahead)
    generated_at = datetime.now(timezone.utc)

    for entry in forecast:
        predicted_day = date.fromisoformat(entry["date"])
        existing = (
            await db.execute(
                select(PricePrediction)
                .where(
                    PricePrediction.crop_id == crop_id,
                    PricePrediction.market_id == market_id,
                    cast(PricePrediction.predicted_date, Date) == predicted_day,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        db.add(
            PricePrediction(
                crop_id=crop_id,
                market_id=market_id,
                predicted_date=datetime(
                    predicted_day.year,
                    predicted_day.month,
                    predicted_day.day,
                    tzinfo=timezone.utc,
                ),
                predicted_price=float(entry["predicted_price"]),
                generated_at=generated_at,
            )
        )

    await db.commit()
    return {
        "crop_id": crop_id,
        "market_id": market_id,
        "predictions": forecast,
        "generated_at": generated_at,
        "days_ahead": days_ahead,
    }
