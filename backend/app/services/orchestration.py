"""
Decision-engine orchestration.

ML models are owned by teammates. Keep the function signatures stable so their
modules can replace these stubs later, e.g.:

    from teammate_ml.crop_model import predict_crop
    from teammate_ml.price_model import predict_price
"""

from datetime import date, timedelta


def predict_crop(soil_data: dict) -> list[dict]:
    """
    Rank crops for a farm given its latest soil reading.

    PLACEHOLDER: replace this body with the real model import. Dummy values are
    realistic enough for API/demo wiring (names match the Alembic seed crops).

    Expected return: [{"crop": str, "confidence": float}, ...] sorted high → low.
    """
    # Slightly vary dummy ranking using pH so the stub is not a constant.
    ph = soil_data.get("ph") or 6.5
    if ph < 6.0:
        ranking = [("Rice", 0.78), ("Wheat", 0.14), ("Tomato", 0.08)]
    elif ph > 7.5:
        ranking = [("Wheat", 0.72), ("Onion", 0.18), ("Tomato", 0.10)]
    else:
        ranking = [("Tomato", 0.64), ("Onion", 0.22), ("Wheat", 0.14)]
    return [{"crop": name, "confidence": score} for name, score in ranking]


def predict_price(crop_id: int, market_id: int, days_ahead: int) -> list[dict]:
    """
    Forecast modal mandi price for `days_ahead` calendar days.

    PLACEHOLDER: replace this body with the real time-series model. The dummy
    walk is deterministic from crop_id/market_id so tests stay stable.

    Expected return: [{"date": "YYYY-MM-DD", "predicted_price": float}, ...]
    """
    if days_ahead < 1:
        days_ahead = 1
    days_ahead = min(days_ahead, 30)

    base = 1800.0 + (crop_id * 37) + (market_id * 11)
    today = date.today()
    out: list[dict] = []
    for i in range(1, days_ahead + 1):
        # Gentle dummy drift (~0.4% per day) so the 10% alert stub can be demoed.
        price = round(base * (1 + 0.004 * i), 2)
        out.append(
            {
                "date": (today + timedelta(days=i)).isoformat(),
                "predicted_price": price,
            }
        )
    return out
