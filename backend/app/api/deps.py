"""Shared FastAPI dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Farmer

# auto_error=False so we can return a consistent 401 JSON body
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_farmer(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Farmer:
    """Require a valid JWT and load the matching farmer, or raise 401."""
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    farmer_id = decode_access_token(creds.credentials)
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(Farmer).where(Farmer.farmer_id == farmer_id))
    farmer = result.scalar_one_or_none()
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Farmer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return farmer
