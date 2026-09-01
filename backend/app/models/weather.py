from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherLog(Base):
    __tablename__ = "weather_log"

    weather_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    # Stored as timezone-aware datetime so we can apply the 3-hour cache window.
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    forecast_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
