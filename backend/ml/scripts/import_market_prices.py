import asyncio
import json
from datetime import datetime

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models import Crop, Market, MarketPrice

DATASETS = [
    ("soyabean_biaora.json", "Soyabean", "Biaora", "Madhya Pradesh", "Rajgarh"),
    ("wheat_khilchipur.json", "Wheat", "Khilchipur", "Madhya Pradesh", "Rajgarh"),
    ("maize_jaspur.json", "Maize", "Jaspur", "Chattisgarh", "Jashpur"),
    ("groundnut_sendhwa.json", "Groundnut", "Sendhwa", "Madhya Pradesh", "Badwani"),
]


async def main():
    async with AsyncSessionLocal() as db:
        for filename, crop_name, market_name, state, district in DATASETS:

            crop = (
                await db.execute(
                    select(Crop).where(Crop.name == crop_name)
                )
            ).scalar_one_or_none()

            if crop is None:
                crop = Crop(name=crop_name)
                db.add(crop)
                await db.flush()

            market = (
                await db.execute(
                    select(Market).where(
                        Market.name == market_name,
                        Market.state == state,
                        Market.district == district,
                    )
                )
            ).scalar_one_or_none()

            if market is None:
                market = Market(
                    name=market_name,
                    state=state,
                    district=district,
                )
                db.add(market)
                await db.flush()

            with open(f"ml/data/{filename}", "r", encoding="utf-8-sig") as f:
                records = json.load(f)

            # Keep only one record per date.
            unique_records = {}

            for record in records:
                raw_date = record.get("Arrival_Date")
                if not raw_date:
                    continue

                try:
                    price_date = datetime.strptime(
                        raw_date, "%d/%m/%Y"
                    ).date()
                    min_price = float(record["Min_Price"])
                    max_price = float(record["Max_Price"])
                    modal_price = float(record["Modal_Price"])
                except (ValueError, TypeError, KeyError):
                    continue

                if min_price <= 0 or max_price <= 0 or modal_price <= 0:
                    continue

                unique_records[price_date] = (
                    min_price,
                    max_price,
                    modal_price,
                )

            dates = list(unique_records.keys())

            # Find dates already present in the database.
            existing_result = await db.execute(
                select(MarketPrice.date).where(
                    MarketPrice.crop_id == crop.crop_id,
                    MarketPrice.market_id == market.market_id,
                    MarketPrice.date.in_(dates),
                )
            )

            existing_dates = {row[0] for row in existing_result.fetchall()}

            inserted = 0

            for price_date, prices in unique_records.items():
                if price_date in existing_dates:
                    continue

                min_price, max_price, modal_price = prices

                db.add(
                    MarketPrice(
                        crop_id=crop.crop_id,
                        market_id=market.market_id,
                        date=price_date,
                        min_price=min_price,
                        max_price=max_price,
                        modal_price=modal_price,
                    )
                )
                inserted += 1

            await db.flush()

            print(
                f"{crop_name} - {market_name}: "
                f"{inserted} new price records inserted "
                f"(crop_id={crop.crop_id}, market_id={market.market_id})"
            )

        await db.commit()


asyncio.run(main())
