from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Crop(Base):
    __tablename__ = "crop"

    crop_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    season: Mapped[str | None] = mapped_column(String(50), nullable=True)

    market_prices: Mapped[list["MarketPrice"]] = relationship(back_populates="crop")
    price_predictions: Mapped[list["PricePrediction"]] = relationship(back_populates="crop")
    recommendations: Mapped[list["CropRecommendation"]] = relationship(back_populates="crop")


class Market(Base):
    __tablename__ = "market"

    market_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)

    market_prices: Mapped[list["MarketPrice"]] = relationship(back_populates="market")
    price_predictions: Mapped[list["PricePrediction"]] = relationship(back_populates="market")


class MarketPrice(Base):
    __tablename__ = "market_price"
    __table_args__ = (
        UniqueConstraint("crop_id", "market_id", "date", name="uq_market_price_crop_market_date"),
    )

    price_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False, index=True
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("market.market_id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    min_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    modal_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    crop: Mapped["Crop"] = relationship(back_populates="market_prices")
    market: Mapped["Market"] = relationship(back_populates="market_prices")


class PricePrediction(Base):
    __tablename__ = "price_prediction"

    prediction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False, index=True
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("market.market_id", ondelete="CASCADE"), nullable=False, index=True
    )
    predicted_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predicted_price: Mapped[float] = mapped_column(Float, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    crop: Mapped["Crop"] = relationship(back_populates="price_predictions")
    market: Mapped["Market"] = relationship(back_populates="price_predictions")


class CropRecommendation(Base):
    __tablename__ = "crop_recommendation"

    reco_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farm.farm_id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crop.crop_id", ondelete="CASCADE"), nullable=False, index=True
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    farm: Mapped["Farm"] = relationship(back_populates="recommendations")
    crop: Mapped["Crop"] = relationship(back_populates="recommendations")
