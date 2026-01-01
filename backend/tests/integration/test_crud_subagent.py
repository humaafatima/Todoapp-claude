"""Integration tests for CrudSubagent."""

import pytest
from unittest.mock import patch
from backend.src.agents import CrudSubagent
from backend.src.exceptions import TaskNotFoundError, ValidationError


# Mock get_session for all tests in this module
@pytest.fixture(autouse=True)
def mock_get_session(test_db_session):
    """Mock get_session to use test database session."""
    with patch("backend.src.tools.task_tools.get_session") as mock:
        mock.return_value.__enter__ = lambda self: test_db_session
        mock.return_value.__exit__ = lambda self, *args: False
        yield mock


def test_crud_subagent_initialization():
    """Test CrudSubagent can be initialized."""
    agent = CrudSubagent()

    assert agent is not None
    assert "CrudSubagent" in agent.system_prompt
    assert len(agent.get_tools()) == 5


def test_crud_subagent_system_prompt():
    """Test system prompt contains required elements."""
    agent = CrudSubagent()

    # Verify prompt contains key phrases from spec
    assert "CrudSubagent" in agent.system_prompt
    assert "Create, Read, Update, and Delete" in agent.system_prompt
    assert "user_id" in agent.system_prompt
    assert "add_task" in agent.system_prompt
    assert "list_tasks" in agent.system_prompt
    assert "update_task" in agent.system_prompt
    assert "complete_task" in agent.system_prompt
    assert "delete_task" in agent.system_prompt

    # Verify current date is injected
    assert "Current date:" in agent.system_prompt
    assert "2025" in agent.system_prompt  # Current year


def test_crud_subagent_get_tools():
    """Test get_tools returns all 5 tool definitions."""
    agent = CrudSubagent()
    tools = agent.get_tools()

    assert len(tools) == 5

    tool_names = [tool["function"]["name"] for tool in tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names
    assert "update_task" in tool_names
    assert "complete_task" in tool_names
    assert "delete_task" in tool_names


def test_crud_subagent_add_task(test_user_id):
    """Test CrudSubagent.add_task method."""
    agent = CrudSubagent()

    result = agent.add_task(user_id=test_user_id, title="Test Task")

    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert isinstance(result["task_id"], int)


def test_crud_subagent_list_tasks(test_user_id):
    """Test CrudSubagent.list_tasks method."""
    agent = CrudSubagent()

    # Create some tasks
    agent.add_task(test_user_id, "Task 1")
    agent.add_task(test_user_id, "Task 2")

    result = agent.list_tasks(user_id=test_user_id)

    assert len(result) == 2
    assert all(isinstance(task, dict) for task in result)


def test_crud_subagent_update_task(test_user_id):
    """Test CrudSubagent.update_task method."""
    agent = CrudSubagent()

    # Create task
    task = agent.add_task(test_user_id, "Original")

    # Update task
    result = agent.update_task(test_user_id, task["task_id"], title="Updated")

    assert result["status"] == "updated"
    assert result["title"] == "Updated"


def test_crud_subagent_complete_task(test_user_id):
    """Test CrudSubagent.complete_task method."""
    agent = CrudSubagent()

    # Create task
    task = agent.add_task(test_user_id, "To Complete")

    # Complete task
    result = agent.complete_task(test_user_id, task["task_id"])

    assert result["status"] == "completed"


def test_crud_subagent_delete_task(test_user_id):
    """Test CrudSubagent.delete_task method."""
    agent = CrudSubagent()

    # Create task
    task = agent.add_task(test_user_id, "To Delete")

    # Delete task
    result = agent.delete_task(test_user_id, task["task_id"])

    assert result["status"] == "deleted"
    assert result["title"] == "To Delete"


def test_crud_subagent_end_to_end_workflow(test_user_id):
    """Test complete CRUD workflow."""
    agent = CrudSubagent()

    # 1. Create task
    task = agent.add_task(
        test_user_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
    )
    assert task["status"] == "created"
    task_id = task["task_id"]

    # 2. List tasks (should have 1)
    tasks = agent.list_tasks(test_user_id)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy groceries"
    assert tasks[0]["completed"] is False

    # 3. Update task
    updated = agent.update_task(
        test_user_id,
        task_id,
        title="Buy organic groceries",
        description="Organic milk, free-range eggs, whole grain bread",
    )
    assert updated["status"] == "updated"
    assert updated["title"] == "Buy organic groceries"

    # 4. List pending tasks
    pending = agent.list_tasks(test_user_id, status="pending")
    assert len(pending) == 1

    # 5. Complete task
    completed = agent.complete_task(test_user_id, task_id)
    assert completed["status"] == "completed"

    # 6. List completed tasks
    completed_tasks = agent.list_tasks(test_user_id, status="completed")
    assert len(completed_tasks) == 1
    assert completed_tasks[0]["id"] == task_id

    # 7. List pending tasks (should be empty now)
    pending = agent.list_tasks(test_user_id, status="pending")
    assert len(pending) == 0

    # 8. Delete task
    deleted = agent.delete_task(test_user_id, task_id)
    assert deleted["status"] == "deleted"

    # 9. List all tasks (should be empty)
    all_tasks = agent.list_tasks(test_user_id)
    assert len(all_tasks) == 0


def test_crud_subagent_multi_tenant_isolation(test_user_id, test_user_id_2):
    """CRITICAL: Test multi-tenant isolation through CrudSubagent."""
    agent = CrudSubagent()

    # User A creates tasks
    task_a1 = agent.add_task(test_user_id, "User A Task 1")
    task_a2 = agent.add_task(test_user_id, "User A Task 2")

    # User B creates tasks
    task_b1 = agent.add_task(test_user_id_2, "User B Task 1")

    # User A lists their tasks
    tasks_a = agent.list_tasks(test_user_id)
    assert len(tasks_a) == 2
    assert all(t["user_id"] == test_user_id for t in tasks_a)

    # User B lists their tasks
    tasks_b = agent.list_tasks(test_user_id_2)
    assert len(tasks_b) == 1
    assert all(t["user_id"] == test_user_id_2 for t in tasks_b)

    # User B cannot update User A's task
    with pytest.raises(TaskNotFoundError):
        agent.update_task(test_user_id_2, task_a1["task_id"], title="Hacked")

    # User B cannot complete User A's task
    with pytest.raises(TaskNotFoundError):
        agent.complete_task(test_user_id_2, task_a1["task_id"])

    # User B cannot delete User A's task
    with pytest.raises(TaskNotFoundError):
        agent.delete_task(test_user_id_2, task_a1["task_id"])

    # Verify User A's tasks unchanged
    tasks_a_after = agent.list_tasks(test_user_id)
    assert len(tasks_a_after) == 2


def test_crud_subagent_error_handling(test_user_id):
    """Test CrudSubagent properly propagates errors."""
    agent = CrudSubagent()

    # ValidationError for empty title
    with pytest.raises(ValidationError) as exc_info:
        agent.add_task(test_user_id, title="")
    assert exc_info.value.field == "title"

    # TaskNotFoundError for non-existent task
    with pytest.raises(TaskNotFoundError) as exc_info:
        agent.update_task(test_user_id, 99999, title="Won't work")
    assert exc_info.value.task_id == 99999

    # ValidationError for invalid status
    with pytest.raises(ValidationError) as exc_info:
        agent.list_tasks(test_user_id, status="invalid")
    assert exc_info.value.field == "status"


def test_crud_subagent_repr():
    """Test CrudSubagent string representation."""
    agent = CrudSubagent()

    repr_str = repr(agent)
    assert "CrudSubagent" in repr_str
    assert "tools=5" in repr_str


def test_crud_subagent_reusability():
    """Test CrudSubagent is reusable across multiple users."""
    agent = CrudSubagent()

    # Use agent for multiple users
    user1_task = agent.add_task("user_001", "User 1 Task")
    user2_task = agent.add_task("user_002", "User 2 Task")
    user3_task = agent.add_task("user_003", "User 3 Task")

    # Verify each user's data is isolated
    assert len(agent.list_tasks("user_001")) == 1
    assert len(agent.list_tasks("user_002")) == 1
    assert len(agent.list_tasks("user_003")) == 1

    # Verify agent is stateless
    assert agent.list_tasks("user_001")[0]["title"] == "User 1 Task"
    assert agent.list_tasks("user_002")[0]["title"] == "User 2 Task"
    assert agent.list_tasks("user_003")[0]["title"] == "User 3 Task"
