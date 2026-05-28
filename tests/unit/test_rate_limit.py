"""Unit tests for rate limiting integration.

Tests verify:
1. Rate limit headers (X-RateLimit-*) are present on responses
2. 429 status with error message after exceeding the limit
3. Rate limiting does not interfere with normal API operation
"""

# mypy: disable-error-code="no-untyped-def"

from __future__ import annotations

import pytest


class TestRateLimitHeaders:
    """Rate limit headers should be present on /token responses."""

    async def test_rate_limit_headers_present_on_token(
        self, client, test_user
    ) -> None:
        """X-RateLimit-* headers must appear on /token responses."""
        resp = await client.post(
            "/token",
            data={"username": test_user["username"], "password": test_user["password"]},
        )
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
        )
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers
        assert "X-RateLimit-Reset" in resp.headers

    async def test_rate_limit_headers_expected_values(self, client, test_user) -> None:
        """Rate limit headers should contain sensible numeric values."""
        resp = await client.post(
            "/token",
            data={"username": test_user["username"], "password": test_user["password"]},
        )
        assert resp.status_code == 200
        limit = int(resp.headers["X-RateLimit-Limit"])
        remaining = int(resp.headers["X-RateLimit-Remaining"])
        # With TOKEN_RATE_LIMIT=100000 in tests, the limit should be high
        assert limit > 0
        assert 0 <= remaining <= limit


class TestRateLimitExceeded:
    """Exceeding the rate limit should return 429."""

    async def _trigger_rate_limit(
        self, client, test_user, monkeypatch, low_limit: int = 5
    ):
        """Lower the rate limit and make requests until a 429 is returned.

        Returns the first 429 response. Fails the test if the rate limit
        is not triggered after ``low_limit + 1`` requests.
        """
        import app.config as cfg

        monkeypatch.setattr(cfg.settings, "TOKEN_RATE_LIMIT", low_limit)

        for _ in range(low_limit + 1):
            resp = await client.post(
                "/token",
                data={
                    "username": test_user["username"],
                    "password": test_user["password"],
                },
            )
            if resp.status_code == 429:
                return resp
        pytest.fail("Rate limit was not triggered after %d requests", low_limit + 1)

    async def test_rate_limit_exceeded_returns_429(self, client, test_user, monkeypatch) -> None:
        """Rapid requests to /token must eventually return 429."""
        resp = await self._trigger_rate_limit(client, test_user, monkeypatch)
        assert resp.status_code == 429

    async def test_rate_limit_exceeded_response_format(self, client, test_user, monkeypatch) -> None:
        """429 responses must follow RFC 7807 Problem Details format."""
        resp = await self._trigger_rate_limit(client, test_user, monkeypatch)
        assert resp.status_code == 429
        data = resp.json()
        assert data["title"] == "Rate Limit Exceeded"
        assert data["status"] == 429
        assert "Rate limit exceeded" in data["detail"]


class TestRateLimitDoesNotInterfere:
    """Normal API operation should not be affected by rate limiting."""

    async def test_health_check_still_works(self, client) -> None:
        """GET / should work normally (not rate limited)."""
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def _trigger_upload_rate_limit(
        self, client, test_user, monkeypatch, low_limit: int = 5
    ):
        """Lower the upload rate limit and make requests until a 429 is returned.

        Returns the first 429 response. Fails the test if the rate limit
        is not triggered after ``low_limit + 1`` requests.
        """
        import uuid

        import app.config as cfg

        monkeypatch.setattr(cfg.settings, "UPLOAD_RATE_LIMIT", low_limit)

        login_resp = await client.post(
            "/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        for _ in range(low_limit + 1):
            resp = await client.post(
                "/upload",
                json={
                    "orders": [
                        {
                            "customer_id": str(uuid.uuid4()),
                            "items": [
                                {
                                    "product_id": str(uuid.uuid4()),
                                    "quantity": 1,
                                    "price": 10.0,
                                }
                            ],
                        }
                    ]
                },
                headers=headers,
            )
            if resp.status_code == 429:
                return resp
        pytest.fail("Upload rate limit was not triggered after %d requests", low_limit + 1)

    async def test_upload_rate_limit_exceeded_returns_429(
        self, client, test_user, monkeypatch
    ) -> None:
        """Rapid authenticated requests to /upload must eventually return 429."""
        resp = await self._trigger_upload_rate_limit(client, test_user, monkeypatch)
        assert resp.status_code == 429
        data = resp.json()
        assert data["title"] == "Rate Limit Exceeded"
        assert data["status"] == 429

    async def test_upload_still_works_with_auth(self, client, test_user) -> None:
        """Authenticated upload should work normally."""
        # Login
        login_resp = await client.post(
            "/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        assert login_resp.status_code == 200, (
            f"Login failed: {login_resp.status_code} {login_resp.text[:200]}"
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload — use a valid minimal payload (invalid IDs → 422, not crash)
        import uuid

        resp = await client.post(
            "/upload",
            json={
                "orders": [
                    {
                        "customer_id": str(uuid.uuid4()),
                        "items": [
                            {
                                "product_id": str(uuid.uuid4()),
                                "quantity": 1,
                                "price": 10.0,
                            }
                        ],
                    }
                ]
            },
            headers=headers,
        )
        assert resp.status_code == 422, (
            f"Expected 422 for invalid IDs, got {resp.status_code}: {resp.text[:200]}"
        )
