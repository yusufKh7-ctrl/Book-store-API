from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.repositories.book_repository import BookRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


async def create_book_service(book_data: BookCreate, db: AsyncSession):
    repo = BookRepository(db)
    book = Book(**book_data.model_dump())
    existing_book = await repo.get_book_by_title_and_author(book.title, book.author)
    if existing_book:
        logger.warning(f"Book already exists: '{book.title}' by {book.author}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book is already registered in the system",
        )
    book = repo.create(book)
    await db.commit()
    await db.refresh(book)
    logger.info(f"Book created: '{book.title}' by {book.author} (id={book.id})")
    return book


async def get_books_service(db: AsyncSession, skip: int = 0, limit: int = 10):
    repo = BookRepository(db)
    return await repo.get_all(skip, limit)


async def get_book_by_id_service(book_id: int, db: AsyncSession):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)

    if not book:
        logger.warning(f"Book not found: id={book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


async def update_book_by_id_service(
    book_id: int, book_data: BookUpdate, db: AsyncSession
):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)
    if not book:
        logger.warning(f"Update failed - book not found: id={book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    update_data = book_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    logger.info(f"Book updated: id={book_id}")
    return book


async def delete_book_by_id_service(book_id: int, db: AsyncSession):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)

    if not book:
        logger.warning(f"Delete failed - book not found: id={book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    await repo.delete(book)
    await db.commit()
    logger.info(f"Book deleted: id={book_id}")
    return {"detail": "The book has been deleted"}


async def search_books_service(
    db: AsyncSession,
    title: str | None,
    author: str | None,
    skip: int = 0,
    limit: int = 10,
):
    repo = BookRepository(db)
    return await repo.search(title, author, skip, limit)
