"""OpenWeatherMap client with a 3-hour Postgres cache (weather_log)."""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models import WeatherLog

CACHE_HOURS = 3
COORD_DECIMALS = 3  # ~100 m; avoids cache misses from GPS jitter
COORD_EPS = 10 ** (-COORD_DECIMALS)
OWM_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


def round_coord(value: float) -> float:
    return round(value, COORD_DECIMALS)


def _validate_coords(lat: float, lng: float) -> None:
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coordinates: lat must be between -90 and 90, lng between -180 and 180",
        )


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


async def _cached_row(db: AsyncSession, lat_r: float, lng_r: float) -> WeatherLog | None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_HOURS)
    result = await db.execute(
        select(WeatherLog)
        .where(
            WeatherLog.latitude.between(lat_r - COORD_EPS, lat_r + COORD_EPS),
            WeatherLog.longitude.between(lng_r - COORD_EPS, lng_r + COORD_EPS),
            WeatherLog.date >= cutoff,
        )
        .order_by(WeatherLog.date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _short_forecast(forecast_payload: dict) -> list[dict]:
    short_forecast: list[dict] = []
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
    return short_forecast


async def _fetch_from_openweather(lat_r: float, lng_r: float) -> tuple[dict, dict]:
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENWEATHER_API_KEY is not configured",
        )

    params = {
        "lat": lat_r,
        "lon": lng_r,
        "appid": api_key,
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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenWeatherMap returned an invalid response",
        ) from exc

    if not isinstance(current, dict) or not isinstance(forecast_payload, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenWeatherMap returned an invalid response",
        )
    return current, forecast_payload


async def _get_weather_with_db(lat: float, lng: float, db: AsyncSession) -> dict:
    lat_r = round_coord(lat)
    lng_r = round_coord(lng)

    row = await _cached_row(db, lat_r, lng_r)
    if row is not None:
        return _weather_dict(row, cached=True)

    current, forecast_payload = await _fetch_from_openweather(lat_r, lng_r)
    main = current.get("main") or {}
    now = datetime.now(timezone.utc)
    row = WeatherLog(
        latitude=lat_r,
        longitude=lng_r,
        date=now,
        temp=main.get("temp"),
        rainfall=_extract_rainfall(current),
        humidity=main.get("humidity"),
        forecast_json=_short_forecast(forecast_payload),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _weather_dict(row, cached=False)


async def get_weather(lat: float, lng: float, db: AsyncSession | None = None) -> dict:
    """Return current weather for lat/lng, using weather_log if newer than 3 hours."""
    _validate_coords(lat, lng)
    if db is not None:
        return await _get_weather_with_db(lat, lng, db)

    async with AsyncSessionLocal() as session:
        try:
            return await _get_weather_with_db(lat, lng, session)
        except Exception:
            await session.rollback()
            raise
