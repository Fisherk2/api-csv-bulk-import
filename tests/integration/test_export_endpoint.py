"""Integration tests for GET /export endpoint (T18 verification).

Tests JSON and CSV export formats, authentication, pagination,
and data integrity against the test database.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
class TestExportEndpoint:
    """GET /export must return orders in JSON or CSV with pagination."""

    @pytest.fixture(autouse=True)
    async def _setup(self, test_db_session, test_user):
        """Seed test data and create authenticated client."""
        from app.core.entities.customer import Customer
        from app.core.entities.product import Product
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        # Create test customer + product
        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        self.customer = await cust_repo.create(
            Customer(name="Export Test", email="export@example.com")
        )
        self.product = await prod_repo.create(
            Product(name="Export Widget", price=25.0, stock=50)
        )

        # Upload a test order via the upload endpoint
        self.client, self.token, self._app = await self._create_auth_client(
            test_db_session, test_user
        )
        await self.client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(self.customer.id),
                        "items": [
                            {
                                "product_id": str(self.product.id),
                                "quantity": 3,
                                "price": 25.0,
                            }
                        ],
                    }
                ]
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        yield
        await self.client.aclose()
        self._app.dependency_overrides.clear()

    async def test_export_json_default(self) -> None:
        """GET /export without format must return 200 with JSON array."""
        response = await self.client.get(
            "/export",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        order = data[0]
        assert "id" in order
        assert "customer_id" in order
        assert "status" in order
        assert "items" in order
        assert "created_at" in order
        assert len(order["items"]) >= 1
        assert order["items"][0]["product_id"] == str(self.product.id)
        assert order["items"][0]["quantity"] == 3

    async def test_export_json_explicit_format(self) -> None:
        """GET /export?format=json must return JSON array."""
        response = await self.client.get(
            "/export?format=json",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, list)

    async def test_export_csv(self) -> None:
        """GET /export?format=csv must return CSV with proper headers."""
        response = await self.client.get(
            "/export?format=csv",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers.get("content-disposition", "")
        text = response.text
        lines = text.strip().split("\n")
        assert len(lines) >= 2  # Header + at least 1 data row
        header = lines[0]
        assert header == (
            "order_id,customer_id,product_id,quantity,price,status,created_at"
        )
        # Data row should have 7 fields
        data = lines[1].split(",")
        assert len(data) == 7

    async def test_export_unauthorized(self) -> None:
        """GET /export without token must return 401."""
        response = await self.client.get("/export")
        assert response.status_code == 401

    async def test_export_invalid_format(self) -> None:
        """GET /export?format=xml must return 400."""
        response = await self.client.get(
            "/export?format=xml",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 400

    async def test_export_pagination(self) -> None:
        """GET /export?skip=0&limit=10 must respect pagination."""
        response = await self.client.get(
            "/export?skip=0&limit=10",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    async def test_export_empty_result(self) -> None:
        """GET /export with skip beyond data must return empty array."""
        response = await self.client.get(
            "/export?skip=9999&limit=10",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_export_limit_exceeded(self) -> None:
        """GET /export?limit=1001 must return 422 (exceeds max 1000)."""
        response = await self.client.get(
            "/export?limit=1001",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    async def test_export_limit_zero(self) -> None:
        """GET /export?limit=0 must return 422 (below min 1)."""
        response = await self.client.get(
            "/export?limit=0",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    @staticmethod
    async def _create_auth_client(test_db_session, test_user):
        """Create authenticated httpx client with test DB override."""
        from httpx import ASGITransport, AsyncClient

        from app.infrastructure.database.session import get_db
        from app.main import create_app

        app = create_app()

        async def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        login_response = await client.post(
            "/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        token = login_response.json()["access_token"]
        return client, token, app
