"""Schemas for the Multilingual AI Assistant."""

from typing import Any
from pydantic import BaseModel, Field


class AssistantContext(BaseModel):
    """Context passed from the frontend (farm, soil, weather, recommendations, market)."""

    farm_id: int | None = None
    farm_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    area_acres: float | None = None

    # Soil measurements
    soil_ph: float | None = None
    nitrogen: float | None = None
    phosphorus: float | None = None
    potassium: float | None = None
    moisture: float | None = None
    soil_type: str | None = None

    # Weather observations
    temperature: float | None = None
    humidity: float | None = None
    rainfall: float | None = None
    weather_condition: str | None = None

    # Market & Advisory
    recommended_crops: list[str] | None = None
    selected_crop: str | None = None
    market_name: str | None = None
    mandi_price: float | None = None
    msp_price: float | None = None


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en", max_length=10)
    context: AssistantContext | None = None


class AssistantChatResponse(BaseModel):
    response: str
    language: str
    suggestions: list[str] = []
    context_used: dict[str, Any] = {}
