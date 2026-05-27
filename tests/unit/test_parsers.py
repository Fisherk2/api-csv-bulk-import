"""Tests for CSV, JSON parsers and file_utils (T16 verification)."""

from __future__ import annotations


class TestCSVParser:
    """CSV parser must handle valid and invalid CSV content."""

    def test_parse_valid_csv(self) -> None:
        """Valid CSV must return list of dicts."""
        from app.utils.csv_parser import parse_csv

        content = "customer_name,customer_email,product_id,quantity,price\n"
        content += "John Doe,john@example.com,abc-123,2,19.99\n"
        content += "Jane Smith,jane@example.com,def-456,1,9.99\n"

        rows = parse_csv(content)
        assert len(rows) == 2
        assert rows[0]["customer_name"] == "John Doe"
        assert rows[1]["customer_email"] == "jane@example.com"

    def test_parse_empty_csv(self) -> None:
        """Empty CSV must raise ValueError."""
        from app.utils.csv_parser import parse_csv

        try:
            parse_csv("")
            raise AssertionError("Should have raised")
        except ValueError:
            pass

    def test_parse_header_only_csv(self) -> None:
        """CSV with only header (no data rows) must raise ValueError."""
        from app.utils.csv_parser import parse_csv

        try:
            parse_csv("customer_name,customer_email\n")
            raise AssertionError("Should have raised")
        except ValueError:
            pass


class TestJSONParser:
    """JSON parser must handle valid and invalid JSON content."""

    def test_parse_valid_json(self) -> None:
        """Valid JSON must extract orders list."""
        from app.utils.json_parser import parse_json

        content = '{"orders": [{"customer_id": "abc", "items": []}]}'
        result = parse_json(content)
        assert len(result) == 1

    def test_parse_json_missing_orders(self) -> None:
        """JSON without 'orders' key must raise ValueError."""
        from app.utils.json_parser import parse_json

        try:
            parse_json('{"other": []}')
            raise AssertionError("Should have raised")
        except ValueError:
            pass

    def test_parse_invalid_json(self) -> None:
        """Malformed JSON must raise ValueError."""
        from app.utils.json_parser import parse_json

        try:
            parse_json("{invalid")
            raise AssertionError("Should have raised")
        except ValueError:
            pass

    def test_parse_json_orders_not_list(self) -> None:
        """'orders' not being a list must raise ValueError."""
        from app.utils.json_parser import parse_json

        try:
            parse_json('{"orders": "not-a-list"}')
            raise AssertionError("Should have raised")
        except ValueError:
            pass


class TestFileUtils:
    """File size validation must work correctly."""

    def test_file_size_within_limit(self) -> None:
        """File within limit must return True."""
        from app.utils.file_utils import validate_file_size

        assert validate_file_size(1024, max_mb=10) is True

    def test_file_size_exceeds_limit(self) -> None:
        """File exceeding limit must return False."""
        from app.utils.file_utils import validate_file_size

        assert validate_file_size(11 * 1024 * 1024, max_mb=10) is False

    def test_file_size_at_limit(self) -> None:
        """File exactly at limit must return True."""
        from app.utils.file_utils import validate_file_size

        assert validate_file_size(10 * 1024 * 1024, max_mb=10) is True
