"""Reference crop and mandi lists (seeded in Alembic)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Crop, Market
from app.schemas.market import CropOut, MarketOut

crops_router = APIRouter(prefix="/crops", tags=["catalog"])
markets_router = APIRouter(prefix="/markets", tags=["catalog"])


@crops_router.get("", response_model=list[CropOut])
async def list_crops(db: AsyncSession = Depends(get_db)) -> list[Crop]:
    result = await db.execute(select(Crop).order_by(Crop.name))
    return list(result.scalars().all())


@markets_router.get("", response_model=list[MarketOut])
async def list_markets(db: AsyncSession = Depends(get_db)) -> list[Market]:
    result = await db.execute(select(Market).order_by(Market.name))
    return list(result.scalars().all())
