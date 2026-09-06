from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SoilIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    soil_id: int
    farm_id: int

    latitude: float
    longitude: float

    ph: float | None
    nitrogen: float | None
    phosphorus: float | None
    potassium: float | None
    moisture: float | None
    soil_type: str | None

    recorded_at: datetime
    message: str