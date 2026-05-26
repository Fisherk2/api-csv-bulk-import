"""Application configuration via pydantic-settings.

Loads all environment variables with validation and sensible defaults.
Uses asyncpg for runtime database connections and psycopg2 for Alembic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All values can be overridden via environment variables or a .env file.
    Defaults are secure — DEBUG is off, CORS is restrictive, and batch
    sizes are capped.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:change-me@localhost:5432/api_csv_import"
    )

    SYNC_DATABASE_URL: str = (
        "postgresql://postgres:change-me@localhost:5432/api_csv_import"
    )

    # ── Auth (JWT) ───────────────────────────────────────
    SECRET_KEY: str = "change-me-please-use-a-real-secret-in-production"

    ALGORITHM: Literal["HS256", "RS256"] = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Upload Limits ────────────────────────────────────
    MAX_BATCH_SIZE: int = 1000

    MAX_FILE_SIZE_MB: int = 10

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ── General ──────────────────────────────────────────
    DEBUG: bool = False

    HOST: str = "0.0.0.0"

    PORT: int = 8000

    # ── Application ──────────────────────────────────────
    APP_NAME: str = "api-csv-bulk-import"

    APP_VERSION: str = "1.0.0"


# Singleton instance for use throughout the application
settings = Settings()
