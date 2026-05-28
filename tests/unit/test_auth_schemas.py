"""Tests for User domain entity and auth schemas (T06 verification).

Validates User entity (pure Python, no framework imports), Pydantic
auth schemas, and RFC 7807 ProblemDetailSchema.
"""

from __future__ import annotations

from datetime import UTC
from uuid import UUID


class TestUserEntity:
    """User domain entity must be a pure Python dataclass."""

    def test_user_entity_imports(self) -> None:
        """User entity must be importable from app.core.entities.user."""
        from app.core.entities.user import User

        assert User is not None

    def test_user_entity_has_required_fields(self) -> None:
        """User must have id, username, hashed_password, is_active, created_at."""
        from app.core.entities.user import User

        user = User(username="test", hashed_password="hash")
        assert isinstance(user.id, UUID)
        assert user.username == "test"
        assert user.hashed_password == "hash"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_entity_has_no_framework_imports(self) -> None:
        """User entity module must have zero external dependencies."""
        import ast
        from pathlib import Path

        entity_path = (
            Path(__file__).resolve().parents[2]
            / "app"
            / "core"
            / "entities"
            / "user.py"
        )
        source = entity_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden = {"sqlalchemy", "fastapi", "http"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden, (
                        f"Forbidden import: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden, (
                    f"Forbidden import: {node.module}"
                )


class TestTokenSchema:
    """TokenSchema must validate JWT response structure."""

    def test_token_schema_structure(self) -> None:
        """TokenSchema must have access_token and token_type fields."""
        from app.schemas.user import TokenSchema

        token = TokenSchema(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_token_schema_default_type(self) -> None:
        """TokenSchema token_type must default to 'bearer'."""
        from app.schemas.user import TokenSchema

        token = TokenSchema(access_token="abc123")
        assert token.token_type == "bearer"


class TestUserCreateSchema:
    """UserCreateSchema must validate authentication input."""

    def test_user_create_valid(self) -> None:
        """Valid username and password must pass validation."""
        from app.schemas.user import UserCreateSchema

        schema = UserCreateSchema(username="testuser", password="Secure123")
        assert schema.username == "testuser"
        assert schema.password == "Secure123"

    def test_user_create_password_no_uppercase(self) -> None:
        """Password without uppercase letter must fail validation."""
        from pydantic import ValidationError

        from app.schemas.user import UserCreateSchema

        try:
            UserCreateSchema(username="testuser", password="secure123")
        except ValidationError as e:
            assert any("uppercase" in str(err["msg"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_user_create_password_no_lowercase(self) -> None:
        """Password without lowercase letter must fail validation."""
        from pydantic import ValidationError

        from app.schemas.user import UserCreateSchema

        try:
            UserCreateSchema(username="testuser", password="SECURE123")
        except ValidationError as e:
            assert any("lowercase" in str(err["msg"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_user_create_password_no_digit(self) -> None:
        """Password without digit must fail validation."""
        from pydantic import ValidationError

        from app.schemas.user import UserCreateSchema

        try:
            UserCreateSchema(username="testuser", password="SecurePass")
        except ValidationError as e:
            assert any("digit" in str(err["msg"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_user_create_username_too_short(self) -> None:
        """Username shorter than 3 chars must fail validation."""
        from pydantic import ValidationError

        from app.schemas.user import UserCreateSchema

        try:
            UserCreateSchema(username="ab", password="secure123")
        except ValidationError as e:
            assert any("username" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_user_create_password_too_short(self) -> None:
        """Password shorter than 8 chars must fail validation."""
        from pydantic import ValidationError

        from app.schemas.user import UserCreateSchema

        try:
            UserCreateSchema(username="testuser", password="Sh0rt")
        except ValidationError as e:
            assert any("password" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestUserResponseSchema:
    """UserResponseSchema must support ORM mode."""

    def test_user_response_has_required_fields(self) -> None:
        """UserResponseSchema must include id, username, is_active, created_at."""
        from datetime import datetime
        from uuid import uuid4

        from app.schemas.user import UserResponseSchema

        uid = uuid4()
        now = datetime.now(UTC)
        schema = UserResponseSchema(
            id=uid, username="test", is_active=True, created_at=now
        )
        assert schema.id == uid
        assert schema.username == "test"
        assert schema.is_active is True
        assert schema.created_at == now

    def test_user_response_from_attributes_config(self) -> None:
        """UserResponseSchema must have from_attributes=True config."""
        from app.schemas.user import UserResponseSchema

        assert UserResponseSchema.model_config.get("from_attributes") is True


class TestProblemDetailSchema:
    """ProblemDetailSchema must follow RFC 7807."""

    def test_problem_detail_structure(self) -> None:
        """ProblemDetailSchema must have type, title, status, detail, instance."""
        from app.schemas.error import ProblemDetailSchema

        error = ProblemDetailSchema(
            title="Not Found",
            status=404,
            detail="User not found",
        )
        assert error.type == "about:blank"
        assert error.title == "Not Found"
        assert error.status == 404
        assert error.detail == "User not found"

    def test_problem_detail_defaults(self) -> None:
        """ProblemDetailSchema must have sensible defaults."""
        from app.schemas.error import ProblemDetailSchema

        error = ProblemDetailSchema(title="Error", status=400)
        assert error.detail is None
        assert error.instance is None
