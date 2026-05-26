"""Password hashing and verification service.

Uses bcrypt for secure password storage.
"""

from __future__ import annotations

import bcrypt


class PasswordService:
    """Stateless service for password operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password to hash.

        Returns:
            Bcrypt hashed password string.
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a bcrypt hash.

        Args:
            plain_password: The password to check.
            hashed_password: The stored bcrypt hash.

        Returns:
            True if the password matches the hash.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
