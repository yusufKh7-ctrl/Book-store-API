from fastapi import FastAPI
from app.api import users, books, auth, order

app = FastAPI(title="Book-store")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["user"])
app.include_router(books.router, prefix="/api/books", tags=["book"])
app.include_router(order.router, prefix="/api/order", tags=["order"])
