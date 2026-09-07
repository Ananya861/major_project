"""Mandi prices (cached) and price forecasts via the ML adapter."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Crop, Farmer, Market, MarketPrice
from app.schemas.market import MarketPriceOut, PriceForecastItem, PricePredictionOut
from app.services.mandi_service import get_mandi_prices
from app.services.orchestration import get_price_predictions

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=list[MarketPriceOut])
async def read_market_prices(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[MarketPriceOut]:
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
        out = MarketPriceOut.model_validate(cached)
        out.cached = True
        return [out]

    # Attempt to fetch live arrival records from data.gov.in
    live_records: list[dict] = []
    fetch_error: HTTPException | None = None
    try:
        live_records = await get_mandi_prices(crop.name, market.name)
    except HTTPException as exc:
        fetch_error = exc

    if live_records:
        chosen = next((r for r in live_records if r.get("date") == today), live_records[0])
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
        out = MarketPriceOut.model_validate(row)
        out.cached = False
        return [out]

    # Graceful fallback: check if PostgreSQL has the latest previously recorded price
    fallback = (
        await db.execute(
            select(MarketPrice)
            .where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
            )
            .order_by(MarketPrice.date.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if fallback is not None:
        out = MarketPriceOut.model_validate(fallback)
        out.cached = True
        return [out]

    if fetch_error is not None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Official Mandi API (data.gov.in) is currently unreachable "
                f"({fetch_error.detail}) and no cached market price exists for this crop and market."
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No mandi prices returned for this crop/market",
    )



@router.get("/predict", response_model=PricePredictionOut)
async def predict_market_price(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    days_ahead: int = Query(7, ge=1, le=30),
    _farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> PricePredictionOut:
    payload = await get_price_predictions(crop_id, market_id, days_ahead, db)
    items = [
        PriceForecastItem(date=entry["date"], predicted_price=float(entry["predicted_price"]))
        for entry in payload["predictions"]
    ]
    return PricePredictionOut(
        crop_id=crop_id,
        market_id=market_id,
        days_ahead=days_ahead,
        forecast=items,
    )
