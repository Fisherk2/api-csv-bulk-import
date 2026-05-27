"""Tests for ProductRepository implementation (T09 verification).

Validates async CRUD operations, batch insert with ON CONFLICT
handling, and domain-model conversion.
"""

from __future__ import annotations

import pytest

from app.core.entities.product import Product


class TestProductRepositoryCRUD:
    """ProductRepository must support async CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_product(self, test_db_session) -> None:
        """create must persist a Product and return it with an id."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        product = Product(name="Widget", price=19.99, stock=50)
        created = await repo.create(product)

        assert created.id is not None
        assert created.name == "Widget"
        assert created.price == 19.99
        assert created.stock == 50

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, test_db_session) -> None:
        """get_by_id must return the Product for an existing id."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        product = Product(name="Widget", price=19.99, stock=50)
        created = await repo.create(product)

        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.name == "Widget"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_db_session) -> None:
        """get_by_id must return None for a non-existent id."""
        from uuid import uuid4

        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        found = await repo.get_by_id(uuid4())
        assert found is None

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, test_db_session) -> None:
        """get_all must return products with correct pagination."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        for i in range(5):
            await repo.create(Product(name=f"Product {i}", price=10.0, stock=i))

        page = await repo.get_all(skip=1, limit=3)
        assert len(page) == 3
        assert all(isinstance(p, Product) for p in page)

    @pytest.mark.asyncio
    async def test_create_batch_inserts_multiple(self, test_db_session) -> None:
        """create_batch must insert multiple products."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        products = [
            Product(name="A", price=1.0, stock=10),
            Product(name="B", price=2.0, stock=20),
            Product(name="C", price=3.0, stock=30),
        ]
        created = await repo.create_batch(products)
        assert len(created) == 3

    @pytest.mark.asyncio
    async def test_create_batch_empty(self, test_db_session) -> None:
        """create_batch with empty list must return empty list."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        result = await repo.create_batch([])
        assert result == []

    @pytest.mark.asyncio
    async def test_create_batch_duplicate_handling(self, test_db_session) -> None:
        """create_batch must skip duplicate IDs and insert unique ones."""
        from uuid import uuid4

        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)

        # Create a product with a known UUID
        known_id = uuid4()
        original = Product(id=known_id, name="Original", price=5.0, stock=10)
        await repo.create(original)

        # Batch insert: one duplicate ID, one unique product
        duplicate = Product(id=known_id, name="Duplicate", price=10.0, stock=20)
        unique = Product(name="Unique", price=1.0, stock=1)

        result = await repo.create_batch([duplicate, unique])

        # No error should be raised
        assert len(result) == 2

        # Unique product must be persisted
        found_unique = await repo.get_by_id(unique.id)
        assert found_unique is not None
        assert found_unique.name == "Unique"

        # Original product must be unchanged (duplicate skipped)
        found_original = await repo.get_by_id(known_id)
        assert found_original is not None
        assert found_original.name == "Original"
        assert found_original.price == 5.0

    @pytest.mark.asyncio
    async def test_get_by_ids_retrieves_multiple(self, test_db_session) -> None:
        """get_by_ids must retrieve multiple products by their ids."""
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        repo = ProductRepository(session=test_db_session)
        p1 = await repo.create(Product(name="X", price=1.0, stock=1))
        p2 = await repo.create(Product(name="Y", price=2.0, stock=2))

        found = await repo.get_by_ids([p1.id, p2.id])
        assert len(found) == 2
        names = {p.name for p in found}
        assert names == {"X", "Y"}


class TestProductRepositoryInterface:
    """IProductRepository must be an ABC with all abstract methods."""

    def test_interface_imports(self) -> None:
        """IProductRepository must be importable."""
        from app.core.repositories.product_repository import IProductRepository

        assert IProductRepository is not None

    def test_interface_is_abstract(self) -> None:
        """IProductRepository must be an abstract base class."""
        from abc import ABC

        from app.core.repositories.product_repository import IProductRepository

        assert issubclass(IProductRepository, ABC)

    def test_impl_inherits_from_interface(self) -> None:
        """ProductRepository must inherit from IProductRepository."""
        from app.core.repositories.product_repository import IProductRepository
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        assert issubclass(ProductRepository, IProductRepository)
