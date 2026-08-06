import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def clear_data():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE books, users RESTART IDENTITY CASCADE;"))
        print("All tables cleared successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(clear_data())