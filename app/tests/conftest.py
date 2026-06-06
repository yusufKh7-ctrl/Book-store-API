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
        app.dependency_overrides[get_db] = lambda: (
            session
        )  # Understand what is this code line.
        yield session
        await session.rollback()
        app.dependency_overrides.clear()
