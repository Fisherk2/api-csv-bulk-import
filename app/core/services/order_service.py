"""OrderService — application service for order upload orchestration.

Orchestrates the batch upload flow: validates raw data via Pydantic
schemas, validates product foreign keys via repository, and persists
orders via repository interfaces.

Depends on repository interfaces (DIP), not concrete implementations.
ZERO imports from sqlalchemy or fastapi.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.core.entities.order import Order, OrderItem
from app.core.repositories.customer_repository import ICustomerRepository
from app.core.repositories.order_repository import IOrderRepository
from app.core.repositories.product_repository import IProductRepository
from app.schemas.order import (
    BatchErrorDetailSchema,
    BatchUploadResponseSchema,
    OrderCreateSchema,
)

logger = logging.getLogger(__name__)


class OrderService:
    """Application service orchestrating the batch order upload flow.

    Coordinates schema validation, product FK validation, and
    persistence. All infrastructure dependencies are injected via
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

        # Step 1: Schema validation with index tracking
        valid_schemas: list[OrderCreateSchema] = []
        valid_indices: list[int] = []  # 0-indexed positions in orders_data
        errors: list[BatchErrorDetailSchema] = []

        for i, item_data in enumerate(orders_data):
            try:
                validated = OrderCreateSchema.model_validate(item_data)
                valid_schemas.append(validated)
                valid_indices.append(i)
            except ValueError as exc:
                errors.append(
                    BatchErrorDetailSchema(
                        type="about:blank",
                        title="Validation Error",
                        status=422,
                        detail=str(exc),
                        row_number=i + 1,
                    )
                )

        if not valid_schemas:
            return BatchUploadResponseSchema(
                total=total,
                successful=0,
                failed=total,
                errors=errors,
            )

        # Step 2: Product foreign key validation via batch query
        all_product_ids: set[UUID] = set()
        for s in valid_schemas:
            for item in s.items:
                all_product_ids.add(item.product_id)

        existing_products = await self._product_repo.get_by_ids(
            list(all_product_ids)
        )
        existing_pids: set[UUID] = {p.id for p in existing_products}

        # Filter valid schemas: remove orders with missing product references
        fk_valid_schemas: list[OrderCreateSchema] = []
        for idx, s in enumerate(valid_schemas):
            missing_pids = [
                item.product_id
                for item in s.items
                if item.product_id not in existing_pids
            ]
            if missing_pids:
                errors.append(
                    BatchErrorDetailSchema(
                        type="about:blank",
                        title="Foreign Key Error",
                        status=422,
                        detail=(
                            f"Product(s) not found: "
                            f"{', '.join(str(pid) for pid in missing_pids)}"
                        ),
                        row_number=valid_indices[idx] + 1,
                    )
                )
            else:
                fk_valid_schemas.append(s)

        if not fk_valid_schemas:
            return BatchUploadResponseSchema(
                total=total,
                successful=0,
                failed=total,
                errors=errors,
            )

        # Step 3: Convert valid schemas to domain entities
        domain_orders: list[Order] = []
        for s in fk_valid_schemas:
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

        successful = len(fk_valid_schemas)
        failed = total - successful

        return BatchUploadResponseSchema(
            total=total,
            successful=successful,
            failed=failed,
            errors=errors,
        )
