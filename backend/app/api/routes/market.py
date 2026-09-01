"""Mandi prices (cached) and stubbed price forecasts."""

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Crop, Farmer, Market, MarketPrice, PricePrediction
from app.schemas.market import MarketPriceOut, PriceForecastItem, PricePredictionOut
from app.services.mandi_service import get_mandi_prices
from app.services.orchestration import predict_price

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=list[MarketPriceOut])
async def read_market_prices(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[MarketPrice]:
    crop = (
        await db.execute(select(Crop).where(Crop.crop_id == crop_id))
    ).scalar_one_or_none()
    market = (
        await db.execute(select(Market).where(Market.market_id == market_id))
    ).scalar_one_or_none()
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")

    today = date.today()
    cached = (
        await db.execute(
            select(MarketPrice).where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date == today,
            )
        )
    ).scalar_one_or_none()
    if cached is not None:
        return [cached]

    records = await get_mandi_prices(crop.name, market.name)
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No mandi prices returned for this crop/market",
        )

    # Prefer a record whose arrival date is today; otherwise take the first row.
    chosen = next((r for r in records if r.get("date") == today), records[0])
    row = MarketPrice(
        crop_id=crop_id,
        market_id=market_id,
        date=today,
        min_price=chosen.get("min_price"),
        max_price=chosen.get("max_price"),
        modal_price=chosen.get("modal_price"),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return [row]


@router.get("/predict", response_model=PricePredictionOut)
async def predict_market_price(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    days_ahead: int = Query(7, ge=1, le=30),
    _farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> PricePredictionOut:
    crop = (
        await db.execute(select(Crop).where(Crop.crop_id == crop_id))
    ).scalar_one_or_none()
    market = (
        await db.execute(select(Market).where(Market.market_id == market_id))
    ).scalar_one_or_none()
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    if market is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")

    forecast = predict_price(crop_id, market_id, days_ahead)
    now = datetime.now(timezone.utc)
    items: list[PriceForecastItem] = []
    for entry in forecast:
        predicted_day = date.fromisoformat(entry["date"])
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
                generated_at=now,
            )
        )
        items.append(
            PriceForecastItem(
                date=entry["date"],
                predicted_price=float(entry["predicted_price"]),
            )
        )
    await db.commit()
    return PricePredictionOut(
        crop_id=crop_id,
        market_id=market_id,
        days_ahead=days_ahead,
        forecast=items,
    )
