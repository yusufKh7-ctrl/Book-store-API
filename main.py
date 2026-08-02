from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api import users, books, auth, order
from app.core.limiter import limiter
from app.core.logger import get_logger

logger = get_logger(__name__)


app = FastAPI(title="Book-store")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["user"])
app.include_router(books.router, prefix="/api/books", tags=["book"])
app.include_router(order.router, prefix="/api/order", tags=["order"])

logger.info("Book-store-API started")