"""IProductRepository interface — contract for product data access.

Defines the abstraction that domain services depend on.
Implementations live in app/infrastructure/repositories/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.entities.product import Product


class IProductRepository(ABC):
    """Repository interface for Product aggregate."""

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Retrieve a product by its UUID. Returns None if not found."""
        ...

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[Product]:
        """Retrieve all products with pagination."""
        ...

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Persist a new product. Returns the created product with id."""
        ...

    @abstractmethod
    async def create_batch(self, products: list[Product]) -> list[Product]:
        """Insert multiple products using INSERT ... ON CONFLICT DO NOTHING.

        Silently skips duplicates. Returns the list of successfully
        inserted products.
        """
        ...

    @abstractmethod
    async def get_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        """Retrieve multiple products by their UUIDs."""
        ...
