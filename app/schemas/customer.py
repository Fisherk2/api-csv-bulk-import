"""Pydantic schemas for customer validation and API responses.

Defines request/response shapes for customer data in upload/export flows.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerCreateSchema(BaseModel):
    """Schema for creating a customer via batch upload.

    Validates name length and email format.
    """

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Strip leading/trailing whitespace from customer name."""
        return value.strip()


class CustomerResponseSchema(BaseModel):
    """Schema for customer data in API responses."""

    id: UUID
    name: str
    email: str

    model_config = {"from_attributes": True}
