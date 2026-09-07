"""Agmarknet (data.gov.in) mandi price client."""

from datetime import date, datetime
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

# Official Government of India Open Government Data (OGD) Agmarknet endpoint
AGMARKNET_URL = (
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
)

# Standard browser headers to prevent WAF connection resets from government gateways
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


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
    api_key = settings.DATA_GOV_API_KEY.strip().strip("\"'")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATA_GOV_API_KEY is not configured",
        )

    params: dict[str, Any] = {
        "api-key": api_key,
        "format": "json",
        "limit": 20,
        "filters[commodity]": crop_name,
    }
    if market_name:
        params["filters[market]"] = market_name

    timeout_config = httpx.Timeout(10.0, connect=5.0)

    try:
        async with httpx.AsyncClient(timeout=timeout_config, headers=DEFAULT_HEADERS) as client:
            response = await client.get(AGMARKNET_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (401, 403):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid or unauthorized DATA_GOV_API_KEY for data.gov.in",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"data.gov.in error: {exc.response.status_code}",
        ) from exc
    except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Connection to data.gov.in timed out",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach data.gov.in",
        ) from exc


    if isinstance(payload, dict) and payload.get("status") in ("failed", "error"):
        error_msg = payload.get("message") or "data.gov.in returned an error status"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"data.gov.in error: {error_msg}",
        )

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
