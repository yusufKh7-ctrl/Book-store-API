from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate
from app.repositories.order_reository import OrderRepository
from app.repositories.book_repository import BookRepository

from decimal import Decimal


async def create_order_service(
    db: AsyncSession, order_data: OrderCreate, current_user: User
):
    order_repo = OrderRepository(db)
    book_repo = BookRepository(db)

    user_id = current_user.id

    total_order_price = Decimal("0.00")
    order = Order(user_id=user_id, total_price=total_order_price)
    items = order_data.items

    for item in items:
        book = await book_repo.get_by_id(item.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {item.book_id} not found.",
            )

        if item.quantity > book.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantity for '{book.title}' is not currently available.",
            )

        book.stock -= item.quantity

        item_total_price = book.price * item.quantity
        total_order_price += item_total_price

        order_item = OrderItem(
            book_id=item.book_id, quantity=item.quantity, unit_price=book.price
        )

        order.items.append(order_item)

    order.total_price = total_order_price

    await order_repo.create_order(order)

    await db.commit()
    return await order_repo.get_order_by_id(order.id)


async def get_order_by_id_service(db: AsyncSession, order_id: int):
    repo = OrderRepository(db)
    order = await repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    return order


async def get_all_orders_service(db: AsyncSession):
    repo = OrderRepository(db)
    return await repo.get_all_orders()


async def delete_order_by_id_service(db: AsyncSession, order_id: int, current_user: User):
    repo = OrderRepository(db)
    order = await repo.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )
    
    if current_user.id != order.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this order",
        )
    for item in order.items:
        if item.book:
            item.book.stock += item.quantity
    
    await repo.delete_order(order)
    await db.commit()