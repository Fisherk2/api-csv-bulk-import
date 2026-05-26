"""JWT token creation and verification service.

Handles JWT encoding/decoding using HS256 algorithm with configurable
expiration. Tokens include a 'sub' claim with the username.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import settings
from app.schemas.user import TokenDataSchema


class JWTService:
    """Stateless service for JWT token operations."""

    @staticmethod
    def create_token(
        username: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a JWT access token for the given username.

        Args:
            username: The subject (user) to encode in the token.
            expires_delta: Optional custom expiration. Defaults to
                ACCESS_TOKEN_EXPIRE_MINUTES from settings.

        Returns:
            Encoded JWT string.
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        now = datetime.now(UTC)
        expire = now + expires_delta

        payload = {
            "sub": username,
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> TokenDataSchema | None:
        """Verify and decode a JWT access token.

        Args:
            token: The JWT string to verify.

        Returns:
            TokenDataSchema with username if valid, None otherwise.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            username: str | None = payload.get("sub")
            if username is None:
                return None
            return TokenDataSchema(username=username)
        except JWTError:
            return None
