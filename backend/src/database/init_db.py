"""Database initialization script."""

import sys
from pathlib import Path
from backend.src.database.connection import create_tables, engine
from backend.src.config import get_settings


def init_db() -> None:
    """Initialize the database by creating all tables."""
    settings = get_settings()

    print(f"Initializing database: {settings.database_url}")

    # Create data directory if using SQLite
    if "sqlite" in settings.database_url:
        db_path = settings.database_url.replace("sqlite:///", "").replace("sqlite://", "")
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"Database file location: {db_file.absolute()}")

    # Create all tables
    create_tables()
    print("✓ Database tables created successfully")

    # Verify tables were created
    with engine.connect() as conn:
        if "sqlite" in settings.database_url:
            result = conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
            )
            tables = result.fetchall()
            if tables:
                print(f"✓ Verified table exists: tasks")
            else:
                print("✗ Warning: tasks table not found")
        else:
            # PostgreSQL verification
            result = conn.exec_driver_sql(
                "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='tasks'"
            )
            tables = result.fetchall()
            if tables:
                print(f"✓ Verified table exists: tasks")
            else:
                print("✗ Warning: tasks table not found")

    print("\nDatabase initialization complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env: cp .env.example .env")
    print("2. Add your OpenAI API key to .env")
    print("3. Run tests: pytest")


def main() -> None:
    """CLI entry point for database initialization."""
    try:
        init_db()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Database initialization failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
