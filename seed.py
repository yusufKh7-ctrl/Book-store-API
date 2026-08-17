import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models import *
from app.models.book import Book
from app.models.user import User
from app.config import settings
from app.core.logger import get_logger
from app.services.auth_service import hash_password

logger = get_logger(__name__)
DATABASE_URL = settings.DATABASE_URL

books_data = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "description": "Programming book",
        "price": Decimal("49.99"),
        "stock": 10,
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas",
        "description": "Software craftsmanship",
        "price": Decimal("44.99"),
        "stock": 8,
    },
    {
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "description": "Elements of reusable object-oriented software",
        "price": Decimal("54.99"),
        "stock": 12,
    },
    {
        "title": "Refactoring",
        "author": "Martin Fowler",
        "description": "Improving the design of existing code",
        "price": Decimal("47.50"),
        "stock": 15,
    },
    {
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen",
        "description": "Comprehensive guide to algorithms",
        "price": Decimal("89.99"),
        "stock": 5,
    },
    {
        "title": "Head First Design Patterns",
        "author": "Eric Freeman",
        "description": "A brain-friendly guide to design patterns",
        "price": Decimal("38.20"),
        "stock": 20,
    },
    {
        "title": "You Don't Know JS Yet",
        "author": "Kyle Simpson",
        "description": "Deep dive into JavaScript core mechanisms",
        "price": Decimal("29.99"),
        "stock": 18,
    },
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "description": "A hands-on, project-based introduction to programming",
        "price": Decimal("35.00"),
        "stock": 25,
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "description": "Big data system architecture and concepts",
        "price": Decimal("59.99"),
        "stock": 7,
    },
    {
        "title": "Grokking Algorithms",
        "author": "Aditya Bhargava",
        "description": "An illustrated guide for programmers",
        "price": Decimal("39.99"),
        "stock": 14,
    },
    {
        "title": "Code Complete",
        "author": "Steve McConnell",
        "description": "A practical handbook of software construction",
        "price": Decimal("52.00"),
        "stock": 6,
    },
    {
        "title": "Effective Java",
        "author": "Joshua Bloch",
        "description": "Best practices for the Java platform",
        "price": Decimal("48.99"),
        "stock": 11,
    },
    {
        "title": "Domain-Driven Design",
        "author": "Eric Evans",
        "description": "Tackling complexity in the heart of software",
        "price": Decimal("58.00"),
        "stock": 9,
    },
    {
        "title": "The Clean Coder",
        "author": "Robert C. Martin",
        "description": "A code of conduct for professional programmers",
        "price": Decimal("34.95"),
        "stock": 13,
    },
    {
        "title": "Structure and Interpretation of Computer Programs",
        "author": "Harold Abelson",
        "description": "Computer science principles with Scheme",
        "price": Decimal("65.00"),
        "stock": 4,
    },
    {
        "title": "Working Effectively with Legacy Code",
        "author": "Michael Feathers",
        "description": "Strategies for modifying existing software",
        "price": Decimal("46.99"),
        "stock": 10,
    },
    {
        "title": "Site Reliability Engineering",
        "author": "Betsy Beyer",
        "description": "How Google runs production systems",
        "price": Decimal("42.50"),
        "stock": 16,
    },
    {
        "title": "Continuous Delivery",
        "author": "Jez Humble",
        "description": "Automated software delivery pipeline",
        "price": Decimal("51.99"),
        "stock": 8,
    },
    {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "description": "A craftsman's guide to software structure and design",
        "price": Decimal("43.99"),
        "stock": 17,
    },
    {
        "title": "The Phoenix Project",
        "author": "Gene Kim",
        "description": "A novel about IT, DevOps, and helping your business win",
        "price": Decimal("26.99"),
        "stock": 22,
    },
]


async def seed_admin_user(session: AsyncSession):
    stmt = select(User).where(User.email == "adminuser@example.com")
    result = await session.execute(stmt)
    admin = result.scalar_one_or_none()

    if not admin:
        admin_user = User(
            name="admin",
            email="adminuser@example.com",
            hashed_password=hash_password("admin123123"),
            is_admin=True,
        )
        session.add(admin_user)
        await session.commit()
        logger.info(
            "Admin created successfully: email: adminuser@example.com, password: admin123123"
        )
    else:
        logger.info("Admin user already exists, skipping creation.")


async def seed_books(session: AsyncSession):
    stmt = select(Book)
    result = await session.execute(stmt)
    existing_books = result.scalars().all()
    if not existing_books:
        books = [Book(**book_data) for book_data in books_data]
        session.add_all(books)
        await session.commit()
        logger.info(f"Added {len(books)} books successfully.")
    else:
        logger.info("Books already seeded, skipping book creation.")


async def seed():
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

    async with SessionLocal() as session:
        await seed_admin_user(session)
        await seed_books(session)

    await engine.dispose()
    logger.info("Database seeding process completed.")


if __name__ == "__main__":
    asyncio.run(seed())
