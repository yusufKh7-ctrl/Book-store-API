from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
import pytest_asyncio
from app.models import *

from main import app
from app.db.session import get_db
from app.db.base import Base
from app.config import settings
from app.schemas.user import UserCreate
from app.schemas.book import BookCreate
from app.services.user_service import create_user_service
from app.services.auth_service import create_access_token
from app.services.book_service import create_book_service
from decimal import Decimal

@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    TestingSessionLocal = async_sessionmaker(
        bind=async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with TestingSessionLocal() as session:
        app.dependency_overrides[get_db] = lambda: session
        yield session
        await session.rollback()
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def normal_user(db_session):
    user_data = UserCreate(
        name="Test User",
        email="testuser@example.com",
        password="testpassword123",
    )
    return await create_user_service(user_data, db_session)


@pytest_asyncio.fixture
async def admin_user(db_session):
    user_data = UserCreate(
        name="Admin User",
        email="admin@example.com",
        password="adminpassword123",
    )
    user = await create_user_service(user_data, db_session)
    user.is_admin = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_token(normal_user):
    token = create_access_token({"sub": str(normal_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_token(admin_user):
    token = create_access_token({"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_book(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    return await create_book_service(book_data, db_session)