import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationType(str, enum.Enum):
    PRICE_ALERT = "price_alert"
    WEATHER_ALERT = "weather_alert"


class Notification(Base):
    __tablename__ = "notification"

    notif_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmer.farmer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            name="notification_type",
            values_callable=lambda members: [m.value for m in members],
            native_enum=True,
        ),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farmer: Mapped["Farmer"] = relationship(back_populates="notifications")
