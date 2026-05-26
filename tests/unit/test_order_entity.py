"""Tests for Order and OrderItem domain entities (T12 verification).

Validates Order and OrderItem entities — pure Python dataclasses,
no framework imports, correct aggregate structure.
"""

from __future__ import annotations


class TestOrderEntity:
    """Order domain entity must be a pure Python dataclass (aggregate root)."""

    def test_order_entity_imports(self) -> None:
        """Order entity must be importable."""
        from app.core.entities.order import Order

        assert Order is not None

    def test_order_entity_is_dataclass(self) -> None:
        """Order must be a @dataclass."""
        from dataclasses import is_dataclass

        from app.core.entities.order import Order

        assert is_dataclass(Order), "Order must be a @dataclass"

    def test_order_entity_has_required_fields(self) -> None:
        """Order must have id, customer_id, status, items, created_at."""
        from datetime import datetime
        from uuid import UUID, uuid4

        from app.core.entities.order import Order, OrderItem

        order = Order(
            customer_id=uuid4(),
            items=[OrderItem(product_id=uuid4(), quantity=2, price=19.99)],
        )
        assert isinstance(order.id, UUID)
        assert isinstance(order.customer_id, UUID)
        assert order.status == "pending"
        assert len(order.items) == 1
        assert isinstance(order.created_at, datetime)

    def test_order_entity_defaults(self) -> None:
        """Order defaults: status='pending', items=[], created_at auto, id auto."""
        from uuid import uuid4

        from app.core.entities.order import Order

        order = Order(customer_id=uuid4())
        assert order.status == "pending"
        assert order.items == []
        assert order.id is not None

    def test_order_entity_no_framework_imports(self) -> None:
        """Order entity module must have zero external dependencies."""
        import ast
        from pathlib import Path

        entity_path = (
            Path(__file__).resolve().parents[2]
            / "app" / "core" / "entities" / "order.py"
        )
        source = entity_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden = {"sqlalchemy", "fastapi", "http"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden


class TestOrderItemEntity:
    """OrderItem domain entity must be a pure Python dataclass."""

    def test_orderitem_entity_imports(self) -> None:
        """OrderItem entity must be importable."""
        from app.core.entities.order import OrderItem

        assert OrderItem is not None

    def test_orderitem_entity_is_dataclass(self) -> None:
        """OrderItem must be a @dataclass."""
        from dataclasses import is_dataclass

        from app.core.entities.order import OrderItem

        assert is_dataclass(OrderItem), "OrderItem must be a @dataclass"

    def test_orderitem_entity_has_required_fields(self) -> None:
        """OrderItem must have id, product_id, quantity, price."""
        from uuid import UUID, uuid4

        from app.core.entities.order import OrderItem

        item = OrderItem(product_id=uuid4(), quantity=3, price=29.99)
        assert isinstance(item.id, UUID)
        assert isinstance(item.product_id, UUID)
        assert item.quantity == 3
        assert item.price == 29.99

    def test_orderitem_entity_default_id_unique(self) -> None:
        """Each OrderItem must get a unique UUID id."""
        from uuid import uuid4

        from app.core.entities.order import OrderItem

        pid = uuid4()
        i1 = OrderItem(product_id=pid, quantity=1, price=10.0)
        i2 = OrderItem(product_id=pid, quantity=2, price=20.0)
        assert i1.id != i2.id
