# MCP Tools API Specification

## Overview
This document defines the Model Context Protocol (MCP) tool interface for the CrudSubagent. These tools provide structured CRUD operations on todo tasks with strict multi-tenant isolation.

All tools are designed to return structured JSON data only - no natural language responses. They are callable by the TodoOrchestratorAgent or other agents via MCP.

## Tool Signatures

### 1. add_task

Create a new todo task for the authenticated user.

**Signature:**
```python
def add_task(user_id: str, title: str, description: str = "") -> dict:
```

**Parameters:**

| Parameter   | Type   | Required | Constraints                    | Description                          |
|-------------|--------|----------|--------------------------------|--------------------------------------|
| user_id     | string | Yes      | Non-empty, max 255 chars       | User identifier for task ownership   |
| title       | string | Yes      | Non-empty, max 200 chars       | Task title/summary                   |
| description | string | No       | Max 2000 chars, default=""     | Optional detailed task description   |

**Returns:**
```json
{
  "task_id": 123,
  "status": "created",
  "title": "Buy groceries"
}
```

| Field   | Type    | Description                          |
|---------|---------|--------------------------------------|
| task_id | integer | Unique ID of the newly created task  |
| status  | string  | Always "created" for this operation  |
| title   | string  | Echo of the task title               |

**Errors:**

| Error Type        | Condition                    | HTTP Status | Message Example                            |
|-------------------|------------------------------|-------------|--------------------------------------------|
| ValidationError   | title is empty               | 400         | "Task title cannot be empty"               |
| ValidationError   | title exceeds 200 chars      | 400         | "Task title must be 200 characters or less"|
| ValidationError   | user_id is empty             | 400         | "User ID is required"                      |
| ValidationError   | description exceeds 2000     | 400         | "Description must be 2000 characters or less" |
| DatabaseError     | Database write fails         | 500         | "Failed to create task: {error_details}"   |

**Example Usage:**
```python
# Success case
result = add_task(user_id="user_123", title="Buy milk", description="2% milk from store")
# Returns: {"task_id": 45, "status": "created", "title": "Buy milk"}

# Minimal case
result = add_task(user_id="user_123", title="Call dentist")
# Returns: {"task_id": 46, "status": "created", "title": "Call dentist"}
```

**Business Rules:**
- New tasks always start with `completed=False`
- `created_at` and `updated_at` timestamps automatically set to current UTC time
- `user_id` determines ownership and cannot be changed later
- Empty or whitespace-only titles are invalid

---

### 2. list_tasks

Retrieve a list of tasks for the authenticated user, optionally filtered by completion status.

**Signature:**
```python
def list_tasks(user_id: str, status: str = "all") -> list[dict]:
```

**Parameters:**

| Parameter | Type   | Required | Allowed Values              | Description                              |
|-----------|--------|----------|-----------------------------|------------------------------------------|
| user_id   | string | Yes      | Non-empty, max 255 chars    | User identifier for filtering            |
| status    | string | No       | "all", "pending", "completed" | Filter by completion status, default="all" |

**Returns:**
```json
[
  {
    "id": 123,
    "user_id": "user_123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-30T10:30:00Z",
    "updated_at": "2025-12-30T10:30:00Z"
  },
  {
    "id": 124,
    "user_id": "user_123",
    "title": "Call dentist",
    "description": "",
    "completed": true,
    "created_at": "2025-12-29T14:20:00Z",
    "updated_at": "2025-12-30T09:15:00Z"
  }
]
```

| Field       | Type    | Description                                      |
|-------------|---------|--------------------------------------------------|
| id          | integer | Task ID                                          |
| user_id     | string  | User identifier (always matches request user_id) |
| title       | string  | Task title                                       |
| description | string  | Task description (empty string if not set)       |
| completed   | boolean | Completion status                                |
| created_at  | string  | ISO 8601 UTC timestamp of creation               |
| updated_at  | string  | ISO 8601 UTC timestamp of last modification      |

**Errors:**

| Error Type      | Condition                       | HTTP Status | Message Example                                     |
|-----------------|---------------------------------|-------------|-----------------------------------------------------|
| ValidationError | user_id is empty                | 400         | "User ID is required"                               |
| ValidationError | status not in allowed values    | 400         | "Status must be 'all', 'pending', or 'completed'"   |
| DatabaseError   | Database query fails            | 500         | "Failed to retrieve tasks: {error_details}"         |

**Example Usage:**
```python
# List all tasks
result = list_tasks(user_id="user_123")
# Returns: [{"id": 1, ...}, {"id": 2, ...}]

# List only pending tasks
result = list_tasks(user_id="user_123", status="pending")
# Returns: [{"id": 1, "completed": false, ...}]

# List only completed tasks
result = list_tasks(user_id="user_123", status="completed")
# Returns: [{"id": 5, "completed": true, ...}]

# No tasks for user
result = list_tasks(user_id="new_user_456")
# Returns: []
```

**Business Rules:**
- Results ordered by `created_at` DESC (newest first)
- Only returns tasks where `user_id` matches (multi-tenant isolation)
- Empty list returned if no matching tasks
- `status="all"` ignores the `completed` field
- `status="pending"` returns tasks with `completed=False`
- `status="completed"` returns tasks with `completed=True`

---

### 3. update_task

Update one or more fields of an existing task. Partial updates supported.

**Signature:**
```python
def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> dict:
```

**Parameters:**

| Parameter   | Type         | Required | Constraints                    | Description                              |
|-------------|--------------|----------|--------------------------------|------------------------------------------|
| user_id     | string       | Yes      | Non-empty, max 255 chars       | User identifier for authorization        |
| task_id     | integer      | Yes      | Positive integer               | ID of task to update                     |
| title       | string\|None | No       | If provided: non-empty, max 200 | New task title                           |
| description | string\|None | No       | If provided: max 2000 chars    | New task description                     |

**Returns:**
```json
{
  "task_id": 123,
  "status": "updated",
  "title": "Buy organic milk"
}
```

| Field   | Type    | Description                          |
|---------|---------|--------------------------------------|
| task_id | integer | ID of the updated task               |
| status  | string  | Always "updated" for this operation  |
| title   | string  | Current title after update           |

**Errors:**

| Error Type        | Condition                              | HTTP Status | Message Example                                      |
|-------------------|----------------------------------------|-------------|------------------------------------------------------|
| ValidationError   | user_id is empty                       | 400         | "User ID is required"                                |
| ValidationError   | task_id is not positive integer        | 400         | "Task ID must be a positive integer"                 |
| ValidationError   | No fields to update                    | 400         | "At least one field (title or description) required" |
| ValidationError   | title is empty string                  | 400         | "Task title cannot be empty"                         |
| ValidationError   | title exceeds 200 chars                | 400         | "Task title must be 200 characters or less"          |
| ValidationError   | description exceeds 2000 chars         | 400         | "Description must be 2000 characters or less"        |
| TaskNotFoundError | Task doesn't exist for user            | 404         | "Task 123 not found for user user_123"               |
| DatabaseError     | Database update fails                  | 500         | "Failed to update task: {error_details}"             |

**Example Usage:**
```python
# Update title only
result = update_task(user_id="user_123", task_id=45, title="Buy 2% milk")
# Returns: {"task_id": 45, "status": "updated", "title": "Buy 2% milk"}

# Update description only
result = update_task(user_id="user_123", task_id=45, description="From Whole Foods")
# Returns: {"task_id": 45, "status": "updated", "title": "Buy 2% milk"}

# Update both fields
result = update_task(
    user_id="user_123",
    task_id=45,
    title="Buy organic milk",
    description="2% from Whole Foods"
)
# Returns: {"task_id": 45, "status": "updated", "title": "Buy organic milk"}

# Task not found (wrong user)
result = update_task(user_id="user_456", task_id=45, title="Hack attempt")
# Raises: TaskNotFoundError("Task 45 not found for user user_456")
```

**Business Rules:**
- `updated_at` timestamp automatically updated
- At least one field (title or description) must be provided
- Partial updates supported - only provided fields are changed
- Cannot update `user_id`, `id`, `completed`, `created_at` via this tool
- User can only update their own tasks (verified via user_id)
- Setting description to empty string ("") is allowed (clears description)

---

### 4. complete_task

Mark a task as completed. Idempotent operation.

**Signature:**
```python
def complete_task(user_id: str, task_id: int) -> dict:
```

**Parameters:**

| Parameter | Type    | Required | Constraints              | Description                       |
|-----------|---------|----------|--------------------------|-----------------------------------|
| user_id   | string  | Yes      | Non-empty, max 255 chars | User identifier for authorization |
| task_id   | integer | Yes      | Positive integer         | ID of task to complete            |

**Returns:**
```json
{
  "task_id": 123,
  "status": "completed",
  "title": "Buy groceries"
}
```

| Field   | Type    | Description                            |
|---------|---------|----------------------------------------|
| task_id | integer | ID of the completed task               |
| status  | string  | Always "completed" for this operation  |
| title   | string  | Task title                             |

**Errors:**

| Error Type        | Condition                       | HTTP Status | Message Example                             |
|-------------------|---------------------------------|-------------|---------------------------------------------|
| ValidationError   | user_id is empty                | 400         | "User ID is required"                       |
| ValidationError   | task_id is not positive integer | 400         | "Task ID must be a positive integer"        |
| TaskNotFoundError | Task doesn't exist for user     | 404         | "Task 123 not found for user user_123"      |
| DatabaseError     | Database update fails           | 500         | "Failed to complete task: {error_details}"  |

**Example Usage:**
```python
# Complete a pending task
result = complete_task(user_id="user_123", task_id=45)
# Returns: {"task_id": 45, "status": "completed", "title": "Buy milk"}

# Complete an already completed task (idempotent)
result = complete_task(user_id="user_123", task_id=45)
# Returns: {"task_id": 45, "status": "completed", "title": "Buy milk"}

# Task not found (wrong user)
result = complete_task(user_id="user_456", task_id=45)
# Raises: TaskNotFoundError("Task 45 not found for user user_456")
```

**Business Rules:**
- Sets `completed=True` on the task
- `updated_at` timestamp automatically updated
- Idempotent - can mark already-completed tasks as completed without error
- User can only complete their own tasks (verified via user_id)
- No "uncomplete" operation - use `update_task` to modify `completed` field if needed (future)

---

### 5. delete_task

Permanently delete a task. This is a hard delete with no recovery.

**Signature:**
```python
def delete_task(user_id: str, task_id: int) -> dict:
```

**Parameters:**

| Parameter | Type    | Required | Constraints              | Description                       |
|-----------|---------|----------|--------------------------|-----------------------------------|
| user_id   | string  | Yes      | Non-empty, max 255 chars | User identifier for authorization |
| task_id   | integer | Yes      | Positive integer         | ID of task to delete              |

**Returns:**
```json
{
  "task_id": 123,
  "status": "deleted",
  "title": "Buy groceries"
}
```

| Field   | Type    | Description                          |
|---------|---------|--------------------------------------|
| task_id | integer | ID of the deleted task               |
| status  | string  | Always "deleted" for this operation  |
| title   | string  | Title of the task before deletion    |

**Errors:**

| Error Type        | Condition                       | HTTP Status | Message Example                            |
|-------------------|---------------------------------|-------------|-------------------------------------------|
| ValidationError   | user_id is empty                | 400         | "User ID is required"                     |
| ValidationError   | task_id is not positive integer | 400         | "Task ID must be a positive integer"      |
| TaskNotFoundError | Task doesn't exist for user     | 404         | "Task 123 not found for user user_123"    |
| DatabaseError     | Database delete fails           | 500         | "Failed to delete task: {error_details}"  |

**Example Usage:**
```python
# Delete a task
result = delete_task(user_id="user_123", task_id=45)
# Returns: {"task_id": 45, "status": "deleted", "title": "Buy milk"}

# Delete again (not idempotent)
result = delete_task(user_id="user_123", task_id=45)
# Raises: TaskNotFoundError("Task 45 not found for user user_123")

# Task not found (wrong user)
result = delete_task(user_id="user_456", task_id=45)
# Raises: TaskNotFoundError("Task 45 not found for user user_456")
```

**Business Rules:**
- Hard delete - task is permanently removed from database
- NOT idempotent - second delete attempt raises TaskNotFoundError
- User can only delete their own tasks (verified via user_id)
- No soft delete or "trash" functionality
- Returns task details before deletion (for confirmation/undo UI)

---

## Common Error Responses

### ValidationError

Raised when input parameters fail validation rules.

**Structure:**
```json
{
  "error": "validation",
  "field": "title",
  "message": "Task title cannot be empty",
  "status_code": 400
}
```

**Common Causes:**
- Empty required fields (user_id, title)
- Field exceeds max length (title > 200, description > 2000)
- Invalid enum values (status not in ["all", "pending", "completed"])
- Invalid types (task_id not integer)

---

### TaskNotFoundError

Raised when task doesn't exist or doesn't belong to the specified user.

**Structure:**
```json
{
  "error": "not_found",
  "task_id": 123,
  "user_id": "user_123",
  "message": "Task 123 not found for user user_123",
  "status_code": 404
}
```

**Common Causes:**
- Task ID doesn't exist in database
- Task belongs to different user (multi-tenant isolation)
- Task was already deleted

**Security Note:** Error message intentionally doesn't reveal whether task exists for a different user - always says "not found" to prevent information leakage.

---

### DatabaseError

Raised when underlying database operation fails.

**Structure:**
```json
{
  "error": "database",
  "operation": "update",
  "message": "Failed to update task: database locked",
  "status_code": 500
}
```

**Common Causes:**
- Database connection lost
- Database file locked (SQLite concurrency limit)
- Disk full
- Constraint violation (should be rare, caught by validation)

---

## Multi-Tenant Security Requirements

### Authorization Enforcement

Every tool MUST:
1. Accept `user_id` as first parameter
2. Filter all database queries by `WHERE user_id = ?`
3. Raise `TaskNotFoundError` if task exists but doesn't belong to user
4. Never return or modify tasks from other users

### Test Cases

**Critical Security Tests:**
```python
def test_list_tasks_isolation():
    """User A cannot see User B's tasks."""
    # User A creates task
    task_a = add_task(user_id="user_a", title="User A's task")

    # User B lists tasks
    tasks_b = list_tasks(user_id="user_b")

    # Assert User A's task not in User B's list
    assert len(tasks_b) == 0
    assert task_a["task_id"] not in [t["id"] for t in tasks_b]

def test_update_task_isolation():
    """User B cannot update User A's task."""
    # User A creates task
    task = add_task(user_id="user_a", title="Original")

    # User B attempts to update
    with pytest.raises(TaskNotFoundError):
        update_task(user_id="user_b", task_id=task["task_id"], title="Hacked")

def test_delete_task_isolation():
    """User B cannot delete User A's task."""
    # User A creates task
    task = add_task(user_id="user_a", title="Important")

    # User B attempts to delete
    with pytest.raises(TaskNotFoundError):
        delete_task(user_id="user_b", task_id=task["task_id"])

    # Verify task still exists for User A
    tasks = list_tasks(user_id="user_a")
    assert len(tasks) == 1
```

---

## OpenAI Agents SDK Integration

### Tool Registration

Tools are registered with the CrudSubagent using the OpenAI Agents SDK's `Tool` decorator:

```python
from openai_agents import Tool

@Tool(
    name="add_task",
    description="Create a new todo task for the authenticated user",
    parameters={
        "user_id": {
            "type": "string",
            "description": "User identifier",
            "required": True
        },
        "title": {
            "type": "string",
            "description": "Task title",
            "required": True
        },
        "description": {
            "type": "string",
            "description": "Optional task description",
            "required": False,
            "default": ""
        }
    }
)
def add_task(user_id: str, title: str, description: str = "") -> dict:
    # Implementation
    pass
```

### MCP Server Registration

Tools are exposed via MCP server for inter-agent communication:

```python
from mcp import MCPServer, Tool as MCPTool

mcp_server = MCPServer()

# Register each tool
mcp_server.register_tool(
    MCPTool(
        name="add_task",
        description="Create a new todo task",
        handler=add_task,
        parameters={...}
    )
)
```

---

## Performance Expectations

### Response Time Targets (p95)

| Tool         | Expected Rows | Target Latency | Notes                          |
|--------------|---------------|----------------|--------------------------------|
| add_task     | 1 INSERT      | <50ms          | Single write operation         |
| list_tasks   | 10-1000 rows  | <200ms         | Indexed query, ordered results |
| update_task  | 1 UPDATE      | <30ms          | Primary key + user_id lookup   |
| complete_task| 1 UPDATE      | <30ms          | Primary key + user_id lookup   |
| delete_task  | 1 DELETE      | <30ms          | Primary key + user_id lookup   |

### Optimization Strategies

**Database Indexes:**
- `idx_user_id` - Essential for multi-tenant queries
- `idx_user_completed` - Speeds up filtered lists
- `idx_user_created` - Optimizes chronological ordering

**Connection Pooling:**
- Reuse database connections across tool calls
- Limit pool size to SQLite concurrency limits (5-10 connections)

**Prepared Statements:**
- SQLModel automatically uses parameterized queries
- Prevents SQL injection, improves performance

---

## Version History

| Version | Date       | Changes                                          | Author |
|---------|------------|--------------------------------------------------|--------|
| 1.0     | 2025-12-30 | Initial specification for 5 core CRUD tools      | Claude |

---

## References

- **Spec**: `@specs/agents/crud-subagent.md` - CrudSubagent implementation details
- **Schema**: `@specs/database/schema.md` - Task model definition
- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **MCP Protocol**: https://modelcontextprotocol.io/
