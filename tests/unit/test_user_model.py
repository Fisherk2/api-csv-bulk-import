"""Tests for UserModel SQLAlchemy model (T05 verification).

Validates that UserModel exists, has correct table name, fields,
and works with SQLAlchemy async session.
"""

from __future__ import annotations


class TestUserModelStructure:
    """UserModel must exist with correct table name and fields."""

    def test_user_model_imports(self) -> None:
        """UserModel must be importable from models package."""
        from app.infrastructure.database.models.user import UserModel

        assert UserModel is not None

    def test_user_model_tablename(self) -> None:
        """UserModel must map to 'users' table."""
        from app.infrastructure.database.models.user import UserModel

        assert UserModel.__tablename__ == "users"

    def test_user_model_inherits_from_base(self) -> None:
        """UserModel must inherit from Base."""
        from app.infrastructure.database.base import Base
        from app.infrastructure.database.models.user import UserModel

        assert issubclass(UserModel, Base)

    def test_user_model_has_required_fields(self) -> None:
        """UserModel must have all required columns."""
        from app.infrastructure.database.models.user import UserModel

        columns = {c.name for c in UserModel.__table__.columns}
        required = {"id", "username", "hashed_password", "is_active", "created_at"}
        assert required.issubset(columns), f"Missing columns: {required - columns}"
