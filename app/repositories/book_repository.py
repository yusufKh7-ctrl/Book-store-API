from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.book import Book


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_by_id(self, book_id: int):
        return await self.db.get(Book, book_id)
    
    def create(self, book: Book):
        self.db.add(book)
        return book
        
    async def get_all(self):
        result = await self.db.execute(select(Book))
        return result.scalars().all()
        
    
    async def delete(self, book: Book) -> None:
        await self.db.delete(book)
        
    def update_stock(self, book: Book):
        self.db.add(book)
        return book
    
    async def get_book_by_title_and_author(self, book_title: str, author: str):
        book = await self.db.execute(select(Book).where(Book.title == book_title, Book.author == author))
        return book