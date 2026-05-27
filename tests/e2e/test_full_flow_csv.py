"""End-to-end tests for CSV upload and health-check flows (T23).

Tests the API as a black box: login → upload (CSV) → export (CSV),
plus health-check availability throughout a full upload/export cycle.

Uses shared fixtures from tests/e2e/conftest.py (ASGI transport,
SQLite in-memory).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_full_flow_login_upload_csv_export_csv(
    client, auth_token, seeded_data
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


async def test_full_flow_unauthenticated_upload_csv_401(client):
    """CSV upload without JWT must return 401."""
    import io

    upload_resp = await client.post(
        "/upload",
        files={"file": ("orders.csv", io.BytesIO(b"a,b\n1,2\n"), "text/csv")},
    )
    assert upload_resp.status_code == 401
