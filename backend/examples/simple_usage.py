"""
Simple usage examples for the CrudSubagent.

This script demonstrates how to use the CrudSubagent to perform
CRUD operations on todo tasks with multi-tenant isolation.

Prerequisites:
1. Database initialized: python -m backend.src.database.init_db
2. .env file configured with OPENAI_API_KEY (optional for direct tool usage)
"""

from backend.src.agents import CrudSubagent
from backend.src.exceptions import TaskNotFoundError, ValidationError


def example_basic_workflow():
    """
    Example 1: Basic CRUD workflow for a single user.
    """
    print("\n=== Example 1: Basic CRUD Workflow ===\n")

    agent = CrudSubagent()
    user_id = "demo_user_001"

    # 1. Create tasks
    print("1. Creating tasks...")
    task1 = agent.add_task(
        user_id=user_id,
        title="Buy groceries",
        description="Milk, eggs, bread, butter"
    )
    print(f"   Created: {task1}")

    task2 = agent.add_task(
        user_id=user_id,
        title="Call dentist",
        description="Schedule annual checkup"
    )
    print(f"   Created: {task2}")

    task3 = agent.add_task(
        user_id=user_id,
        title="Finish project report"
    )
    print(f"   Created: {task3}")

    # 2. List all tasks
    print("\n2. Listing all tasks...")
    all_tasks = agent.list_tasks(user_id=user_id)
    for task in all_tasks:
        status = "✓" if task["completed"] else "○"
        print(f"   {status} [{task['id']}] {task['title']}")

    # 3. Update a task
    print("\n3. Updating task...")
    updated = agent.update_task(
        user_id=user_id,
        task_id=task1["task_id"],
        title="Buy organic groceries",
        description="Organic milk, free-range eggs, whole grain bread"
    )
    print(f"   Updated: {updated}")

    # 4. Complete a task
    print("\n4. Completing task...")
    completed = agent.complete_task(user_id=user_id, task_id=task2["task_id"])
    print(f"   Completed: {completed}")

    # 5. List pending tasks only
    print("\n5. Listing pending tasks...")
    pending = agent.list_tasks(user_id=user_id, status="pending")
    for task in pending:
        print(f"   ○ [{task['id']}] {task['title']}")

    # 6. List completed tasks only
    print("\n6. Listing completed tasks...")
    completed_tasks = agent.list_tasks(user_id=user_id, status="completed")
    for task in completed_tasks:
        print(f"   ✓ [{task['id']}] {task['title']}")

    # 7. Delete a task
    print("\n7. Deleting task...")
    deleted = agent.delete_task(user_id=user_id, task_id=task3["task_id"])
    print(f"   Deleted: {deleted}")

    # 8. Final task list
    print("\n8. Final task list...")
    final_tasks = agent.list_tasks(user_id=user_id)
    for task in final_tasks:
        status = "✓" if task["completed"] else "○"
        print(f"   {status} [{task['id']}] {task['title']}")


def example_multi_tenant_isolation():
    """
    Example 2: Multi-tenant isolation demonstration.

    Shows that users cannot access each other's tasks.
    """
    print("\n=== Example 2: Multi-Tenant Isolation ===\n")

    agent = CrudSubagent()
    user_a = "alice_user_001"
    user_b = "bob_user_002"

    # User A creates tasks
    print("1. Alice creates her tasks...")
    task_a1 = agent.add_task(user_a, "Alice's personal task")
    task_a2 = agent.add_task(user_a, "Alice's work task")
    print(f"   Alice created 2 tasks")

    # User B creates tasks
    print("\n2. Bob creates his tasks...")
    task_b1 = agent.add_task(user_b, "Bob's personal task")
    print(f"   Bob created 1 task")

    # Each user sees only their own tasks
    print("\n3. Alice lists her tasks...")
    alice_tasks = agent.list_tasks(user_a)
    print(f"   Alice sees {len(alice_tasks)} tasks:")
    for task in alice_tasks:
        print(f"     - {task['title']}")

    print("\n4. Bob lists his tasks...")
    bob_tasks = agent.list_tasks(user_b)
    print(f"   Bob sees {len(bob_tasks)} tasks:")
    for task in bob_tasks:
        print(f"     - {task['title']}")

    # Bob cannot update Alice's task
    print("\n5. Bob attempts to update Alice's task...")
    try:
        agent.update_task(user_b, task_a1["task_id"], title="Bob's hack attempt")
        print("   ✗ SECURITY BREACH: Bob was able to update Alice's task!")
    except TaskNotFoundError:
        print("   ✓ Security enforced: Bob cannot update Alice's task")

    # Bob cannot delete Alice's task
    print("\n6. Bob attempts to delete Alice's task...")
    try:
        agent.delete_task(user_b, task_a1["task_id"])
        print("   ✗ SECURITY BREACH: Bob was able to delete Alice's task!")
    except TaskNotFoundError:
        print("   ✓ Security enforced: Bob cannot delete Alice's task")

    print("\n7. Verifying Alice's tasks are intact...")
    alice_tasks_after = agent.list_tasks(user_a)
    print(f"   Alice still has {len(alice_tasks_after)} tasks (unchanged)")


def example_error_handling():
    """
    Example 3: Error handling demonstration.
    """
    print("\n=== Example 3: Error Handling ===\n")

    agent = CrudSubagent()
    user_id = "error_demo_user"

    # Example 1: Empty title
    print("1. Attempting to create task with empty title...")
    try:
        agent.add_task(user_id, title="")
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e.validation_message}")
        print(f"   Field: {e.field}")

    # Example 2: Title too long
    print("\n2. Attempting to create task with title > 200 characters...")
    try:
        long_title = "A" * 201
        agent.add_task(user_id, title=long_title)
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e.validation_message}")

    # Example 3: Task not found
    print("\n3. Attempting to update non-existent task...")
    try:
        agent.update_task(user_id, task_id=99999, title="Won't work")
    except TaskNotFoundError as e:
        print(f"   ✓ Not found error caught: {e}")
        print(f"   Task ID: {e.task_id}, User ID: {e.user_id}")

    # Example 4: Invalid status filter
    print("\n4. Attempting to list tasks with invalid status...")
    try:
        agent.list_tasks(user_id, status="invalid_status")
    except ValidationError as e:
        print(f"   ✓ Validation error caught: {e.validation_message}")

    # Example 5: Delete non-idempotent
    print("\n5. Attempting to delete same task twice...")
    task = agent.add_task(user_id, "Task to delete")
    agent.delete_task(user_id, task["task_id"])
    print(f"   First delete: Success")
    try:
        agent.delete_task(user_id, task["task_id"])
        print(f"   Second delete: Unexpected success!")
    except TaskNotFoundError:
        print(f"   ✓ Second delete failed: Task already deleted (not idempotent)")


def example_direct_tool_usage():
    """
    Example 4: Using tools directly without CrudSubagent class.
    """
    print("\n=== Example 4: Direct Tool Usage ===\n")

    from backend.src.tools.task_tools import (
        add_task,
        list_tasks,
        update_task,
        complete_task,
        delete_task,
    )

    user_id = "direct_tool_user"

    print("1. Creating task with add_task function...")
    task = add_task(user_id, "Direct tool task")
    print(f"   Created: {task}")

    print("\n2. Listing tasks with list_tasks function...")
    tasks = list_tasks(user_id)
    print(f"   Found {len(tasks)} tasks")

    print("\n3. Updating task with update_task function...")
    updated = update_task(user_id, task["task_id"], title="Updated direct task")
    print(f"   Updated: {updated}")

    print("\n4. Completing task with complete_task function...")
    completed = complete_task(user_id, task["task_id"])
    print(f"   Completed: {completed}")

    print("\n5. Deleting task with delete_task function...")
    deleted = delete_task(user_id, task["task_id"])
    print(f"   Deleted: {deleted}")


def main():
    """Run all examples."""
    print("=" * 70)
    print("CrudSubagent Usage Examples")
    print("=" * 70)

    try:
        example_basic_workflow()
        example_multi_tenant_isolation()
        example_error_handling()
        example_direct_tool_usage()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
