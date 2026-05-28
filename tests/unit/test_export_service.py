"""Tests for ExportService (T18 verification).

Validates export orchestration: JSON serialization via OrderResponseSchema,
raw domain entity retrieval, and pagination forwarding to repository.
"""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest


class TestExportService:
    """ExportService must orchestrate export with mocked IOrderRepository."""

    @pytest.mark.asyncio
    async def test_export_json_returns_serializable_dicts(self) -> None:
        """export_orders_json must return JSON-serializable dicts."""
        from app.core.entities.order import Order, OrderItem
        from app.core.services.export_service import ExportService

        order_id = uuid4()
        product_id = uuid4()
        order = Order(
            id=order_id,
            customer_id=uuid4(),
            status="pending",
            items=[
                OrderItem(id=uuid4(), product_id=product_id, quantity=2, price=19.99)
            ],
        )

        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = [order]

        service = ExportService(order_repo=mock_repo)
        result = await service.export_orders_json(skip=0, limit=100)

        assert len(result) == 1
        item = result[0]
        assert item["id"] == str(order_id)
        assert item["status"] == "pending"
        assert len(item["items"]) == 1
        assert item["items"][0]["product_id"] == str(product_id)
        assert item["items"][0]["quantity"] == 2
        assert item["items"][0]["price"] == 19.99
        mock_repo.get_all.assert_called_once_with(skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_export_json_pagination(self) -> None:
        """Pagination params must be forwarded to repository."""
        from app.core.entities.order import Order
        from app.core.services.export_service import ExportService

        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = [
            Order(id=uuid4(), customer_id=uuid4(), items=[]) for _ in range(50)
        ]

        service = ExportService(order_repo=mock_repo)
        result = await service.export_orders_json(skip=10, limit=50)

        assert len(result) == 50
        mock_repo.get_all.assert_called_once_with(skip=10, limit=50)

    @pytest.mark.asyncio
    async def test_export_raw_returns_domain_entities(self) -> None:
        """export_orders_raw must return domain Order entities."""
        from app.core.entities.order import Order, OrderItem
        from app.core.services.export_service import ExportService

        domain_order = Order(
            id=uuid4(),
            customer_id=uuid4(),
            status="completed",
            items=[OrderItem(id=uuid4(), product_id=uuid4(), quantity=1, price=5.0)],
        )

        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = [domain_order]

        service = ExportService(order_repo=mock_repo)
        result = await service.export_orders_raw(skip=0, limit=10)

        assert len(result) == 1
        assert isinstance(result[0], Order)
        assert result[0].id == domain_order.id
        assert result[0].status == "completed"
        assert len(result[0].items) == 1
        assert result[0].items[0].price == 5.0
        mock_repo.get_all.assert_called_once_with(skip=0, limit=10)

    @pytest.mark.asyncio
    async def test_export_empty(self) -> None:
        """Empty repository must return empty lists."""
        from app.core.services.export_service import ExportService

        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = []

        service = ExportService(order_repo=mock_repo)

        json_result = await service.export_orders_json(skip=0, limit=100)
        assert json_result == []

        raw_result = await service.export_orders_raw(skip=0, limit=100)
        assert raw_result == []

    @pytest.mark.asyncio
    async def test_default_pagination(self) -> None:
        """Default pagination values must be 0/100."""
        from app.core.services.export_service import ExportService

        mock_repo = AsyncMock()
        mock_repo.get_all.return_value = []

        service = ExportService(order_repo=mock_repo)

        # Call with no args (use defaults)
        await service.export_orders_json()
        mock_repo.get_all.assert_called_once_with(skip=0, limit=100)
