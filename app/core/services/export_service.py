"""ExportService — application service for data export.

Orchestrates data retrieval from repositories and format conversion.
Depends on repository interfaces only (DIP). Zero HTTP/framework imports.
"""

from __future__ import annotations

from typing import Any

from app.core.entities.order import Order
from app.core.repositories.order_repository import IOrderRepository
from app.schemas.order import OrderResponseSchema


class ExportService:
    """Application service for exporting order data.

    Retrieves orders via the repository and converts them to
    the appropriate response format (JSON-serializable dicts).
    CSV formatting is handled separately by csv_exporter.py.
    """

    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    async def export_orders_json(
        self, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Export orders as JSON-serializable dictionaries.

        Args:
            skip: Number of records to skip (pagination offset).
            limit: Maximum number of records to return.

        Returns:
            List of OrderResponseSchema-compatible dictionaries.
        """
        orders = await self._order_repo.get_all(skip=skip, limit=limit)
        return [
            OrderResponseSchema.model_validate(o).model_dump(mode="json")
            for o in orders
        ]

    async def export_orders_raw(self, skip: int = 0, limit: int = 100) -> list[Order]:
        """Export orders as domain entities (for CSV path).

        Args:
            skip: Number of records to skip (pagination offset).
            limit: Maximum number of records to return.

        Returns:
            List of Order domain entities.
        """
        return await self._order_repo.get_all(skip=skip, limit=limit)
