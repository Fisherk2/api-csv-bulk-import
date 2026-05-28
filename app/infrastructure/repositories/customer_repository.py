"""SQLAlchemy implementation of ICustomerRepository.

Maps domain Customer entities to CustomerModel ORM objects and vice versa.
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

from app.core.entities.customer import Customer
from app.core.repositories.customer_repository import ICustomerRepository
from app.infrastructure.database.models.customer import CustomerModel

logger = logging.getLogger(__name__)


class CustomerRepository(ICustomerRepository):
    """SQLAlchemy-backed customer repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        """Retrieve a customer by UUID."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.id == customer_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Customer | None:
        """Retrieve a customer by email (business key)."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        """Retrieve all customers with pagination."""
        result = await self._session.execute(
            select(CustomerModel).offset(skip).limit(limit)
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def create(self, customer: Customer) -> Customer:
        """Persist a new customer."""
        model = self._to_model(customer)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def create_batch(self, customers: list[Customer]) -> list[Customer]:
        """Insert multiple customers, skipping duplicates by email.

        Uses INSERT ... ON CONFLICT (email) DO NOTHING for email-based
        deduplication. Customers with duplicate emails are silently skipped.

        Args:
            customers: Domain entities to insert.

        Returns:
            All customer entities from the input, regardless of which
            were actually persisted.
        """
        if not customers:
            return []

        now = datetime.now(UTC)
        models = [self._to_model(c) for c in customers]
        values = [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
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
                insert_fn(CustomerModel)
                .values(values)
                .on_conflict_do_nothing(index_elements=["email"])
            )
            await self._session.execute(stmt)
        except Exception:
            logger.exception(
                "create_batch failed for %d customers, rolling back",
                len(customers),
            )
            await self._session.rollback()
            raise
        return [self._to_domain(m) for m in models]

    async def get_by_ids(self, customer_ids: list[UUID]) -> list[Customer]:
        """Retrieve multiple customers by UUIDs."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.id.in_(customer_ids))
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(model: CustomerModel) -> Customer:
        """Convert a CustomerModel ORM object to a Customer domain entity."""
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
        )

    @staticmethod
    def _to_model(customer: Customer) -> CustomerModel:
        """Convert a Customer domain entity to a CustomerModel ORM object."""
        return CustomerModel(
            id=customer.id,
            name=customer.name,
            email=customer.email,
        )
