from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.repositories.book_repository import BookRepository


async def create_book_service(book_data: BookCreate, db: AsyncSession):
    repo = BookRepository(db)
    book = Book(**book_data.model_dump())
    existing_book = await repo.get_book_by_title_and_author(book.title, book.author)
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book is already registered in the system",
        )
    book = repo.create(book)
    await db.commit()
    await db.refresh(book)
    return book


async def get_books_service(db: AsyncSession):
    repo = BookRepository(db)
    return await repo.get_all()


async def get_book_by_id_service(book_id: int, db: AsyncSession):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)

    if not book:
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    update_data = book_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(book, key, value)

    await db.commit()
    await db.refresh(book)
    return book


async def delete_book_by_id_service(book_id: int, db: AsyncSession):
    repo = BookRepository(db)
    book = await repo.get_by_id(book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    await repo.delete(book)
    await db.commit()

    return {"detail": "The book has deleted"}


