"""FastAPI application factory.

Creates and configures the FastAPI app with CORS middleware,
health check endpoint, and all API routers.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.api.routers import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app ready to serve requests.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────
    origins = [
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────
    app.include_router(api_router)

    # ── Health Check ──────────────────────────────────────
    @app.get("/")
    async def health_check() -> dict[str, str]:
        """Health check endpoint returning API status."""
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
