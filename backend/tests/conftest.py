"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from backend.src.models import Task


@pytest.fixture(scope="function")
def test_db_session():
    """
    Provide an in-memory SQLite database session for testing.

    This fixture creates a fresh database for each test function,
    ensuring test isolation.

    Yields:
        Session: SQLModel database session
    """
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    session = Session(engine)

    try:
        yield session
    finally:
        session.close()
        # Clean up
        SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_user_id():
    """Provide a test user ID."""
    return "test_user_123"


@pytest.fixture
def test_user_id_2():
    """Provide a second test user ID for multi-tenant tests."""
    return "test_user_456"


@pytest.fixture
def sample_task(test_db_session, test_user_id):
    """
    Create a sample task in the test database.

    Args:
        test_db_session: Test database session
        test_user_id: Test user identifier

    Returns:
        Task: Created task instance
    """
    task = Task(
        user_id=test_user_id,
        title="Sample Task",
        description="This is a test task",
        completed=False,
    )
    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)
    return task


@pytest.fixture
def completed_task(test_db_session, test_user_id):
    """
    Create a completed sample task in the test database.

    Args:
        test_db_session: Test database session
        test_user_id: Test user identifier

    Returns:
        Task: Created completed task instance
    """
    task = Task(
        user_id=test_user_id,
        title="Completed Task",
        description="This task is already done",
        completed=True,
    )
    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)
    return task
