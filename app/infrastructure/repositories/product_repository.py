"""SQLAlchemy implementation of IProductRepository.

Maps domain Product entities to ProductModel ORM objects and vice versa.
Uses async SQLAlchemy sessions for non-blocking database operations.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.product import Product
from app.core.repositories.product_repository import IProductRepository
from app.infrastructure.database.models.product import ProductModel


class ProductRepository(IProductRepository):
    """SQLAlchemy-backed product repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Retrieve a product by UUID."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[Product]:
        """Retrieve all products with pagination."""
        result = await self._session.execute(
            select(ProductModel).offset(skip).limit(limit)
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def create(self, product: Product) -> Product:
        """Persist a new product."""
        model = self._to_model(product)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def create_batch(
        self, products: list[Product]
    ) -> list[Product]:
        """Insert multiple products, skipping duplicates."""
        models = [self._to_model(p) for p in products]
        self._session.add_all(models)
        try:
            await self._session.flush()
        except Exception:
            await self._session.rollback()
        return [self._to_domain(m) for m in models]

    async def get_by_ids(
        self, product_ids: list[UUID]
    ) -> list[Product]:
        """Retrieve multiple products by UUIDs."""
        result = await self._session.execute(
            select(ProductModel).where(
                ProductModel.id.in_(product_ids)
            )
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(model: ProductModel) -> Product:
        """Convert a ProductModel ORM object to a Product domain entity."""
        return Product(
            id=model.id,
            name=model.name,
            price=model.price,
            stock=model.stock,
        )

    @staticmethod
    def _to_model(product: Product) -> ProductModel:
        """Convert a Product domain entity to a ProductModel ORM object."""
        return ProductModel(
            id=product.id,
            name=product.name,
            price=product.price,
            stock=product.stock,
        )
