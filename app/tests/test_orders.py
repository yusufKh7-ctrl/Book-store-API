import asyncio
from decimal import Decimal

import pytest
from sqlalchemy import select

from fastapi import HTTPException
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate
from app.services.order_service import (
    create_order_service,
    delete_order_by_id_service,
    get_all_orders_service,
    get_order_by_id_service,
    update_order_service,
)
from app.schemas.user import UserCreate
from app.schemas.book import BookCreate
from app.services.user_service import create_user_service
from app.services.book_service import create_book_service
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.core.exceptions import InsufficientStockError, BookNotFoundError

from unittest.mock import patch


@pytest.mark.asyncio
async def test_create_order_success(db_session, normal_user, sample_book):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )
    order = await create_order_service(db_session, order_data, normal_user)

    assert order is not None
    assert order.id is not None
    assert order.user_id == normal_user.id

    assert order.total_price == sample_book.price * 5
    assert len(order.items) == 1
    assert order.items[0].quantity == 5
    assert order.items[0].unit_price == sample_book.price

    from app.repositories.book_repository import BookRepository

    repo = BookRepository(db_session)
    updated_book = await repo.get_by_id(sample_book.id)
    assert updated_book is not None
    assert updated_book.stock == 5


@pytest.mark.asyncio
async def test_concurrent_orders_cannot_oversell(
    db_session,
    session_factory,
    normal_user,
):
    user_2_data = UserCreate(
        name="User2",
        email="secondtest@gmail.com",
        password="testpassword123",
    )

    user_2 = await create_user_service(user_2_data, db_session)

    book_data = BookCreate(
        title="Concurrency Test Book",
        description="Book for concurrency testing",
        author="Test Author",
        price=Decimal("10.00"),
        stock=1,
    )

    book = await create_book_service(book_data, db_session)

    # Create two completely independent database sessions
    session_a = session_factory()
    session_b = session_factory()

    order_data_a = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=book.id,
                quantity=1
            )
        ]
    )


    order_data_b = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=book.id,
                quantity=1
            )
        ]
    )

    async def create_order_a():
        try:
            return await create_order_service(
                session_a,
                order_data_a,
                normal_user
            )
        except InsufficientStockError as exc:
            return exc

    async def create_order_b():
        try:
            return await create_order_service(
                session_b,
                order_data_b,
                user_2
            )
        except InsufficientStockError as exc:
            return exc

    barrier = asyncio.Barrier(2)
    original_get_for_update = BookRepository.get_by_id_for_update

    async def patched_get_for_update(self, book_id):
        await asyncio.wait_for(barrier.wait(), timeout=5)
        return await original_get_for_update(self, book_id)

    try:
        with patch.object(BookRepository, "get_by_id_for_update", patched_get_for_update):
            result_a, result_b = await asyncio.gather(
                create_order_a(),
                create_order_b(),
            )
    finally:
        await session_a.close()
        await session_b.close()

    results = [result_a, result_b]

    successful_orders = [
        result for result in results
        if not isinstance(result, Exception)
    ]

    failed_orders = [
        result for result in results
        if isinstance(result, Exception)
    ]

    # Exactly ONE order should seccessd
    assert len(successful_orders) == 1
    assert len(failed_orders) == 1

    failed = failed_orders[0]
    assert isinstance(failed, InsufficientStockError)
    assert failed.book_id == book.id
    assert failed.book_title == book.title
    assert failed.requested == 1
    assert failed.available == 0

    # The remining stock must be zero
    result = await db_session.execute(
        select(Book).where(Book.id == book.id).execution_options(populate_existing=True)
    )
    updated_book = result.scalar_one()

    assert updated_book.stock == 0


@pytest.mark.asyncio
async def test_concurrent_orders_without_lock_oversells(
    db_session,
    session_factory,
    normal_user,
):
    user_2_data = UserCreate(
        name="User2",
        email="secondtest@gmail.com",
        password="testpassword123",
    )

    user_2 = await create_user_service(user_2_data, db_session)

    book_data = BookCreate(
        title="Concurrency Test Book",
        description="Book for concurrency testing",
        author="Test Author",
        price=Decimal("10.00"),
        stock=1,
    )

    book = await create_book_service(book_data, db_session)

    # Create two completely independent database sessions
    session_a = session_factory()
    session_b = session_factory()

    order_data_a = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=book.id,
                quantity=1
            )
        ]
    )


    order_data_b = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=book.id,
                quantity=1
            )
        ]
    )

    async def create_order_a():
        try:
            return await create_order_service(
                session_a,
                order_data_a,
                normal_user
            )
        except InsufficientStockError as exc:
            return exc

    async def create_order_b():
        try:
            return await create_order_service(
                session_b,
                order_data_b,
                user_2
            )
        except InsufficientStockError as exc:
            return exc

    barrier = asyncio.Barrier(2)
    original_get_by_id = BookRepository.get_by_id

    async def get_without_lock(self, book_id):
        await asyncio.wait_for(barrier.wait(), timeout=5)
        return await original_get_by_id(self, book_id)

    try:
        with patch.object(BookRepository, "get_by_id_for_update", get_without_lock):
            result_a, result_b = await asyncio.gather(
                create_order_a(),
                create_order_b()
            )
    finally:
        await session_a.close()
        await session_b.close()

    results = [result_a, result_b]
    successful_orders = [result for result in results if not isinstance(result, Exception)]
    failed_orders = [result for result in results if isinstance(result, Exception)]

    assert len(successful_orders) == 2
    assert len(failed_orders) == 0

@pytest.mark.asyncio
async def test_create_order_book_not_found(db_session, normal_user):
    order_data = OrderCreate(items=[OrderItemCreate(book_id=999, quantity=3)])

    with pytest.raises(BookNotFoundError) as exc_info:
        await create_order_service(db_session, order_data, normal_user)

    assert exc_info.value.book_id == 999

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=11)]
    )

    with pytest.raises(InsufficientStockError) as exc_info:
        await create_order_service(db_session, order_data, normal_user)

    assert exc_info.value.book_id == sample_book.id
    assert exc_info.value.requested == 11
    assert exc_info.value.available == sample_book.stock

@pytest.mark.asyncio
async def test_get_order_by_id(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)

    assert order is not None

    get_order = await get_order_by_id_service(db_session, order.id)
    assert get_order is not None
    assert get_order.id == order.id


@pytest.mark.asyncio
async def test_get_all_orders(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    await create_order_service(db_session, order_data, normal_user)
    await create_order_service(db_session, order_data, normal_user)

    orders = await get_all_orders_service(db_session)

    assert len(orders) == 2


@pytest.mark.asyncio
async def test_delete_order_success(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)

    assert order is not None
    await delete_order_by_id_service(db_session, order.id, normal_user)
    with pytest.raises(HTTPException) as exc_info:
        await get_order_by_id_service(db_session, order.id)

    assert exc_info.value.status_code == 404
    assert sample_book.stock == 10


@pytest.mark.asyncio
async def test_delete_order_by_admin(db_session, sample_book, normal_user, admin_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    assert order is not None
    await delete_order_by_id_service(db_session, order.id, admin_user)
    with pytest.raises(HTTPException) as exc_info:
        await get_order_by_id_service(db_session, order.id)

    assert exc_info.value.status_code == 404
    assert sample_book.stock == 10


@pytest.mark.asyncio
async def test_delete_order_unauthorized(db_session, sample_book, normal_user):
    user_data = UserCreate(
        name="Delete Test", email="testuserdelete@gmail.com", password="testdelete123"
    )
    user = await create_user_service(user_data, db_session)

    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)

    assert order is not None
    with pytest.raises(HTTPException) as exc_info:
        await delete_order_by_id_service(db_session, order.id, user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to delete this order"


@pytest.mark.asyncio
async def test_get_order_not_found(db_session, normal_user):
    with pytest.raises(HTTPException) as exc_info:
        await get_order_by_id_service(db_session, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found."


@pytest.mark.asyncio
async def test_update_order_success(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    order_update = OrderUpdate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=6)]
    )

    assert order is not None
    updated_order = await update_order_service(
        db_session, order.id, order_update, normal_user
    )
    assert updated_order is not None
    assert updated_order.total_price == sample_book.price * 6
    assert sample_book.stock == 4


@pytest.mark.asyncio
async def test_update_order_not_found(db_session, sample_book, normal_user):
    order_update = OrderUpdate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_order_service(db_session, 999, order_update, normal_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found."


@pytest.mark.asyncio
async def test_update_order_unauthorized(
    db_session, sample_book, normal_user, admin_user
):
    user_data = UserCreate(
        name="Delete Test", email="testuserdelete@gmail.com", password="testdelete123"
    )
    user = await create_user_service(user_data, db_session)
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    order_update = OrderUpdate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=6)]
    )

    assert order is not None
    with pytest.raises(HTTPException) as exc_info:
        await update_order_service(db_session, order.id, order_update, user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to update this order"


@pytest.mark.asyncio
async def test_update_order_insufficient_stock(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=5)]
    )

    order = await create_order_service(db_session, order_data, normal_user)

    order_update = OrderUpdate(
        items=[OrderItemCreate(book_id=sample_book.id, quantity=15)]
    )

    assert order is not None
    with pytest.raises(InsufficientStockError) as exc_info:
        await update_order_service(db_session, order.id, order_update, normal_user)

    assert exc_info.value.book_id == sample_book.id
    assert exc_info.value.available == sample_book.stock
    assert exc_info.value.requested == 15
    assert exc_info.value.book_title == sample_book.title
