"""IOrderRepository interface — contract for order data access.

Defines the abstraction that domain services depend on.
Implementations live in app/infrastructure/repositories/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.entities.order import Order


class IOrderRepository(ABC):
    """Repository interface for Order aggregate (Order + OrderItems)."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Retrieve an order by UUID, including its items."""
        ...

    @abstractmethod
    async def get_by_customer(
        self, customer_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        """Retrieve orders for a specific customer with pagination."""
        ...

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        """Retrieve all orders with pagination, including items."""
        ...

    @abstractmethod
    async def create(
        self, order: Order, customer_id: UUID | None = None
    ) -> Order:
        """Persist a new order with its items in a single transaction."""
        ...

    @abstractmethod
    async def create_batch(self, orders: list[Order]) -> list[Order]:
        """Insert multiple orders with items in a single transaction.

        Uses INSERT ... ON CONFLICT (id) DO NOTHING for partial processing.
        """
        ...
