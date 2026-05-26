"""SQLAlchemy User model for authentication.

Maps to the 'users' table with UUID primary key, unique username,
bcrypt-hashed password, and activity/timestamp tracking.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class UserModel(Base):
    """SQLAlchemy model for the users table."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return f"UserModel(id={self.id!r}, username={self.username!r})"
