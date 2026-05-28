"""Tests for ProductModel SQLAlchemy model (T09 verification).

Validates that ProductModel exists, has correct table name, columns,
and inherits from Base.
"""

from __future__ import annotations


class TestProductModelStructure:
    """ProductModel must exist with correct table name and columns."""

    def test_product_model_imports(self) -> None:
        """ProductModel must be importable from models package."""
        from app.infrastructure.database.models.product import ProductModel

        assert ProductModel is not None

    def test_product_model_tablename(self) -> None:
        """ProductModel must map to 'products' table."""
        from app.infrastructure.database.models.product import ProductModel

        assert ProductModel.__tablename__ == "products"

    def test_product_model_inherits_from_base(self) -> None:
        """ProductModel must inherit from Base."""
        from app.infrastructure.database.base import Base
        from app.infrastructure.database.models.product import ProductModel

        assert issubclass(ProductModel, Base)

    def test_product_model_has_required_columns(self) -> None:
        """ProductModel must have all required columns."""
        from app.infrastructure.database.models.product import ProductModel

        columns = {c.name for c in ProductModel.__table__.columns}
        required = {"id", "name", "price", "stock", "created_at", "updated_at"}
        assert required.issubset(columns), f"Missing columns: {required - columns}"

    def test_product_model_repr(self) -> None:
        """ProductModel __repr__ must include id and name."""
        import uuid

        from app.infrastructure.database.models.product import ProductModel

        model = ProductModel(id=uuid.uuid4(), name="Test", price=1.0, stock=1)
        rep = repr(model)
        assert "ProductModel" in rep
        assert "Test" in rep
