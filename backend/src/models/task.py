"""Task model for todo items with multi-tenant isolation."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Task model representing a todo item with multi-tenant isolation.

    All operations on this model MUST filter by user_id to prevent
    cross-tenant data access.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        index=True,
        nullable=False,
        max_length=255,
        description="User identifier for multi-tenant isolation",
    )
    title: str = Field(
        nullable=False,
        max_length=200,
        description="Task title",
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Task description",
    )
    completed: bool = Field(
        default=False,
        description="Completion status",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when task was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp when task was last modified",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "completed" if self.completed else "pending"
        return f"<Task id={self.id} user_id={self.user_id} title='{self.title}' status={status}>"

    def to_dict(self) -> dict:
        """Convert task to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
