from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, CheckConstraint

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from decimal import Decimal

if TYPE_CHECKING:
    from .user import User
    from .book import Book


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="check_total_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="check_unit_price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship(back_populates="order_items")
