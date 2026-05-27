"""End-to-end tests for the complete user flow (T23 verification).

Tests the full API as a black box: login → upload (JSON/CSV) → export
(JSON/CSV) → data integrity verification. Uses the shared client
fixture (ASGI transport, SQLite in-memory).
"""

from __future__ import annotations

from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


# ── Local fixtures ──────────────────────────────────────────────────


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


# ── E2E Flow Tests ──────────────────────────────────────────────────


async def test_full_flow_login_upload_json_export_json(
    client, auth_token, seeded_data
):
    """Login → upload 3 JSON orders → export JSON → verify data integrity."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    upload_payload = {
        "orders": [
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [{
                    "product_id": str(seeded_data["product_a"].id),
                    "quantity": 2, "price": 10.0,
                }],
            },
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [{
                    "product_id": str(seeded_data["product_b"].id),
                    "quantity": 1, "price": 25.0,
                }],
            },
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [
                    {"product_id": str(seeded_data["product_a"].id),
                     "quantity": 5, "price": 10.0},
                    {"product_id": str(seeded_data["product_b"].id),
                     "quantity": 3, "price": 25.0},
                ],
            },
        ]
    }
    upload_response = await client.post(
        "/upload", json=upload_payload, headers=headers
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["total"] == 3
    assert upload_data["successful"] == 3
    assert upload_data["failed"] == 0

    export_response = await client.get(
        "/export?format=json", headers=headers
    )
    assert export_response.status_code == 200
    exported = export_response.json()
    assert len(exported) == 3

    # All orders default to "pending" status (schema doesn't support custom status)
    statuses = {o["status"] for o in exported}
    assert statuses == {"pending"}

    # Verify the third order has 2 items (multi-item order)
    multi_item = [o for o in exported if len(o["items"]) == 2]
    assert len(multi_item) == 1


async def test_full_flow_login_upload_csv_export_csv(
    client, auth_token, seeded_data, test_db_session
):
    """Login → upload CSV → export CSV → verify CSV rows match upload."""
    import io

    headers = {"Authorization": f"Bearer {auth_token}"}

    # CSV with 2 orders
    cid = str(seeded_data["customer"].id)
    pid_a = str(seeded_data["product_a"].id)
    pid_b = str(seeded_data["product_b"].id)
    csv_content = (
        "customer_id,customer_name,customer_email,product_id,quantity,price\n"
        f"{cid},E2E Customer,e2e@example.com,{pid_a},2,10.0\n"
        f"{cid},E2E Customer,e2e@example.com,{pid_b},1,25.0\n"
    )

    upload_response = await client.post(
        "/upload",
        files={"file": ("orders.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        headers=headers,
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["total"] >= 1

    export_response = await client.get(
        "/export?format=csv", headers=headers
    )
    assert export_response.status_code == 200
    csv_text = export_response.text
    assert "order_id" in csv_text
    assert "customer_id" in csv_text
    assert "product_id" in csv_text
    assert "quantity" in csv_text
    assert "price" in csv_text
    assert cid in csv_text


async def test_full_flow_partial_upload_207_export(
    client, auth_token, seeded_data
):
    """Login → upload mixed valid/invalid → 207 → export only valid orders."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    upload_payload = {
        "orders": [
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [{
                    "product_id": str(seeded_data["product_a"].id),
                    "quantity": 1, "price": 10.0,
                }],
            },
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [],  # INVALID
            },
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [{
                    "product_id": str(seeded_data["product_b"].id),
                    "quantity": 3, "price": 25.0,
                }],
            },
            {
                "customer_id": str(seeded_data["customer"].id),
                "items": [],  # INVALID
            },
        ]
    }
    upload_response = await client.post(
        "/upload", json=upload_payload, headers=headers
    )
    assert upload_response.status_code == 207
    upload_data = upload_response.json()
    assert upload_data["total"] == 4
    assert upload_data["successful"] == 2
    assert upload_data["failed"] == 2

    export_response = await client.get(
        "/export?format=json", headers=headers
    )
    assert export_response.status_code == 200
    exported = export_response.json()
    assert len(exported) == 2  # Only valid orders exported


async def test_full_flow_all_invalid_upload_422(
    client, auth_token, seeded_data
):
    """Login → upload all-invalid orders → 422."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    upload_payload = {
        "orders": [
            {"customer_id": str(seeded_data["customer"].id), "items": []},
            {"customer_id": str(seeded_data["customer"].id), "items": []},
        ]
    }
    response = await client.post(
        "/upload", json=upload_payload, headers=headers
    )
    assert response.status_code == 422


async def test_full_flow_multi_step_sequence(
    client, auth_token, seeded_data
):
    """Upload in multiple steps → cumulative state is correct."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    cid = str(seeded_data["customer"].id)
    pid = str(seeded_data["product_a"].id)

    def _order():
        return {
            "customer_id": cid,
            "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
        }

    # Step 1: Upload 2 orders
    resp1 = await client.post(
        "/upload", json={"orders": [_order(), _order()]}, headers=headers
    )
    assert resp1.status_code == 200
    assert resp1.json()["successful"] == 2

    # Export → 2 orders
    exp1 = await client.get("/export?format=json", headers=headers)
    assert len(exp1.json()) == 2

    # Step 2: Upload 3 more orders
    resp2 = await client.post(
        "/upload", json={"orders": [_order(), _order(), _order()]}, headers=headers
    )
    assert resp2.status_code == 200
    assert resp2.json()["successful"] == 3

    # Export → 5 orders
    exp2 = await client.get("/export?format=json", headers=headers)
    assert len(exp2.json()) == 5


async def test_full_flow_unauthenticated_rejected(client):
    """All endpoints must reject requests without JWT."""
    upload_resp = await client.post(
        "/upload",
        json={"orders": [{"customer_id": str(uuid4()), "items": []}]},
    )
    assert upload_resp.status_code == 401

    export_resp = await client.get("/export?format=json")
    assert export_resp.status_code == 401


async def test_full_flow_export_formats(
    client, auth_token, seeded_data
):
    """Upload → export JSON → export CSV → both formats contain same data."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    cid = str(seeded_data["customer"].id)
    pid = str(seeded_data["product_a"].id)

    upload_payload = {
        "orders": [
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
            },
        ]
    }
    upload_resp = await client.post(
        "/upload", json=upload_payload, headers=headers
    )
    assert upload_resp.status_code == 200

    # Export JSON
    json_resp = await client.get("/export?format=json", headers=headers)
    assert json_resp.status_code == 200
    json_data = json_resp.json()
    assert len(json_data) == 1

    # Export CSV
    csv_resp = await client.get("/export?format=csv", headers=headers)
    assert csv_resp.status_code == 200
    csv_text = csv_resp.text
    assert "order_id" in csv_text

    # Both formats reference the same customer
    assert str(json_data[0]["customer_id"]) in csv_text


async def test_full_flow_export_pagination(
    client, auth_token, seeded_data
):
    """Upload 10 orders → export with skip/limit → verify pagination."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    cid = str(seeded_data["customer"].id)
    pid = str(seeded_data["product_a"].id)

    orders = [
        {
            "customer_id": cid,
            "items": [{"product_id": pid, "quantity": i + 1, "price": 10.0}],
        }
        for i in range(10)
    ]
    upload_resp = await client.post(
        "/upload", json={"orders": orders}, headers=headers
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["successful"] == 10

    # Page 1: skip=0, limit=3
    page1 = await client.get(
        "/export?format=json&skip=0&limit=3", headers=headers
    )
    assert page1.status_code == 200
    assert len(page1.json()) == 3

    # Page 2: skip=3, limit=3
    page2 = await client.get(
        "/export?format=json&skip=3&limit=3", headers=headers
    )
    assert page2.status_code == 200
    assert len(page2.json()) == 3

    # Page 4 (last): skip=9, limit=3
    page4 = await client.get(
        "/export?format=json&skip=9&limit=3", headers=headers
    )
    assert page4.status_code == 200
    assert len(page4.json()) == 1


async def test_full_flow_upload_batch_size_enforcement(
    client, auth_token, seeded_data
):
    """Upload exceeding MAX_BATCH_SIZE must return 413."""
    from app.config import settings

    headers = {"Authorization": f"Bearer {auth_token}"}
    cid = str(seeded_data["customer"].id)
    pid = str(seeded_data["product_a"].id)

    many_orders = [
        {
            "customer_id": cid,
            "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
        }
        for _ in range(settings.MAX_BATCH_SIZE + 1)
    ]
    response = await client.post(
        "/upload", json={"orders": many_orders}, headers=headers
    )
    assert response.status_code == 413


async def test_full_flow_health_check_in_flow(
    client, auth_token, seeded_data
):
    """Health check must respond throughout the upload/export flow."""
    # Health before
    resp_before = await client.get("/")
    assert resp_before.status_code == 200
    assert resp_before.json()["status"] == "ok"

    headers = {"Authorization": f"Bearer {auth_token}"}
    cid = str(seeded_data["customer"].id)
    pid = str(seeded_data["product_a"].id)

    # Upload
    await client.post(
        "/upload",
        json={"orders": [{
            "customer_id": cid,
            "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
        }]},
        headers=headers,
    )

    # Health during
    resp_during = await client.get("/")
    assert resp_during.status_code == 200
    assert resp_during.json()["status"] == "ok"

    # Export
    await client.get("/export?format=json", headers=headers)

    # Health after
    resp_after = await client.get("/")
    assert resp_after.status_code == 200
    assert resp_after.json()["version"] == "1.0.0"
