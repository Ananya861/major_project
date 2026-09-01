from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class WeatherOut(BaseModel):
    latitude: float
    longitude: float
    date: datetime
    temp: float | None
    rainfall: float | None
    humidity: float | None
    forecast: Any = None
    cached: bool = False


class MarketPriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    price_id: int
    crop_id: int
    market_id: int
    date: date
    min_price: float | None
    max_price: float | None
    modal_price: float | None


class PriceForecastItem(BaseModel):
    date: str
    predicted_price: float


class PricePredictionOut(BaseModel):
    crop_id: int
    market_id: int
    days_ahead: int
    forecast: list[PriceForecastItem]


class CropRecoItem(BaseModel):
    crop_id: int | None
    crop: str
    confidence: float


class CropRecommendOut(BaseModel):
    farm_id: int
    recommendations: list[CropRecoItem]
