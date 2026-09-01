from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    latitude: float
    longitude: float
    area_acres: float = Field(gt=0)


class SoilCreate(BaseModel):
    ph: float | None = None
    nitrogen: float | None = None
    phosphorus: float | None = None
    potassium: float | None = None
    moisture: float | None = None
    soil_type: str | None = None


class SoilOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    soil_id: int
    farm_id: int
    ph: float | None
    nitrogen: float | None
    phosphorus: float | None
    potassium: float | None
    moisture: float | None
    soil_type: str | None
    recorded_at: datetime


class FarmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    farm_id: int
    farmer_id: int
    latitude: float
    longitude: float
    area_acres: float
    created_at: datetime


class FarmDetailOut(FarmOut):
    latest_soil: SoilOut | None = None
