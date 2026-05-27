"""CSV exporter for order data.

Converts Order domain entities to flat CSV rows (one row per order item).
Pure utility — no framework, DB, or HTTP dependencies.
"""

from __future__ import annotations

import csv
import io

from app.core.entities.order import Order

CSV_HEADER = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "price",
    "status",
    "created_at",
]


def export_orders_to_csv(orders: list[Order]) -> str:
    """Convert a list of Order entities to a CSV string.

    Each order item becomes one row. Order header fields
    (order_id, customer_id, status, created_at) are repeated
    for each item in the order.

    Args:
        orders: List of Order domain entities.

    Returns:
        CSV string with header row + data rows.
    """
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow(CSV_HEADER)

    for order in orders:
        for item in order.items:
            writer.writerow(
                [
                    str(order.id),
                    str(order.customer_id),
                    str(item.product_id),
                    str(item.quantity),
                    str(item.price),
                    order.status,
                    order.created_at.isoformat(),
                ]
            )

    return output.getvalue()
