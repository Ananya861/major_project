"""Agmarknet (data.gov.in) mandi price client."""

from datetime import date, datetime
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

# Current Daily Price of Various Commodities from Various Markets (Mandi)
AGMARKNET_URL = (
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_arrival_date(raw: str | None) -> date:
    """Agmarknet typically uses DD/MM/YYYY; fall back to today if parsing fails."""
    if not raw:
        return date.today()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return date.today()


async def get_mandi_prices(crop_name: str, market_name: str | None = None) -> list[dict]:
    """Fetch min/max/modal prices from Agmarknet. Returns a list of dicts."""
    if not settings.DATA_GOV_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATA_GOV_API_KEY is not configured",
        )

    params: dict[str, Any] = {
        "api-key": settings.DATA_GOV_API_KEY,
        "format": "json",
        "limit": 20,
        "filters[commodity]": crop_name,
    }
    if market_name:
        params["filters[market]"] = market_name

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(AGMARKNET_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"data.gov.in error: {exc.response.status_code}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach data.gov.in",
        ) from exc

    records = payload.get("records") or []
    results: list[dict] = []
    for rec in records:
        results.append(
            {
                "crop": rec.get("commodity") or crop_name,
                "market": rec.get("market") or market_name,
                "state": rec.get("state"),
                "district": rec.get("district"),
                "date": _parse_arrival_date(rec.get("arrival_date")),
                "min_price": _to_float(rec.get("min_price")),
                "max_price": _to_float(rec.get("max_price")),
                "modal_price": _to_float(rec.get("modal_price")),
            }
        )
    return results
