from pydantic import BaseModel, Field


class LocationIntelligenceRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationIntelligenceResponse(BaseModel):
    state: str | None
    district: str | None
    village: str | None
    latitude: float
    longitude: float
    farm_id: int
    area_acres: float
    message: str