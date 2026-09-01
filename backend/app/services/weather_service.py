"""OpenWeatherMap client with a 3-hour Postgres cache (weather_log)."""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import WeatherLog

CACHE_HOURS = 3
COORD_DECIMALS = 3  # ~100 m; avoids cache misses from GPS jitter
OWM_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def round_coord(value: float) -> float:
    return round(value, COORD_DECIMALS)


def _extract_rainfall(payload: dict) -> float:
    rain = payload.get("rain") or {}
    return float(rain.get("1h") or rain.get("3h") or 0)


def _weather_dict(row: WeatherLog, cached: bool) -> dict:
    return {
        "latitude": row.latitude,
        "longitude": row.longitude,
        "date": row.date,
        "temp": row.temp,
        "rainfall": row.rainfall,
        "humidity": row.humidity,
        "forecast": row.forecast_json,
        "cached": cached,
    }


async def get_weather(lat: float, lng: float, db: AsyncSession) -> dict:
    """Return current weather for lat/lng, using weather_log if newer than 3 hours."""
    lat_r = round_coord(lat)
    lng_r = round_coord(lng)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_HOURS)

    cached = await db.execute(
        select(WeatherLog)
        .where(
            WeatherLog.latitude == lat_r,
            WeatherLog.longitude == lng_r,
            WeatherLog.date >= cutoff,
        )
        .order_by(WeatherLog.date.desc())
        .limit(1)
    )
    row = cached.scalar_one_or_none()
    if row is not None:
        return _weather_dict(row, cached=True)

    if not settings.OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENWEATHER_API_KEY is not configured",
        )

    params = {
        "lat": lat_r,
        "lon": lng_r,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            current_resp = await client.get(OWM_CURRENT, params=params)
            forecast_resp = await client.get(OWM_FORECAST, params=params)
            current_resp.raise_for_status()
            forecast_resp.raise_for_status()
            current = current_resp.json()
            forecast_payload = forecast_resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenWeatherMap error: {exc.response.status_code}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach OpenWeatherMap",
        ) from exc

    # Keep a short daily-ish forecast (next few 3-hour slots, not the full 5 days).
    short_forecast = []
    for item in (forecast_payload.get("list") or [])[:8]:
        short_forecast.append(
            {
                "dt_txt": item.get("dt_txt"),
                "temp": (item.get("main") or {}).get("temp"),
                "humidity": (item.get("main") or {}).get("humidity"),
                "rainfall": _extract_rainfall(item),
                "description": ((item.get("weather") or [{}])[0]).get("description"),
            }
        )

    main = current.get("main") or {}
    now = datetime.now(timezone.utc)
    row = WeatherLog(
        latitude=lat_r,
        longitude=lng_r,
        date=now,
        temp=main.get("temp"),
        rainfall=_extract_rainfall(current),
        humidity=main.get("humidity"),
        forecast_json=short_forecast,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _weather_dict(row, cached=False)
