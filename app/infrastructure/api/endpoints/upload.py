"""Upload endpoint — POST /upload.

Accepts JSON body or multipart CSV upload, validates via OrderService,
and returns 200 (all valid), 207 (partial), or 422 (all invalid).
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.core.services.order_service import OrderService
from app.infrastructure.auth.dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)
from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.product_repository import (
    ProductRepository,
)
from app.schemas.order import BatchUploadRequestSchema
from app.schemas.user import UserResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])


async def _get_order_service(db: AsyncSession) -> OrderService:
    """Build an OrderService with concrete repository implementations."""
    return OrderService(
        customer_repo=CustomerRepository(session=db),
        product_repo=ProductRepository(session=db),
        order_repo=OrderRepository(session=db),
    )


@router.post("/upload")
async def upload(
    body: BatchUploadRequestSchema | None = None,
    file: UploadFile | None = None,
    user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload a batch of orders in JSON or CSV format.

    Accepts either a JSON body (application/json) with BatchUploadRequestSchema,
    or a multipart CSV file upload. Both paths require JWT authentication.

    Returns:
        200: All rows valid — total == successful.
        207: Partial success — some rows valid, some with errors.
        422: All rows invalid — no data persisted.
    """
    service = await _get_order_service(db)

    user_id = UUID(user.id) if isinstance(user.id, str) else user.id

    if body is not None:
        # JSON body path
        orders_data: list[dict[str, Any]] = []
        for order in body.orders:
            orders_data.append(order.model_dump())
        result = await service.upload_orders(orders_data, user_id=user_id)
    elif file is not None:
        # CSV upload path
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")

        from app.utils.csv_parser import parse_csv

        rows = parse_csv(content)
        orders_data = rows
        result = await service.upload_orders(orders_data, user_id=user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either JSON body or CSV file upload is required",
        )

    # Determine status code
    if result.failed == 0:
        http_status = status.HTTP_200_OK
    elif result.successful > 0:
        http_status = 207  # Multi-Status
    else:
        http_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    return Response(
        content=result.model_dump_json(),
        media_type="application/json",
        status_code=http_status,
    )
