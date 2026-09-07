"""Price, MSP, and weather alert services."""

from datetime import date, datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import MarketPrice
from app.models.notification import Notification
from app.models.market import MarketPrice, PricePrediction


MSP_PRICES = {
    "Wheat": 2585.0,
    "Maize": 2410.0,
    "Groundnut": 7517.0,
    "Soyabean": 5708.0,
}


async def _has_unread_today(
    db: AsyncSession,
    farmer_id: int,
    notification_type: str,
) -> bool:
    today_start = datetime.combine(date.today(), datetime.min.time())

    result = await db.execute(
        select(Notification)
        .where(
            Notification.farmer_id == farmer_id,
            Notification.type == notification_type,
            Notification.created_at >= today_start,
            Notification.is_read == False,
        )
        .limit(1)
    )

    return result.scalar_one_or_none() is not None


async def check_price_alerts(db: AsyncSession):
    """Create alerts when forecasts differ significantly from current prices/MSP."""

    result = await db.execute(
        select(PricePrediction)
        .order_by(desc(PricePrediction.date))
    )
    predictions = result.scalars().all()

    created = 0

    for prediction in predictions:
        price_result = await db.execute(
            select(MarketPrice)
            .where(
                MarketPrice.crop_id == prediction.crop_id,
                MarketPrice.market_id == prediction.market_id,
            )
            .order_by(desc(MarketPrice.date))
            .limit(1)
        )

        market_price = price_result.scalar_one_or_none()

        if not market_price or market_price.modal_price is None:
            continue

        predicted_price = float(prediction.predicted_price)
        current_price = float(market_price.modal_price)

        # Alert when forecast differs from current market price by 10%+
        if current_price > 0:
            change_percent = (
                (predicted_price - current_price) / current_price
            ) * 100

            if abs(change_percent) >= 10:
                if not await _has_unread_today(
                    db,
                    prediction.farmer_id,
                    "PRICE_ALERT",
                ):
                    direction = "increase" if change_percent > 0 else "decrease"

                    notification = Notification(
                        farmer_id=prediction.farmer_id,
                        type="PRICE_ALERT",
                        title="Market Price Forecast Alert",
                        message=(
                            f"Expected price {direction} of "
                            f"{abs(change_percent):.1f}% for the selected crop "
                            f"and market."
                        ),
                        is_read=False,
                    )

                    db.add(notification)
                    created += 1

        # MSP comparison
        crop_result = await db.execute(
            select(MarketPrice)
            .where(
                MarketPrice.crop_id == prediction.crop_id,
            )
            .order_by(desc(MarketPrice.date))
            .limit(1)
        )

        crop_price = crop_result.scalar_one_or_none()

        if crop_price is None:
            continue

        # Crop name is obtained from the relationship if available.
        crop_name = None
        if hasattr(crop_price, "crop") and crop_price.crop:
            crop_name = crop_price.crop.name

        msp = MSP_PRICES.get(crop_name)

        if msp is None:
            continue

        msp_difference_percent = ((predicted_price - msp) / msp) * 100

        if abs(msp_difference_percent) >= 5:
            if not await _has_unread_today(
                db,
                prediction.farmer_id,
                "MSP_ALERT",
            ):
                direction = "above" if msp_difference_percent > 0 else "below"

                notification = Notification(
                    farmer_id=prediction.farmer_id,
                    type="MSP_ALERT",
                    title="MSP Comparison Alert",
                    message=(
                        f"Forecast price is {abs(msp_difference_percent):.1f}% "
                        f"{direction} the MSP of ₹{msp:.0f}/quintal."
                    ),
                    is_read=False,
                )

                db.add(notification)
                created += 1

    if created:
        await db.commit()

    return created


async def check_market_price_updates(
    db: AsyncSession,
    crop_id: int,
    market_id: int,
    previous_modal_price: float | None,
    current_modal_price: float | None,
    farmer_id: int,
):
    """Create a notification when the latest mandi price changes by 5%+."""

    if (
        previous_modal_price is None
        or current_modal_price is None
        or previous_modal_price <= 0
    ):
        return False

    change_percent = (
        (current_modal_price - previous_modal_price)
        / previous_modal_price
    ) * 100

    if abs(change_percent) < 5:
        return False

    if await _has_unread_today(
        db,
        farmer_id,
        "MARKET_PRICE_UPDATE",
    ):
        return False

    direction = "increased" if change_percent > 0 else "decreased"

    notification = Notification(
        farmer_id=farmer_id,
        type="MARKET_PRICE_UPDATE",
        title="Market Price Updated",
        message=(
            f"Latest mandi modal price {direction} by "
            f"{abs(change_percent):.1f}%."
        ),
        is_read=False,
    )

    db.add(notification)
    await db.commit()

    return True


async def check_weather_alerts(db: AsyncSession):
    """
    Weather alert hook.

    The existing notification route expects this function.
    Weather-specific alert generation is handled separately by the
    weather service, so this function safely returns without creating
    duplicate alerts.
    """
    return 0
