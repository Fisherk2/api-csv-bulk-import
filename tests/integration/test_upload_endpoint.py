"""Integration tests for POST /upload endpoint (T17 verification).

Tests the full request/response cycle for JSON body and CSV upload,
including authentication validation and partial processing behavior.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

# ── Shared test helpers ──────────────────────────────────────────


async def _create_test_data(test_db_session) -> tuple:
    """Create customer and product for upload tests."""
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
        Customer(name="Test Customer", email="test@example.com")
    )
    product = await prod_repo.create(
        Product(name="Test Widget", price=10.0, stock=100)
    )
    return customer, product


async def _create_auth_client(test_db_session, test_user):
    """Create authenticated httpx client with test DB override."""
    from httpx import ASGITransport, AsyncClient

    from app.infrastructure.database.session import get_db
    from app.main import create_app

    app = create_app()

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )

    login_response = await client.post(
        "/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"],
        },
    )
    token = login_response.json()["access_token"]
    return client, token, app


# ── Test classes ──────────────────────────────────────────────────


@pytest.mark.asyncio
class TestUploadEndpointJSON:
    """POST /upload with JSON body must validate and persist orders."""

    @pytest.fixture(autouse=True)
    async def _setup(self, test_db_session, test_user):
        self.customer, self.product = await _create_test_data(test_db_session)
        self.auth_client, self.token, self._app = await _create_auth_client(
            test_db_session, test_user
        )
        yield
        await self.auth_client.aclose()
        self._app.dependency_overrides.clear()

    async def test_upload_valid_orders_200(self) -> None:
        """Valid orders must return 200 with all successful."""
        response = await self.auth_client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(self.customer.id),
                        "items": [
                            {
                                "product_id": str(self.product.id),
                                "quantity": 2,
                                "price": 10.0,
                            }
                        ],
                    }
                ]
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0

    async def test_upload_partial_invalid_207(self) -> None:
        """Mixed valid/invalid orders must return 207 with errors."""
        response = await self.auth_client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(self.customer.id),
                        "items": [
                            {
                                "product_id": str(self.product.id),
                                "quantity": 2,
                                "price": 10.0,
                            }
                        ],
                    },
                    {
                        "customer_id": str(self.customer.id),
                        "items": [],  # INVALID: empty items
                    },
                ]
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 207
        data = response.json()
        assert data["total"] == 2
        assert data["successful"] == 1
        assert data["failed"] == 1
        assert len(data["errors"]) == 1

    async def test_upload_all_invalid_422(self) -> None:
        """All invalid orders must return 422."""
        response = await self.auth_client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(self.customer.id),
                        "items": [],  # INVALID
                    },
                ]
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    async def test_upload_no_auth_401(self) -> None:
        """Request without token must return 401."""
        response = await self.auth_client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(self.customer.id),
                        "items": [
                            {
                                "product_id": str(self.product.id),
                                "quantity": 1,
                                "price": 10.0,
                            }
                        ],
                    }
                ]
            },
        )
        assert response.status_code == 401

    async def test_upload_invalid_json_400(self) -> None:
        """Malformed request body must return 400."""
        response = await self.auth_client.post(
            "/upload",
            json={"wrong_key": []},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 400


@pytest.mark.asyncio
class TestUploadEndpointCSV:
    """POST /upload with CSV must parse and persist orders."""

    @pytest.fixture(autouse=True)
    async def _setup(self, test_db_session, test_user):
        self.customer, self.product = await _create_test_data(test_db_session)
        # Ensure unique customer email for CSV
        from app.core.entities.customer import Customer
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )

        cust_repo = CustomerRepository(session=test_db_session)
        self.csv_customer = await cust_repo.create(
            Customer(name="CSV Customer", email="csv@example.com")
        )

        self.auth_client, self.token, self._app = await _create_auth_client(
            test_db_session, test_user
        )
        yield
        await self.auth_client.aclose()
        self._app.dependency_overrides.clear()

    async def test_upload_csv_valid_200(self) -> None:
        """Valid CSV must return 200."""
        import io

        pid = str(self.product.id)
        cid = str(self.csv_customer.id)
        csv_content = (
            "customer_id,customer_name,customer_email,product_id,quantity,price\n"
            f"{cid},CSV Customer,csv@example.com,{pid},2,10.0\n"
        )

        response = await self.auth_client.post(
            "/upload",
            files={
                "file": (
                    "orders.csv",
                    io.BytesIO(csv_content.encode()),
                    "text/csv",
                )
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    async def test_upload_csv_no_auth_401(self) -> None:
        """CSV upload without auth must return 401."""
        import io

        pid = str(self.product.id)
        csv_content = (
            "customer_id,customer_name,customer_email,product_id,quantity,price\n"
            f"some-id,Test,test@example.com,{pid},1,10.0\n"
        )

        response = await self.auth_client.post(
            "/upload",
            files={
                "file": (
                    "orders.csv",
                    io.BytesIO(csv_content.encode()),
                    "text/csv",
                )
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestUploadEndpointEdgeCases:
    """Edge case tests for /upload."""

    @pytest.fixture(autouse=True)
    async def _setup(self, test_db_session, test_user):
        _, self.product = await _create_test_data(test_db_session)
        self.auth_client, self.token, self._app = await _create_auth_client(
            test_db_session, test_user
        )
        yield
        await self.auth_client.aclose()
        self._app.dependency_overrides.clear()

    async def test_upload_empty_orders_list_422(self) -> None:
        """Empty orders list must return 422."""
        response = await self.auth_client.post(
            "/upload",
            json={"orders": []},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 422

    async def test_upload_multiple_valid_orders(self) -> None:
        """Multiple valid orders must all succeed."""
        cid = uuid4()
        pid = str(self.product.id)
        response = await self.auth_client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(cid),
                        "items": [
                            {"product_id": pid, "quantity": 1, "price": 10.0}
                        ],
                    },
                    {
                        "customer_id": str(cid),
                        "items": [
                            {"product_id": pid, "quantity": 2, "price": 20.0}
                        ],
                    },
                ]
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["successful"] == 2
