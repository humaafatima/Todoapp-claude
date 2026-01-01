# Phase 1: In-Memory Python Console Todo App

## Purpose
A simple, interactive command-line todo application that demonstrates the 5 core CRUD operations using in-memory storage. This phase serves as a proof-of-concept for the basic todo app functionality before adding persistence and advanced features.

## Overview
Phase 1 is a standalone Python console application that allows users to manage their todo tasks through a text-based menu interface. All tasks are stored in memory and will be lost when the program exits.

## Location in Project
- Implementation: `phase1-console/`
  - `phase1-console/todo.py` - Main application with CLI loop
  - `phase1-console/task.py` - Task class definition
  - `phase1-console/README.md` - Usage instructions
- Spec reference: `specs/phase1-console-app.md`

## User Stories
- As a user, I want to add a new task with a title and optional description so I can track what I need to do.
- As a user, I want to view all my tasks so I can see what needs to be done.
- As a user, I want to update a task's title or description so I can correct or clarify my todos.
- As a user, I want to mark a task as complete so I can track my progress.
- As a user, I want to delete a task so I can remove items I no longer need.

## Core Features

### 1. Add Task
**Description**: Create a new task with a title and optional description.

**Requirements**:
- Task title is required (cannot be empty or whitespace-only)
- Description is optional (defaults to empty string)
- Each task gets a unique auto-incrementing ID
- Task is marked as incomplete by default
- Return confirmation with task ID

**Validation**:
- Empty title → Show error: "Task title cannot be empty"
- Whitespace-only title → Show error: "Task title cannot be empty"

### 2. List Tasks
**Description**: Display all tasks with their details.

**Requirements**:
- Show task ID, title, description (if present), and completion status
- Display tasks in order of creation (oldest first)
- Show clear indicator for completed vs incomplete tasks
- If no tasks exist, show "No tasks found"

**Display Format**:
```
[ID] [✓/✗] Title
    Description: <description>
```

### 3. Update Task
**Description**: Modify the title and/or description of an existing task.

**Requirements**:
- User specifies task ID
- User can update title, description, or both
- At least one field must be provided for update
- Cannot set title to empty/whitespace
- Return confirmation of what was updated

**Validation**:
- Task ID doesn't exist → Show error: "Task not found"
- Empty title → Show error: "Task title cannot be empty"
- No fields provided → Show error: "Nothing to update"

### 4. Mark as Complete
**Description**: Toggle a task's completion status.

**Requirements**:
- User specifies task ID
- If task is incomplete, mark it as complete
- If task is complete, mark it as incomplete (toggle behavior)
- Return confirmation with new status

**Validation**:
- Task ID doesn't exist → Show error: "Task not found"

### 5. Delete Task
**Description**: Permanently remove a task from the list.

**Requirements**:
- User specifies task ID
- Task is removed from memory
- Return confirmation of deletion
- Task IDs are NOT reused

**Validation**:
- Task ID doesn't exist → Show error: "Task not found"

## Technical Requirements

### Task Class
```python
class Task:
    """
    Represents a single todo task.

    Attributes:
        id (int): Unique task identifier
        title (str): Task title/summary
        description (str): Optional detailed description
        completed (bool): Completion status
    """
```

**Methods**:
- `__init__(self, id, title, description="")` - Initialize task
- `__repr__(self)` - String representation for debugging
- `to_dict(self)` - Convert to dictionary for display

### TodoApp Class
```python
class TodoApp:
    """
    In-memory todo application with CLI interface.

    Attributes:
        tasks (dict): Dictionary mapping task_id to Task objects
        next_id (int): Counter for generating unique task IDs
    """
```

**Methods**:
- `add_task(title, description="")` - Create new task
- `list_tasks()` - Display all tasks
- `update_task(task_id, title=None, description=None)` - Update task
- `complete_task(task_id)` - Toggle completion status
- `delete_task(task_id)` - Remove task
- `run()` - Main CLI loop

### CLI Menu Interface
The application should display an interactive menu:

```
=== Todo App ===
1. Add Task
2. List Tasks
3. Update Task
4. Mark Complete
5. Delete Task
6. Exit

Enter your choice (1-6):
```

### Storage
- **In-memory only**: Tasks stored in a Python dictionary
- **No persistence**: All data lost on exit
- **No external dependencies**: Pure Python 3.11+ only

## Example Interactions

### Example 1: Adding Tasks
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

### Example 2: Listing Tasks
```
Enter your choice (1-6): 2

=== Your Tasks ===
[1] ✗ Buy groceries
    Description: Milk, eggs, bread

[2] ✗ Call dentist

Total: 2 tasks (0 completed, 2 pending)
```

### Example 3: Marking Complete
```
Enter your choice (1-6): 4
Enter task ID: 1
✓ Task marked as complete: "Buy groceries"

Enter your choice (1-6): 2

=== Your Tasks ===
[1] ✓ Buy groceries
    Description: Milk, eggs, bread

[2] ✗ Call dentist

Total: 2 tasks (1 completed, 1 pending)
```

### Example 4: Updating Task
```
Enter your choice (1-6): 3
Enter task ID: 2
Enter new title (press Enter to skip): Call dentist ASAP
Enter new description (press Enter to skip): Schedule appointment for next week
✓ Task updated successfully!
```

### Example 5: Deleting Task
```
Enter your choice (1-6): 5
Enter task ID: 1
✓ Task deleted: "Buy groceries"

Enter your choice (1-6): 2

=== Your Tasks ===
[2] ✗ Call dentist ASAP
    Description: Schedule appointment for next week

Total: 1 task (0 completed, 1 pending)
```

### Example 6: Error Handling
```
Enter your choice (1-6): 1
Enter task title:
✗ Error: Task title cannot be empty

Enter your choice (1-6): 3
Enter task ID: 999
✗ Error: Task not found

Enter your choice (1-6): 7
✗ Error: Invalid choice. Please enter 1-6.
```

## Acceptance Criteria

### Feature Completeness
- [ ] All 5 CRUD operations are implemented and working
- [ ] Add Task: Creates task with title and optional description
- [ ] List Tasks: Displays all tasks with proper formatting
- [ ] Update Task: Modifies title and/or description
- [ ] Mark Complete: Toggles completion status (idempotent)
- [ ] Delete Task: Removes task permanently

### User Experience
- [ ] Menu is clear and easy to navigate
- [ ] All user inputs are validated
- [ ] Error messages are helpful and specific
- [ ] Success confirmations are shown for all operations
- [ ] Task list displays completion status clearly
- [ ] Empty list shows appropriate message

### Technical Requirements
- [ ] Pure Python 3.11+ (no external dependencies)
- [ ] In-memory storage using dictionary
- [ ] Task class with id, title, description, completed
- [ ] TodoApp class with all CRUD methods
- [ ] Clean separation: Task model vs TodoApp logic
- [ ] Proper error handling (task not found, validation errors)

### Code Quality
- [ ] Clean, readable code with clear function/method names
- [ ] Docstrings for classes and methods
- [ ] Input validation for all user inputs
- [ ] No crashes on invalid input
- [ ] Graceful exit on "Exit" option

### Testing
- [ ] Manual testing of all 5 operations
- [ ] Edge cases tested (empty inputs, invalid IDs, etc.)
- [ ] Toggle behavior verified (complete → incomplete → complete)
- [ ] Task ID uniqueness verified
- [ ] Multiple task operations work correctly

## Non-Goals (Out of Scope)
- ❌ Data persistence (no file/database storage)
- ❌ Multi-user support
- ❌ Authentication
- ❌ Search or filter functionality
- ❌ Task priorities or due dates
- ❌ Categories or tags
- ❌ Undo/redo functionality
- ❌ Import/export features
- ❌ GUI or web interface

## File Structure
```
phase1-console/
├── task.py           # Task class definition
├── todo.py           # TodoApp class and main() entry point
├── README.md         # Usage instructions
└── requirements.txt  # Empty (no dependencies)
```

## Success Metrics
- All 5 CRUD operations work without errors
- User can perform a complete workflow: add → list → update → complete → delete
- Invalid inputs are handled gracefully
- Code is clean and maintainable
- README provides clear usage instructions

## Next Steps (Future Phases)
- Phase 2: Add file-based persistence (JSON storage)
- Phase 3: Add SQLite database
- Phase 4: Add REST API
- Phase 5: Add web frontend

## References
- Python 3.11+ documentation: https://docs.python.org/3/
- Similar projects for inspiration (SimpleTask, todo.txt)

---

**Version**: 1.0.0
**Created**: 2025-12-31
**Status**: Ready for Implementation
