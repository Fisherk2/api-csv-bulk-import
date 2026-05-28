"""Upload endpoint — POST /upload.

Accepts JSON body or multipart CSV upload, validates via OrderService,
and returns 200 (all valid), 207 (partial), or 422 (all invalid).
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
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


async def _parse_json_upload(request: Request) -> list[dict[str, Any]]:
    """Parse JSON body into list of order dicts."""
    from app.config import settings

    try:
        body_data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must be valid JSON",
        )

    if not isinstance(body_data, dict) or "orders" not in body_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON body must contain 'orders' key",
        )

    orders_raw = body_data["orders"]
    if not isinstance(orders_raw, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'orders' must be a list",
        )

    if len(orders_raw) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one order is required",
        )

    if len(orders_raw) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Batch size exceeds maximum of {settings.MAX_BATCH_SIZE} orders",
        )

    return orders_raw


@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile | None = None,
    user: UserResponseSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload a batch of orders in JSON or CSV format.

    Accepts either a JSON body (application/json) or a multipart CSV
    file upload via the 'file' form field. Both paths require JWT authentication.

    Returns:
        200: All rows valid.
        207: Partial success — some rows valid, some with errors.
        422: All rows invalid.
    """
    service = await _get_order_service(db)

    if file is not None:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")

        # Validate file size (max MB from config)
        from app.config import settings
        from app.utils.file_utils import validate_file_size

        if not validate_file_size(
            size=len(content_bytes),
            max_mb=settings.MAX_FILE_SIZE_MB,
        ):
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB",
            )

        from app.utils.csv_parser import parse_csv_to_orders

        try:
            orders_data = parse_csv_to_orders(content)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        # Enforce batch size limit for CSV uploads (same as JSON path)
        if len(orders_data) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"Batch size exceeds maximum of {settings.MAX_BATCH_SIZE} orders",
            )
    else:
        orders_data = await _parse_json_upload(request)

    user_id = user.id
    result = await service.upload_orders(orders_data, user_id=user_id)

    http_status = _status_for_result(result)
    return Response(
        content=result.model_dump_json(),
        media_type="application/json",
        status_code=http_status,
    )


def _status_for_result(result: Any) -> int:
    """Determine HTTP status code for batch upload result."""
    if result.failed == 0:
        return status.HTTP_200_OK
    if result.successful > 0:
        return 207  # Multi-Status
    return status.HTTP_422_UNPROCESSABLE_CONTENT
