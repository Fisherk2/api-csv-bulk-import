"""FastAPI application factory.

Creates and configures the FastAPI app with CORS middleware,
health check endpoint, rate limiting, and all API routers.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.infrastructure.api.routers import api_router
from app.infrastructure.rate_limiter import limiter


def _rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Return RFC 7807 Problem Details for rate limit exceeded errors.

    Overrides slowapi's default handler to match the project's error format.
    """
    response = JSONResponse(
        status_code=429,
        content={
            "type": "about:blank",
            "title": "Rate Limit Exceeded",
            "status": 429,
            "detail": f"Rate limit exceeded: {exc.detail}",
        },
    )
    return request.app.state.limiter._inject_headers(  # type: ignore[no-any-return]
        response, request.state.view_rate_limit
    )


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

    # ── Rate Limiting ──────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

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
