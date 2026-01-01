"""Unit tests for CRUD tool functions with multi-tenant isolation."""

import pytest
from unittest.mock import patch, MagicMock
from backend.src.tools.task_tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)
from backend.src.exceptions import TaskNotFoundError, ValidationError
from backend.src.models import Task


# Mock get_session to use test database
@pytest.fixture(autouse=True)
def mock_get_session(test_db_session):
    """Mock get_session to use test database session."""
    with patch("backend.src.tools.task_tools.get_session") as mock:
        mock.return_value.__enter__ = MagicMock(return_value=test_db_session)
        mock.return_value.__exit__ = MagicMock(return_value=False)
        yield mock


# ===== add_task tests =====

def test_add_task_success(test_user_id):
    """Test successful task creation."""
    result = add_task(
        user_id=test_user_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
    )

    assert result["status"] == "created"
    assert result["title"] == "Buy groceries"
    assert isinstance(result["task_id"], int)
    assert result["task_id"] > 0


def test_add_task_minimal(test_user_id):
    """Test task creation with minimal parameters."""
    result = add_task(user_id=test_user_id, title="Call dentist")

    assert result["status"] == "created"
    assert result["title"] == "Call dentist"


def test_add_task_empty_title(test_user_id):
    """Test add_task with empty title raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        add_task(user_id=test_user_id, title="")

    assert exc_info.value.field == "title"
    assert "cannot be empty" in str(exc_info.value)


def test_add_task_whitespace_title(test_user_id):
    """Test add_task with whitespace-only title raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        add_task(user_id=test_user_id, title="   ")

    assert exc_info.value.field == "title"


def test_add_task_empty_user_id():
    """Test add_task with empty user_id raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        add_task(user_id="", title="Test Task")

    assert exc_info.value.field == "user_id"


def test_add_task_title_too_long(test_user_id):
    """Test add_task with title exceeding 200 chars raises ValidationError."""
    long_title = "A" * 201

    with pytest.raises(ValidationError) as exc_info:
        add_task(user_id=test_user_id, title=long_title)

    assert exc_info.value.field == "title"
    assert "200 characters" in str(exc_info.value)


def test_add_task_description_too_long(test_user_id):
    """Test add_task with description exceeding 2000 chars raises ValidationError."""
    long_description = "A" * 2001

    with pytest.raises(ValidationError) as exc_info:
        add_task(user_id=test_user_id, title="Test", description=long_description)

    assert exc_info.value.field == "description"
    assert "2000 characters" in str(exc_info.value)


# ===== list_tasks tests =====

def test_list_tasks_empty(test_user_id):
    """Test list_tasks with no tasks returns empty list."""
    result = list_tasks(user_id=test_user_id)

    assert result == []


def test_list_tasks_all(test_user_id):
    """Test list_tasks returns all user's tasks."""
    # Create multiple tasks
    add_task(test_user_id, "Task 1")
    add_task(test_user_id, "Task 2", description="Description 2")
    add_task(test_user_id, "Task 3")

    result = list_tasks(user_id=test_user_id, status="all")

    assert len(result) == 3
    assert all(task["user_id"] == test_user_id for task in result)
    # Ordered by created_at DESC (newest first)
    assert result[0]["title"] == "Task 3"


def test_list_tasks_pending_only(test_user_id):
    """Test list_tasks with status='pending' filters correctly."""
    # Create tasks
    task1 = add_task(test_user_id, "Pending Task")
    task2 = add_task(test_user_id, "Another Pending")
    task3 = add_task(test_user_id, "Will Complete")

    # Complete one task
    complete_task(test_user_id, task3["task_id"])

    result = list_tasks(user_id=test_user_id, status="pending")

    assert len(result) == 2
    assert all(task["completed"] is False for task in result)


def test_list_tasks_completed_only(test_user_id):
    """Test list_tasks with status='completed' filters correctly."""
    # Create and complete tasks
    task1 = add_task(test_user_id, "Task 1")
    task2 = add_task(test_user_id, "Task 2")
    add_task(test_user_id, "Task 3")

    complete_task(test_user_id, task1["task_id"])
    complete_task(test_user_id, task2["task_id"])

    result = list_tasks(user_id=test_user_id, status="completed")

    assert len(result) == 2
    assert all(task["completed"] is True for task in result)


def test_list_tasks_invalid_status(test_user_id):
    """Test list_tasks with invalid status raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        list_tasks(user_id=test_user_id, status="invalid")

    assert exc_info.value.field == "status"


def test_list_tasks_empty_user_id():
    """Test list_tasks with empty user_id raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        list_tasks(user_id="")

    assert exc_info.value.field == "user_id"


# ===== CRITICAL: Multi-tenant isolation tests =====

def test_list_tasks_isolation(test_user_id, test_user_id_2):
    """CRITICAL: User A cannot see User B's tasks."""
    # User A creates tasks
    add_task(test_user_id, "User A Task 1")
    add_task(test_user_id, "User A Task 2")

    # User B creates tasks
    add_task(test_user_id_2, "User B Task 1")

    # User A lists tasks
    tasks_a = list_tasks(user_id=test_user_id)
    assert len(tasks_a) == 2
    assert all(task["user_id"] == test_user_id for task in tasks_a)

    # User B lists tasks
    tasks_b = list_tasks(user_id=test_user_id_2)
    assert len(tasks_b) == 1
    assert all(task["user_id"] == test_user_id_2 for task in tasks_b)

    # Verify no cross-contamination
    task_ids_a = [t["id"] for t in tasks_a]
    task_ids_b = [t["id"] for t in tasks_b]
    assert len(set(task_ids_a) & set(task_ids_b)) == 0


# ===== update_task tests =====

def test_update_task_title(test_user_id):
    """Test updating task title."""
    task = add_task(test_user_id, "Original Title")

    result = update_task(test_user_id, task["task_id"], title="Updated Title")

    assert result["status"] == "updated"
    assert result["title"] == "Updated Title"


def test_update_task_description(test_user_id):
    """Test updating task description."""
    task = add_task(test_user_id, "Task", description="Original")

    result = update_task(test_user_id, task["task_id"], description="Updated description")

    assert result["status"] == "updated"


def test_update_task_both_fields(test_user_id):
    """Test updating both title and description."""
    task = add_task(test_user_id, "Original", "Original desc")

    result = update_task(
        test_user_id,
        task["task_id"],
        title="New Title",
        description="New description",
    )

    assert result["status"] == "updated"
    assert result["title"] == "New Title"


def test_update_task_not_found(test_user_id):
    """Test update_task with non-existent task ID."""
    with pytest.raises(TaskNotFoundError) as exc_info:
        update_task(test_user_id, 99999, title="Won't work")

    assert exc_info.value.task_id == 99999
    assert exc_info.value.user_id == test_user_id


def test_update_task_isolation(test_user_id, test_user_id_2):
    """CRITICAL: User B cannot update User A's task."""
    # User A creates task
    task = add_task(test_user_id, "User A Task")

    # User B attempts to update
    with pytest.raises(TaskNotFoundError) as exc_info:
        update_task(test_user_id_2, task["task_id"], title="Hacked")

    # Verify task unchanged
    tasks = list_tasks(test_user_id)
    assert tasks[0]["title"] == "User A Task"


def test_update_task_no_fields(test_user_id):
    """Test update_task with no fields raises ValidationError."""
    task = add_task(test_user_id, "Task")

    with pytest.raises(ValidationError) as exc_info:
        update_task(test_user_id, task["task_id"])

    assert "at least one field" in str(exc_info.value).lower()


def test_update_task_empty_title(test_user_id):
    """Test update_task with empty title raises ValidationError."""
    task = add_task(test_user_id, "Task")

    with pytest.raises(ValidationError) as exc_info:
        update_task(test_user_id, task["task_id"], title="")

    assert exc_info.value.field == "title"


# ===== complete_task tests =====

def test_complete_task_success(test_user_id):
    """Test completing a task."""
    task = add_task(test_user_id, "Task to complete")

    result = complete_task(test_user_id, task["task_id"])

    assert result["status"] == "completed"
    assert result["task_id"] == task["task_id"]

    # Verify task is completed
    tasks = list_tasks(test_user_id, status="completed")
    assert len(tasks) == 1


def test_complete_task_idempotent(test_user_id):
    """Test completing an already completed task (idempotent)."""
    task = add_task(test_user_id, "Task")
    complete_task(test_user_id, task["task_id"])

    # Complete again - should not raise error
    result = complete_task(test_user_id, task["task_id"])

    assert result["status"] == "completed"


def test_complete_task_not_found(test_user_id):
    """Test complete_task with non-existent task ID."""
    with pytest.raises(TaskNotFoundError):
        complete_task(test_user_id, 99999)


def test_complete_task_isolation(test_user_id, test_user_id_2):
    """CRITICAL: User B cannot complete User A's task."""
    # User A creates task
    task = add_task(test_user_id, "User A Task")

    # User B attempts to complete
    with pytest.raises(TaskNotFoundError):
        complete_task(test_user_id_2, task["task_id"])

    # Verify task still pending
    tasks = list_tasks(test_user_id, status="pending")
    assert len(tasks) == 1


# ===== delete_task tests =====

def test_delete_task_success(test_user_id):
    """Test deleting a task."""
    task = add_task(test_user_id, "Task to delete")

    result = delete_task(test_user_id, task["task_id"])

    assert result["status"] == "deleted"
    assert result["task_id"] == task["task_id"]
    assert result["title"] == "Task to delete"

    # Verify task is gone
    tasks = list_tasks(test_user_id)
    assert len(tasks) == 0


def test_delete_task_not_idempotent(test_user_id):
    """Test deleting a task twice raises TaskNotFoundError."""
    task = add_task(test_user_id, "Task")
    delete_task(test_user_id, task["task_id"])

    # Second delete should fail
    with pytest.raises(TaskNotFoundError):
        delete_task(test_user_id, task["task_id"])


def test_delete_task_not_found(test_user_id):
    """Test delete_task with non-existent task ID."""
    with pytest.raises(TaskNotFoundError):
        delete_task(test_user_id, 99999)


def test_delete_task_isolation(test_user_id, test_user_id_2):
    """CRITICAL: User B cannot delete User A's task."""
    # User A creates task
    task = add_task(test_user_id, "Important Task")

    # User B attempts to delete
    with pytest.raises(TaskNotFoundError):
        delete_task(test_user_id_2, task["task_id"])

    # Verify task still exists for User A
    tasks = list_tasks(test_user_id)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Important Task"


def test_delete_task_invalid_task_id(test_user_id):
    """Test delete_task with invalid task_id type."""
    with pytest.raises(ValidationError) as exc_info:
        delete_task(test_user_id, "not_an_int")

    assert exc_info.value.field == "task_id"
