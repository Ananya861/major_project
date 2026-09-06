from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farm, Farmer, SoilData
from app.schemas.soil_intelligence import SoilIntelligenceResponse
from app.services.soil_intelligence_service import get_soil_information


router = APIRouter(
    prefix="/soil",
    tags=["Soil Intelligence"],
)


@router.post(
    "/intelligence/{farm_id}",
    response_model=SoilIntelligenceResponse,
)
async def get_farm_soil_intelligence(
    farm_id: int,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    """
    Get soil information automatically using stored farm coordinates.
    """

    # Verify that the farm belongs to the logged-in farmer
    result = await db.execute(
        select(Farm).where(
            Farm.farm_id == farm_id,
            Farm.farmer_id == farmer.farmer_id,
        )
    )

    farm = result.scalar_one_or_none()

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or does not belong to the current farmer",
        )

    try:
        soil_info = await get_soil_information(
            latitude=farm.latitude,
            longitude=farm.longitude,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to fetch soil information: {str(exc)}",
        ) from exc

    # Store soil reading
    soil_reading = SoilData(
        farm_id=farm.farm_id,
        ph=soil_info.get("ph"),
        nitrogen=soil_info.get("nitrogen"),
        phosphorus=soil_info.get("phosphorus"),
        potassium=soil_info.get("potassium"),
        moisture=soil_info.get("moisture"),
        soil_type=soil_info.get("soil_type"),
        recorded_at=datetime.now(timezone.utc),
    )

    db.add(soil_reading)

    await db.commit()
    await db.refresh(soil_reading)

    return SoilIntelligenceResponse(
        soil_id=soil_reading.soil_id,
        farm_id=farm.farm_id,
        latitude=farm.latitude,
        longitude=farm.longitude,
        ph=soil_reading.ph,
        nitrogen=soil_reading.nitrogen,
        phosphorus=soil_reading.phosphorus,
        potassium=soil_reading.potassium,
        moisture=soil_reading.moisture,
        soil_type=soil_reading.soil_type,
        recorded_at=soil_reading.recorded_at,
        message="Soil intelligence processed successfully",
    )