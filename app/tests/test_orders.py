import pytest
from fastapi import HTTPException
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate
from app.services.order_service import (
    create_order_service,
    delete_order_by_id_service,
    get_all_orders_service,
    get_order_by_id_service,
    update_order_service,
)
from app.services.user_service import create_user_service
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_order_success(db_session, normal_user, sample_book):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5)
        ]
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
async def test_create_order_book_not_found(db_session, normal_user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=999,
                quantity=3
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_order_service(db_session, order_data, normal_user)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Book with ID 999 not found."


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=11
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_order_service(db_session, order_data, normal_user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Quantity for '{sample_book.title}' is not currently available."


@pytest.mark.asyncio
async def test_get_order_by_id(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    order = await create_order_service(db_session, order_data, normal_user)

    assert order is not None
    
    get_order = await get_order_by_id_service(db_session, order.id)
    assert get_order is not None
    assert get_order.id == order.id


@pytest.mark.asyncio
async def test_get_all_orders(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    await create_order_service(db_session, order_data, normal_user)
    await create_order_service(db_session, order_data, normal_user)

    orders = await get_all_orders_service(db_session)

    assert len(orders) == 2


@pytest.mark.asyncio
async def test_delete_order_success(db_session, sample_book, normal_user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
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
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
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
        name="Delete Test",
        email="testuserdelete@gmail.com",
        password="testdelete123"
    )
    user = await create_user_service(user_data, db_session)

    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
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
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    order_update = OrderUpdate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=6
            )
        ]
    )

    assert order is not None
    updated_order = await update_order_service(db_session, order.id, order_update, normal_user)
    assert updated_order is not None
    assert updated_order.total_price == sample_book.price * 6
    assert sample_book.stock == 4


@pytest.mark.asyncio
async def test_update_order_not_found(db_session,sample_book, normal_user):
    order_update = OrderUpdate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_order_service(db_session, 999, order_update, normal_user)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found."


@pytest.mark.asyncio
async def test_update_order_unauthorized(db_session, sample_book, normal_user, admin_user):
    user_data = UserCreate(
        name="Delete Test",
        email="testuserdelete@gmail.com",
        password="testdelete123"
    )
    user = await create_user_service(user_data, db_session)
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    order_update = OrderUpdate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=6
            )
        ]
    )

    assert order is not None
    with pytest.raises(HTTPException) as exc_info:
        await update_order_service(db_session, order.id, order_update, user)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to update this order"


@pytest.mark.asyncio
async def test_update_order_insufficient_stock(db_session, sample_book, normal_user): 
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=5
            )
        ]
    )

    order = await create_order_service(db_session, order_data, normal_user)
    
    order_update = OrderUpdate(
        items=[
            OrderItemCreate(
                book_id=sample_book.id,
                quantity=15
            )
        ]
    )

    assert order is not None
    with pytest.raises(HTTPException) as exc_info:
        await update_order_service(db_session, order.id, order_update, normal_user)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Quantity for '{sample_book.title}' is not currently available."
