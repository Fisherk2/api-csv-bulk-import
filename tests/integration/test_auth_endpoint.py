"""Integration tests for POST /token and GET / endpoints (T07 verification)."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
class TestTokenEndpoint:
    """POST /token must authenticate users and return JWT tokens."""

    async def test_login_valid_credentials(self, client, test_user):
        """Valid credentials must return 200 with access_token."""
        response = await client.post(
            "/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_password(self, client, test_user):
        """Wrong password must return 401."""
        response = await client.post(
            "/token",
            data={
                "username": test_user["username"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        """Nonexistent username must return 401."""
        response = await client.post(
            "/token",
            data={"username": "noone", "password": "test123"},
        )
        assert response.status_code == 401

    async def test_login_missing_fields(self, client):
        """Missing required fields must return 422."""
        response = await client.post(
            "/token",
            data={"username": "test"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestHealthEndpoint:
    """GET / must return health check."""

    async def test_health_check(self, client):
        """GET / must return 200 with status and version."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
