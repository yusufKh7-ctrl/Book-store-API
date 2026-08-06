from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api import users, books, auth, order
from app.core.limiter import limiter
from app.core.logger import get_logger
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
        """),
    version="1.0.0"
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["user"])
app.include_router(books.router, prefix="/api/books", tags=["book"])
app.include_router(order.router, prefix="/api/order", tags=["order"])

logger.info("Book-store-API started")