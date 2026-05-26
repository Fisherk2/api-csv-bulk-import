"""SQLAlchemy declarative base and shared types.

Defines the DeclarativeBase for all ORM models and a UUIDType
for consistent UUID primary keys across entities.
"""

from __future__ import annotations

import uuid

from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


class UUIDType(types.TypeDecorator[uuid.UUID]):
    """Platform-independent UUID type.

    Stores as PostgreSQL native UUID, falls back to CHAR(36) on SQLite.
    Uses Python's uuid.UUID for application-level representation.
    """

    impl = types.Uuid
    cache_ok = True

    def process_bind_param(
        self, value: uuid.UUID | None, dialect: object
    ) -> str | None:
        """Convert Python UUID to string for the database."""
        if value is None:
            return None
        return str(value)

    def process_result_value(
        self, value: str | None, dialect: object
    ) -> uuid.UUID | None:
        """Convert database value to Python UUID."""
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
