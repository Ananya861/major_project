from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farm, Farmer
from app.schemas.location_prediction import (
    FarmLocationPredictionRequest,
    LocationPredictionResponse,
)
from app.services.location_prediction_service import predict_crop_yield


router = APIRouter(
    prefix="/location",
    tags=["Location Crop Yield Prediction"],
)


@router.post(
    "/predict-yield/farm",
    response_model=LocationPredictionResponse,
)
async def predict_yield_from_farm(
    request: FarmLocationPredictionRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
):

    # Verify that the farm belongs to the logged-in farmer
    result = await db.execute(
        select(Farm).where(
            Farm.farm_id == request.farm_id,
            Farm.farmer_id == farmer.farmer_id,
        )
    )

    farm = result.scalar_one_or_none()

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or does not belong to the current farmer",
        )

    # Get district from farmer profile
    district = farmer.district

    if not district:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer district is not available. Please update farmer profile.",
        )

    try:
        predicted_yield = predict_crop_yield(
            district=district.upper(),
            crop=request.crop,
            season=request.season,
            year=request.year,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return LocationPredictionResponse(
        farm_id=farm.farm_id,
        district=district.upper(),
        crop=request.crop,
        season=request.season,
        year=request.year,
        predicted_yield=predicted_yield,
        message="Crop yield prediction generated successfully using farm information",
    )