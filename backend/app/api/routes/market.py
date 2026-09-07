from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.market import Crop, Market, MarketPrice
from app.services.alerts import check_market_price_updates
from app.services.mandi_service import get_mandi_prices
from app.services.orchestration import get_price_predictions


router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


MSP_PRICES = {
    "Wheat": {
        "season": "Rabi",
        "marketing_year": "2026-27",
        "msp_per_quintal": 2585,
    },
    "Maize": {
        "season": "Kharif",
        "marketing_year": "2026-27",
        "msp_per_quintal": 2410,
    },
    "Groundnut": {
        "season": "Kharif",
        "marketing_year": "2026-27",
        "msp_per_quintal": 7517,
    },
    "Soyabean": {
        "season": "Kharif",
        "marketing_year": "2026-27",
        "msp_per_quintal": 5708,
    },
}


@router.get("/prices")
async def get_market_prices(
    crop_id: int,
    market_id: int,
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

    # Get the previously stored price before updating it.
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
        if previous_price is not None
        and previous_price.modal_price is not None
        else None
    )

    mandi_records = await get_mandi_prices(
        crop_name=crop.name,
        market_name=market.name,
        state_name=market.state,
        district_name=market.district,
    )

    today = date.today()

    current_record = next(
        (
            record
            for record in mandi_records
            if record.get("date") == today
        ),
        None,
    )

    if current_record is not None:
        min_price = current_record.get("min_price")
        max_price = current_record.get("max_price")
        modal_price = current_record.get("modal_price")

        existing_result = await db.execute(
            select(MarketPrice).where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
                MarketPrice.date == today,
            )
        )

        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.min_price = min_price
            existing.max_price = max_price
            existing.modal_price = modal_price
            price = existing
        else:
            price = MarketPrice(
                crop_id=crop_id,
                market_id=market_id,
                date=today,
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
            )
            db.add(price)

        await db.flush()

        # Create a notification when the new price changes
        # significantly compared with the previous stored price.
        # This uses the existing farmer relationship through
        # the latest notification recipient.
        if (
            previous_modal_price is not None
            and modal_price is not None
        ):
            farmer_result = await db.execute(
                select(PricePrediction)
                .where(
                    PricePrediction.crop_id == crop_id,
                    PricePrediction.market_id == market_id,
                )
                .order_by(PricePrediction.date.desc())
            )

            latest_prediction = (
                farmer_result.scalars().first()
            )

            if latest_prediction is not None:
                await check_market_price_updates(
                    db=db,
                    crop_id=crop_id,
                    market_id=market_id,
                    previous_modal_price=previous_modal_price,
                    current_modal_price=float(
                        modal_price
                    ),
                    farmer_id=latest_prediction.farmer_id,
                )

        await db.commit()
        await db.refresh(price)

    else:
        latest_result = await db.execute(
            select(MarketPrice)
            .where(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
            )
            .order_by(MarketPrice.date.desc())
        )

        price = latest_result.scalars().first()

        if price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No market price data available",
            )

    return {
        "price_id": price.price_id,
        "crop_id": crop_id,
        "market_id": market_id,
        "date": price.date,
        "min_price": price.min_price,
        "max_price": price.max_price,
        "modal_price": price.modal_price,
    }


@router.get("/predict")
async def predict_market_price(
    crop_id: int,
    market_id: int,
    days_ahead: int = 5,
    db: AsyncSession = Depends(get_db),
):
    return await get_price_predictions(
        db=db,
        crop_id=crop_id,
        market_id=market_id,
        days_ahead=days_ahead,
    )


@router.get("/msp")
async def get_msp_comparison(
    crop_id: int,
    market_id: int,
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

    msp = MSP_PRICES.get(crop.name)

    if msp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MSP data is not available for {crop.name}",
        )

    latest_result = await db.execute(
        select(MarketPrice)
        .where(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
        )
        .order_by(MarketPrice.date.desc())
    )

    latest_price = latest_result.scalars().first()

    if latest_price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No market price data available",
        )

    modal_price = float(latest_price.modal_price)
    msp_price = float(msp["msp_per_quintal"])

    difference = modal_price - msp_price

    difference_percent = (
        (difference / msp_price) * 100
        if msp_price
        else 0
    )

    if difference > 0:
        status_text = "ABOVE_MSP"
    elif difference < 0:
        status_text = "BELOW_MSP"
    else:
        status_text = "AT_MSP"

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
        "season": msp["season"],
        "marketing_year": msp["marketing_year"],
        "difference": round(difference, 2),
        "difference_percent": round(
            difference_percent,
            2,
        ),
        "status": status_text,
    }