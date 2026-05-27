"""Tests for ValidationService (T14 verification).

Validates the batch validation service — validates raw data dicts
against a Pydantic schema, returns (valid_items, error_details) tuple
with 1-indexed row numbers.
"""

from __future__ import annotations

from uuid import uuid4

from app.schemas.order import OrderCreateSchema


class TestValidationService:
    """ValidationService must validate batches and return errors with row numbers."""

    def test_validate_all_valid(self) -> None:
        """All valid items must return all in valid list, zero errors."""
        from app.core.services.validation_service import ValidationService

        pid = uuid4()
        cid = uuid4()
        data = [
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
            },
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 2, "price": 20.0}],
            },
        ]

        valid, errors = ValidationService.validate_batch(data, OrderCreateSchema)
        assert len(valid) == 2
        assert len(errors) == 0

    def test_validate_partial_invalid(self) -> None:
        """Mix of valid and invalid must return partial results."""
        from app.core.services.validation_service import ValidationService

        pid = uuid4()
        cid = uuid4()
        data = [
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
            },
            {
                "customer_id": cid,
                "items": [],  # INVALID: empty items
            },
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 3, "price": 30.0}],
            },
        ]

        valid, errors = ValidationService.validate_batch(data, OrderCreateSchema)
        assert len(valid) == 2
        assert len(errors) == 1
        assert errors[0].row_number == 2

    def test_validate_all_invalid(self) -> None:
        """All invalid must return zero valid, all errors."""
        from app.core.services.validation_service import ValidationService

        cid = uuid4()
        data = [
            {"customer_id": cid, "items": []},
            {"customer_id": cid, "items": []},
        ]

        valid, errors = ValidationService.validate_batch(data, OrderCreateSchema)
        assert len(valid) == 0
        assert len(errors) == 2
        assert errors[0].row_number == 1
        assert errors[1].row_number == 2

    def test_validate_empty_batch(self) -> None:
        """Empty batch must return empty valid and empty errors."""
        from app.core.services.validation_service import ValidationService

        valid, errors = ValidationService.validate_batch([], OrderCreateSchema)
        assert len(valid) == 0
        assert len(errors) == 0

    def test_validate_row_numbers_are_sequential(self) -> None:
        """Row numbers must be 1-indexed and sequential."""
        from app.core.services.validation_service import ValidationService

        pid = uuid4()
        cid = uuid4()
        data = [
            {
                "customer_id": cid,
                "items": [{"product_id": pid, "quantity": 1, "price": 10.0}],
            },
            {"customer_id": cid, "items": []},  # INVALID
            {"customer_id": cid, "items": []},  # INVALID
        ]

        valid, errors = ValidationService.validate_batch(data, OrderCreateSchema)
        assert len(valid) == 1
        assert len(errors) == 2
        assert errors[0].row_number == 2
        assert errors[1].row_number == 3

    def test_validation_service_no_external_imports(self) -> None:
        """ValidationService must have zero external dependencies."""
        import ast
        from pathlib import Path

        svc_path = (
            Path(__file__).resolve().parents[2]
            / "app" / "core" / "services" / "validation_service.py"
        )
        source = svc_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        forbidden = {"sqlalchemy", "fastapi", "http"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden
