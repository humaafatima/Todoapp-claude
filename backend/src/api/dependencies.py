"""FastAPI dependencies for database sessions and other shared resources."""

from typing import Generator
from sqlmodel import Session
from src.database.connection import engine


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database session management.

    Yields:
        Session: SQLModel database session

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    with Session(engine) as session:
        yield session
