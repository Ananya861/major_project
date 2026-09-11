"""Agmarknet (data.gov.in) mandi price client and region-wise agricultural catalog."""

from __future__ import annotations

import json
import subprocess
import time
from datetime import date, datetime
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Crop, Market

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

# State name aliases for data.gov.in official naming differences
STATE_NAME_ALIASES: dict[str, str] = {
    "kerala": "Keralam",
    "keralam": "Keralam",
    "chhattisgarh": "Chattisgarh",
    "chattisgarh": "Chattisgarh",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "uttarakhand": "Uttarakhand",
    "uttaranchal": "Uttarakhand",
}

# Supported Indian States & Union Territories represented in agricultural market data
ALL_INDIAN_STATES: list[str] = [
    "Andhra Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Delhi",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]

# Agmarknet commodity name aliases mapping to our canonical Crop database names
COMMODITY_ALIASES: dict[str, str] = {
    "wheat": "Wheat",
    "rice": "Rice",
    "paddy(common)": "Rice",
    "paddy": "Rice",
    "tomato": "Tomato",
    "onion": "Onion",
    "cotton": "Cotton",
    "apple": "Apple",
    "banana": "Banana",
    "banana - green": "Banana",
    "black gram(urd beans)(whole)": "Blackgram",
    "blackgram": "Blackgram",
    "urad": "Blackgram",
    "chickpea": "Chickpea",
    "bengal gram(gram)(whole)": "Chickpea",
    "bengal gram dal(chana dal)": "Chickpea",
    "gram": "Chickpea",
    "chana": "Chickpea",
    "coconut": "Coconut",
    "coffee": "Coffee",
    "grapes": "Grapes",
    "jute": "Jute",
    "kidneybeans": "Kidneybeans",
    "rajma": "Kidneybeans",
    "lentil": "Lentil",
    "masur": "Lentil",
    "maize": "Maize",
    "mango": "Mango",
    "mothbeans": "Mothbeans",
    "moth beans": "Mothbeans",
    "mungbean": "Mungbean",
    "green gram(moong)(whole)": "Mungbean",
    "moong": "Mungbean",
    "muskmelon": "Muskmelon",
    "orange": "Orange",
    "papaya": "Papaya",
    "pigeonpeas": "Pigeonpeas",
    "arhar(tur/red gram)(whole)": "Pigeonpeas",
    "tur": "Pigeonpeas",
    "pomegranate": "Pomegranate",
    "watermelon": "Watermelon",
    "soyabean": "Soyabean",
    "soybean": "Soyabean",
    "groundnut": "Groundnut",
    "groundnut(split)": "Groundnut",
}

# Reverse lookup: canonical Crop name to list of matching Agmarknet commodity names
CROP_TO_API_COMMODITIES: dict[str, list[str]] = {
    "Rice": ["Rice", "Paddy(Common)", "Paddy"],
    "Chickpea": ["Chickpea", "Bengal Gram(Gram)(Whole)", "Bengal Gram Dal(Chana Dal)", "Gram", "Chana"],
    "Blackgram": ["Blackgram", "Black Gram(Urd Beans)(Whole)", "Urad"],
    "Mungbean": ["Mungbean", "Green Gram(Moong)(Whole)", "Moong"],
    "Pigeonpeas": ["Pigeonpeas", "Arhar(Tur/Red Gram)(Whole)", "Tur"],
    "Kidneybeans": ["Kidneybeans", "Rajma"],
    "Lentil": ["Lentil", "Masur"],
    "Soyabean": ["Soyabean", "Soybean"],
    "Groundnut": ["Groundnut", "Groundnut(Split)"],
    "Banana": ["Banana", "Banana - Green"],
}

# 15-minute in-memory cache for state-level records to ensure sub-second UI responsiveness
_STATE_RECORDS_CACHE: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL_SECONDS = 900.0  # 15 minutes


def normalize_state_for_api(state_name: str) -> str:
    """Map display state name to Agmarknet's official state identifier."""
    cleaned = state_name.strip()
    return STATE_NAME_ALIASES.get(cleaned.lower(), cleaned)


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


def get_available_states() -> list[str]:
    """Return the authoritative list of supported Indian states and UTs."""
    return list(ALL_INDIAN_STATES)


async def fetch_raw_state_records(state_name: str) -> list[dict]:
    """Fetch all available daily records for a given state from data.gov.in with in-memory caching."""
    api_state = normalize_state_for_api(state_name)
    now = time.time()

    # Check cache
    if api_state in _STATE_RECORDS_CACHE:
        cache_time, cached_records = _STATE_RECORDS_CACHE[api_state]
        if now - cache_time < CACHE_TTL_SECONDS and cached_records:
            return cached_records

    raw_api_key = settings.DATA_GOV_API_KEY or ""
    api_key = raw_api_key.strip().strip("\"'")
    if not api_key:
        return []

    params: list[tuple[str, str]] = [
        ("api-key", api_key),
        ("format", "json"),
        ("limit", "500"),
        ("filters[state]", api_state),
    ]

    timeout_config = httpx.Timeout(12.0, connect=5.0)
    payload: Any = None

    try:
        async with httpx.AsyncClient(timeout=timeout_config, headers=DEFAULT_HEADERS) as client:
            response = await client.get(AGMARKNET_URL, params=params)
            if response.status_code == 200:
                payload = response.json()
    except Exception:
        # Fallback to curl.exe if httpx fails
        try:
            query_string = urlencode(params)
            url = f"{AGMARKNET_URL}?{query_string}"
            completed = subprocess.run(
                [
                    "curl.exe",
                    "-s",
                    "--max-time",
                    "15",
                    "-H",
                    f"User-Agent: {DEFAULT_HEADERS['User-Agent']}",
                    "-H",
                    f"Accept: {DEFAULT_HEADERS['Accept']}",
                    url,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if completed.returncode == 0 and completed.stdout.strip():
                payload = json.loads(completed.stdout)
        except Exception:
            payload = None

    records = payload.get("records") if isinstance(payload, dict) else []
    if records:
        _STATE_RECORDS_CACHE[api_state] = (now, records)
        return records

    # If primary state name returned 0 records, and an alias exists, try the alias
    if api_state == "Keralam" and not records:
        alt_state = "Kerala"
    elif api_state == "Kerala" and not records:
        alt_state = "Keralam"
    elif api_state == "Chattisgarh" and not records:
        alt_state = "Chhattisgarh"
    elif api_state == "Chhattisgarh" and not records:
        alt_state = "Chattisgarh"
    else:
        alt_state = None

    if alt_state:
        params_alt = [
            ("api-key", api_key),
            ("format", "json"),
            ("limit", "500"),
            ("filters[state]", alt_state),
        ]
        try:
            async with httpx.AsyncClient(timeout=timeout_config, headers=DEFAULT_HEADERS) as client:
                resp_alt = await client.get(AGMARKNET_URL, params=params_alt)
                if resp_alt.status_code == 200:
                    records = resp_alt.json().get("records", [])
                    if records:
                        _STATE_RECORDS_CACHE[api_state] = (now, records)
                        return records
        except Exception:
            pass

    return records


def match_commodity_to_crop(commodity_name: str, db_crops_by_lower: dict[str, Crop]) -> Crop | None:
    """Map a raw Agmarknet commodity string to a canonical Crop entity."""
    c_lower = commodity_name.lower().strip()

    # 1. Exact match
    if c_lower in db_crops_by_lower:
        return db_crops_by_lower[c_lower]

    # 2. Known alias match
    if c_lower in COMMODITY_ALIASES:
        canonical = COMMODITY_ALIASES[c_lower].lower()
        if canonical in db_crops_by_lower:
            return db_crops_by_lower[canonical]

    # 3. Substring match against known aliases
    for alias, canonical in COMMODITY_ALIASES.items():
        if alias in c_lower or c_lower in alias:
            can_lower = canonical.lower()
            if can_lower in db_crops_by_lower:
                return db_crops_by_lower[can_lower]

    # 4. Direct substring match against database crop names
    for name_lower, crop_obj in db_crops_by_lower.items():
        if name_lower in c_lower:
            return crop_obj

    return None


async def get_crops_for_state(state_name: str, db: AsyncSession) -> list[dict]:
    """Retrieve only the crops that actually have current market data in the selected state."""
    db_crops = (await db.execute(select(Crop).order_by(Crop.name))).scalars().all()
    db_crops_by_lower = {c.name.lower(): c for c in db_crops}

    records = await fetch_raw_state_records(state_name)
    if not records:
        # If external API is unreachable or has no records, fallback to crops that have recorded prices in this state
        fallback_query = (
            select(Crop)
            .join(Crop.market_prices)
            .join(Market, Market.market_id == Crop.market_prices.property.mapper.class_.market_id)
            .where(Market.state.ilike(f"%{state_name}%"))
            .distinct()
            .order_by(Crop.name)
        )
        fallback_crops = (await db.execute(fallback_query)).scalars().all()
        if fallback_crops:
            return [
                {"crop_id": c.crop_id, "name": c.name, "season": c.season}
                for c in fallback_crops
            ]
        # Default fallback: return all crops if no records exist
        return [
            {"crop_id": c.crop_id, "name": c.name, "season": c.season}
            for c in db_crops
        ]

    matched_crop_ids: set[int] = set()
    available_crops: list[dict] = []

    for r in records:
        comm = r.get("commodity")
        if not comm:
            continue
        matched_crop = match_commodity_to_crop(comm, db_crops_by_lower)
        if matched_crop and matched_crop.crop_id not in matched_crop_ids:
            matched_crop_ids.add(matched_crop.crop_id)
            available_crops.append(
                {
                    "crop_id": matched_crop.crop_id,
                    "name": matched_crop.name,
                    "season": matched_crop.season,
                }
            )

    available_crops.sort(key=lambda x: x["name"])
    return available_crops


async def get_markets_for_state_and_crop(
    state_name: str,
    crop_name: str,
    db: AsyncSession,
) -> list[dict]:
    """Retrieve only the mandis in the given state where the specified crop actually has records."""
    records = await fetch_raw_state_records(state_name)
    crop_lower = crop_name.lower().strip()
    acceptable_names = [crop_lower]
    if crop_name in CROP_TO_API_COMMODITIES:
        acceptable_names.extend([c.lower() for c in CROP_TO_API_COMMODITIES[crop_name]])

    # Filter state records that match the crop
    matching_records: list[dict] = []
    for r in records:
        comm = (r.get("commodity") or "").lower().strip()
        if not comm:
            continue
        if any(name in comm or comm in name for name in acceptable_names):
            matching_records.append(r)

    # Collect distinct markets from matching records
    market_map: dict[str, dict] = {}
    for r in matching_records:
        m_name = (r.get("market") or "").strip()
        if not m_name or m_name in market_map:
            continue
        market_map[m_name] = {
            "name": m_name,
            "district": (r.get("district") or "").strip() or None,
            "state": state_name,
        }

    # Ensure all distinct markets exist in PostgreSQL Market table
    results: list[dict] = []
    for m_info in market_map.values():
        name = m_info["name"]
        district = m_info["district"]
        state = m_info["state"]

        # Check existing market by name and state
        existing_result = await db.execute(
            select(Market).where(
                Market.name == name,
                Market.state == state,
            )
        )
        existing_market = existing_result.scalar_one_or_none()

        if existing_market is None:
            # Check by name alone if state was null or slightly different
            existing_result = await db.execute(
                select(Market).where(Market.name == name)
            )
            existing_market = existing_result.scalar_one_or_none()

        if existing_market is None:
            new_market = Market(name=name, state=state, district=district)
            db.add(new_market)
            await db.flush()
            existing_market = new_market

        results.append(
            {
                "market_id": existing_market.market_id,
                "name": existing_market.name,
                "district": existing_market.district,
                "state": existing_market.state or state,
            }
        )

    await db.commit()

    # Fallback to database markets if external API yielded no mandis
    if not results:
        db_markets = (
            await db.execute(
                select(Market)
                .where(Market.state.ilike(f"%{state_name}%"))
                .order_by(Market.name)
            )
        ).scalars().all()
        results = [
            {
                "market_id": m.market_id,
                "name": m.name,
                "district": m.district,
                "state": m.state,
            }
            for m in db_markets
        ]

    results.sort(key=lambda x: x["name"])
    return results


async def get_mandi_prices(
    crop_name: str,
    market_name: str | None = None,
    state_name: str | None = None,
    district_name: str | None = None,
) -> list[dict]:
    """Fetch current daily mandi prices from the official data.gov.in Agmarknet API."""
    raw_api_key = settings.DATA_GOV_API_KEY or ""
    api_key = raw_api_key.strip().strip("\"'")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATA_GOV_API_KEY is not configured",
        )

    # First check state cache if state is given
    if state_name:
        cached_records = await fetch_raw_state_records(state_name)
        if cached_records:
            crop_lower = crop_name.lower().strip()
            acceptable_names = [crop_lower]
            if crop_name in CROP_TO_API_COMMODITIES:
                acceptable_names.extend([c.lower() for c in CROP_TO_API_COMMODITIES[crop_name]])

            filtered: list[dict] = []
            for r in cached_records:
                comm = (r.get("commodity") or "").lower().strip()
                if not any(name in comm or comm in name for name in acceptable_names):
                    continue
                if market_name and market_name.lower().strip() not in (r.get("market") or "").lower().strip():
                    continue
                filtered.append(
                    {
                        "crop": r.get("commodity") or crop_name,
                        "market": r.get("market") or market_name,
                        "state": r.get("state") or state_name,
                        "district": r.get("district") or district_name,
                        "variety": r.get("variety"),
                        "grade": r.get("grade"),
                        "date": _parse_arrival_date(r.get("arrival_date")),
                        "min_price": _to_float(r.get("min_price")),
                        "max_price": _to_float(r.get("max_price")),
                        "modal_price": _to_float(r.get("modal_price")),
                    }
                )
            if filtered:
                return filtered

    # Query API directly
    api_state = normalize_state_for_api(state_name) if state_name else None

    # Possible commodity names to query
    commodities_to_try = [crop_name]
    if crop_name in CROP_TO_API_COMMODITIES:
        commodities_to_try.extend(CROP_TO_API_COMMODITIES[crop_name])

    for query_commodity in commodities_to_try:
        params: list[tuple[str, str]] = [
            ("api-key", api_key),
            ("format", "json"),
            ("limit", "25"),
            ("filters[commodity]", query_commodity),
        ]

        if market_name:
            params.append(("filters[market]", market_name))

        if api_state:
            params.append(("filters[state]", api_state))

        if district_name:
            params.append(("filters[district]", district_name))

        timeout_config = httpx.Timeout(10.0, connect=5.0)
        payload: Any = None

        try:
            async with httpx.AsyncClient(timeout=timeout_config, headers=DEFAULT_HEADERS) as client:
                response = await client.get(AGMARKNET_URL, params=params)
                if response.status_code in (401, 403):
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Invalid or unauthorized DATA_GOV_API_KEY for data.gov.in",
                    )
                if response.status_code == 200:
                    payload = response.json()
        except HTTPException:
            raise
        except Exception:
            # Fallback attempt via curl.exe
            try:
                query_string = urlencode(params)
                url = f"{AGMARKNET_URL}?{query_string}"
                completed = subprocess.run(
                    [
                        "curl.exe",
                        "-s",
                        "--max-time",
                        "15",
                        "-H",
                        f"User-Agent: {DEFAULT_HEADERS['User-Agent']}",
                        "-H",
                        f"Accept: {DEFAULT_HEADERS['Accept']}",
                        url,
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                if completed.returncode == 0 and completed.stdout.strip():
                    payload = json.loads(completed.stdout)
            except Exception:
                payload = None

        records = payload.get("records") if isinstance(payload, dict) else []
        if records:
            results: list[dict] = []
            for rec in records:
                results.append(
                    {
                        "crop": rec.get("commodity") or crop_name,
                        "market": rec.get("market") or market_name,
                        "state": rec.get("state") or state_name,
                        "district": rec.get("district") or district_name,
                        "variety": rec.get("variety"),
                        "grade": rec.get("grade"),
                        "date": _parse_arrival_date(rec.get("arrival_date")),
                        "min_price": _to_float(rec.get("min_price")),
                        "max_price": _to_float(rec.get("max_price")),
                        "modal_price": _to_float(rec.get("modal_price")),
                    }
                )
            return results

    return []