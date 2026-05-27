"""CSV parser for flat order-item rows.

CSV format (one row per order item):
    customer_name, customer_email, product_id, quantity, price

Returns one dict per CSV row for downstream grouping by customer_email.
"""

from __future__ import annotations

import csv
import io
from typing import Any


def parse_csv(content: str) -> list[dict[str, Any]]:
    """Parse CSV content into a list of dictionaries.

    Args:
        content: Raw CSV string with header row.

    Returns:
        List of dictionaries, one per CSV data row.

    Raises:
        ValueError: If CSV is empty, has no header, or is malformed.
    """
    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        raise ValueError("CSV file has no header row")

    rows: list[dict[str, Any]] = []
    for row_number, row in enumerate(reader, start=1):
        if not any(value.strip() for value in row.values()):
            raise ValueError(
                f"Row {row_number} is empty or contains only whitespace"
            )
        rows.append(dict(row))

    if not rows:
        raise ValueError("CSV file contains no data rows")

    return rows
