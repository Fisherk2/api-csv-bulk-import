"""Export endpoint — GET /export.

Returns order data in JSON or CSV format with pagination.
Requires JWT authentication.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.services.export_service import ExportService
from app.infrastructure.auth.dependencies import get_current_user
from app.infrastructure.database.session import get_db
from app.infrastructure.rate_limiter import limiter as _limiter
from app.infrastructure.repositories.order_repository import OrderRepository
from app.schemas.user import UserResponseSchema

router = APIRouter(tags=["export"])


def _get_export_service(db: AsyncSession) -> ExportService:
    """Build an ExportService with the concrete OrderRepository.

    Synchronous factory — no I/O needed to construct the service.
    """
    return ExportService(order_repo=OrderRepository(session=db))


@router.get("/export")
@_limiter.limit(lambda: f"{settings.EXPORT_RATE_LIMIT}/minute")
async def export_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserResponseSchema = Depends(get_current_user),
    fmt: str = Query("json", alias="format"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Response:
    """Export orders in JSON or CSV format.

    Requires JWT authentication. Supports pagination via skip/limit.
    Format is selected via the `format` query parameter (default: "json").

    Args:
        fmt: Output format — "json" (default) or "csv".
        skip: Number of records to skip (pagination offset).
        limit: Maximum number of records to return (1-1000).

    Returns:
        200: Orders in the requested format.
        400: Invalid format parameter.
        401: Missing or invalid JWT token.
    """
    if fmt not in ("json", "csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: '{fmt}'. Use 'json' or 'csv'.",
        )

    service = _get_export_service(db)

    if fmt == "json":
        data = await service.export_orders_json(skip=skip, limit=limit)
        return Response(
            content=json.dumps(data, default=str),
            media_type="application/json",
        )

    # fmt == "csv"
    from app.utils.csv_exporter import export_orders_to_csv

    orders = await service.export_orders_raw(skip=skip, limit=limit)
    csv_content = export_orders_to_csv(orders)
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )
