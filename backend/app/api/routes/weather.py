"""Weather endpoint (public so it is easy to try in /docs)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.market import WeatherOut
from app.services.weather_service import get_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherOut)
async def read_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await get_weather(lat, lng, db)
