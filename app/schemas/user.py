"""Pydantic schemas for user authentication and API responses.

Defines request/response shapes for the /token endpoint and user
data exposed through the API.
"""

from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TokenSchema(BaseModel):
    """JWT token response — returned by POST /token on successful auth."""

    access_token: str
    token_type: str = "bearer"


class TokenDataSchema(BaseModel):
    """Decoded JWT payload — used internally by JWTService.verify_token."""

    username: str


class UserCreateSchema(BaseModel):
    """Request schema for POST /token authentication."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=50)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        """Enforce password complexity: uppercase, lowercase, digit."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponseSchema(BaseModel):
    """Response schema for user data returned in API responses."""

    id: UUID
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
