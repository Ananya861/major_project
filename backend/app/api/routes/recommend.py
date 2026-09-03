"""Crop recommendation and price-prediction endpoints (JWT). Existing /crop is kept."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Farm, Farmer
from app.schemas.market import CropRecoItem, CropRecommendOut
from app.schemas.recommend import CropRecommendationResponse, PricePredictionResponse
from app.services.orchestration import get_crop_recommendations, get_price_predictions

router = APIRouter(prefix="/recommend", tags=["recommend"])


async def _owned_farm(farm_id: int, farmer: Farmer, db: AsyncSession) -> Farm:
    farm = (
        await db.execute(
            select(Farm).where(Farm.farm_id == farm_id, Farm.farmer_id == farmer.farmer_id)
        )
    ).scalar_one_or_none()
    if farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return farm


@router.get("/crop", response_model=CropRecommendOut)
async def recommend_crop(
    farm_id: int = Query(...),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> CropRecommendOut:
    await _owned_farm(farm_id, farmer, db)
    payload = await get_crop_recommendations(farm_id, db)
    return CropRecommendOut(
        farm_id=payload["farm_id"],
        recommendations=[CropRecoItem(**item) for item in payload["recommendations"]],
    )


@router.get("/crops/{farm_id}", response_model=CropRecommendationResponse)
async def recommend_crops_for_farm(
    farm_id: int,
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> CropRecommendationResponse:
    await _owned_farm(farm_id, farmer, db)
    payload = await get_crop_recommendations(farm_id, db)
    return CropRecommendationResponse(
        farm_id=payload["farm_id"],
        recommendations=[CropRecoItem(**item) for item in payload["recommendations"]],
        generated_at=payload["generated_at"],
    )


@router.get("/prices", response_model=PricePredictionResponse)
async def recommend_prices(
    crop_id: int = Query(..., ge=1),
    market_id: int = Query(..., ge=1),
    days_ahead: int = Query(7, ge=1, le=30),
    _farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> PricePredictionResponse:
    payload = await get_price_predictions(crop_id, market_id, days_ahead, db)
    return PricePredictionResponse(
        crop_id=payload["crop_id"],
        market_id=payload["market_id"],
        predictions=payload["predictions"],
        generated_at=payload["generated_at"],
    )
