"""Mandi prices (cached/live), price forecasts, and MSP comparison."""

from datetime import date
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models.farmer import Farm, Farmer
from app.models.market import Crop, CropRecommendation, Market, MarketPrice
from app.schemas.market import MarketPriceOut, PriceForecastItem, PricePredictionOut
from app.services.alerts import check_market_price_updates
from app.services.mandi_service import get_mandi_prices
from app.services.orchestration import get_price_predictions

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)

MSP_DATA_PATH = Path(__file__).resolve().parents[3] / "ml" / "data" / "msp_prices.json"
with MSP_DATA_PATH.open("r", encoding="utf-8") as f:
    MSP_PRICES = {item["commodity"].lower(): item for item in json.load(f)}


@router.get("/prices", response_model=list[MarketPriceOut])
async def get_market_prices(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
) -> list[MarketPriceOut]:
    crop_result = await db.execute(
        select(Crop).where(Crop.crop_id == crop_id)
    )
    crop = crop_result.scalar_one_or_none()

    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    market_result = await db.execute(
        select(Market).where(Market.market_id == market_id)
    )
    market = market_result.scalar_one_or_none()

    if market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found",
        )

    today = date.today()

    # Return cached price if already present for today
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

    # Get the previously stored price before updating it (used for alert detection)
    previous_result = await db.execute(
        select(MarketPrice)
        .where(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
        )
        .order_by(MarketPrice.date.desc())
    )
    previous_price = previous_result.scalars().first()
    previous_modal_price = (
        float(previous_price.modal_price)
        if previous_price is not None and previous_price.modal_price is not None
        else None
    )

    # Attempt to fetch live arrival records from data.gov.in
    live_records: list[dict] = []
    fetch_error: HTTPException | None = None
    try:
        live_records = await get_mandi_prices(
            crop_name=crop.name,
            market_name=market.name,
            state_name=market.state,
            district_name=market.district,
        )
    except HTTPException as exc:
        fetch_error = exc

    if live_records:
        chosen = next(
            (r for r in live_records if r.get("date") == today),
            live_records[0],
        )
        arrival_date = chosen.get("date") or today
        min_price = chosen.get("min_price")
        max_price = chosen.get("max_price")
        modal_price = chosen.get("modal_price")

        existing_result = await db.execute(
            select(MarketPrice).where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date == arrival_date,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.min_price = min_price
            existing.max_price = max_price
            existing.modal_price = modal_price
            price_row = existing
        else:
            price_row = MarketPrice(
                crop_id=crop_id,
                market_id=market_id,
                date=arrival_date,
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
            )
            db.add(price_row)

        await db.flush()

        # Check for price changes and notify interested farmers
        if previous_modal_price is not None and modal_price is not None:
            farmer_subq = (
                select(Farm.farmer_id)
                .join(CropRecommendation, CropRecommendation.farm_id == Farm.farm_id)
                .where(CropRecommendation.crop_id == crop_id)
                .limit(1)
            )
            target_farmer_id = (await db.execute(farmer_subq)).scalar_one_or_none()
            if target_farmer_id is None:
                target_farmer_id = (
                    await db.execute(select(Farmer.farmer_id).limit(1))
                ).scalar_one_or_none()

            if target_farmer_id is not None:
                try:
                    await check_market_price_updates(
                        db=db,
                        crop_id=crop_id,
                        market_id=market_id,
                        previous_modal_price=previous_modal_price,
                        current_modal_price=float(modal_price),
                        farmer_id=target_farmer_id,
                    )
                except Exception:
                    pass

        await db.commit()
        await db.refresh(price_row)
        out = MarketPriceOut.model_validate(price_row)
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
        detail="No market price data available",
    )


@router.get("/predict", response_model=PricePredictionOut)
async def predict_market_price(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    days_ahead: int = Query(7, ge=1, le=30),
    _farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> PricePredictionOut:
    payload = await get_price_predictions(
        crop_id=crop_id,
        market_id=market_id,
        days_ahead=days_ahead,
        db=db,
    )
    items = [
        PriceForecastItem(
            date=entry["date"],
            predicted_price=float(entry["predicted_price"]),
        )
        for entry in payload["predictions"]
    ]
    return PricePredictionOut(
        crop_id=crop_id,
        market_id=market_id,
        days_ahead=days_ahead,
        forecast=items,
    )


MSP_CROP_ALIASES: dict[str, str] = {
    "chickpea": "bengal gram(gram)(whole)",
    "mungbean": "green gram(moong)(whole)",
    "paddy": "paddy(common)",
    "soybean": "soyabean",
    "urad": "blackgram",
    "tur": "pigeonpeas",
    "arhar": "pigeonpeas",
    "masur": "lentil",
}


@router.get("/msp")
async def get_msp_comparison(
    crop_id: int = Query(...),
    market_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    crop_result = await db.execute(
        select(Crop).where(Crop.crop_id == crop_id)
    )
    crop = crop_result.scalar_one_or_none()

    if crop is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    market_result = await db.execute(
        select(Market).where(Market.market_id == market_id)
    )
    market = market_result.scalar_one_or_none()

    if market is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found",
        )

    # 1. Resolve MSP for the crop
    crop_key = crop.name.lower().strip()
    msp = MSP_PRICES.get(crop_key)
    if msp is None and crop_key in MSP_CROP_ALIASES:
        msp = MSP_PRICES.get(MSP_CROP_ALIASES[crop_key].lower())

    # 2. Check cached market price in database
    latest_result = await db.execute(
        select(MarketPrice)
        .where(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
        )
        .order_by(MarketPrice.date.desc())
    )
    latest_price = latest_result.scalars().first()

    # 3. If price is not cached or is stale, attempt to fetch live from data.gov.in
    today = date.today()
    if latest_price is None or latest_price.date != today:
        try:
            live_records = await get_mandi_prices(
                crop_name=crop.name,
                market_name=market.name,
                state_name=market.state,
                district_name=market.district,
            )
            if live_records:
                chosen = next(
                    (r for r in live_records if r.get("date") == today),
                    live_records[0],
                )
                arrival_date = chosen.get("date") or today
                min_p = chosen.get("min_price")
                max_p = chosen.get("max_price")
                modal_p = chosen.get("modal_price")

                existing_result = await db.execute(
                    select(MarketPrice).where(
                        MarketPrice.crop_id == crop_id,
                        MarketPrice.market_id == market_id,
                        MarketPrice.date == arrival_date,
                    )
                )
                existing = existing_result.scalar_one_or_none()
                if existing:
                    existing.min_price = min_p
                    existing.max_price = max_p
                    existing.modal_price = modal_p
                    price_row = existing
                else:
                    price_row = MarketPrice(
                        crop_id=crop_id,
                        market_id=market_id,
                        date=arrival_date,
                        min_price=min_p,
                        max_price=max_p,
                        modal_price=modal_p,
                    )
                    db.add(price_row)

                await db.commit()
                await db.refresh(price_row)
                latest_price = price_row
        except Exception:
            pass

    # If still no price is available, return 404 with exact requested message
    if latest_price is None or latest_price.modal_price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No mandi price data available for this crop and market.",
        )

    modal_price = float(latest_price.modal_price)
    raw_msp = msp.get("msp_per_quintal") if msp else None
    msp_price = float(raw_msp) if raw_msp is not None else None

    if msp_price is not None:
        difference = modal_price - msp_price
        difference_percent = ((difference / msp_price) * 100) if msp_price else 0.0
        if difference > 0:
            status_text = "ABOVE_MSP"
        elif difference < 0:
            status_text = "BELOW_MSP"
        else:
            status_text = "AT_MSP"
    else:
        difference = 0.0
        difference_percent = 0.0
        status_text = "NOT_APPLICABLE"

    return {
        "crop_id": crop_id,
        "crop": crop.name,
        "market_id": market_id,
        "market": market.name,
        "state": market.state,
        "district": market.district,
        "market_price_date": latest_price.date,
        "modal_price": modal_price,
        "msp": msp_price,
        "season": msp.get("season") if msp else None,
        "marketing_year": msp.get("marketing_year", "2026-27") if msp else "2026-27",
        "difference": round(difference, 2) if difference is not None else None,
        "difference_percent": round(difference_percent, 2) if difference_percent is not None else None,
        "status": status_text,
    }




