class DomainError(Exception):
    """Base class for all domain-level errors."""


class BookNotFoundError(DomainError):
    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
        super().__init__(f"Book with ID {book_id} not found.")


class InsufficientStockError(DomainError):
    def __init__(self, book_id: int, book_title: str, requested: int, available: int):
        self.book_id, self.book_title = book_id, book_title
        self.requested, self.available = requested, available

        super().__init__(
            f"Quantity for '{book_title}' is not currently available. "
            f"Requested {requested}, but only {available} in stock."
        )
