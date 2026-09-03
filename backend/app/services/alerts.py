"""
Alert helpers for mandi price swings and extreme weather.

TODO (scheduled job): call these from APScheduler / cron, e.g.

    from app.services.alerts import check_price_alerts, check_weather_alerts
    # every hour: asyncio.run(...)

Until then, POST /notifications/check-alerts runs both for a demo.
"""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Farm, Farmer, MarketPrice, Notification, NotificationType, PricePrediction
from app.services.weather_service import get_weather

RAINFALL_ALERT_MM = 20.0
TEMP_HIGH_C = 40.0
TEMP_LOW_C = 5.0


async def _has_unread_today(
    db: AsyncSession,
    farmer_id: int,
    alert_type: NotificationType,
    message: str,
) -> bool:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    existing = await db.execute(
        select(Notification).where(
            Notification.farmer_id == farmer_id,
            Notification.type == alert_type,
            Notification.message == message,
            Notification.is_read.is_(False),
            Notification.created_at >= today_start,
        )
    )
    return existing.scalar_one_or_none() is not None


async def check_price_alerts(db: AsyncSession) -> int:
    """
    Create a price_alert notification when the latest predicted price differs
    from the latest cached mandi modal price by more than 10%.

    Returns the number of notifications created. This is a simple loop suitable
    for a later scheduled job — it is not started automatically by the API.
    """
    created = 0
    farmers = (await db.execute(select(Farmer))).scalars().all()
    if not farmers:
        return 0

    preds = (
        await db.execute(
            select(PricePrediction).order_by(PricePrediction.generated_at.desc())
        )
    ).scalars().all()
    seen: set[tuple[int, int]] = set()
    latest_preds: list[PricePrediction] = []
    for row in preds:
        key = (row.crop_id, row.market_id)
        if key in seen:
            continue
        seen.add(key)
        latest_preds.append(row)

    for pred in latest_preds:
        price_row = (
            await db.execute(
                select(MarketPrice)
                .where(
                    MarketPrice.crop_id == pred.crop_id,
                    MarketPrice.market_id == pred.market_id,
                )
                .order_by(MarketPrice.date.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if price_row is None or not price_row.modal_price:
            continue
        current = float(price_row.modal_price)
        if current == 0:
            continue
        change = abs(pred.predicted_price - current) / current
        if change <= 0.10:
            continue

        direction = "up" if pred.predicted_price > current else "down"
        pct = round(change * 100, 1)
        message = (
            f"Predicted price is {pct}% {direction} vs current mandi modal "
            f"(current={current}, predicted={pred.predicted_price})."
        )
        for farmer in farmers:
            if await _has_unread_today(
                db, farmer.farmer_id, NotificationType.PRICE_ALERT, message
            ):
                continue
            db.add(
                Notification(
                    farmer_id=farmer.farmer_id,
                    type=NotificationType.PRICE_ALERT,
                    message=message,
                    is_read=False,
                )
            )
            created += 1

    if created:
        await db.commit()
    return created


def _weather_alert_message(temp: float | None, rainfall: float | None) -> str | None:
    reasons: list[str] = []
    if rainfall is not None and rainfall >= RAINFALL_ALERT_MM:
        reasons.append(f"heavy rainfall ({rainfall} mm)")
    if temp is not None and temp >= TEMP_HIGH_C:
        reasons.append(f"high temperature ({temp} C)")
    if temp is not None and temp <= TEMP_LOW_C:
        reasons.append(f"low temperature ({temp} C)")
    if not reasons:
        return None
    return "Weather alert for your farm: " + ", ".join(reasons) + "."


async def check_weather_alerts(db: AsyncSession) -> int:
    """
    Create a weather_alert when a farm's latest weather exceeds rainfall or
    temperature thresholds. Duplicate unread messages on the same UTC day are skipped.
    """
    created = 0
    farms = (await db.execute(select(Farm))).scalars().all()
    for farm in farms:
        try:
            weather = await get_weather(farm.latitude, farm.longitude, db)
        except HTTPException:
            continue

        message = _weather_alert_message(weather.get("temp"), weather.get("rainfall"))
        if message is None:
            continue
        if await _has_unread_today(
            db, farm.farmer_id, NotificationType.WEATHER_ALERT, message
        ):
            continue

        db.add(
            Notification(
                farmer_id=farm.farmer_id,
                type=NotificationType.WEATHER_ALERT,
                message=message,
                is_read=False,
            )
        )
        created += 1

    if created:
        await db.commit()
    return created
