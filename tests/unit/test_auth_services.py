"""Tests for JWT and password services (T07 verification).

Validates JWT token creation/verification and bcrypt password
hashing/verification.
"""

from __future__ import annotations

from datetime import timedelta


class TestJWTService:
    """JWTService must create and verify tokens correctly."""

    def test_create_token_returns_string(self) -> None:
        """create_token must return a JWT string."""
        from app.infrastructure.auth.jwt_service import JWTService

        token = JWTService.create_token(username="testuser")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_returns_token_data(self) -> None:
        """verify_token must decode a valid token returning TokenDataSchema."""
        from app.infrastructure.auth.jwt_service import JWTService

        token = JWTService.create_token(username="testuser")
        result = JWTService.verify_token(token)
        assert result is not None
        assert result.username == "testuser"

    def test_verify_invalid_token_returns_none(self) -> None:
        """verify_token must return None for an invalid token."""
        from app.infrastructure.auth.jwt_service import JWTService

        result = JWTService.verify_token("invalid.token.string")
        assert result is None

    def test_verify_expired_token_returns_none(self) -> None:
        """verify_token must return None for an expired token."""
        from app.infrastructure.auth.jwt_service import JWTService

        token = JWTService.create_token(
            username="testuser",
            expires_delta=timedelta(hours=-1),
        )
        result = JWTService.verify_token(token)
        assert result is None


class TestPasswordService:
    """PasswordService must hash and verify passwords with bcrypt."""

    def test_hash_returns_string(self) -> None:
        """hash_password must return a string."""
        from app.infrastructure.auth.password_service import PasswordService

        hashed = PasswordService.hash_password("test123")
        assert isinstance(hashed, str)
        assert hashed != "test123"

    def test_verify_correct_password(self) -> None:
        """verify_password must return True for correct password."""
        from app.infrastructure.auth.password_service import PasswordService

        hashed = PasswordService.hash_password("test123")
        assert PasswordService.verify_password("test123", hashed) is True

    def test_verify_wrong_password(self) -> None:
        """verify_password must return False for wrong password."""
        from app.infrastructure.auth.password_service import PasswordService

        hashed = PasswordService.hash_password("test123")
        assert PasswordService.verify_password("wrong", hashed) is False
