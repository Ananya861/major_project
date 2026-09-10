"""Crop recommendation and price-prediction endpoints (JWT). Existing /crop is kept."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.models import Crop, CropRecommendation, Farm, Farmer, SoilData
from app.schemas.market import CropRecoItem, CropRecommendOut
from app.schemas.recommend import (
    CropRecommendationHistoryItem,
    CropRecommendationResponse,
    HistoricalSoilOut,
    PricePredictionResponse,
)
from app.services.orchestration import get_crop_recommendations, get_price_predictions

router = APIRouter(prefix="/recommend", tags=["recommend"])
recommendations_router = APIRouter(prefix="/recommendations", tags=["recommend"])


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


async def _get_recommendation_history(
    farm_id: int | None,
    farmer: Farmer,
    db: AsyncSession,
) -> list[CropRecommendationHistoryItem]:
    """Query genuine historical crop recommendations for the authenticated farmer."""
    query = (
        select(CropRecommendation, Farm, Crop)
        .join(Farm, CropRecommendation.farm_id == Farm.farm_id)
        .join(Crop, CropRecommendation.crop_id == Crop.crop_id)
        .where(Farm.farmer_id == farmer.farmer_id)
    )
    if farm_id is not None:
        query = query.where(Farm.farm_id == farm_id)

    query = query.order_by(CropRecommendation.generated_at.desc())

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return []

    # Retrieve genuine soil data recorded for the farms in this result set
    farm_ids = {farm.farm_id for _, farm, _ in rows}
    latest_soils: dict[int, SoilData] = {}
    for fid in farm_ids:
        soil = (
            await db.execute(
                select(SoilData)
                .where(SoilData.farm_id == fid)
                .order_by(SoilData.recorded_at.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if soil is not None:
            latest_soils[fid] = soil

    history_items: list[CropRecommendationHistoryItem] = []
    for reco, farm, crop in rows:
        soil = latest_soils.get(farm.farm_id)
        soil_out = None
        if soil is not None:
            soil_out = HistoricalSoilOut(
                ph=soil.ph,
                nitrogen=soil.nitrogen,
                phosphorus=soil.phosphorus,
                potassium=soil.potassium,
                moisture=soil.moisture,
                soil_type=soil.soil_type,
            )

        history_items.append(
            CropRecommendationHistoryItem(
                reco_id=reco.reco_id,
                farm_id=farm.farm_id,
                farm_area_acres=farm.area_acres,
                crop_id=crop.crop_id,
                crop_name=crop.name,
                crop_season=crop.season,
                confidence_score=reco.confidence_score,
                generated_at=reco.generated_at,
                soil=soil_out,
            )
        )

    return history_items


@router.get("/history", response_model=list[CropRecommendationHistoryItem])
async def get_crop_recommendations_history(
    farm_id: int | None = Query(None),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> list[CropRecommendationHistoryItem]:
    return await _get_recommendation_history(farm_id, farmer, db)


@recommendations_router.get("/history", response_model=list[CropRecommendationHistoryItem])
async def get_crop_recommendations_history_alias(
    farm_id: int | None = Query(None),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> list[CropRecommendationHistoryItem]:
    return await _get_recommendation_history(farm_id, farmer, db)
