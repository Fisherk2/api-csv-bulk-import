"""Tests for Product Pydantic schemas (T08 verification).

Validates ProductCreateSchema validation rules and ProductResponseSchema
output structure.
"""

from __future__ import annotations


class TestProductCreateSchema:
    """ProductCreateSchema must validate product creation input."""

    def test_product_create_valid(self) -> None:
        """Valid name, price, and stock must pass validation."""
        from app.schemas.product import ProductCreateSchema

        schema = ProductCreateSchema(name="Widget", price=19.99, stock=100)
        assert schema.name == "Widget"
        assert schema.price == 19.99
        assert schema.stock == 100

    def test_product_create_name_whitespace_stripping(self) -> None:
        """Product name must strip leading/trailing whitespace."""
        from app.schemas.product import ProductCreateSchema

        schema = ProductCreateSchema(name="  Widget  ", price=9.99, stock=50)
        assert schema.name == "Widget"

    def test_product_create_name_too_short(self) -> None:
        """Empty name must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(name="", price=10.0, stock=5)
        except ValidationError as e:
            assert any("name" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_product_create_price_not_positive(self) -> None:
        """Price <= 0 must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(name="Widget", price=0, stock=50)
        except ValidationError as e:
            assert any("price" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_product_create_negative_price(self) -> None:
        """Negative price must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(name="Widget", price=-10.0, stock=50)
        except ValidationError as e:
            assert any("price" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_product_create_price_exceeds_max(self) -> None:
        """Price > 1,000,000 must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(name="Widget", price=2_000_000, stock=50)
        except ValidationError as e:
            assert any("price" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_product_create_negative_stock(self) -> None:
        """Negative stock must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(name="Widget", price=10.0, stock=-1)
        except ValidationError as e:
            assert any("stock" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_product_create_max_price_allowed(self) -> None:
        """Price exactly at 1,000,000 must pass validation."""
        from app.schemas.product import ProductCreateSchema

        schema = ProductCreateSchema(name="Expensive", price=1_000_000, stock=1)
        assert schema.price == 1_000_000

    def test_product_create_zero_stock_allowed(self) -> None:
        """Stock of 0 must pass validation."""
        from app.schemas.product import ProductCreateSchema

        schema = ProductCreateSchema(name="OutOfStock", price=5.0, stock=0)
        assert schema.stock == 0

    def test_product_create_max_name_length(self) -> None:
        """Name exactly at 100 chars must pass validation."""
        from app.schemas.product import ProductCreateSchema

        name = "A" * 100
        schema = ProductCreateSchema(name=name, price=1.0, stock=1)
        assert schema.name == name

    def test_product_create_name_too_long(self) -> None:
        """Name > 100 chars must fail validation."""
        from pydantic import ValidationError

        from app.schemas.product import ProductCreateSchema

        try:
            ProductCreateSchema(
                name="A" * 101, price=1.0, stock=1
            )
        except ValidationError as e:
            assert any("name" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestProductResponseSchema:
    """ProductResponseSchema must support ORM mode and all fields."""

    def test_product_response_has_required_fields(self) -> None:
        """ProductResponseSchema must include id, name, price, stock."""
        from uuid import uuid4

        from app.schemas.product import ProductResponseSchema

        uid = uuid4()
        schema = ProductResponseSchema(
            id=uid, name="Widget", price=19.99, stock=100
        )
        assert schema.id == uid
        assert schema.name == "Widget"
        assert schema.price == 19.99
        assert schema.stock == 100

    def test_product_response_from_attributes_config(self) -> None:
        """ProductResponseSchema must have from_attributes=True config."""
        from app.schemas.product import ProductResponseSchema

        assert (
            ProductResponseSchema.model_config.get("from_attributes") is True
        )
