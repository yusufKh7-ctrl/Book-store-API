from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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