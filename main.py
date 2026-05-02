from fastapi import FastAPI
from app.api import users

app = FastAPI(title="Book-store")
app.include_router(users.router, prefix="/api/users", tags=["user"])
