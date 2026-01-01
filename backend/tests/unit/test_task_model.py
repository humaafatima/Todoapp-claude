"""Unit tests for Task model."""

from datetime import datetime
from backend.src.models import Task


def test_task_creation():
    """Test creating a Task instance."""
    task = Task(
        user_id="user_123",
        title="Test Task",
        description="Test description",
    )

    assert task.user_id == "user_123"
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.completed is False  # Default value
    assert task.id is None  # Not yet in database


def test_task_defaults():
    """Test Task default values."""
    task = Task(user_id="user_123", title="Minimal Task")

    assert task.description == ""  # Default empty string
    assert task.completed is False  # Default False
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_repr():
    """Test Task string representation."""
    task = Task(
        id=1,
        user_id="user_123",
        title="Test Task",
        completed=False,
    )

    repr_str = repr(task)
    assert "Task" in repr_str
    assert "id=1" in repr_str
    assert "user_id=user_123" in repr_str
    assert "status=pending" in repr_str


def test_task_to_dict():
    """Test Task to_dict method."""
    now = datetime.utcnow()
    task = Task(
        id=1,
        user_id="user_123",
        title="Test Task",
        description="Test description",
        completed=True,
        created_at=now,
        updated_at=now,
    )

    task_dict = task.to_dict()

    assert task_dict["id"] == 1
    assert task_dict["user_id"] == "user_123"
    assert task_dict["title"] == "Test Task"
    assert task_dict["description"] == "Test description"
    assert task_dict["completed"] is True
    assert task_dict["created_at"] == now.isoformat()
    assert task_dict["updated_at"] == now.isoformat()


def test_task_persistence(test_db_session):
    """Test Task can be saved to and retrieved from database."""
    # Create and save task
    task = Task(
        user_id="user_123",
        title="Persisted Task",
        description="This should persist",
    )
    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)

    # Verify ID was assigned
    assert task.id is not None

    # Verify timestamps were set
    assert task.created_at is not None
    assert task.updated_at is not None

    # Verify fields persisted correctly
    assert task.title == "Persisted Task"
    assert task.description == "This should persist"
    assert task.completed is False
