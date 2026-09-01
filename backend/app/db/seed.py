"""Optional helper to (re)seed reference crops and markets if the tables are empty."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Crop, Market

DEFAULT_CROPS = [
    ("Wheat", "rabi"),
    ("Rice", "kharif"),
    ("Tomato", "year-round"),
    ("Onion", "rabi"),
    ("Cotton", "kharif"),
]

DEFAULT_MARKETS = [
    ("Azadpur", "Delhi", "North Delhi"),
    ("Pimpalgaon", "Maharashtra", "Nashik"),
    ("Kolar", "Karnataka", "Kolar"),
]


async def seed_reference_data(db: AsyncSession) -> None:
    if (await db.execute(select(Crop))).first() is None:
        for name, season in DEFAULT_CROPS:
            db.add(Crop(name=name, season=season))
    if (await db.execute(select(Market))).first() is None:
        for name, state, district in DEFAULT_MARKETS:
            db.add(Market(name=name, state=state, district=district))
    await db.commit()
