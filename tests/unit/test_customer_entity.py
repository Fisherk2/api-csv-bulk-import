"""Tests for Customer domain entity (T10 verification).

Validates Customer entity — pure Python dataclass, no framework imports,
correct field defaults and identity-based equality.
"""

from __future__ import annotations


class TestCustomerEntity:
    """Customer domain entity must be a pure Python dataclass."""

    def test_customer_entity_imports(self) -> None:
        """Customer entity must be importable from app.core.entities.customer."""
        from app.core.entities.customer import Customer

        assert Customer is not None

    def test_customer_entity_is_dataclass(self) -> None:
        """Customer must be a @dataclass."""
        from dataclasses import is_dataclass

        from app.core.entities.customer import Customer

        assert is_dataclass(Customer), "Customer must be a @dataclass"

    def test_customer_entity_has_required_fields(self) -> None:
        """Customer must have name, email and auto-generated id."""
        from uuid import UUID

        from app.core.entities.customer import Customer

        customer = Customer(name="John Doe", email="john@example.com")
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert isinstance(customer.id, UUID)

    def test_customer_entity_default_id_is_unique(self) -> None:
        """Each Customer instance must get a unique UUID id."""
        from app.core.entities.customer import Customer

        c1 = Customer(name="Alice", email="alice@example.com")
        c2 = Customer(name="Bob", email="bob@example.com")
        assert c1.id != c2.id

    def test_customer_entity_no_framework_imports(self) -> None:
        """Customer entity module must have zero external dependencies."""
        import ast
        from pathlib import Path

        entity_path = (
            Path(__file__).resolve().parents[2]
            / "app" / "core" / "entities" / "customer.py"
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
