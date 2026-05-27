"""Upload endpoint — POST /upload.

Accepts JSON body or multipart CSV upload, validates via OrderService,
and returns 200 (all valid), 207 (partial), or 422 (all invalid).
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one order is required",
        )

    if len(orders_raw) > 1000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Batch size exceeds maximum of 1000 orders",
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
        # CSV upload via UploadFile parameter (FastAPI handles multipart)
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")

        from app.utils.csv_parser import parse_csv

        try:
            rows = parse_csv(content)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        # Transform flat CSV rows into OrderCreateSchema-compatible dicts
        # Group rows by customer_email into orders with multiple items
        orders_by_customer: dict[str, dict[str, Any]] = {}
        for row in rows:
            email = row.get("customer_email", "")
            if email not in orders_by_customer:
                orders_by_customer[email] = {
                    "customer_id": row.get("customer_id", ""),
                    "items": [],
                }
            orders_by_customer[email]["items"].append(
                {
                    "product_id": row.get("product_id", ""),
                    "quantity": int(row.get("quantity", 1)),
                    "price": float(row.get("price", 0)),
                }
            )

        orders_data = list(orders_by_customer.values())
    else:
        # JSON body path
        orders_data = await _parse_json_upload(request)

    user_id = UUID(user.id) if isinstance(user.id, str) else user.id
    result = await service.upload_orders(orders_data, user_id=user_id)

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
