"""Async SQLAlchemy engine and session factory.

Provides the async engine, session factory, and a FastAPI dependency
(get_db) for injecting database sessions into request handlers.

RUNTIME DEPENDENCY: Requires asyncpg driver and a running PostgreSQL
instance. In tests, use the dependency override pattern to inject
an in-memory SQLite session.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an async database session.

    Sessions are committed on success and rolled back on failure.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
