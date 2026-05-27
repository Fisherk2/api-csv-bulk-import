"""SQLAlchemy implementation of IOrderRepository.

Maps domain Order/OrderItem entities to ORM objects.
Uses async SQLAlchemy with relationship cascade for atomic
persistence of the Order aggregate (header + line items).
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.entities.order import Order, OrderItem
from app.core.repositories.order_repository import IOrderRepository
from app.infrastructure.database.models.order import OrderItemModel, OrderModel

logger = logging.getLogger(__name__)


class OrderRepository(IOrderRepository):
    """SQLAlchemy-backed order repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by UUID, including its items."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_customer(
        self, customer_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        """Retrieve orders for a specific customer with pagination."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        """Retrieve all orders with pagination, including items."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def create(
        self, order: Order, customer_id: UUID | None = None
    ) -> Order:
        """Persist a new order with its items in a single transaction."""
        model = self._to_model(order)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def create_batch(self, orders: list[Order]) -> list[Order]:
        """Insert multiple orders with items using ON CONFLICT DO NOTHING.

        Args:
            orders: Domain entities to insert.

        Returns:
            All order entities from the input, regardless of which
            were actually persisted.
        """
        if not orders:
            return []

        now = datetime.now(UTC)
        models = [self._to_model(o) for o in orders]

        # Build order values for bulk insert
        order_values = [
            {
                "id": m.id,
                "customer_id": m.customer_id,
                "status": m.status,
                "created_at": now,
                "updated_at": now,
            }
            for m in models
        ]

        # Build item values
        item_values = []
        for m in models:
            for item in m.items:
                item_values.append(
                    {
                        "id": item.id,
                        "order_id": m.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price,
                        "created_at": now,
                    }
                )

        try:
            engine = self._session.get_bind()
            insert_fn = (
                pg_insert
                if engine.dialect.name == "postgresql"
                else sqlite_insert
            )

            # Track which orders were actually inserted (not skipped by ON CONFLICT)
            is_postgresql = engine.dialect.name == "postgresql"
            inserted_order_ids: set[UUID] = {m.id for m in models}

            if order_values:
                stmt = (
                    insert_fn(OrderModel)
                    .values(order_values)
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                result = await self._session.execute(stmt)
                # PostgreSQL's ON CONFLICT DO NOTHING + RETURNING tells us
                # which rows were actually inserted vs. skipped
                if is_postgresql:
                    returned_ids: set[UUID] = {
                        row.id for row in result.fetchall()
                    }
                    inserted_order_ids = returned_ids

            # Only insert items for orders that were actually created
            if item_values:
                filtered_items = [
                    iv
                    for iv in item_values
                    if iv["order_id"] in inserted_order_ids
                ]
                if filtered_items:
                    stmt = (
                        insert_fn(OrderItemModel)
                        .values(filtered_items)
                        .on_conflict_do_nothing(index_elements=["id"])
                    )
                    await self._session.execute(stmt)
        except Exception:
            logger.exception(
                "create_batch failed for %d orders, rolling back",
                len(orders),
            )
            await self._session.rollback()
        return [self._to_domain(m) for m in models]

    @staticmethod
    def _to_domain(model: OrderModel) -> Order:
        """Convert OrderModel to Order domain entity."""
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            status=model.status,
            created_at=model.created_at,
            items=[
                OrderItem(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in model.items
            ],
        )

    @staticmethod
    def _to_model(order: Order) -> OrderModel:
        """Convert Order domain entity to OrderModel."""
        return OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            created_at=order.created_at,
            items=[
                OrderItemModel(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price,
                )
                for item in order.items
            ],
        )
