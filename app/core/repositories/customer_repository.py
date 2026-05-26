"""ICustomerRepository interface — contract for customer data access.

Defines the abstraction that domain services depend on.
Implementations live in app/infrastructure/repositories/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.entities.customer import Customer


class ICustomerRepository(ABC):
    """Repository interface for Customer aggregate."""

    @abstractmethod
    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        """Retrieve a customer by UUID. Returns None if not found."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Customer | None:
        """Retrieve a customer by email (business key)."""
        ...

    @abstractmethod
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[Customer]:
        """Retrieve all customers with pagination."""
        ...

    @abstractmethod
    async def create(self, customer: Customer) -> Customer:
        """Persist a new customer. Returns the created customer with id."""
        ...

    @abstractmethod
    async def create_batch(
        self, customers: list[Customer]
    ) -> list[Customer]:
        """Insert multiple customers, skipping duplicates by email.

        Uses INSERT ... ON CONFLICT (email) DO NOTHING.
        """
        ...

    @abstractmethod
    async def get_by_ids(
        self, customer_ids: list[UUID]
    ) -> list[Customer]:
        """Retrieve multiple customers by UUIDs."""
        ...
