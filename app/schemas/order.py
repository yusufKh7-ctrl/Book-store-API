from pydantic import BaseModel, Field, ConfigDict
from .book import BookPublic
from .user import UserPublic
from decimal import Decimal


class OrderItemCreate(BaseModel):
    book_id: int
    quantity: int = Field(..., gt=0)


class OrderItemPublic(BaseModel):
    book: BookPublic
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderPublic(BaseModel):
    id: int
    user: UserPublic
    total_price: Decimal
    items: list[OrderItemPublic]

    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    items: list[OrderItemCreate]
