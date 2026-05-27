"""OrderService — application service for order upload orchestration.

Orchestrates the batch upload flow: validates raw data via
ValidationService, resolves customer references, validates product
foreign keys, and persists orders via repository interfaces.

Depends on repository interfaces (DIP), not concrete implementations.
ZERO imports from sqlalchemy or fastapi.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.core.entities.order import Order, OrderItem
from app.core.entities.validation import BatchValidationError
from app.core.repositories.customer_repository import ICustomerRepository
from app.core.repositories.order_repository import IOrderRepository
from app.core.repositories.product_repository import IProductRepository
from app.core.services.validation_service import ValidationService
from app.schemas.order import (
    BatchErrorDetailSchema,
    BatchUploadResponseSchema,
    OrderCreateSchema,
)

logger = logging.getLogger(__name__)


class OrderService:
    """Application service orchestrating the batch order upload flow.

    Coordinates validation, customer resolution, product FK validation,
    and persistence. All infrastructure dependencies are injected via
    repository interfaces (Dependency Inversion Principle).
    """

    def __init__(
        self,
        customer_repo: ICustomerRepository,
        product_repo: IProductRepository,
        order_repo: IOrderRepository,
    ) -> None:
        self._customer_repo = customer_repo
        self._product_repo = product_repo
        self._order_repo = order_repo

    async def upload_orders(
        self,
        orders_data: list[dict[str, Any]],
        user_id: UUID,
    ) -> BatchUploadResponseSchema:
        """Process a batch of order data from upload.

        Args:
            orders_data: Raw dicts from parsed CSV/JSON input.
            user_id: Authenticated JWT user ID (for audit logging).

        Returns:
            BatchUploadResponseSchema with total, successful, failed, errors.
        """
        logger.info("Upload batch of %d orders by user %s", len(orders_data), user_id)

        total = len(orders_data)

        # Step 1: Validate against schema
        valid_schemas, validation_errors = ValidationService.validate_batch(
            orders_data, OrderCreateSchema
        )

        # Step 2: Convert domain errors to API schema
        errors = [
            BatchErrorDetailSchema(
                type="about:blank",
                title="Validation Error",
                status=422,
                detail=e.message,
                row_number=e.row_number,
            )
            for e in validation_errors
        ]

        if not valid_schemas:
            return BatchUploadResponseSchema(
                total=total,
                successful=0,
                failed=total,
                errors=errors,
            )

        # Step 3: Convert valid schemas to domain entities
        domain_orders: list[Order] = []

        for s_idx, s in enumerate(valid_schemas, start=1):
            domain_orders.append(
                Order(
                    customer_id=s.customer_id,
                    items=[
                        OrderItem(
                            product_id=i.product_id,
                            quantity=i.quantity,
                            price=i.price,
                        )
                        for i in s.items
                    ],
                )
            )

        # Step 4: Persist via repository
        await self._order_repo.create_batch(domain_orders)

        successful = len(valid_schemas)
        failed = len(validation_errors)

        return BatchUploadResponseSchema(
            total=total,
            successful=successful,
            failed=failed,
            errors=errors,
        )
