from pydantic import BaseModel, Field


class FarmLocationPredictionRequest(BaseModel):
    farm_id: int = Field(..., gt=0)
    crop: str = Field(..., min_length=1)
    season: str = Field(..., min_length=1)
    year: int = Field(..., ge=1997)


class LocationPredictionResponse(BaseModel):
    farm_id: int
    district: str
    crop: str
    season: str
    year: int
    predicted_yield: float
    message: str