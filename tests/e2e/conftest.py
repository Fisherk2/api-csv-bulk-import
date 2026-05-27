"""Shared fixtures for e2e tests.

Provides auth_token and seeded_data fixtures used across all
e2e test files (ASGI transport, SQLite in-memory).
"""

from __future__ import annotations

import pytest


@pytest.fixture
async def auth_token(client, test_user):
    """Obtain a JWT token for the test user."""
    response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def seeded_data(test_db_session):
    """Seed customers and products needed for upload tests."""
    from app.core.entities.customer import Customer
    from app.core.entities.product import Product
    from app.infrastructure.repositories.customer_repository import (
        CustomerRepository,
    )
    from app.infrastructure.repositories.product_repository import (
        ProductRepository,
    )

    cust_repo = CustomerRepository(session=test_db_session)
    prod_repo = ProductRepository(session=test_db_session)

    customer = await cust_repo.create(
        Customer(name="E2E Customer", email="e2e@example.com")
    )
    product_a = await prod_repo.create(
        Product(name="E2E Widget A", price=10.0, stock=50)
    )
    product_b = await prod_repo.create(
        Product(name="E2E Widget B", price=25.0, stock=100)
    )
    return {
        "customer": customer,
        "product_a": product_a,
        "product_b": product_b,
    }
