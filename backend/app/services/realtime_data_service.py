"""
Real-time environmental data aggregation service.

Gets live weather data directly from OpenWeatherMap
for crop recommendation.
"""

import httpx
from fastapi import HTTPException

from app.core.config import settings


OWM_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"


async def get_live_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """Fetch live weather directly from OpenWeatherMap."""

    if not settings.OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHER_API_KEY is not configured",
        )

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:

            current_response = await client.get(
                OWM_CURRENT,
                params=params,
            )

            forecast_response = await client.get(
                OWM_FORECAST,
                params=params,
            )

            current_response.raise_for_status()
            forecast_response.raise_for_status()

            current = current_response.json()
            forecast = forecast_response.json()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch live weather: {str(exc)}",
        )

    main = current.get("main", {})
    rain = current.get("rain", {})

    rainfall = (
        rain.get("1h")
        or rain.get("3h")
        or 0
    )

    forecast_list = []

    for item in forecast.get("list", [])[:8]:

        item_main = item.get("main", {})
        item_weather = item.get("weather", [{}])

        forecast_list.append(
            {
                "datetime": item.get("dt_txt"),
                "temperature": item_main.get("temp"),
                "humidity": item_main.get("humidity"),
                "description": item_weather[0].get("description"),
            }
        )

    return {
        "temperature": main.get("temp"),
        "humidity": main.get("humidity"),
        "rainfall": rainfall,
        "forecast": forecast_list,
    }


async def get_realtime_farm_data(
    latitude: float,
    longitude: float,
) -> dict:
    """
    Collect real-time environmental information
    for a farm location.
    """

    weather = await get_live_weather(
        latitude=latitude,
        longitude=longitude,
    )

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "weather": weather,
    }