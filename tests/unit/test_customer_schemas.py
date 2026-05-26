"""Tests for Customer Pydantic schemas (T10 verification).

Validates CustomerCreateSchema validation rules and CustomerResponseSchema
output structure.
"""

from __future__ import annotations


class TestCustomerCreateSchema:
    """CustomerCreateSchema must validate customer creation input."""

    def test_customer_create_valid(self) -> None:
        """Valid name and email must pass validation."""
        from app.schemas.customer import CustomerCreateSchema

        schema = CustomerCreateSchema(
            name="John Doe", email="john@example.com"
        )
        assert schema.name == "John Doe"
        assert schema.email == "john@example.com"

    def test_customer_create_name_whitespace_stripping(self) -> None:
        """Customer name must strip leading/trailing whitespace."""
        from app.schemas.customer import CustomerCreateSchema

        schema = CustomerCreateSchema(
            name="  John Doe  ", email="john@example.com"
        )
        assert schema.name == "John Doe"

    def test_customer_create_name_too_short(self) -> None:
        """Empty name must fail validation."""
        from pydantic import ValidationError

        from app.schemas.customer import CustomerCreateSchema

        try:
            CustomerCreateSchema(name="", email="john@example.com")
        except ValidationError as e:
            assert any("name" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_customer_create_name_too_long(self) -> None:
        """Name > 100 chars must fail validation."""
        from pydantic import ValidationError

        from app.schemas.customer import CustomerCreateSchema

        try:
            CustomerCreateSchema(
                name="A" * 101, email="john@example.com"
            )
        except ValidationError as e:
            assert any("name" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_customer_create_max_name_length(self) -> None:
        """Name exactly at 100 chars must pass validation."""
        from app.schemas.customer import CustomerCreateSchema

        name = "A" * 100
        schema = CustomerCreateSchema(
            name=name, email="john@example.com"
        )
        assert schema.name == name

    def test_customer_create_invalid_email(self) -> None:
        """Invalid email must fail validation."""
        from pydantic import ValidationError

        from app.schemas.customer import CustomerCreateSchema

        try:
            CustomerCreateSchema(name="John", email="invalid-email")
        except ValidationError as e:
            assert any("email" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_customer_create_empty_email(self) -> None:
        """Empty email must fail validation."""
        from pydantic import ValidationError

        from app.schemas.customer import CustomerCreateSchema

        try:
            CustomerCreateSchema(name="John", email="")
        except ValidationError as e:
            assert any("email" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestCustomerResponseSchema:
    """CustomerResponseSchema must support ORM mode and all fields."""

    def test_customer_response_has_required_fields(self) -> None:
        """CustomerResponseSchema must include id, name, email."""
        from uuid import uuid4

        from app.schemas.customer import CustomerResponseSchema

        uid = uuid4()
        schema = CustomerResponseSchema(
            id=uid, name="John Doe", email="john@example.com"
        )
        assert schema.id == uid
        assert schema.name == "John Doe"
        assert schema.email == "john@example.com"

    def test_customer_response_from_attributes_config(self) -> None:
        """CustomerResponseSchema must have from_attributes=True config."""
        from app.schemas.customer import CustomerResponseSchema

        assert (
            CustomerResponseSchema.model_config.get("from_attributes") is True
        )
