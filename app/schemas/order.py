"""Pydantic schemas for order validation, batch upload, and API responses.

Defines the complete batch upload contract including request/response
shapes and RFC 7807 error details.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class OrderItemCreateSchema(BaseModel):
    """Schema for creating a single order item via batch upload.

    Validates product reference, quantity range, and unit price.
    """

    product_id: UUID
    quantity: int = Field(gt=0, le=1000)
    price: float = Field(gt=0, le=1_000_000)


class OrderCreateSchema(BaseModel):
    """Schema for creating an order with nested items via batch upload."""

    customer_id: UUID
    items: list[OrderItemCreateSchema] = Field(min_length=1)


class OrderItemResponseSchema(BaseModel):
    """Schema for order item data in API responses."""

    id: UUID
    product_id: UUID
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponseSchema(BaseModel):
    """Schema for order data in API responses."""

    id: UUID
    customer_id: UUID
    status: str
    items: list[OrderItemResponseSchema]
    created_at: str

    model_config = {"from_attributes": True}


class BatchUploadRequestSchema(BaseModel):
    """Schema for the batch upload request body (JSON path).

    Validates batch size against MAX_BATCH_SIZE (1000).
    """

    orders: list[OrderCreateSchema] = Field(
        min_length=1,
        max_length=1000,
    )


class BatchErrorDetailSchema(BaseModel):
    """RFC 7807 Problem Details with row_number for batch processing.

    Extends ProblemDetailSchema with an integer row_number to identify
    which specific row in the batch failed validation.
    """

    type: str = "about:blank"
    title: str
    status: int = 422
    detail: str | None = None
    instance: str | None = None
    row_number: int


class BatchUploadResponseSchema(BaseModel):
    """Schema for the batch upload response.

    Reports total rows processed, successful inserts, failures,
    and detailed errors per invalid row.
    """

    total: int
    successful: int
    failed: int
    errors: list[BatchErrorDetailSchema] = Field(default_factory=list)
