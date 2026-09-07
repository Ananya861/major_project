"""Agmarknet (data.gov.in) mandi price client."""

import json
import subprocess
from datetime import date, datetime
from typing import Any

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


async def get_mandi_prices(
    crop_name: str,
    market_name: str | None = None,
    state_name: str | None = None,
    district_name: str | None = None,
) -> list[dict]:
    """Fetch current daily mandi prices from the official data.gov.in API."""

    if not settings.DATA_GOV_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATA_GOV_API_KEY is not configured",
        )

    # Build the API URL.
    params = [
        ("api-key", settings.DATA_GOV_API_KEY),
        ("format", "json"),
        ("limit", "20"),
        ("filters[commodity]", crop_name),
    ]

    if market_name:
        params.append(("filters[market]", market_name))

    if state_name:
        params.append(("filters[state]", state_name))

    if district_name:
        params.append(("filters[district]", district_name))

    from urllib.parse import urlencode

    query_string = urlencode(params)
    url = f"{AGMARKNET_URL}?{query_string}"

    try:
        completed = subprocess.run(
            [
                "curl.exe",
                "-s",
                "--max-time",
                "60",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if completed.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not reach data.gov.in",
            )

        if not completed.stdout.strip():
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty response from data.gov.in",
            )

        payload = json.loads(completed.stdout)

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response received from data.gov.in",
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="curl.exe is not available on this system",
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
                "variety": rec.get("variety"),
                "grade": rec.get("grade"),
                "date": _parse_arrival_date(rec.get("arrival_date")),
                "min_price": _to_float(rec.get("min_price")),
                "max_price": _to_float(rec.get("max_price")),
                "modal_price": _to_float(rec.get("modal_price")),
            }
        )

    return results