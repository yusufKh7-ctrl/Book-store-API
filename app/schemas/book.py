from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    author: str = Field(..., min_length=2, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock: int = Field(..., ge=0)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    author: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)


class BookPublic(BaseModel):
    id: int
    title: str
    description: Optional[str]
    author: str
    price: Decimal
    stock: int

    model_config = ConfigDict(from_attributes=True)
