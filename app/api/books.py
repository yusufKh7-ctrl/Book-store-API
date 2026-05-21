from fastapi import APIRouter, Depends
from app.schemas.book import BookCreate, BookPublic
from app.services.book_service import (
    create_book_service,
    get_books_service,
    get_book_by_id_service,
    delete_book_by_id_service,
)
from app.core.dependencies import get_admin_user
from app.db.session import  SessionDep

router = APIRouter()

@router.post("", response_model=BookPublic)
async def create_book(
    book: BookCreate,
    db: SessionDep,
    user = Depends(get_admin_user)
):
    return await create_book_service(book, db)


@router.get("", response_model=list[BookPublic])
async def get_books(db: SessionDep):
    return await get_books_service(db)


@router.get("/{book_id}", response_model=BookPublic)
async def get_book_by_id(book_id: int, db: SessionDep):
    return await get_book_by_id_service(book_id, db)


@router.delete("/{book_id}", status_code=204)
async def delete_book_by_id(book_id: int, db: SessionDep, user = Depends(get_admin_user)):
    return await delete_book_by_id_service(book_id, db)