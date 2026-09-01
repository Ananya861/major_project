from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Farmer(Base):
    __tablename__ = "farmer"

    farmer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)
    land_size_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farms: Mapped[list["Farm"]] = relationship(back_populates="farmer")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="farmer")


class Farm(Base):
    __tablename__ = "farm"

    farm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmer.farmer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farmer: Mapped["Farmer"] = relationship(back_populates="farms")
    soil_readings: Mapped[list["SoilData"]] = relationship(back_populates="farm")
    recommendations: Mapped[list["CropRecommendation"]] = relationship(back_populates="farm")


class SoilData(Base):
    __tablename__ = "soil_data"

    soil_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farm.farm_id", ondelete="CASCADE"), nullable=False, index=True
    )
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    nitrogen: Mapped[float | None] = mapped_column(Float, nullable=True)
    phosphorus: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farm: Mapped["Farm"] = relationship(back_populates="soil_readings")
