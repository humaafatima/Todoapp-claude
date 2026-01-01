"""Database connection and session management."""

from contextlib import contextmanager
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from backend.src.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.log_level == "DEBUG",  # Log SQL queries in debug mode
)


def _configure_sqlite_pragmas() -> None:
    """Configure SQLite PRAGMA settings for better performance and consistency."""
    if "sqlite" in settings.database_url:
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.exec_driver_sql("PRAGMA foreign_keys=ON")  # Enable foreign keys
        except Exception:
            # Ignore errors if database doesn't exist yet (e.g., during testing)
            pass


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic commit/rollback.

    Usage:
        with get_session() as session:
            task = session.get(Task, task_id)
            task.title = "Updated"
            session.commit()

    Yields:
        Session: SQLModel database session
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables() -> None:
    """
    Create all database tables.

    This should be called once during application initialization or
    via the init-db CLI command.
    """
    _configure_sqlite_pragmas()  # Configure SQLite before creating tables
    SQLModel.metadata.create_all(engine)
