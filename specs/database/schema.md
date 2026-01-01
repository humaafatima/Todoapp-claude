# Database Schema Specification

## Overview
This document defines the database schema for the Todo App, with a focus on multi-tenant data isolation. The schema is designed to work with SQLite for local development and can be migrated to Neon PostgreSQL for production.

## Task Model

### Table: `tasks`

The `tasks` table stores all todo items with strict user-level isolation.

| Column      | Type     | Constraints                    | Description                                      |
|-------------|----------|--------------------------------|--------------------------------------------------|
| id          | INTEGER  | PRIMARY KEY, AUTO INCREMENT    | Unique task identifier                           |
| user_id     | VARCHAR  | NOT NULL, INDEX                | User identifier for multi-tenant isolation       |
| title       | VARCHAR  | NOT NULL, MAX LENGTH 200       | Task title/summary                               |
| description | TEXT     | DEFAULT '', MAX LENGTH 2000    | Optional detailed task description               |
| completed   | BOOLEAN  | NOT NULL, DEFAULT FALSE        | Task completion status                           |
| created_at  | DATETIME | NOT NULL, DEFAULT UTC NOW      | Timestamp when task was created                  |
| updated_at  | DATETIME | NOT NULL, DEFAULT UTC NOW      | Timestamp when task was last modified            |

### Indexes

**Primary Index:**
- `PRIMARY KEY (id)` - Fast lookup by task ID

**Secondary Indexes:**
- `INDEX idx_user_id (user_id)` - Essential for multi-tenant queries
- `INDEX idx_user_completed (user_id, completed)` - Optimizes filtered task lists
- `INDEX idx_user_created (user_id, created_at DESC)` - Optimizes chronological queries

### Constraints

**Field Validations:**
- `user_id`: Cannot be NULL or empty string; must match authenticated user
- `title`: Cannot be NULL or empty string; max 200 characters
- `description`: Optional; max 2000 characters
- `completed`: Boolean only (TRUE/FALSE)
- `created_at`: Automatically set on insert, immutable
- `updated_at`: Automatically updated on every modification

**Multi-Tenant Isolation:**
- Every query MUST include `WHERE user_id = ?` clause
- No foreign key to users table (managed by Better Auth externally)
- Task ownership cannot be transferred between users

## Multi-Tenant Data Isolation Strategy

### Row-Level Security via Application Layer

**Approach**: User ID Filtering on All Queries

Every database operation enforces tenant isolation by:
1. Accepting `user_id` as a required parameter in all tool functions
2. Including `WHERE user_id = ?` in every SELECT, UPDATE, DELETE query
3. Setting `user_id` field on INSERT operations
4. Raising `TaskNotFoundError` if task doesn't exist for the given user

**Example Query Pattern:**
```sql
-- Good: Enforces user isolation
SELECT * FROM tasks WHERE user_id = ? AND id = ?

-- Bad: Cross-tenant data leakage
SELECT * FROM tasks WHERE id = ?
```

**Validation Rules:**
- `add_task`: Must set user_id on new tasks
- `list_tasks`: Must filter by user_id
- `update_task`: Must verify user_id matches before update
- `complete_task`: Must verify user_id matches before update
- `delete_task`: Must verify user_id matches before delete

### Security Guarantees

- **No Cross-User Data Leakage**: User A cannot access, modify, or delete User B's tasks
- **Query Enforcement**: All database queries automatically filtered by user_id
- **Test Coverage**: Multi-tenant isolation tests verify no data leakage

## SQLModel Definition

### Python Implementation

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model representing a todo item with multi-tenant isolation.

    All operations on this model MUST filter by user_id to prevent
    cross-tenant data access.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User identifier for multi-tenant isolation")
    title: str = Field(nullable=False, max_length=200, description="Task title")
    description: str = Field(default="", max_length=2000, description="Task description")
    completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Task id={self.id} user_id={self.user_id} title='{self.title}' completed={self.completed}>"
```

### Field Details

**id** (Optional[int]):
- Auto-generated primary key
- None until record inserted into database
- Unique across all users globally

**user_id** (str):
- Required for every task
- Typically JWT subject or auth provider user ID
- Indexed for query performance
- Cannot be changed after creation

**title** (str):
- Required, cannot be empty
- Max 200 characters (display-friendly length)
- Trimmed of leading/trailing whitespace on validation

**description** (str):
- Optional, defaults to empty string
- Max 2000 characters (sufficient for detailed notes)
- Supports multiline text

**completed** (bool):
- Defaults to False (pending state)
- Toggle between pending/completed
- No "archived" or "deleted" states (use hard delete)

**created_at** (datetime):
- Automatically set on task creation
- Immutable (never updated)
- UTC timezone always

**updated_at** (datetime):
- Automatically set on task creation
- Updated on every modification (title, description, completed changes)
- UTC timezone always

## Database Initialization

### SQLite Setup (Development)

```python
from sqlmodel import create_engine, SQLModel
from backend.src.config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,  # "sqlite:///./data/todo.db"
    connect_args={"check_same_thread": False},  # Allow multi-threading
    echo=settings.LOG_LEVEL == "DEBUG"  # Log SQL in debug mode
)

# Enable WAL mode for better concurrency
with engine.connect() as conn:
    conn.exec_driver_sql("PRAGMA journal_mode=WAL")
    conn.exec_driver_sql("PRAGMA foreign_keys=ON")

# Create all tables
SQLModel.metadata.create_all(engine)
```

### Migration Strategy

**Development (SQLite)**:
- Use `SQLModel.metadata.create_all(engine)` for initial schema
- For schema changes, drop and recreate (acceptable for local dev)

**Production (Neon PostgreSQL - Future)**:
- Use Alembic for migrations
- Maintain backward compatibility
- Test migrations on staging before production

## Migration Path to PostgreSQL

### Differences to Address

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Auto-increment | `INTEGER PRIMARY KEY` | `SERIAL` or `IDENTITY` |
| Boolean | Integer (0/1) | Native BOOLEAN |
| Datetime | TEXT ISO8601 | Native TIMESTAMP |
| Concurrency | Limited (file-based) | Excellent (MVCC) |
| Full-text search | FTS5 extension | Native with GIN indexes |

### PostgreSQL-Specific Enhancements

**Row-Level Security (RLS)**:
```sql
-- Enable RLS on tasks table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own tasks
CREATE POLICY user_isolation_policy ON tasks
    USING (user_id = current_setting('app.current_user_id')::text);
```

**Composite Indexes**:
```sql
CREATE INDEX idx_user_completed ON tasks (user_id, completed);
CREATE INDEX idx_user_created ON tasks (user_id, created_at DESC);
```

### Connection String Migration

**SQLite**:
```env
DATABASE_URL=sqlite:///./data/todo.db
```

**Neon PostgreSQL**:
```env
DATABASE_URL=postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/todo_db?sslmode=require
```

## Schema Versioning

### Version Tracking Table

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Initial version
INSERT INTO schema_version (version, description) VALUES (1, 'Initial schema with tasks table');
```

## Query Performance Considerations

### Expected Query Patterns

1. **List user's tasks** (most common):
   ```sql
   SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC;
   ```
   - Uses `idx_user_created` index
   - Expected rows: 10-1000 per user
   - Target p95: <100ms

2. **List user's pending tasks**:
   ```sql
   SELECT * FROM tasks WHERE user_id = ? AND completed = FALSE ORDER BY created_at DESC;
   ```
   - Uses `idx_user_completed` index
   - Expected rows: 5-500 per user
   - Target p95: <50ms

3. **Get specific task**:
   ```sql
   SELECT * FROM tasks WHERE user_id = ? AND id = ?;
   ```
   - Uses primary key + user_id filter
   - Expected rows: 0 or 1
   - Target p95: <10ms

4. **Update task**:
   ```sql
   UPDATE tasks SET title = ?, updated_at = ? WHERE user_id = ? AND id = ?;
   ```
   - Uses primary key + user_id filter
   - Target p95: <20ms

### Scaling Considerations

**SQLite Limits**:
- Max database size: 140 TB (practical limit much lower)
- Max concurrent writers: 1 (locks entire DB)
- Suitable for: <10 concurrent users, <100k tasks total

**When to Migrate to PostgreSQL**:
- More than 10 concurrent users
- Write-heavy workload (many updates per second)
- Need for advanced features (full-text search, JSON queries)
- Geographic distribution (read replicas)

## Data Retention and Archival

### Current Approach
- **Hard deletes**: Deleted tasks are permanently removed
- **No soft deletes**: No `deleted_at` field or `is_deleted` flag
- **No audit log**: Task history not preserved

### Future Enhancements
- Soft delete with `deleted_at` field
- Audit log table for task history
- Retention policy (auto-delete after N days)
- Export functionality (JSON, CSV)

## Testing Strategy

### Database Test Fixtures

```python
# conftest.py
import pytest
from sqlmodel import Session, create_engine, SQLModel

@pytest.fixture
def test_db_session():
    """In-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_user_id():
    return "test_user_123"

@pytest.fixture
def sample_task(test_db_session, test_user_id):
    task = Task(user_id=test_user_id, title="Sample Task", description="Test description")
    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)
    return task
```

### Multi-Tenant Isolation Tests

**Critical Test Cases**:
1. User A creates task → User B cannot list it
2. User A creates task → User B cannot update it
3. User A creates task → User B cannot complete it
4. User A creates task → User B cannot delete it
5. Direct query without user_id filter raises error

## References

- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Neon PostgreSQL**: https://neon.tech/docs
- **Better Auth**: https://www.better-auth.com/ (user authentication)
- **Related Specs**:
  - `@specs/agents/crud-subagent.md` - CRUD subagent implementation
  - `@specs/api/mcp-tools.md` - MCP tool signatures
