"""Task model for Phase 1 in-memory todo app."""


class Task:
    """
    Represents a single todo task.

    Attributes:
        id (int): Unique task identifier
        title (str): Task title/summary
        description (str): Optional detailed description
        completed (bool): Completion status
    """

    def __init__(self, task_id: int, title: str, description: str = ""):
        """
        Initialize a new task.

        Args:
            task_id: Unique identifier for the task
            title: Task title (required)
            description: Optional detailed description (default: "")
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = False

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "completed" if self.completed else "pending"
        return f"<Task id={self.id} title='{self.title}' status={status}>"

    def to_dict(self) -> dict:
        """
        Convert task to dictionary.

        Returns:
            dict: Task data as dictionary
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
        }
