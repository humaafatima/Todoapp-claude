"""MCP tool implementations for task CRUD operations."""

from datetime import datetime
from typing import Optional
from sqlmodel import select
from backend.src.models import Task
from backend.src.database import get_session
from backend.src.exceptions import TaskNotFoundError, ValidationError, DatabaseError


def add_task(user_id: str, title: str, description: str = "") -> dict:
    """
    Create a new todo task for the authenticated user.

    Args:
        user_id: User identifier for task ownership (required)
        title: Task title/summary (required, max 200 chars)
        description: Optional detailed task description (max 2000 chars)

    Returns:
        dict: {"task_id": int, "status": "created", "title": str}

    Raises:
        ValidationError: If validation fails (empty title, invalid lengths)
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValidationError("user_id", "User ID is required")

    if not title or not title.strip():
        raise ValidationError("title", "Task title cannot be empty")

    title = title.strip()
    if len(title) > 200:
        raise ValidationError("title", "Task title must be 200 characters or less")

    if len(description) > 2000:
        raise ValidationError("description", "Description must be 2000 characters or less")

    # Create task
    try:
        with get_session() as session:
            task = Task(
                user_id=user_id.strip(),
                title=title,
                description=description.strip(),
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
    except Exception as e:
        if isinstance(e, (ValidationError, TaskNotFoundError)):
            raise
        raise DatabaseError("create", e)


def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """
    Retrieve a list of tasks for the authenticated user.

    Args:
        user_id: User identifier for filtering (required)
        status: Filter by completion status: "all", "pending", or "completed" (default: "all")

    Returns:
        list[dict]: Array of task dictionaries with all fields

    Raises:
        ValidationError: If validation fails (invalid status value)
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValidationError("user_id", "User ID is required")

    allowed_statuses = ["all", "pending", "completed"]
    if status not in allowed_statuses:
        raise ValidationError(
            "status",
            f"Status must be one of: {', '.join(allowed_statuses)}",
        )

    # Query tasks
    try:
        with get_session() as session:
            # Build query with user_id filter (CRITICAL for multi-tenant isolation)
            query = select(Task).where(Task.user_id == user_id.strip())

            # Apply status filter
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Order by creation date (newest first)
            query = query.order_by(Task.created_at.desc())

            tasks = session.exec(query).all()

            # Convert to dictionaries
            return [task.to_dict() for task in tasks]
    except Exception as e:
        if isinstance(e, (ValidationError, TaskNotFoundError)):
            raise
        raise DatabaseError("list", e)


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update one or more fields of an existing task.

    Args:
        user_id: User identifier for authorization (required)
        task_id: ID of task to update (required)
        title: New task title (optional, max 200 chars)
        description: New task description (optional, max 2000 chars)

    Returns:
        dict: {"task_id": int, "status": "updated", "title": str}

    Raises:
        ValidationError: If validation fails
        TaskNotFoundError: If task doesn't exist for user
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValidationError("user_id", "User ID is required")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValidationError("task_id", "Task ID must be a positive integer")

    if title is None and description is None:
        raise ValidationError(
            "fields",
            "At least one field (title or description) is required",
        )

    if title is not None:
        title = title.strip()
        if not title:
            raise ValidationError("title", "Task title cannot be empty")
        if len(title) > 200:
            raise ValidationError("title", "Task title must be 200 characters or less")

    if description is not None and len(description) > 2000:
        raise ValidationError("description", "Description must be 2000 characters or less")

    # Update task
    try:
        with get_session() as session:
            # Fetch task with user_id filter (CRITICAL for multi-tenant isolation)
            query = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(query).first()

            if not task:
                raise TaskNotFoundError(task_id, user_id)

            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description.strip()

            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
            }
    except Exception as e:
        if isinstance(e, (ValidationError, TaskNotFoundError)):
            raise
        raise DatabaseError("update", e)


def complete_task(user_id: str, task_id: int) -> dict:
    """
    Mark a task as completed. Idempotent operation.

    Args:
        user_id: User identifier for authorization (required)
        task_id: ID of task to complete (required)

    Returns:
        dict: {"task_id": int, "status": "completed", "title": str}

    Raises:
        ValidationError: If validation fails
        TaskNotFoundError: If task doesn't exist for user
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValidationError("user_id", "User ID is required")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValidationError("task_id", "Task ID must be a positive integer")

    # Complete task
    try:
        with get_session() as session:
            # Fetch task with user_id filter (CRITICAL for multi-tenant isolation)
            query = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(query).first()

            if not task:
                raise TaskNotFoundError(task_id, user_id)

            # Set completed=True (idempotent)
            task.completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title,
            }
    except Exception as e:
        if isinstance(e, (ValidationError, TaskNotFoundError)):
            raise
        raise DatabaseError("complete", e)


def delete_task(user_id: str, task_id: int) -> dict:
    """
    Permanently delete a task. This is a hard delete with no recovery.

    Args:
        user_id: User identifier for authorization (required)
        task_id: ID of task to delete (required)

    Returns:
        dict: {"task_id": int, "status": "deleted", "title": str}

    Raises:
        ValidationError: If validation fails
        TaskNotFoundError: If task doesn't exist for user
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not user_id or not user_id.strip():
        raise ValidationError("user_id", "User ID is required")

    if not isinstance(task_id, int) or task_id <= 0:
        raise ValidationError("task_id", "Task ID must be a positive integer")

    # Delete task
    try:
        with get_session() as session:
            # Fetch task with user_id filter (CRITICAL for multi-tenant isolation)
            query = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id.strip(),
            )
            task = session.exec(query).first()

            if not task:
                raise TaskNotFoundError(task_id, user_id)

            # Store task details before deletion
            task_info = {
                "task_id": task.id,
                "status": "deleted",
                "title": task.title,
            }

            # Hard delete
            session.delete(task)
            session.commit()

            return task_info
    except Exception as e:
        if isinstance(e, (ValidationError, TaskNotFoundError)):
            raise
        raise DatabaseError("delete", e)
