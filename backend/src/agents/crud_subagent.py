"""CrudSubagent - Reusable subagent for task CRUD operations."""

from datetime import datetime
from typing import Callable
from openai import OpenAI
from backend.src.tools.task_tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)
from backend.src.config import get_settings

# System prompt exactly as specified in crud-subagent.md
CRUD_SYSTEM_PROMPT_TEMPLATE = """You are CrudSubagent, a precise and reliable subagent specialized in performing Create, Read, Update, and Delete operations on a user's personal todo tasks.

Rules:
- You are NOT responsible for generating natural language responses to the user. Only return the structured tool results.
- Always enforce data isolation: every operation must use the provided user_id and only affect that user's tasks.
- Validate all inputs strictly. If required fields are missing or invalid, return an error.
- Use the minimal number of tool calls necessary.
- You have access to these tools only:
  - add_task
  - list_tasks
  - update_task
  - complete_task
  - delete_task
- Never attempt to call any other tool or perform actions outside these five.

Current date: {current_date}"""


class CrudSubagent:
    """
    Reusable subagent for CRUD operations on todo tasks.

    This subagent encapsulates the 5 core MCP tools (add_task, list_tasks,
    update_task, complete_task, delete_task) and provides a clean interface
    for other agents to perform task operations.

    Features:
    - Stateless design (no instance state between calls)
    - Multi-tenant isolation (all operations require user_id)
    - Structured responses only (no natural language generation)
    - Reusable by multiple orchestrators

    Example usage:
        agent = CrudSubagent()
        result = agent.add_task(user_id="user_123", title="Buy milk")
        # Returns: {"task_id": 1, "status": "created", "title": "Buy milk"}
    """

    def __init__(self):
        """
        Initialize the CrudSubagent.

        The agent is stateless - all state is stored in the database.
        Configuration is loaded from environment variables via settings.
        """
        self.settings = get_settings()
        self._client: OpenAI | None = None
        self._tools = self._get_tool_definitions()

        # System prompt with current date injected
        self.system_prompt = CRUD_SYSTEM_PROMPT_TEMPLATE.format(
            current_date=datetime.now().strftime("%Y-%m-%d")
        )

    @property
    def client(self) -> OpenAI:
        """
        Lazy-load OpenAI client.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if self._client is None:
            if not self.settings.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required. Please set it in your .env file.\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def _get_tool_definitions(self) -> list[dict]:
        """
        Get OpenAI function calling tool definitions for all 5 CRUD tools.

        Returns:
            list[dict]: Tool definitions in OpenAI function calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new todo task for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for task ownership",
                            },
                            "title": {
                                "type": "string",
                                "description": "Task title/summary (max 200 chars)",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed task description (max 2000 chars)",
                            },
                        },
                        "required": ["user_id", "title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve a list of tasks for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for filtering",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by completion status (default: all)",
                            },
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update one or more fields of an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for authorization",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of task to update",
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional, max 200 chars)",
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional, max 2000 chars)",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed (idempotent)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for authorization",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of task to complete",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently delete a task (hard delete, no recovery)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User identifier for authorization",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "ID of task to delete",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
        ]

    def _get_tool_function(self, tool_name: str) -> Callable:
        """
        Get the actual tool function by name.

        Args:
            tool_name: Name of the tool (add_task, list_tasks, etc.)

        Returns:
            Callable: The tool function

        Raises:
            ValueError: If tool_name is not recognized
        """
        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "update_task": update_task,
            "complete_task": complete_task,
            "delete_task": delete_task,
        }
        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        return tool_map[tool_name]

    # Direct tool access methods (for use without OpenAI API)

    def add_task(self, user_id: str, title: str, description: str = "") -> dict:
        """Direct access to add_task tool."""
        return add_task(user_id, title, description)

    def list_tasks(self, user_id: str, status: str = "all") -> list[dict]:
        """Direct access to list_tasks tool."""
        return list_tasks(user_id, status)

    def update_task(
        self,
        user_id: str,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> dict:
        """Direct access to update_task tool."""
        return update_task(user_id, task_id, title, description)

    def complete_task(self, user_id: str, task_id: int) -> dict:
        """Direct access to complete_task tool."""
        return complete_task(user_id, task_id)

    def delete_task(self, user_id: str, task_id: int) -> dict:
        """Direct access to delete_task tool."""
        return delete_task(user_id, task_id)

    def get_tools(self) -> list[dict]:
        """
        Get all tool definitions for MCP server registration.

        Returns:
            list[dict]: Tool definitions in OpenAI function calling format
        """
        return self._tools

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CrudSubagent tools={len(self._tools)}>"
