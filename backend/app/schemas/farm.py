from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FarmCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    area_acres: float = Field(gt=0)


class SoilCreate(BaseModel):
    ph: float | None = Field(default=None, ge=0, le=14)
    nitrogen: float | None = Field(default=None, ge=0)
    phosphorus: float | None = Field(default=None, ge=0)
    potassium: float | None = Field(default=None, ge=0)
    moisture: float | None = Field(default=None, ge=0, le=100)
    soil_type: str | None = Field(default=None, max_length=80)

    @field_validator("soil_type")
    @classmethod
    def strip_soil_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def require_at_least_one_value(self) -> "SoilCreate":
        if all(
            getattr(self, field) is None
            for field in (
                "ph",
                "nitrogen",
                "phosphorus",
                "potassium",
                "moisture",
                "soil_type",
            )
        ):
            raise ValueError("Provide at least one soil measurement or soil_type")
        return self


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
