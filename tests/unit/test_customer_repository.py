"""Tests for CustomerRepository implementation (T11 verification).

Validates async CRUD operations, email-based lookup, batch insert
with ON CONFLICT (email) handling, and domain-model conversion.
"""

from __future__ import annotations

import pytest

from app.core.entities.customer import Customer


class TestCustomerRepositoryCRUD:
    """CustomerRepository must support async CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_customer(self, test_db_session) -> None:
        """create must persist a Customer and return it with an id."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        customer = Customer(name="John Doe", email="john@example.com")
        created = await repo.create(customer)

        assert created.id is not None
        assert created.name == "John Doe"
        assert created.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, test_db_session) -> None:
        """get_by_id must return the Customer for an existing id."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        customer = Customer(name="John Doe", email="john@example.com")
        created = await repo.create(customer)

        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_db_session) -> None:
        """get_by_id must return None for a non-existent id."""
        from uuid import uuid4

        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        found = await repo.get_by_id(uuid4())
        assert found is None

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, test_db_session) -> None:
        """get_by_email must return the Customer for an existing email."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        customer = Customer(name="John Doe", email="john@example.com")
        await repo.create(customer)

        found = await repo.get_by_email("john@example.com")
        assert found is not None
        assert found.email == "john@example.com"
        assert found.name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, test_db_session) -> None:
        """get_by_email must return None for a non-existent email."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        found = await repo.get_by_email("nobody@example.com")
        assert found is None

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, test_db_session) -> None:
        """get_all must return customers with correct pagination."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        for i in range(5):
            await repo.create(
                Customer(name=f"Customer {i}", email=f"user{i}@example.com")
            )

        page = await repo.get_all(skip=1, limit=3)
        assert len(page) == 3
        assert all(isinstance(c, Customer) for c in page)

    @pytest.mark.asyncio
    async def test_create_batch_inserts_multiple(self, test_db_session) -> None:
        """create_batch must insert multiple customers."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        customers = [
            Customer(name="A", email="a@example.com"),
            Customer(name="B", email="b@example.com"),
            Customer(name="C", email="c@example.com"),
        ]
        created = await repo.create_batch(customers)
        assert len(created) == 3

    @pytest.mark.asyncio
    async def test_create_batch_email_deduplication(self, test_db_session) -> None:
        """create_batch must skip duplicate emails (ON CONFLICT DO NOTHING)."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)

        # Create an original customer
        original = Customer(
            name="Original Name", email="dup@example.com"
        )
        await repo.create(original)

        # Batch insert: one duplicate email, one unique customer
        duplicate = Customer(
            name="Duplicate Name", email="dup@example.com"
        )
        unique = Customer(name="Unique", email="unique@example.com")

        result = await repo.create_batch([duplicate, unique])
        assert len(result) == 2

        # Unique customer must be persisted
        found_unique = await repo.get_by_email("unique@example.com")
        assert found_unique is not None
        assert found_unique.name == "Unique"

        # Original must be unchanged (duplicate skipped)
        found_original = await repo.get_by_email("dup@example.com")
        assert found_original is not None
        assert found_original.name == "Original Name"

    @pytest.mark.asyncio
    async def test_get_by_ids_retrieves_multiple(self, test_db_session) -> None:
        """get_by_ids must retrieve multiple customers by their ids."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        c1 = await repo.create(
            Customer(name="X", email="x@example.com")
        )
        c2 = await repo.create(
            Customer(name="Y", email="y@example.com")
        )

        found = await repo.get_by_ids([c1.id, c2.id])
        assert len(found) == 2
        emails = {c.email for c in found}
        assert emails == {"x@example.com", "y@example.com"}

    @pytest.mark.asyncio
    async def test_create_batch_empty_list(self, test_db_session) -> None:
        """create_batch with empty list must return empty list."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        result = await repo.create_batch([])
        assert result == []

    @pytest.mark.asyncio
    async def test_create_batch_exception_handling(
        self, test_db_session, mocker
    ) -> None:
        """DB error during create_batch must rollback and propagate."""
        from app.core.entities.customer import Customer
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        repo = CustomerRepository(session=test_db_session)
        mocker.patch.object(
            test_db_session, "execute",
            side_effect=Exception("Simulated DB failure"),
        )
        customer = Customer(name="Error Test", email="error@example.com")
        with pytest.raises(Exception, match="Simulated DB failure"):
            await repo.create_batch([customer])


class TestCustomerRepositoryInterface:
    """ICustomerRepository must be an ABC with all abstract methods."""

    def test_interface_imports(self) -> None:
        """ICustomerRepository must be importable."""
        from app.core.repositories.customer_repository import (
            ICustomerRepository,
        )

        assert ICustomerRepository is not None

    def test_interface_is_abstract(self) -> None:
        """ICustomerRepository must be an abstract base class."""
        from abc import ABC

        from app.core.repositories.customer_repository import (
            ICustomerRepository,
        )

        assert issubclass(ICustomerRepository, ABC)

    def test_impl_inherits_from_interface(self) -> None:
        """CustomerRepository must inherit from ICustomerRepository."""
        from app.core.repositories.customer_repository import (
            ICustomerRepository,
        )
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        assert issubclass(CustomerRepository, ICustomerRepository)
