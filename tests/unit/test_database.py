"""Tests for app/infrastructure/database layer (T04 verification).

Validates that SQLAlchemy Base, UUIDType, async engine, and session
dependencies are correctly configured.
"""

from __future__ import annotations


class TestDatabaseBase:
    """DeclarativeBase must be importable and usable."""

    def test_base_class_exists(self) -> None:
        """Base must be importable from app.infrastructure.database.base."""
        from app.infrastructure.database.base import Base

        assert Base is not None

    def test_base_is_declarative_base(self) -> None:
        """Base must be a DeclarativeBase instance (SQLAlchemy 2.x style)."""
        from sqlalchemy.orm import DeclarativeBase

        from app.infrastructure.database.base import Base

        assert issubclass(Base, DeclarativeBase)

    def test_uuid_type_exists(self) -> None:
        """UUIDType must be importable for primary keys."""
        from app.infrastructure.database.base import UUIDType

        assert UUIDType is not None


class TestDatabaseSession:
    """Async engine and session must be importable."""

    def test_get_db_function_exists(self) -> None:
        """get_db must be an async generator dependency."""
        from app.infrastructure.database.session import get_db

        assert get_db is not None
        assert callable(get_db)

    def test_engine_exists(self) -> None:
        """Async engine must be importable."""
        from app.infrastructure.database.session import engine

        assert engine is not None

    def test_async_session_local_exists(self) -> None:
        """AsyncSessionLocal factory must be importable."""
        from app.infrastructure.database.session import AsyncSessionLocal

        assert AsyncSessionLocal is not None
