"""SQLAlchemy implementation of IProductRepository.

Maps domain Product entities to ProductModel ORM objects and vice versa.
Uses async SQLAlchemy sessions for non-blocking database operations.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.entities.product import Product
from app.core.repositories.product_repository import IProductRepository
from app.infrastructure.database.models.product import ProductModel

logger = logging.getLogger(__name__)


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

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
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

    async def create_batch(self, products: list[Product]) -> list[Product]:
        """Insert multiple products, skipping duplicates by primary key.

        Uses INSERT ... ON CONFLICT (id) DO NOTHING for true partial
        processing. Products with duplicate IDs are silently skipped;
        all other products are inserted.

        Args:
            products: Domain entities to insert.

        Returns:
            All product entities from the input, regardless of which
            were actually persisted.
        """
        if not products:
            return []

        now = datetime.now(UTC)
        models = [self._to_model(p) for p in products]
        values = [
            {
                "id": m.id,
                "name": m.name,
                "price": m.price,
                "stock": m.stock,
                "created_at": now,
                "updated_at": now,
            }
            for m in models
        ]

        try:
            engine = self._session.get_bind()
            insert_fn = (
                pg_insert if engine.dialect.name == "postgresql" else sqlite_insert
            )
            stmt = (
                insert_fn(ProductModel)
                .values(values)
                .on_conflict_do_nothing(index_elements=["id"])
            )
            await self._session.execute(stmt)
        except Exception:
            logger.exception(
                "create_batch failed for %d products, rolling back",
                len(products),
            )
            await self._session.rollback()
        return [self._to_domain(m) for m in models]

    async def get_by_ids(self, product_ids: list[UUID]) -> list[Product]:
        """Retrieve multiple products by UUIDs."""
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id.in_(product_ids))
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
