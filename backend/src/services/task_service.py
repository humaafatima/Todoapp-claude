"""Task service layer - wraps CRUD tools with session management."""

from sqlmodel import Session
from src.tools import task_tools


class TaskService:
    """
    Service layer for task operations.

    This wraps the existing CRUD tools which manage their own database sessions.
    The session parameter is provided for future flexibility if we need to
    refactor tools to use injected sessions instead of creating their own.
    """

    @staticmethod
    def list_tasks(session: Session, user_id: str, status: str = "all") -> list[dict]:
        """
        List tasks for a user with optional status filter.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            status: Filter by status: "all", "pending", or "completed"

        Returns:
            List of task dictionaries
        """
        return task_tools.list_tasks(user_id, status)

    @staticmethod
    def create_task(session: Session, user_id: str, title: str, description: str = "") -> dict:
        """
        Create a new task.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            title: Task title
            description: Task description

        Returns:
            Dictionary with task_id, status, and title
        """
        return task_tools.add_task(user_id, title, description)

    @staticmethod
    def get_task(session: Session, user_id: str, task_id: int) -> dict | None:
        """
        Get a single task by ID.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            task_id: Task ID to retrieve

        Returns:
            Task dictionary if found, None otherwise
        """
        tasks = task_tools.list_tasks(user_id, "all")
        return next((t for t in tasks if t["id"] == task_id), None)

    @staticmethod
    def update_task(
        session: Session,
        user_id: str,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> dict:
        """
        Update task fields.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            Dictionary with task_id, status, and title
        """
        return task_tools.update_task(user_id, task_id, title, description)

    @staticmethod
    def toggle_complete(session: Session, user_id: str, task_id: int) -> dict:
        """
        Toggle task completion status.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            task_id: Task ID to toggle

        Returns:
            Dictionary with task_id, status, and title
        """
        return task_tools.complete_task(user_id, task_id)

    @staticmethod
    def delete_task(session: Session, user_id: str, task_id: int) -> dict:
        """
        Delete a task.

        Args:
            session: Database session (currently unused, for future refactoring)
            user_id: User identifier
            task_id: Task ID to delete

        Returns:
            Dictionary with task_id, status, and title
        """
        return task_tools.delete_task(user_id, task_id)
