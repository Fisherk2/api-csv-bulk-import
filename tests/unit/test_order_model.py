"""Tests for Order and OrderItem SQLAlchemy models (T13 verification).

Validates that OrderModel and OrderItemModel have correct table names,
columns, FK relationships, and inherit from Base.
"""

from __future__ import annotations


class TestOrderModelStructure:
    """OrderModel must exist with correct table name and columns."""

    def test_order_model_imports(self) -> None:
        """OrderModel must be importable."""
        from app.infrastructure.database.models.order import OrderModel

        assert OrderModel is not None

    def test_order_model_tablename(self) -> None:
        """OrderModel must map to 'orders' table."""
        from app.infrastructure.database.models.order import OrderModel

        assert OrderModel.__tablename__ == "orders"

    def test_order_model_inherits_from_base(self) -> None:
        """OrderModel must inherit from Base."""
        from app.infrastructure.database.base import Base
        from app.infrastructure.database.models.order import OrderModel

        assert issubclass(OrderModel, Base)

    def test_order_model_has_required_columns(self) -> None:
        """OrderModel must have required columns."""
        from app.infrastructure.database.models.order import OrderModel

        columns = {c.name for c in OrderModel.__table__.columns}
        required = {"id", "customer_id", "status", "created_at", "updated_at"}
        assert required.issubset(columns), f"Missing: {required - columns}"

    def test_order_model_customer_id_fk(self) -> None:
        """OrderModel.customer_id must be a ForeignKey."""
        from app.infrastructure.database.models.order import OrderModel

        col = OrderModel.__table__.columns["customer_id"]
        assert col.foreign_keys, "customer_id must have FK constraint"

    def test_order_model_items_relationship(self) -> None:
        """OrderModel must have items relationship."""
        from app.infrastructure.database.models.order import OrderModel

        assert hasattr(OrderModel, "items"), "OrderModel must have items relationship"


class TestOrderItemModelStructure:
    """OrderItemModel must exist with correct columns and FK relationships."""

    def test_orderitem_model_imports(self) -> None:
        """OrderItemModel must be importable."""
        from app.infrastructure.database.models.order import OrderItemModel

        assert OrderItemModel is not None

    def test_orderitem_model_tablename(self) -> None:
        """OrderItemModel must map to 'order_items' table."""
        from app.infrastructure.database.models.order import OrderItemModel

        assert OrderItemModel.__tablename__ == "order_items"

    def test_orderitem_model_inherits_from_base(self) -> None:
        """OrderItemModel must inherit from Base."""
        from app.infrastructure.database.base import Base
        from app.infrastructure.database.models.order import OrderItemModel

        assert issubclass(OrderItemModel, Base)

    def test_orderitem_model_has_required_columns(self) -> None:
        """OrderItemModel must have required columns."""
        from app.infrastructure.database.models.order import OrderItemModel

        columns = {c.name for c in OrderItemModel.__table__.columns}
        required = {"id", "order_id", "product_id", "quantity", "price", "created_at"}
        assert required.issubset(columns), f"Missing: {required - columns}"

    def test_orderitem_model_fks(self) -> None:
        """OrderItemModel must have FK to orders and products."""
        from app.infrastructure.database.models.order import OrderItemModel

        order_col = OrderItemModel.__table__.columns["order_id"]
        product_col = OrderItemModel.__table__.columns["product_id"]
        assert order_col.foreign_keys, "order_id must have FK"
        assert product_col.foreign_keys, "product_id must have FK"

    def test_orderitem_model_order_relationship(self) -> None:
        """OrderItemModel must have order relationship."""
        from app.infrastructure.database.models.order import OrderItemModel

        assert hasattr(OrderItemModel, "order"), "OrderItemModel must have order relationship"
