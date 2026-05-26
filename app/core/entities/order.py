"""Order and OrderItem domain entities — pure business logic, no framework.

Represents a customer order with one or more line items.
Order and OrderItem form a single aggregate — Order is the aggregate root.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class OrderItem:
    """Domain entity representing a single line item within an order.

    References a product by ID with quantity purchased and unit price.
    Always belongs to exactly one Order aggregate.
    """

    product_id: UUID
    quantity: int
    price: float
    id: UUID = field(default_factory=uuid4)


@dataclass
class Order:
    """Domain entity representing a customer order (aggregate root).

    An Order has a status lifecycle and contains one or more OrderItems.
    The Order is the aggregate root — items are accessed only through it.
    """

    customer_id: UUID
    status: str = "pending"
    items: list[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: UUID = field(default_factory=uuid4)
