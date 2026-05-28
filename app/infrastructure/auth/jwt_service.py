"""JWT token creation and verification service.

Handles JWT encoding/decoding using HS256 algorithm with configurable
expiration. Tokens include 'sub' (username), 'aud' (audience), and
'iss' (issuer) claims for proper validation and scope restriction.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from app.config import settings
from app.schemas.user import TokenDataSchema

# JWT audience and issuer — used for token scope validation
JWT_AUDIENCE = settings.APP_NAME
JWT_ISSUER = settings.APP_NAME


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
            "aud": JWT_AUDIENCE,
            "iss": JWT_ISSUER,
            "jti": str(uuid4()),
            "iat": now,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> TokenDataSchema | None:
        """Verify and decode a JWT access token.

        Validates the token signature, expiration, audience, and issuer.

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
                audience=JWT_AUDIENCE,
                issuer=JWT_ISSUER,
            )
            username: str | None = payload.get("sub")
            if username is None:
                return None
            return TokenDataSchema(username=username)
        except JWTError:
            return None
