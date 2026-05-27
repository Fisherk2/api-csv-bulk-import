"""Docker smoke tests — verify the app works with real PostgreSQL.

These tests require 'docker-compose up' to be running with the full
stack (API + PostgreSQL). They use real HTTP (httpx against
localhost:8000), not ASGI transport.

Usage:
    docker-compose up -d
    sleep 5  # Wait for services to become healthy
    pytest tests/e2e/test_smoke_docker.py -v -m docker

Skip in CI unless Docker is available:
    pytest -m "not docker"
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
import pytest

pytestmark = pytest.mark.docker

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def event_loop():
    """Create a module-scoped event loop for the Docker client."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def docker_client():
    """Create an httpx client targeting the Docker Compose stack."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Wait for the API to be ready
        for _ in range(30):
            try:
                resp = await client.get("/")
                if resp.status_code == 200:
                    break
            except httpx.ConnectError:
                pass
            await asyncio.sleep(1)
        yield client


async def test_smoke_docker_app_boots(docker_client):
    """Docker Compose stack must boot and respond to health check."""
    response = await docker_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


async def test_smoke_docker_full_flow(docker_client):
    """Full flow must work with real PostgreSQL (no 500 errors)."""
    # Login
    login_resp = await docker_client.post(
        "/token",
        data={"username": "testuser", "password": "test123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload with non-existent IDs → must return structured error (422), not 500

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
    assert upload_resp.status_code == 422, (
        f"Upload with invalid data must return 422, got {upload_resp.status_code}: "
        f"{upload_resp.text[:200]}"
    )
    upload_data = upload_resp.json()
    assert "total" in upload_data
    assert "successful" in upload_data
    assert "failed" in upload_data
    assert upload_data["failed"] >= 1

    # Export — must return valid JSON array (even if empty)
    export_resp = await docker_client.get(
        "/export?format=json", headers=headers
    )
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert isinstance(export_data, list)
