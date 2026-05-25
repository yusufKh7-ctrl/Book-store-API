from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import String, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Book(Base):
    __tablename__ = "books"

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    author: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column()

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
