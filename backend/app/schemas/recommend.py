from datetime import datetime

from pydantic import BaseModel

from app.schemas.market import CropRecoItem, PriceForecastItem


class CropRecommendationResponse(BaseModel):
    farm_id: int
    recommendations: list[CropRecoItem]
    generated_at: datetime


class PricePredictionResponse(BaseModel):
    crop_id: int
    market_id: int
    predictions: list[PriceForecastItem]
    generated_at: datetime
