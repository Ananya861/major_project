"""
Price-alert helper.

TODO (scheduled job): call `check_price_alerts(db)` from APScheduler / cron, e.g.

    from app.services.alerts import check_price_alerts
    # every hour: asyncio.run(check_price_alerts())
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Farmer, MarketPrice, Notification, NotificationType, PricePrediction


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

    # Latest prediction per crop/market
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
