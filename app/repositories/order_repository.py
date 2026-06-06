from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order: Order):
        self.db.add(order)
        return order

    async def create_order_items(self, order_item: OrderItem):
        self.db.add(order_item)
        return order_item

    async def get_order_by_id(self, order_id: int):
        statement = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).options(selectinload(OrderItem.book)),
            )
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_all_orders(self):
        statement = select(Order).options(
            selectinload(Order.user),
            selectinload(Order.items).options(selectinload(OrderItem.book)),
        )
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def delete_order(self, order: Order):
        await self.db.delete(order)

    async def update_order(self, order: Order):
        self.db.add(order)
        return order

    async def clear_order_items(self, order: Order):
        order.items.clear()
        await self.db.flush()
