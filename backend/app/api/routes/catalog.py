"""Reference crop and mandi lists with region-based availability."""

from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Crop, Market
from app.schemas.market import CropOut, MarketOut
from app.services.mandi_service import (
    get_available_states,
    get_crops_for_state,
    get_markets_for_state_and_crop,
)

crops_router = APIRouter(prefix="/crops", tags=["catalog"])
markets_router = APIRouter(prefix="/markets", tags=["catalog"])


@crops_router.get("/states", response_model=list[str])
@markets_router.get("/states", response_model=list[str])
async def list_available_states() -> list[str]:
    """Return all supported Indian states/UTs with available agricultural market data."""
    return get_available_states()


@crops_router.get("", response_model=list[CropOut])
async def list_crops(
    state: str | None = Query(default=None, description="Filter crops available in this region/state"),
    db: AsyncSession = Depends(get_db),
) -> list[Any]:
    """List crops, dynamically filtered by real availability in the selected state."""
    if state and state.strip():
        return await get_crops_for_state(state_name=state.strip(), db=db)
    result = await db.execute(select(Crop).order_by(Crop.name))
    return list(result.scalars().all())


@markets_router.get("", response_model=list[MarketOut])
async def list_markets(
    state: str | None = Query(default=None, description="Filter mandis in this region/state"),
    crop: str | None = Query(default=None, description="Filter mandis that have data for this crop"),
    db: AsyncSession = Depends(get_db),
) -> list[Any]:
    """List mandis, dynamically filtered by state and crop."""
    if state and state.strip() and crop and crop.strip():
        return await get_markets_for_state_and_crop(state_name=state.strip(), crop_name=crop.strip(), db=db)
    if state and state.strip():
        result = await db.execute(
            select(Market).where(Market.state.ilike(f"%{state.strip()}%")).order_by(Market.name)
        )
        markets = list(result.scalars().all())
        if markets:
            return markets
        return await get_markets_for_state_and_crop(state_name=state.strip(), crop_name="", db=db)

    result = await db.execute(select(Market).order_by(Market.name))
    return list(result.scalars().all())
