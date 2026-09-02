"""Farm and soil endpoints. All farms belong to the logged-in farmer."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farm, Farmer, SoilData
from app.schemas.farm import FarmCreate, FarmDetailOut, FarmOut, SoilCreate, SoilOut

router = APIRouter(prefix="/farms", tags=["farms"])


async def _owned_farm(
    farm_id: int, farmer: Farmer, db: AsyncSession
) -> Farm:
    result = await db.execute(
        select(Farm).where(Farm.farm_id == farm_id, Farm.farmer_id == farmer.farmer_id)
    )
    farm = result.scalar_one_or_none()
    if farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return farm


@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
async def create_farm(
    payload: FarmCreate,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> Farm:
    farm = Farm(
        farmer_id=farmer.farmer_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_acres=payload.area_acres,
    )
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return farm


@router.get("", response_model=list[FarmOut])
async def list_farms(
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> list[Farm]:
    result = await db.execute(
        select(Farm)
        .where(Farm.farmer_id == farmer.farmer_id)
        .order_by(Farm.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{farm_id}", response_model=FarmDetailOut)
async def get_farm(
    farm_id: int,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> FarmDetailOut:
    farm = await _owned_farm(farm_id, farmer, db)
    soil_result = await db.execute(
        select(SoilData)
        .where(SoilData.farm_id == farm.farm_id)
        .order_by(SoilData.recorded_at.desc())
        .limit(1)
    )
    latest = soil_result.scalar_one_or_none()
    return FarmDetailOut(
        farm_id=farm.farm_id,
        farmer_id=farm.farmer_id,
        latitude=farm.latitude,
        longitude=farm.longitude,
        area_acres=farm.area_acres,
        created_at=farm.created_at,
        latest_soil=SoilOut.model_validate(latest) if latest else None,
    )


@router.post("/{farm_id}/soil", response_model=SoilOut, status_code=status.HTTP_201_CREATED)
async def add_soil_reading(
    farm_id: int,
    payload: SoilCreate,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> SoilData:
    farm = await _owned_farm(farm_id, farmer, db)
    reading = SoilData(
        farm_id=farm.farm_id,
        recorded_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading
