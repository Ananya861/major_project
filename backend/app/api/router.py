from fastapi import APIRouter

from app.api.routes import auth, farms, market, notifications, recommend, weather

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(farms.router)
api_router.include_router(weather.router)
api_router.include_router(market.router)
api_router.include_router(recommend.router)
api_router.include_router(notifications.router)
