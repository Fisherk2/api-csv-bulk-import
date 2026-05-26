"""Tests for Product domain entity (T08 verification).

Validates Product entity — pure Python dataclass, no framework imports,
correct field defaults and identity-based equality.
"""

from __future__ import annotations


class TestProductEntity:
    """Product domain entity must be a pure Python dataclass."""

    def test_product_entity_imports(self) -> None:
        """Product entity must be importable from app.core.entities.product."""
        from app.core.entities.product import Product

        assert Product is not None

    def test_product_entity_is_dataclass(self) -> None:
        """Product must be a @dataclass."""
        from dataclasses import is_dataclass

        from app.core.entities.product import Product

        assert is_dataclass(Product), "Product must be a @dataclass"

    def test_product_entity_has_required_fields(self) -> None:
        """Product must have name, price, stock and auto-generated id."""
        from uuid import UUID

        from app.core.entities.product import Product

        product = Product(name="Widget", price=19.99, stock=100)
        assert product.name == "Widget"
        assert product.price == 19.99
        assert product.stock == 100
        assert isinstance(product.id, UUID)

    def test_product_entity_default_id_is_unique(self) -> None:
        """Each Product instance must get a unique UUID id."""
        from app.core.entities.product import Product

        p1 = Product(name="A", price=1.0, stock=1)
        p2 = Product(name="B", price=2.0, stock=2)
        assert p1.id != p2.id

    def test_product_entity_no_framework_imports(self) -> None:
        """Product entity module must have zero external dependencies."""
        import ast
        from pathlib import Path

        entity_path = (
            Path(__file__).resolve().parents[2]
            / "app" / "core" / "entities" / "product.py"
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
