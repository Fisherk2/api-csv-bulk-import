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


async def _make_client() -> httpx.AsyncClient:
    """Create an httpx client, skipping if Docker stack is not running."""
    client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)

    # Wait for the API to be ready
    reachable = False
    for _ in range(30):
        try:
            resp = await client.get("/")
            if resp.status_code == 200:
                reachable = True
                break
        except httpx.ConnectError:
            pass
        await asyncio.sleep(1)

    if not reachable:
        await client.aclose()
        pytest.skip("Docker stack not running — start with: docker-compose up -d")

    return client


async def test_smoke_docker_app_boots():
    """Docker Compose stack must boot and respond to health check."""
    client = await _make_client()
    try:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
    finally:
        await client.aclose()


async def test_smoke_docker_upload_requires_auth():
    """Upload endpoint must require authentication (return 401 without token)."""
    client = await _make_client()
    try:
        upload_payload = {
            "orders": [
                {
                    "customer_id": str(uuid4()),
                    "items": [
                        {"product_id": str(uuid4()), "quantity": 1, "price": 10.0}
                    ],
                }
            ]
        }
        resp = await client.post("/upload", json=upload_payload)
        assert resp.status_code == 401
    finally:
        await client.aclose()


async def test_smoke_docker_export_requires_auth():
    """Export endpoint must require authentication (return 401 without token)."""
    client = await _make_client()
    try:
        resp = await client.get("/export")
        assert resp.status_code == 401
    finally:
        await client.aclose()


async def test_smoke_docker_upload_validates_batch():
    """Upload with valid structure but non-existent IDs returns 422 (not 500)."""
    client = await _make_client()
    try:
        # Register a test user to get a token
        test_email = f"smoke-{uuid4().hex[:8]}@test.com"
        test_password = "test123456"

        login_resp = await client.post(
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
                    "items": [
                        {"product_id": str(uuid4()), "quantity": 1, "price": 10.0}
                    ],
                }
            ]
        }
        upload_resp = await client.post(
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
    finally:
        await client.aclose()


async def test_smoke_docker_export_returns_json():
    """Export returns valid JSON array (even if empty)."""
    client = await _make_client()
    try:
        test_email = f"smoke-{uuid4().hex[:8]}@test.com"
        test_password = "test123456"

        login_resp = await client.post(
            "/token",
            data={"username": test_email, "password": test_password},
        )
        if login_resp.status_code != 200:
            pytest.skip("Cannot authenticate — no test user in DB")

        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        export_resp = await client.get("/export?format=json", headers=headers)
        assert export_resp.status_code == 200
        export_data = export_resp.json()
        assert isinstance(export_data, list)
    finally:
        await client.aclose()
