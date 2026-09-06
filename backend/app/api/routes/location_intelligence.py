from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farm, Farmer
from app.schemas.location_intelligence import (
    LocationIntelligenceRequest,
    LocationIntelligenceResponse,
)
from app.services.location_service import reverse_geocode


router = APIRouter(
    prefix="/location",
    tags=["Location Intelligence"],
)


@router.post(
    "/intelligence",
    response_model=LocationIntelligenceResponse,
)
async def process_location(
    payload: LocationIntelligenceRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):
    """
    Process farmer GPS location and automatically fetch location details.
    """

    try:
        location_data = await reverse_geocode(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to fetch location information: {str(exc)}",
        ) from exc

    # Automatically update farmer location
    farmer.state = location_data.get("state")
    farmer.district = location_data.get("district")
    farmer.village = location_data.get("village")

    # Check whether farmer already has a farm
    result = await db.execute(
        select(Farm).where(Farm.farmer_id == farmer.farmer_id)
    )
    farm = result.scalar_one_or_none()

    if farm is None:
        # Create farm automatically using land size from registration
        if farmer.land_size_acres is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land size is missing from farmer registration",
            )

        farm = Farm(
            farmer_id=farmer.farmer_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            area_acres=farmer.land_size_acres,
        )

        db.add(farm)

    else:
        # Update existing farm location
        farm.latitude = payload.latitude
        farm.longitude = payload.longitude

    await db.commit()
    await db.refresh(farmer)
    await db.refresh(farm)

    return LocationIntelligenceResponse(
        state=farmer.state,
        district=farmer.district,
        village=farmer.village,
        latitude=farm.latitude,
        longitude=farm.longitude,
        farm_id=farm.farm_id,
        area_acres=farm.area_acres,
        message="Location processed and farm configured successfully",
    )