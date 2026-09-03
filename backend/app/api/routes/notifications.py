"""Farmer notifications."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farmer, Notification
from app.schemas.notification import AlertCheckOut, NotificationOut
from app.services.alerts import check_price_alerts, check_weather_alerts

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> list[Notification]:
    result = await db.execute(
        select(Notification)
        .where(Notification.farmer_id == farmer.farmer_id)
        .order_by(Notification.created_at.desc())
    )
    return list(result.scalars().all())


@router.post(
    "/check-alerts",
    response_model=AlertCheckOut,
    summary="Run price and weather alert checks (demo; use cron/APScheduler in production)",
)
async def run_alert_checks(
    _farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> AlertCheckOut:
    price_created = await check_price_alerts(db)
    weather_created = await check_weather_alerts(db)
    return AlertCheckOut(
        price_alerts_created=price_created,
        weather_alerts_created=weather_created,
    )


@router.patch("/{notif_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notif_id: int,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> Notification:
    result = await db.execute(
        select(Notification).where(
            Notification.notif_id == notif_id,
            Notification.farmer_id == farmer.farmer_id,
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif
