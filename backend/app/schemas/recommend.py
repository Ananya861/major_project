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


class HistoricalSoilOut(BaseModel):
    ph: float | None = None
    nitrogen: float | None = None
    phosphorus: float | None = None
    potassium: float | None = None
    moisture: float | None = None
    soil_type: str | None = None


class CropRecommendationHistoryItem(BaseModel):
    reco_id: int
    farm_id: int
    farm_area_acres: float | None = None
    crop_id: int
    crop_name: str
    crop_season: str | None = None
    confidence_score: float
    generated_at: datetime
    soil: HistoricalSoilOut | None = None
