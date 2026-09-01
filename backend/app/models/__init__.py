"""SQLAlchemy models. Import this package so Alembic sees all tables."""

from app.models.farmer import Farm, Farmer, SoilData
from app.models.market import Crop, CropRecommendation, Market, MarketPrice, PricePrediction
from app.models.notification import Notification, NotificationType
from app.models.weather import WeatherLog

__all__ = [
    "Farmer",
    "Farm",
    "SoilData",
    "Crop",
    "Market",
    "MarketPrice",
    "PricePrediction",
    "CropRecommendation",
    "WeatherLog",
    "Notification",
    "NotificationType",
]
