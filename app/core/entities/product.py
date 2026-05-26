"""Product domain entity — pure business logic, no framework dependencies.

Represents a sellable product with pricing and stock tracking.
This is a DDD entity, not a database model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Product:
    """Domain entity representing a product available for sale.

    Equality is based on identity (id), not attributes.
    Products are uniquely identified by their UUID, while the
    (name, price) combination serves as a business key for
    batch import deduplication.
    """

    name: str
    price: float
    stock: int
    id: UUID = field(default_factory=uuid4)
