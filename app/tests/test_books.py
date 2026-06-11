import pytest
from decimal import Decimal
from fastapi import HTTPException
from app.schemas.book import BookCreate, BookUpdate
from app.services.book_service import (
    create_book_service,
    get_books_service,
    get_book_by_id_service,
    update_book_by_id_service,
    delete_book_by_id_service,
)


@pytest.mark.asyncio
async def test_create_book_success(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    book = await create_book_service(book_data, db_session)

    assert book.id is not None
    assert book.title == book_data.title
    assert book.author == book_data.author
    assert book.price == book_data.price
    assert book.stock == book_data.stock


@pytest.mark.asyncio
async def test_create_book_fail(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    await create_book_service(book_data, db_session)

    with pytest.raises(HTTPException) as exc_info:
        await create_book_service(book_data, db_session)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "This book is already registered in the system"


@pytest.mark.asyncio
async def test_get_books_empty(db_session):
    books = await get_books_service(db_session)
    assert books == []


@pytest.mark.asyncio
async def test_get_books_success(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )
    await create_book_service(book_data, db_session)
    books = await get_books_service(db_session)
    assert len(books) == 1
    assert books[0].title == book_data.title
    assert books[0].author == book_data.author


@pytest.mark.asyncio
async def test_get_book_by_id_success(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    created_book = await create_book_service(book_data, db_session)

    book = await get_book_by_id_service(created_book.id, db_session)

    assert book.id == created_book.id
    assert book.title == created_book.title
    assert book.author == created_book.author


@pytest.mark.asyncio
async def test_get_book_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_book_by_id_service(999, db_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Book not found"


@pytest.mark.asyncio
async def test_update_book_by_id_success(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    book = await create_book_service(book_data, db_session)

    update_data = BookUpdate(
        price=Decimal("39.99"),
        stock=5,
    )

    updated_book = await update_book_by_id_service(book.id, update_data, db_session)
    assert updated_book.price == update_data.price
    assert updated_book.stock == update_data.stock


@pytest.mark.asyncio
async def test_update_book_by_id_not_found(db_session):
    update_data = BookUpdate(
        price=Decimal("39.99"),
        stock=5,
    )

    with pytest.raises(HTTPException) as exc_info:
        await update_book_by_id_service(999, update_data, db_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Book not found"


@pytest.mark.asyncio
async def test_delete_book_by_id_success(db_session):
    book_data = BookCreate(
        title="Clean Code",
        description="Programming book",
        author="Robert C. Martin",
        price=Decimal("49.99"),
        stock=10,
    )

    book = await create_book_service(book_data, db_session)

    await delete_book_by_id_service(book.id, db_session)

    with pytest.raises(HTTPException) as exc_info:
        await get_book_by_id_service(book.id, db_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Book not found"


@pytest.mark.asyncio
async def test_delete_book_by_id_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        await delete_book_by_id_service(999, db_session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Book not found"
