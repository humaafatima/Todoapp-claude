"""Task REST API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from pydantic import BaseModel, Field

from src.api.dependencies import get_db
from src.auth.middleware import get_current_user
from src.services.task_service import TaskService
from src.exceptions.errors import TaskNotFoundError, ValidationError, DatabaseError

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Request/Response Schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=2000, description="Task description")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: str | None = Field(None, min_length=1, max_length=200, description="New task title")
    description: str | None = Field(None, max_length=2000, description="New task description")


# Endpoints
@router.get("", summary="List all tasks")
async def list_tasks(
    status_filter: Annotated[str, Query(alias="status", pattern="^(all|pending|completed)$")] = "all",
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Retrieve a list of tasks for the authenticated user.

    Args:
        status_filter: Filter by completion status (all/pending/completed)
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        JSON with tasks array, total count, and applied filter
    """
    try:
        tasks = TaskService.list_tasks(db, user_id, status_filter)
        return {
            "tasks": tasks,
            "total": len(tasks),
            "filter": status_filter
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(
    data: TaskCreate,
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Create a new task for the authenticated user.

    Args:
        data: Task creation data (title and optional description)
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        JSON with task_id, status, and title
    """
    try:
        result = TaskService.create_task(db, user_id, data.title, data.description)
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )


@router.get("/{task_id}", summary="Get a single task")
async def get_task(
    task_id: int,
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Retrieve a single task by ID.

    Args:
        task_id: Task identifier
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        Task dictionary with all fields
    """
    try:
        task = TaskService.get_task(db, user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "not_found",
                    "task_id": task_id,
                    "message": f"Task {task_id} not found for user {user_id}"
                }
            )
        return task
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )


@router.put("/{task_id}", summary="Update a task")
async def update_task(
    task_id: int,
    data: TaskUpdate,
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Update one or more fields of an existing task.

    Args:
        task_id: Task identifier
        data: Fields to update (title and/or description)
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        JSON with task_id, status, and title
    """
    try:
        result = TaskService.update_task(db, user_id, task_id, data.title, data.description)
        return result
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )


@router.patch("/{task_id}/complete", summary="Toggle task completion")
async def toggle_complete(
    task_id: int,
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Toggle the completion status of a task.

    Args:
        task_id: Task identifier
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        JSON with task_id, status, and title
    """
    try:
        result = TaskService.toggle_complete(db, user_id, task_id)
        return result
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )


@router.delete("/{task_id}", summary="Delete a task")
async def delete_task(
    task_id: int,
    user_id: Annotated[str, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None
):
    """
    Permanently delete a task (hard delete with no recovery).

    Args:
        task_id: Task identifier
        user_id: Extracted from JWT token
        db: Database session

    Returns:
        JSON with success message, task_id, and title
    """
    try:
        result = TaskService.delete_task(db, user_id, task_id)
        return {
            "message": "Task deleted successfully",
            "task_id": result["task_id"],
            "title": result["title"]
        }
    except TaskNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
