"""User domain entity — pure business logic, no framework dependencies.

Represents an authenticated user with identity, credentials, and
activity tracking. This is a DDD entity, not a database model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class User:
    """Domain entity representing an authenticated user.

    Equality is based on identity (id), not attributes.
    """

    username: str
    hashed_password: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
