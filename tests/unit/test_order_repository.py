"""Tests for OrderRepository implementation (T13 verification).

Validates async CRUD operations for Order aggregate (Order + OrderItems),
including creation in single transaction, batch insert, and get_by_customer.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.entities.customer import Customer
from app.core.entities.order import Order, OrderItem
from app.core.entities.product import Product


class TestOrderRepositoryCRUD:
    """OrderRepository must support async CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_order_with_items(self, test_db_session) -> None:
        """create must persist both order header and items in one tx."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        # Setup: create customer and product
        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        order_repo = OrderRepository(session=test_db_session)

        customer = await cust_repo.create(
            Customer(name="Test", email="test@example.com")
        )
        product = await prod_repo.create(
            Product(name="Widget", price=10.0, stock=100)
        )

        # Create order with items
        order = Order(
            customer_id=customer.id,
            items=[OrderItem(product_id=product.id, quantity=2, price=10.0)],
        )
        created = await order_repo.create(order)

        assert created.id is not None
        assert created.customer_id == customer.id
        assert len(created.items) == 1
        assert created.items[0].product_id == product.id
        assert created.items[0].quantity == 2
        assert created.items[0].price == 10.0

    @pytest.mark.asyncio
    async def test_get_by_id_returns_items(self, test_db_session) -> None:
        """get_by_id must return order with nested items."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        order_repo = OrderRepository(session=test_db_session)

        customer = await cust_repo.create(
            Customer(name="Test", email="test@example.com")
        )
        product = await prod_repo.create(
            Product(name="Widget", price=10.0, stock=100)
        )

        order = Order(
            customer_id=customer.id,
            items=[
                OrderItem(product_id=product.id, quantity=3, price=10.0),
                OrderItem(product_id=product.id, quantity=1, price=9.99),
            ],
        )
        created = await order_repo.create(order)

        found = await order_repo.get_by_id(created.id)
        assert found is not None
        assert len(found.items) == 2

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, test_db_session) -> None:
        """get_by_id must return None for non-existent id."""
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )

        repo = OrderRepository(session=test_db_session)
        found = await repo.get_by_id(uuid4())
        assert found is None

    @pytest.mark.asyncio
    async def test_get_by_customer(self, test_db_session) -> None:
        """get_by_customer must return orders for a specific customer."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        order_repo = OrderRepository(session=test_db_session)

        c1 = await cust_repo.create(
            Customer(name="A", email="a@example.com")
        )
        c2 = await cust_repo.create(
            Customer(name="B", email="b@example.com")
        )
        product = await prod_repo.create(
            Product(name="Widget", price=10.0, stock=100)
        )

        await order_repo.create(
            Order(customer_id=c1.id, items=[
                OrderItem(product_id=product.id, quantity=1, price=10.0)
            ])
        )
        await order_repo.create(
            Order(customer_id=c1.id, items=[
                OrderItem(product_id=product.id, quantity=2, price=10.0)
            ])
        )
        await order_repo.create(
            Order(customer_id=c2.id, items=[
                OrderItem(product_id=product.id, quantity=3, price=10.0)
            ])
        )

        c1_orders = await order_repo.get_by_customer(c1.id)
        assert len(c1_orders) == 2

    @pytest.mark.asyncio
    async def test_get_all_pagination(self, test_db_session) -> None:
        """get_all must handle pagination."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        order_repo = OrderRepository(session=test_db_session)

        customer = await cust_repo.create(
            Customer(name="Test", email="test@example.com")
        )
        product = await prod_repo.create(
            Product(name="Widget", price=10.0, stock=100)
        )

        for _ in range(5):
            await order_repo.create(
                Order(customer_id=customer.id, items=[
                    OrderItem(product_id=product.id, quantity=1, price=10.0)
                ])
            )

        page = await order_repo.get_all(skip=1, limit=3)
        assert len(page) == 3

    @pytest.mark.asyncio
    async def test_create_batch(self, test_db_session) -> None:
        """create_batch must insert multiple orders with items."""
        from app.infrastructure.repositories.customer_repository import (
            CustomerRepository,
        )
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )
        from app.infrastructure.repositories.product_repository import (
            ProductRepository,
        )

        cust_repo = CustomerRepository(session=test_db_session)
        prod_repo = ProductRepository(session=test_db_session)
        order_repo = OrderRepository(session=test_db_session)

        customer = await cust_repo.create(
            Customer(name="Test", email="test@example.com")
        )
        product = await prod_repo.create(
            Product(name="Widget", price=10.0, stock=100)
        )

        orders = [
            Order(customer_id=customer.id, items=[
                OrderItem(product_id=product.id, quantity=1, price=10.0)
            ]),
            Order(customer_id=customer.id, items=[
                OrderItem(product_id=product.id, quantity=2, price=10.0)
            ]),
        ]
        created = await order_repo.create_batch(orders)
        assert len(created) == 2


class TestOrderRepositoryInterface:
    """IOrderRepository must be an ABC with all abstract methods."""

    def test_interface_imports(self) -> None:
        """IOrderRepository must be importable."""
        from app.core.repositories.order_repository import IOrderRepository

        assert IOrderRepository is not None

    def test_interface_is_abstract(self) -> None:
        """IOrderRepository must be an ABC."""
        from abc import ABC

        from app.core.repositories.order_repository import IOrderRepository

        assert issubclass(IOrderRepository, ABC)

    def test_impl_inherits_from_interface(self) -> None:
        """OrderRepository must inherit from IOrderRepository."""
        from app.core.repositories.order_repository import IOrderRepository
        from app.infrastructure.repositories.order_repository import (
            OrderRepository,
        )

        assert issubclass(OrderRepository, IOrderRepository)
