"""Tests for OrderService (T15 verification).

Validates order orchestration: validation, product FK validation,
and persistence via repository interfaces.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest


class TestOrderService:
    """OrderService must orchestrate upload with mocked repositories."""

    @pytest.mark.asyncio
    async def test_upload_valid_orders(self) -> None:
        """Valid orders must be persisted and return success."""
        from app.core.services.order_service import OrderService

        pid = uuid4()
        cid = uuid4()

        # Mock repositories
        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_ids.return_value = [
            MagicMock(id=pid)
        ]
        mock_order_repo = AsyncMock()

        service = OrderService(
            product_repo=mock_product_repo,
            order_repo=mock_order_repo,
        )

        data = [
            {
                "customer_id": str(cid),
                "items": [{"product_id": str(pid), "quantity": 1, "price": 10.0}],
            },
        ]

        result = await service.upload_orders(data, user_id=uuid4())
        assert result.total == 1
        assert result.successful == 1
        assert result.failed == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_upload_partial_validation_errors(self) -> None:
        """Validation errors must be reported, valid orders persisted."""
        from app.core.services.order_service import OrderService

        pid = uuid4()
        cid = uuid4()

        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_ids.return_value = [
            MagicMock(id=pid)
        ]
        mock_order_repo = AsyncMock()

        service = OrderService(
            product_repo=mock_product_repo,
            order_repo=mock_order_repo,
        )

        data = [
            {
                "customer_id": str(cid),
                "items": [{"product_id": str(pid), "quantity": 1, "price": 10.0}],
            },
            {
                "customer_id": str(cid),
                "items": [],  # INVALID
            },
        ]

        result = await service.upload_orders(data, user_id=uuid4())
        assert result.total == 2
        assert result.successful == 1
        assert result.failed == 1
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_upload_all_invalid(self) -> None:
        """All invalid orders must return all errors, zero successful."""
        from app.core.services.order_service import OrderService

        cid = uuid4()
        mock_product_repo = AsyncMock()
        mock_order_repo = AsyncMock()

        service = OrderService(
            product_repo=mock_product_repo,
            order_repo=mock_order_repo,
        )

        data = [
            {"customer_id": str(cid), "items": []},
            {"customer_id": str(cid), "items": []},
        ]

        result = await service.upload_orders(data, user_id=uuid4())
        assert result.total == 2
        assert result.successful == 0
        assert result.failed == 2
        assert len(result.errors) == 2

    @pytest.mark.asyncio
    async def test_upload_all_fk_invalid(self) -> None:
        """All orders with non-existent product IDs must return FK errors."""
        from app.core.services.order_service import OrderService

        cid = uuid4()
        fake_pid = uuid4()

        mock_product_repo = AsyncMock()
        mock_product_repo.get_by_ids.return_value = []  # No products exist
        mock_order_repo = AsyncMock()

        service = OrderService(
            product_repo=mock_product_repo,
            order_repo=mock_order_repo,
        )

        data = [
            {
                "customer_id": str(cid),
                "items": [{"product_id": str(fake_pid), "quantity": 1, "price": 10.0}],
            },
            {
                "customer_id": str(cid),
                "items": [{"product_id": str(uuid4()), "quantity": 2, "price": 20.0}],
            },
        ]

        result = await service.upload_orders(data, user_id=uuid4())
        assert result.total == 2
        assert result.successful == 0
        assert result.failed == 2
        assert len(result.errors) == 2
        # Verify FK error detail
        assert "Product(s) not found" in result.errors[0].detail
        assert "Product(s) not found" in result.errors[1].detail

    @staticmethod
    def _setup_service(mock_product_repo, mock_order_repo):
        """Create OrderService with mocked repos."""
        from app.core.services.order_service import OrderService

        return OrderService(
            product_repo=mock_product_repo,
            order_repo=mock_order_repo,
        )
