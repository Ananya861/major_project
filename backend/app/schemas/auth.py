from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FarmerRegister(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=8, max_length=20)
    password: str = Field(min_length=6, max_length=128)
    state: str | None = None
    district: str | None = None
    village: str | None = None
    land_size_acres: float | None = None
    category: str | None = None
    preferred_language: str | None = None


class FarmerLogin(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FarmerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    farmer_id: int
    name: str
    phone: str
    state: str | None
    district: str | None
    village: str | None
    land_size_acres: float | None
    category: str | None
    preferred_language: str | None
    created_at: datetime
