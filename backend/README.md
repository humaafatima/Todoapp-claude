# Todo CRUD Agent Backend

A reusable, stateless subagent for performing CRUD operations on todo tasks with strict multi-tenant isolation.

## Features

- **5 Core CRUD Operations**: add_task, list_tasks, update_task, complete_task, delete_task
- **Multi-Tenant Isolation**: Strict user-level data isolation via `user_id` filtering
- **Reusable Architecture**: Can be imported and used by multiple orchestrator agents
- **Structured Responses**: Returns JSON data only, no natural language generation
- **OpenAI Integration**: Compatible with OpenAI Agents SDK
- **Type-Safe**: Built with SQLModel and Pydantic for runtime validation
- **Comprehensive Tests**: >85% code coverage with multi-tenant isolation tests

## Tech Stack

- **Python**: 3.11+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Framework**: OpenAI SDK
- **Testing**: pytest with async support

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   │   └── task.py      # Task model with user_id
│   ├── agents/          # Agent implementations
│   │   └── crud_subagent.py  # CrudSubagent class
│   ├── tools/           # MCP tool implementations
│   │   └── task_tools.py     # 5 CRUD tool functions
│   ├── database/        # Database management
│   │   ├── connection.py     # Session factory
│   │   └── init_db.py        # Initialization script
│   ├── exceptions/      # Custom exceptions
│   │   └── errors.py         # TaskNotFoundError, etc.
│   └── config/          # Configuration
│       └── settings.py       # Environment settings
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── examples/
│   └── simple_usage.py       # Usage examples
├── docs/
│   └── api.md                # API documentation
├── pyproject.toml            # Project configuration
└── .env.example              # Environment template
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Setup Steps

1. **Clone the repository** (or navigate to the backend directory):
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .

   # Or for development (includes test dependencies):
   pip install -e ".[dev]"
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-proj-your-key-here
   ```

5. **Initialize the database**:
   ```bash
   python -m backend.src.database.init_db

   # Or use the CLI command:
   init-db
   ```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional (with defaults)
DATABASE_URL=sqlite:///./data/todo.db
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Getting an OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

**Note**: You need billing enabled on your OpenAI account to use the Agents SDK.

## Usage

### Direct Tool Usage

```python
from backend.src.tools.task_tools import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)

# Create a task
task = add_task(user_id="user_123", title="Buy groceries", description="Milk, eggs, bread")
# Returns: {"task_id": 1, "status": "created", "title": "Buy groceries"}

# List all tasks
tasks = list_tasks(user_id="user_123")
# Returns: [{"id": 1, "user_id": "user_123", "title": "Buy groceries", ...}]

# Update task
updated = update_task(user_id="user_123", task_id=1, title="Buy organic groceries")
# Returns: {"task_id": 1, "status": "updated", "title": "Buy organic groceries"}

# Complete task
completed = complete_task(user_id="user_123", task_id=1)
# Returns: {"task_id": 1, "status": "completed", "title": "Buy organic groceries"}

# Delete task
deleted = delete_task(user_id="user_123", task_id=1)
# Returns: {"task_id": 1, "status": "deleted", "title": "Buy organic groceries"}
```

### Using CrudSubagent

```python
from backend.src.agents import CrudSubagent

# Initialize the agent (reusable across requests)
agent = CrudSubagent()

# The agent provides direct access to all 5 tools
task = agent.add_task(user_id="user_123", title="Call dentist")
tasks = agent.list_tasks(user_id="user_123")
updated = agent.update_task(user_id="user_123", task_id=1, title="Call dentist ASAP")
completed = agent.complete_task(user_id="user_123", task_id=1)
deleted = agent.delete_task(user_id="user_123", task_id=1)
```

### Error Handling

```python
from backend.src.agents import CrudSubagent
from backend.src.exceptions import TaskNotFoundError, ValidationError

agent = CrudSubagent()

try:
    # Attempt to update non-existent task
    agent.update_task(user_id="user_123", task_id=99999, title="Won't work")
except TaskNotFoundError as e:
    print(f"Task not found: {e}")
    # Task not found: Task 99999 not found for user user_123

try:
    # Attempt to create task with empty title
    agent.add_task(user_id="user_123", title="")
except ValidationError as e:
    print(f"Validation error on {e.field}: {e.validation_message}")
    # Validation error on title: Task title cannot be empty
```

## Testing

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest backend/tests/unit/test_crud_tools.py

# Run tests matching a pattern
pytest -k "test_multi_tenant"

# Run with verbose output
pytest -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=backend.src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Critical Tests

The test suite includes critical multi-tenant isolation tests:

- **test_list_tasks_isolation**: Verify User A cannot see User B's tasks
- **test_update_task_isolation**: Verify User B cannot update User A's tasks
- **test_complete_task_isolation**: Verify User B cannot complete User A's tasks
- **test_delete_task_isolation**: Verify User B cannot delete User A's tasks

These tests MUST pass to ensure data security.

## Code Quality

### Format Code

```bash
# Format with Black
black backend/src backend/tests

# Lint with Ruff
ruff check backend/src backend/tests

# Type check with mypy
mypy backend/src
```

### Pre-commit Checks

Before committing, run:

```bash
black backend/src backend/tests
ruff check --fix backend/src backend/tests
pytest
```

## Database Management

### Initialize Database

```bash
python -m backend.src.database.init_db
```

### Reset Database

```bash
# Delete the database file
rm data/todo.db

# Reinitialize
python -m backend.src.database.init_db
```

### Inspect Database

```bash
# SQLite CLI
sqlite3 data/todo.db

# Show schema
.schema tasks

# Query tasks
SELECT * FROM tasks;

# Exit
.quit
```

## Migration to PostgreSQL

To migrate from SQLite to PostgreSQL (e.g., Neon):

1. **Update `.env`**:
   ```env
   DATABASE_URL=postgresql://user:password@host/database
   ```

2. **Initialize PostgreSQL database**:
   ```bash
   python -m backend.src.database.init_db
   ```

3. **Migrate data** (if needed):
   ```bash
   # Export from SQLite
   sqlite3 data/todo.db .dump > backup.sql

   # Import to PostgreSQL (manual migration required)
   ```

## API Reference

See [docs/api.md](docs/api.md) for detailed API documentation.

### Quick Reference

| Tool          | Parameters                                           | Returns                                   |
|---------------|------------------------------------------------------|-------------------------------------------|
| add_task      | user_id, title, description=""                       | {"task_id", "status": "created", "title"} |
| list_tasks    | user_id, status="all"                                | Array of task dicts                       |
| update_task   | user_id, task_id, title?, description?               | {"task_id", "status": "updated", "title"} |
| complete_task | user_id, task_id                                     | {"task_id", "status": "completed", "title"}|
| delete_task   | user_id, task_id                                     | {"task_id", "status": "deleted", "title"} |

## Architecture

### Multi-Tenant Isolation

Every database operation enforces tenant isolation by:

1. Accepting `user_id` as a required parameter
2. Filtering all queries with `WHERE user_id = ?`
3. Raising `TaskNotFoundError` if task doesn't exist for the user

**Example Query**:
```sql
-- Good: Enforces isolation
SELECT * FROM tasks WHERE user_id = ? AND id = ?

-- Bad: Security vulnerability
SELECT * FROM tasks WHERE id = ?
```

### Stateless Design

The CrudSubagent is stateless:
- No instance state between calls
- All state stored in database
- Reusable by multiple orchestrators
- Thread-safe (with proper database connection pooling)

## Troubleshooting

### "OPENAI_API_KEY is required"

**Problem**: The OpenAI API key is not configured.

**Solution**: Add your API key to `.env`:
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### "Failed to connect to database"

**Problem**: Database file doesn't exist or is inaccessible.

**Solution**: Initialize the database:
```bash
python -m backend.src.database.init_db
```

### "Task not found" errors

**Problem**: Attempting to access a task that doesn't exist or belongs to another user.

**Solution**:
- Verify the task ID exists
- Verify you're using the correct user_id
- Remember: tasks are isolated by user_id (multi-tenant design)

### Import errors

**Problem**: Cannot import backend modules.

**Solution**: Install the package in editable mode:
```bash
pip install -e .
```

## Contributing

### Development Setup

1. Install dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests before committing:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black backend/src backend/tests
   ruff check --fix backend/src backend/tests
   ```

### Adding New Features

1. Add spec to `specs/` directory
2. Implement feature in `backend/src/`
3. Add tests in `backend/tests/`
4. Update documentation
5. Run full test suite

## License

[Your License Here]

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the spec files in `specs/`

## References

- [Spec: CRUD Subagent](../specs/agents/crud-subagent.md)
- [Spec: Database Schema](../specs/database/schema.md)
- [Spec: MCP Tools API](../specs/api/mcp-tools.md)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
