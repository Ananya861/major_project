"""FastAPI entrypoint. Swagger UI is served at /docs."""

import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings


app = FastAPI(
    title="Smart Farmer Advisory Platform",
    description="Backend API for farms, weather, mandi prices, and crop advice.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    print("\n========== SERVER ERROR ==========")
    print(f"Request: {request.method} {request.url}")
    traceback.print_exc()
    print("==================================\n")

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
