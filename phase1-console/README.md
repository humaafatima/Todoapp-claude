# Phase 1: In-Memory Console Todo App

A simple, interactive command-line todo application with in-memory storage. This is Phase 1 of the Todo App project, demonstrating the 5 core CRUD operations without persistence.

## Features

- **Add Task**: Create new tasks with title and optional description
- **List Tasks**: View all tasks with completion status
- **Update Task**: Modify task title and/or description
- **Mark Complete**: Toggle task completion status
- **Delete Task**: Permanently remove tasks
- **In-Memory Storage**: All data stored in memory (lost on exit)

## Requirements

- Python 3.11 or higher
- No external dependencies (pure Python)

## Installation

No installation required! This is a standalone Python script.

```bash
# Navigate to the phase1-console directory
cd phase1-console
```

## Usage

### Starting the Application

```bash
python todo.py
```

### Menu Options

```
=== Todo App ===
1. Add Task
2. List Tasks
3. Update Task
4. Mark Complete
5. Delete Task
6. Exit
```

### Example Session

#### Adding Tasks
```
Enter your choice (1-6): 1
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
✓ Task added successfully! (ID: 1)

Enter your choice (1-6): 1
Enter task title: Call dentist
Enter description (optional):
✓ Task added successfully! (ID: 2)
```

#### Listing Tasks
```
Enter your choice (1-6): 2

=== Your Tasks ===
[1] ✗ Buy groceries
    Description: Milk, eggs, bread

[2] ✗ Call dentist

Total: 2 tasks (0 completed, 2 pending)
```

#### Marking Complete
```
Enter your choice (1-6): 4
Enter task ID: 1
✓ Task marked as complete: "Buy groceries"
```

#### Updating Tasks
```
Enter your choice (1-6): 3
Enter task ID: 2
Enter new title (press Enter to skip): Call dentist ASAP
Enter new description (press Enter to skip): Schedule appointment for next week
✓ Task updated successfully!
```

#### Deleting Tasks
```
Enter your choice (1-6): 5
Enter task ID: 1
✓ Task deleted: "Buy groceries"
```

## Project Structure

```
phase1-console/
├── task.py           # Task class definition
├── todo.py           # TodoApp class and main CLI loop
├── README.md         # This file
└── requirements.txt  # Empty (no dependencies)
```

## Features Detail

### Task Properties
- **ID**: Unique auto-incrementing identifier (starts at 1)
- **Title**: Required, cannot be empty
- **Description**: Optional text field
- **Completed**: Boolean status (default: False)

### Validation
- Empty task titles are rejected
- Invalid task IDs show "Task not found" error
- Invalid menu choices show helpful error messages
- All user inputs are validated before processing

### Data Storage
- Tasks stored in Python dictionary (in-memory)
- Task IDs never reused, even after deletion
- All data lost when application exits

## Limitations (By Design)

This is Phase 1, so it intentionally has these limitations:
- ❌ No data persistence (tasks lost on exit)
- ❌ No file or database storage
- ❌ No multi-user support
- ❌ No search or filter features
- ❌ No task priorities or due dates
- ❌ No categories or tags

These features will be added in later phases.

## Testing

### Manual Test Cases

1. **Add Task**
   - Add task with title only
   - Add task with title and description
   - Try adding task with empty title (should fail)

2. **List Tasks**
   - List when no tasks exist
   - List multiple tasks
   - List mixed completed/incomplete tasks

3. **Update Task**
   - Update title only
   - Update description only
   - Update both fields
   - Try updating with empty title (should fail)
   - Try updating non-existent task (should fail)

4. **Mark Complete**
   - Complete a pending task
   - Complete an already-completed task (should toggle to incomplete)
   - Try completing non-existent task (should fail)

5. **Delete Task**
   - Delete an existing task
   - Try deleting non-existent task (should fail)
   - Verify deleted task ID is not reused

6. **Menu**
   - Try invalid menu choice
   - Exit application (option 6)
   - Exit with Ctrl+C

## Error Handling

The application handles common errors gracefully:

- **Empty title**: "Task title cannot be empty"
- **Task not found**: "Task not found"
- **Invalid menu choice**: "Invalid choice. Please enter 1-6"
- **Invalid integer input**: "invalid literal for int()"
- **Nothing to update**: "Nothing to update"

All errors are displayed with a ✗ symbol for easy identification.

## Next Steps

Future phases will add:
- **Phase 2**: File-based persistence (JSON storage)
- **Phase 3**: SQLite database integration
- **Phase 4**: REST API with FastAPI
- **Phase 5**: Web frontend interface

## License

Part of the Todo App project. See main repository for license details.

## Support

For issues or questions about Phase 1:
1. Check the specification: `specs/phase1-console-app.md`
2. Review the code comments in `task.py` and `todo.py`
3. Verify Python version: `python --version` (requires 3.11+)

---

**Version**: 1.0.0
**Phase**: 1 (In-Memory Console)
**Status**: Complete
