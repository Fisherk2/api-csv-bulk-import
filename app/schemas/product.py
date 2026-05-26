"""Pydantic schemas for product validation and API responses.

Defines request/response shapes for product data in upload/export flows.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProductCreateSchema(BaseModel):
    """Schema for creating a product via batch upload.

    Validates name length, price range, and stock quantity.
    """

    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, le=1_000_000)
    stock: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Strip leading/trailing whitespace from product name."""
        return value.strip()


class ProductResponseSchema(BaseModel):
    """Schema for product data in API responses.

    Includes the auto-generated UUID for client-side tracking.
    """

    id: UUID
    name: str
    price: float
    stock: int

    model_config = {"from_attributes": True}
