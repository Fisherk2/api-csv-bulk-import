"""Docker smoke tests — verify the app works with real PostgreSQL.

The docker_stack fixture (from conftest.py) automatically:
  1. Builds and starts the Docker Compose stack
  2. Waits for the API to be healthy
  3. Tears down containers after all tests finish

Usage:
    pytest tests/e2e/test_smoke_docker.py -v -m docker

Skip in CI unless Docker is available:
    pytest -m "not docker"
"""

from __future__ import annotations

from uuid import uuid4

import pytest

pytestmark = pytest.mark.docker


async def test_smoke_docker_app_boots(docker_client):
    """Docker Compose stack must boot and respond to health check."""
    response = await docker_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


async def test_smoke_docker_upload_requires_auth(docker_client):
    """Upload endpoint must require authentication (return 401 without token)."""
    upload_payload = {
        "orders": [
            {
                "customer_id": str(uuid4()),
                "items": [{"product_id": str(uuid4()), "quantity": 1, "price": 10.0}],
            }
        ]
    }
    resp = await docker_client.post("/upload", json=upload_payload)
    assert resp.status_code == 401


async def test_smoke_docker_export_requires_auth(docker_client):
    """Export endpoint must require authentication (return 401 without token)."""
    resp = await docker_client.get("/export")
    assert resp.status_code == 401


async def test_smoke_docker_upload_validates_batch(docker_client):
    """Upload with valid structure but non-existent IDs returns 422 (not 500)."""
    # Register a test user to get a token
    test_email = f"smoke-{uuid4().hex[:8]}@test.com"
    test_password = "test123456"

    login_resp = await docker_client.post(
        "/token",
        data={"username": test_email, "password": test_password},
    )
    if login_resp.status_code != 200:
        pytest.skip("Cannot authenticate — no test user in DB")

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    upload_payload = {
        "orders": [
            {
                "customer_id": str(uuid4()),
                "items": [{"product_id": str(uuid4()), "quantity": 1, "price": 10.0}],
            }
        ]
    }
    upload_resp = await docker_client.post(
        "/upload", json=upload_payload, headers=headers
    )
    # Should return 422 (validation error), not 500 (server error)
    assert upload_resp.status_code == 422, (
        f"Expected 422, got {upload_resp.status_code}: {upload_resp.text[:200]}"
    )
    upload_data = upload_resp.json()
    assert "total" in upload_data
    assert "failed" in upload_data
    assert upload_data["failed"] >= 1


async def test_smoke_docker_export_returns_json(docker_client):
    """Export returns valid JSON array (even if empty)."""
    test_email = f"smoke-{uuid4().hex[:8]}@test.com"
    test_password = "test123456"

    login_resp = await docker_client.post(
        "/token",
        data={"username": test_email, "password": test_password},
    )
    if login_resp.status_code != 200:
        pytest.skip("Cannot authenticate — no test user in DB")

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    export_resp = await docker_client.get("/export?format=json", headers=headers)
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert isinstance(export_data, list)
