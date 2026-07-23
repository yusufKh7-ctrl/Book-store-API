import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import *
from app.db.base import Base
from app.models.book import Book
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

books = [
    Book(
        title="Clean Code",
        author="Robert C. Martin",
        description="Programming book",
        price=Decimal("49.99"),
        stock=10,
    ),
    Book(
        title="The Pragmatic Programmer",
        author="David Thomas",
        description="Software craftsmanship",
        price=Decimal("44.99"),
        stock=8,
    ),
    Book(
        title="Design Patterns",
        author="Erich Gamma",
        description="Elements of reusable object-oriented software",
        price=Decimal("54.99"),
        stock=12,
    ),
    Book(
        title="Refactoring",
        author="Martin Fowler",
        description="Improving the design of existing code",
        price=Decimal("47.50"),
        stock=15,
    ),
    Book(
        title="Introduction to Algorithms",
        author="Thomas H. Cormen",
        description="Comprehensive guide to algorithms",
        price=Decimal("89.99"),
        stock=5,
    ),
    Book(
        title="Head First Design Patterns",
        author="Eric Freeman",
        description="A brain-friendly guide to design patterns",
        price=Decimal("38.20"),
        stock=20,
    ),
    Book(
        title="You Don't Know JS Yet",
        author="Kyle Simpson",
        description="Deep dive into JavaScript core mechanisms",
        price=Decimal("29.99"),
        stock=18,
    ),
    Book(
        title="Python Crash Course",
        author="Eric Matthes",
        description="A hands-on, project-based introduction to programming",
        price=Decimal("35.00"),
        stock=25,
    ),
    Book(
        title="Designing Data-Intensive Applications",
        author="Martin Kleppmann",
        description="Big data system architecture and concepts",
        price=Decimal("59.99"),
        stock=7,
    ),
    Book(
        title="Grokking Algorithms",
        author="Aditya Bhargava",
        description="An illustrated guide for programmers",
        price=Decimal("39.99"),
        stock=14,
    ),
    Book(
        title="Code Complete",
        author="Steve McConnell",
        description="A practical handbook of software construction",
        price=Decimal("52.00"),
        stock=6,
    ),
    Book(
        title="Effective Java",
        author="Joshua Bloch",
        description="Best practices for the Java platform",
        price=Decimal("48.99"),
        stock=11,
    ),
    Book(
        title="Domain-Driven Design",
        author="Eric Evans",
        description="Tackling complexity in the heart of software",
        price=Decimal("58.00"),
        stock=9,
    ),
    Book(
        title="The Clean Coder",
        author="Robert C. Martin",
        description="A code of conduct for professional programmers",
        price=Decimal("34.95"),
        stock=13,
    ),
    Book(
        title="Structure and Interpretation of Computer Programs",
        author="Harold Abelson",
        description="Computer science principles with Scheme",
        price=Decimal("65.00"),
        stock=4,
    ),
    Book(
        title="Working Effectively with Legacy Code",
        author="Michael Feathers",
        description="Strategies for modifying existing software",
        price=Decimal("46.99"),
        stock=10,
    ),
    Book(
        title="Site Reliability Engineering",
        author="Betsy Beyer",
        description="How Google runs production systems",
        price=Decimal("42.50"),
        stock=16,
    ),
    Book(
        title="Continuous Delivery",
        author="Jez Humble",
        description="Automated software delivery pipeline",
        price=Decimal("51.99"),
        stock=8,
    ),
    Book(
        title="Clean Architecture",
        author="Robert C. Martin",
        description="A craftsman's guide to software structure and design",
        price=Decimal("43.99"),
        stock=17,
    ),
    Book(
        title="The Phoenix Project",
        author="Gene Kim",
        description="A novel about IT, DevOps, and helping your business win",
        price=Decimal("26.99"),
        stock=22,
    ),
]


async def seed():
    engine = create_async_engine(DATABASE_URL)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

    async with SessionLocal() as session:
        session.add_all(books)
        await session.commit()
        print(f"Added {len(books)} books")

    await engine.dispose()


asyncio.run(seed())
