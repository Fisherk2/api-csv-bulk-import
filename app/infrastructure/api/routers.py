"""API router aggregation.

Combines all endpoint-specific routers into a single
include structure for the FastAPI application.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.infrastructure.api.endpoints import auth, upload

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(upload.router)
