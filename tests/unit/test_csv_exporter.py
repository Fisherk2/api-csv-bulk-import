"""Tests for csv_exporter utility (T18 verification).

Validates CSV serialization of Order domain entities:
header row, data rows, edge cases like empty orders.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.entities.order import Order, OrderItem


class TestExportOrdersToCsv:
    """export_orders_to_csv must serialize Order entities to CSV format."""

    CSV_HEADER = "order_id,customer_id,product_id,quantity,price,status,created_at"

    def test_header_row(self) -> None:
        """Empty orders list must return header-only CSV."""
        from app.utils.csv_exporter import export_orders_to_csv

        result = export_orders_to_csv([])
        lines = result.strip().split("\n")

        assert len(lines) == 1, "Expected only header row for empty orders"
        assert lines[0] == self.CSV_HEADER

    def test_single_order_one_item(self) -> None:
        """One order with one item must produce header + 1 data row."""
        from app.utils.csv_exporter import export_orders_to_csv

        order_id = uuid4()
        customer_id = uuid4()
        product_id = uuid4()
        created_at = datetime(2026, 5, 26, 10, 30, 0, tzinfo=UTC)

        order = Order(
            id=order_id,
            customer_id=customer_id,
            status="pending",
            created_at=created_at,
            items=[
                OrderItem(
                    id=uuid4(),
                    product_id=product_id,
                    quantity=2,
                    price=19.99,
                ),
            ],
        )

        result = export_orders_to_csv([order])
        lines = result.strip().split("\n")

        assert len(lines) == 2, "Expected header + 1 data row"
        assert lines[0] == self.CSV_HEADER

        # Data row: order_id,customer_id,product_id,quantity,price,status,created_at
        data = lines[1].split(",")
        assert data[0] == str(order_id)
        assert data[1] == str(customer_id)
        assert data[2] == str(product_id)
        assert data[3] == "2"
        assert data[4] == "19.99"
        assert data[5] == "pending"
        assert data[6] == "2026-05-26T10:30:00+00:00"

    def test_order_with_multiple_items(self) -> None:
        """One order with 3 items must produce header + 3 data rows."""
        from app.utils.csv_exporter import export_orders_to_csv

        order_id = uuid4()
        customer_id = uuid4()
        created_at = datetime(2026, 5, 26, 10, 30, 0, tzinfo=UTC)

        order = Order(
            id=order_id,
            customer_id=customer_id,
            status="shipped",
            created_at=created_at,
            items=[
                OrderItem(id=uuid4(), product_id=uuid4(), quantity=1, price=10.0),
                OrderItem(id=uuid4(), product_id=uuid4(), quantity=2, price=20.0),
                OrderItem(id=uuid4(), product_id=uuid4(), quantity=3, price=30.0),
            ],
        )

        result = export_orders_to_csv([order])
        lines = result.strip().split("\n")

        assert len(lines) == 4, "Expected header + 3 data rows"
        assert lines[0] == self.CSV_HEADER
        # All 3 rows should have the same order_id and customer_id
        for i in range(1, 4):
            data = lines[i].split(",")
            assert data[0] == str(order_id)
            assert data[1] == str(customer_id)
            assert data[5] == "shipped"

    def test_multiple_orders(self) -> None:
        """Multiple orders must produce correct number of data rows."""
        from app.utils.csv_exporter import export_orders_to_csv

        created_at = datetime(2026, 5, 26, 10, 30, 0, tzinfo=UTC)

        order1 = Order(
            id=uuid4(),
            customer_id=uuid4(),
            status="pending",
            created_at=created_at,
            items=[OrderItem(id=uuid4(), product_id=uuid4(), quantity=1, price=5.0)],
        )
        order2 = Order(
            id=uuid4(),
            customer_id=uuid4(),
            status="completed",
            created_at=created_at,
            items=[
                OrderItem(id=uuid4(), product_id=uuid4(), quantity=2, price=15.0),
                OrderItem(id=uuid4(), product_id=uuid4(), quantity=1, price=25.0),
            ],
        )

        result = export_orders_to_csv([order1, order2])
        lines = result.strip().split("\n")

        assert len(lines) == 4, "Expected header + 3 data rows (1 + 2)"
        assert lines[0] == self.CSV_HEADER
        # First data row is from order1
        data_row1 = lines[1].split(",")
        assert data_row1[0] == str(order1.id)
        assert UUID(data_row1[0])
        assert float(data_row1[3]) == 1.0
        # Rows 2 and 3 are from order2
        data_row2 = lines[2].split(",")
        assert data_row2[0] == str(order2.id)
        data_row3 = lines[3].split(",")
        assert data_row3[0] == str(order2.id)
