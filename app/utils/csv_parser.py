"""CSV parser for flat order-item rows.

CSV format (one row per order item):
    customer_name, customer_email, customer_id, product_id, quantity, price

Provides both raw row parsing and grouped order transformation.
"""

from __future__ import annotations

import csv
import io
from typing import Any

_REQUIRED_COLUMNS = frozenset({
    "customer_id",
    "customer_name",
    "customer_email",
    "product_id",
    "quantity",
    "price",
})


def parse_csv(content: str) -> list[dict[str, Any]]:
    """Parse CSV content into a list of dictionaries (one per row).

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


def parse_csv_to_orders(content: str) -> list[dict[str, Any]]:
    """Parse CSV content and group rows by customer into orders.

    Flat CSV rows (one per order item) are grouped by customer_email
    into order dicts compatible with OrderCreateSchema.

    The CSV must have these columns:
        customer_name, customer_email, customer_id, product_id, quantity, price

    Args:
        content: Raw CSV string with header row.

    Returns:
        List of order dicts, each with customer_id and items list.

    Raises:
        ValueError: If CSV is empty, has no header, is malformed,
                    or is missing required columns.
    """
    rows = parse_csv(content)

    # Validate required columns are present (check first row's keys)
    if rows:
        header_cols = set(rows[0].keys())
        missing_cols = _REQUIRED_COLUMNS - header_cols
        if missing_cols:
            raise ValueError(
                f"CSV missing required columns: {', '.join(sorted(missing_cols))}"
            )

    orders_by_customer: dict[str, dict[str, Any]] = {}
    for row_number, row in enumerate(rows, start=1):
        email = row.get("customer_email", "")
        if email not in orders_by_customer:
            orders_by_customer[email] = {
                "customer_id": row.get("customer_id", ""),
                "items": [],
            }

        # Safely parse numeric values with error context
        raw_quantity = row.get("quantity", "1")
        raw_price = row.get("price", "0")
        try:
            quantity = int(raw_quantity)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Row {row_number}: invalid quantity '{raw_quantity}'"
            ) from exc
        try:
            price = float(raw_price)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Row {row_number}: invalid price '{raw_price}'"
            ) from exc

        if quantity < 1:
            raise ValueError(
                f"Row {row_number}: quantity must be at least 1, got {quantity}"
            )
        if price < 0:
            raise ValueError(
                f"Row {row_number}: price must be non-negative, got {price}"
            )

        orders_by_customer[email]["items"].append(
            {
                "product_id": row.get("product_id", ""),
                "quantity": quantity,
                "price": price,
            }
        )

    return list(orders_by_customer.values())
