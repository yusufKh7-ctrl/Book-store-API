from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api import users, books, auth, order
from app.core.limiter import limiter
from app.core.logger import get_logger
from app.core.exceptions import BookNotFoundError, InsufficientStockError

from textwrap import dedent

logger = get_logger(__name__)


app = FastAPI(
    title="Book-store",
    description=dedent("""\
        ## Welcome to the Book Store API 📚
        ---
        ### 🔑 Quick Start (Admin Access)
        To test admin-only features, use the default credentials below:
        * **Username (Email):** `adminuser@example.com`
        * **Password:** `admin123123`

        ---

        ### 👤 Testing as a Regular User
        1. Go to the **`api/users/`** endpoint to register a new account.
        2. Navigate to **`/auth/login`** and enter your credentials to authenticate.
        3. Click the **Authorize** 🔓 button at the top right of the page.
        4. Enter your **Email** and **Password** to unlock protected endpoints.

        ---
        *Feel free to explore and test all available endpoints.*
        <p align="center">
        <a href="https://github.com/yusufKh7-ctrl/Book-store-API" target="_blank">
        <img src="https://img.shields.io/badge/GitHub-Repository-black?style=plastic&logo=github" alt="GitHub Repo">
        </a>
        </p>
        """),
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "book_id": exc.book_id,
            "requested": exc.requested,
            "available": exc.available
        }
    )

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["user"])
app.include_router(books.router, prefix="/api/books", tags=["book"])
app.include_router(order.router, prefix="/api/order", tags=["order"])

logger.info("Book-store-API started")