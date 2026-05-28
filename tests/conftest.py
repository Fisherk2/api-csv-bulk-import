"""Shared pytest fixtures for async testing.

Provides an async SQLite test database engine, async sessions,
an httpx.AsyncClient with dependency overrides, and a test user fixture.
"""

from __future__ import annotations

import os

# Disable global rate limiting for all tests to prevent flaky test behavior.
# Must be set before any app config imports (like settings.RATE_LIMIT_PER_MINUTE).
os.environ["RATE_LIMIT_PER_MINUTE"] = "0"
# Set high per-endpoint rate limits so rate limit tests don't interfere
# with each other (the shared limiter state persists across test files).
os.environ["TOKEN_RATE_LIMIT"] = "100000"
os.environ["UPLOAD_RATE_LIMIT"] = "100000"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Ensure all model modules are loaded so Base.metadata includes all tables.
# Imported here to register tables with SQLAlchemy's declarative base.
import app.infrastructure.database.models.customer  # noqa: F401
import app.infrastructure.database.models.order  # noqa: F401
import app.infrastructure.database.models.product  # noqa: F401
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_db
from app.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create an async SQLite engine for the test session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Provide an async database session with rollback after each test."""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(test_db_session):
    """Provide an async HTTP test client with DB dependency override."""
    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db_session):
    """Create a test user in the database and return credentials."""
    from app.infrastructure.auth.password_service import PasswordService
    from app.infrastructure.database.models.user import UserModel

    # Test-only password — not used in production
    hashed = PasswordService.hash_password("Test1234")
    user = UserModel(username="testuser", hashed_password=hashed)
    test_db_session.add(user)
    await test_db_session.flush()

    return {
        "username": "testuser",
        "password": "Test1234",
        "user_id": str(user.id),
    }
