"""Crop recommendation endpoint (trained model via predict_crop)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.db.session import get_db
from app.ml.crop_inference import CropModelNotAvailable
from app.models import Crop, CropRecommendation, Farm, Farmer, SoilData
from app.schemas.market import CropRecoItem, CropRecommendOut
from app.services.orchestration import predict_crop
from app.services.weather_service import get_weather

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.get("/crop", response_model=CropRecommendOut)
async def recommend_crop(
    farm_id: int = Query(...),
    farmer: Farmer = Depends(get_current_farmer),
    db: AsyncSession = Depends(get_db),
) -> CropRecommendOut:
    farm = (
        await db.execute(
            select(Farm).where(Farm.farm_id == farm_id, Farm.farmer_id == farmer.farmer_id)
        )
    ).scalar_one_or_none()
    if farm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    soil = (
        await db.execute(
            select(SoilData)
            .where(SoilData.farm_id == farm.farm_id)
            .order_by(SoilData.recorded_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if soil is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Add a soil reading for this farm before requesting a recommendation",
        )

    soil_payload = {
        "ph": soil.ph,
        "nitrogen": soil.nitrogen,
        "phosphorus": soil.phosphorus,
        "potassium": soil.potassium,
        "moisture": soil.moisture,
        "soil_type": soil.soil_type,
    }
    try:
        weather = await get_weather(farm.latitude, farm.longitude, db)
        soil_payload["temperature"] = weather.get("temp")
        soil_payload["humidity"] = weather.get("humidity")
        soil_payload["rainfall"] = weather.get("rainfall")
    except HTTPException:
        # Weather is optional for inference; the fitted imputer fills missing climate fields.
        pass

    try:
        ranked = predict_crop(soil_payload)
    except CropModelNotAvailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    items: list[CropRecoItem] = []
    for entry in ranked:
        crop_name = str(entry.get("crop", "")).strip()
        confidence = float(entry.get("confidence", 0))
        crop = (
            await db.execute(select(Crop).where(func.lower(Crop.name) == crop_name.lower()))
        ).scalar_one_or_none()
        if crop is None:
            # Crop is outside the seeded crop table; still return the model label.
            items.append(CropRecoItem(crop_id=None, crop=crop_name, confidence=confidence))
            continue
        db.add(
            CropRecommendation(
                farm_id=farm.farm_id,
                crop_id=crop.crop_id,
                confidence_score=confidence,
            )
        )
        items.append(
            CropRecoItem(crop_id=crop.crop_id, crop=crop.name, confidence=confidence)
        )

    await db.commit()
    items.sort(key=lambda x: x.confidence, reverse=True)
    return CropRecommendOut(farm_id=farm.farm_id, recommendations=items)
