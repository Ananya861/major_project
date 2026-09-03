"""Auth routes: register a farmer and log in to receive a JWT."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_farmer
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import Farmer
from app.schemas.auth import FarmerLogin, FarmerOut, FarmerRegister, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=FarmerOut, status_code=status.HTTP_201_CREATED)
async def register(payload: FarmerRegister, db: AsyncSession = Depends(get_db)) -> Farmer:
    existing = await db.execute(select(Farmer).where(Farmer.phone == payload.phone))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A farmer with this phone number already exists",
        )

    try:
        password_hash = hash_password(payload.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long",
        )

    farmer = Farmer(
        name=payload.name,
        phone=payload.phone,
        password_hash=password_hash,
        state=payload.state,
        district=payload.district,
        village=payload.village,
        land_size_acres=payload.land_size_acres,
        category=payload.category,
        preferred_language=payload.preferred_language,
    )
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    return farmer


@router.post("/login", response_model=TokenResponse)
async def login(payload: FarmerLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(Farmer).where(Farmer.phone == payload.phone))
    farmer = result.scalar_one_or_none()
    if farmer is None or not verify_password(payload.password, farmer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )
    token = create_access_token(farmer.farmer_id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=FarmerOut)
async def read_me(farmer: Farmer = Depends(get_current_farmer)) -> Farmer:
    return farmer
