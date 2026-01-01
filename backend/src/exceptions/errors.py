"""Custom exceptions for the Todo CRUD Agent."""


class TaskNotFoundError(ValueError):
    """Raised when a task doesn't exist or doesn't belong to the specified user."""

    def __init__(self, task_id: int, user_id: str):
        """
        Initialize TaskNotFoundError.

        Args:
            task_id: The task ID that wasn't found
            user_id: The user ID that attempted to access the task
        """
        self.task_id = task_id
        self.user_id = user_id
        super().__init__(f"Task {task_id} not found for user {user_id}")

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": "not_found",
            "task_id": self.task_id,
            "user_id": self.user_id,
            "message": str(self),
            "status_code": 404,
        }


class ValidationError(ValueError):
    """Raised when input parameters fail validation."""

    def __init__(self, field: str, message: str):
        """
        Initialize ValidationError.

        Args:
            field: The field that failed validation
            message: Description of the validation error
        """
        self.field = field
        self.validation_message = message
        super().__init__(f"Validation error on field '{field}': {message}")

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": "validation",
            "field": self.field,
            "message": self.validation_message,
            "status_code": 400,
        }


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, original_error: Exception):
        """
        Initialize DatabaseError.

        Args:
            operation: The database operation that failed (e.g., "create", "update")
            original_error: The underlying exception that caused the failure
        """
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Database {operation} operation failed: {str(original_error)}")

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": "database",
            "operation": self.operation,
            "message": str(self),
            "status_code": 500,
        }
