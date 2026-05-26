"""Tests for CustomerModel SQLAlchemy model (T11 verification).

Validates that CustomerModel exists, has correct table name, columns
(including unique email), and inherits from Base.
"""

from __future__ import annotations


class TestCustomerModelStructure:
    """CustomerModel must exist with correct table name and columns."""

    def test_customer_model_imports(self) -> None:
        """CustomerModel must be importable from models package."""
        from app.infrastructure.database.models.customer import CustomerModel

        assert CustomerModel is not None

    def test_customer_model_tablename(self) -> None:
        """CustomerModel must map to 'customers' table."""
        from app.infrastructure.database.models.customer import CustomerModel

        assert CustomerModel.__tablename__ == "customers"

    def test_customer_model_inherits_from_base(self) -> None:
        """CustomerModel must inherit from Base."""
        from app.infrastructure.database.base import Base
        from app.infrastructure.database.models.customer import CustomerModel

        assert issubclass(CustomerModel, Base)

    def test_customer_model_has_required_columns(self) -> None:
        """CustomerModel must have all required columns."""
        from app.infrastructure.database.models.customer import CustomerModel

        columns = {c.name for c in CustomerModel.__table__.columns}
        required = {"id", "name", "email", "created_at", "updated_at"}
        assert required.issubset(columns), (
            f"Missing columns: {required - columns}"
        )

    def test_customer_model_email_unique(self) -> None:
        """CustomerModel.email must have a unique constraint."""
        from app.infrastructure.database.models.customer import CustomerModel

        email_col = CustomerModel.__table__.columns["email"]
        assert email_col.unique, "email must have unique constraint"

    def test_customer_model_email_indexed(self) -> None:
        """CustomerModel.email must be indexed."""
        from app.infrastructure.database.models.customer import CustomerModel

        email_col = CustomerModel.__table__.columns["email"]
        assert email_col.index, "email must be indexed"

    def test_customer_model_name_indexed(self) -> None:
        """CustomerModel.name must be indexed."""
        from app.infrastructure.database.models.customer import CustomerModel

        name_col = CustomerModel.__table__.columns["name"]
        assert name_col.index, "name must be indexed"

    def test_customer_model_repr(self) -> None:
        """CustomerModel __repr__ must include id and email."""
        import uuid

        from app.infrastructure.database.models.customer import CustomerModel

        model = CustomerModel(
            id=uuid.uuid4(), name="John Doe", email="john@example.com"
        )
        rep = repr(model)
        assert "CustomerModel" in rep
        assert "john@example.com" in rep
