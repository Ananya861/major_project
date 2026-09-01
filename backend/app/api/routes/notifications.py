"""Farmer notifications."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farmer, Notification
from app.schemas.notification import NotificationOut

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
