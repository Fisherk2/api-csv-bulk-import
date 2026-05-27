"""Tests for Order Pydantic schemas (T12 verification).

Validates all batch upload schemas: OrderCreateSchema, OrderItemCreateSchema,
BatchUploadRequestSchema, BatchUploadResponseSchema, BatchErrorDetailSchema,
and response schemas.
"""

from __future__ import annotations


class TestOrderItemCreateSchema:
    """OrderItemCreateSchema must validate order item input."""

    def test_orderitem_create_valid(self) -> None:
        """Valid product_id, quantity, price must pass."""
        from uuid import uuid4

        from app.schemas.order import OrderItemCreateSchema

        pid = uuid4()
        schema = OrderItemCreateSchema(
            product_id=pid, quantity=2, price=19.99
        )
        assert schema.product_id == pid
        assert schema.quantity == 2
        assert schema.price == 19.99

    def test_orderitem_create_quantity_zero(self) -> None:
        """Quantity <= 0 must fail validation."""
        from uuid import uuid4

        from pydantic import ValidationError

        from app.schemas.order import OrderItemCreateSchema

        try:
            OrderItemCreateSchema(
                product_id=uuid4(), quantity=0, price=10.0
            )
        except ValidationError as e:
            assert any("quantity" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")

    def test_orderitem_create_price_zero(self) -> None:
        """Price <= 0 must fail validation."""
        from uuid import uuid4

        from pydantic import ValidationError

        from app.schemas.order import OrderItemCreateSchema

        try:
            OrderItemCreateSchema(
                product_id=uuid4(), quantity=1, price=0
            )
        except ValidationError as e:
            assert any("price" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestOrderCreateSchema:
    """OrderCreateSchema must validate order creation input."""

    def test_order_create_valid(self) -> None:
        """Valid customer_id and non-empty items must pass."""
        from uuid import uuid4

        from app.schemas.order import (
            OrderCreateSchema,
            OrderItemCreateSchema,
        )

        cid = uuid4()
        pid = uuid4()
        schema = OrderCreateSchema(
            customer_id=cid,
            items=[OrderItemCreateSchema(product_id=pid, quantity=1, price=10.0)],
        )
        assert schema.customer_id == cid
        assert len(schema.items) == 1

    def test_order_create_empty_items(self) -> None:
        """Empty items list must fail validation."""
        from uuid import uuid4

        from pydantic import ValidationError

        from app.schemas.order import OrderCreateSchema

        try:
            OrderCreateSchema(customer_id=uuid4(), items=[])
        except ValidationError as e:
            assert any("items" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestBatchUploadRequestSchema:
    """BatchUploadRequestSchema must validate batch input."""

    def test_batch_upload_valid(self) -> None:
        """Valid orders list must pass."""
        from uuid import uuid4

        from app.schemas.order import (
            BatchUploadRequestSchema,
            OrderCreateSchema,
            OrderItemCreateSchema,
        )

        pid = uuid4()
        cid = uuid4()
        schema = BatchUploadRequestSchema(
            orders=[
                OrderCreateSchema(
                    customer_id=cid,
                    items=[OrderItemCreateSchema(product_id=pid, quantity=1, price=10.0)],
                )
            ]
        )
        assert len(schema.orders) == 1

    def test_batch_upload_empty_orders(self) -> None:
        """Empty orders list must fail validation."""
        from pydantic import ValidationError

        from app.schemas.order import BatchUploadRequestSchema

        try:
            BatchUploadRequestSchema(orders=[])
        except ValidationError as e:
            assert any("orders" in str(err["loc"]) for err in e.errors())
        else:
            raise AssertionError("ValidationError not raised")


class TestBatchUploadResponseSchema:
    """BatchUploadResponseSchema must support response structure."""

    def test_batch_upload_response_fields(self) -> None:
        """Response must include total, successful, failed, errors."""
        from app.schemas.order import BatchUploadResponseSchema

        schema = BatchUploadResponseSchema(
            total=10, successful=8, failed=2, errors=[]
        )
        assert schema.total == 10
        assert schema.successful == 8
        assert schema.failed == 2
        assert schema.errors == []


class TestBatchErrorDetailSchema:
    """BatchErrorDetailSchema must include RFC 7807 fields + row_number."""

    def test_batch_error_detail_fields(self) -> None:
        """Error detail must have type, title, status, detail, instance, row_number."""
        from app.schemas.order import BatchErrorDetailSchema

        err = BatchErrorDetailSchema(
            type="about:blank",
            title="Validation Error",
            status=422,
            detail="Invalid data",
            row_number=3,
        )
        assert err.type == "about:blank"
        assert err.title == "Validation Error"
        assert err.status == 422
        assert err.detail == "Invalid data"
        assert err.row_number == 3
        assert err.instance is None

    def test_batch_error_detail_defaults(self) -> None:
        """Error defaults: type='about:blank', status=422, instance=None."""
        from app.schemas.order import BatchErrorDetailSchema

        err = BatchErrorDetailSchema(
            title="Test Error", row_number=1
        )
        assert err.type == "about:blank"
        assert err.status == 422
        assert err.instance is None


class TestOrderResponseSchema:
    """OrderResponseSchema must support from_attributes config."""

    def test_order_response_from_attributes(self) -> None:
        """OrderResponseSchema must have from_attributes=True."""
        from app.schemas.order import OrderResponseSchema

        assert (
            OrderResponseSchema.model_config.get("from_attributes") is True
        )


class TestOrderItemResponseSchema:
    """OrderItemResponseSchema must support from_attributes config."""

    def test_orderitem_response_from_attributes(self) -> None:
        """OrderItemResponseSchema must have from_attributes=True."""
        from app.schemas.order import OrderItemResponseSchema

        assert (
            OrderItemResponseSchema.model_config.get("from_attributes") is True
        )
