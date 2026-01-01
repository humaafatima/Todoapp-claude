"""Simple test script to verify all CRUD operations work."""

from todo import TodoApp


def test_todo_app():
    """Test all CRUD operations."""
    print("Testing Phase 1 Todo App...\n")

    app = TodoApp()

    # Test 1: Add tasks
    print("TEST 1: Adding tasks")
    try:
        app.add_task("Buy groceries", "Milk, eggs, bread")
        app.add_task("Call dentist")
        app.add_task("Write report", "Q4 quarterly report")
        print("[PASS] Add tasks\n")
    except Exception as e:
        print(f"[FAIL] Add tasks - {e}\n")
        return False

    # Test 2: List tasks
    print("TEST 2: Listing tasks")
    try:
        app.list_tasks()
        print("[PASS] List tasks\n")
    except Exception as e:
        print(f"[FAIL] List tasks - {e}\n")
        return False

    # Test 3: Update task
    print("TEST 3: Updating task")
    try:
        app.update_task(2, title="Call dentist ASAP", description="Schedule for next week")
        print("[PASS] Update task\n")
    except Exception as e:
        print(f"[FAIL] Update task - {e}\n")
        return False

    # Test 4: Complete task
    print("TEST 4: Marking task complete")
    try:
        app.complete_task(1)
        app.list_tasks()
        print("[PASS] Complete task\n")
    except Exception as e:
        print(f"[FAIL] Complete task - {e}\n")
        return False

    # Test 5: Toggle complete (back to incomplete)
    print("TEST 5: Toggling task back to incomplete")
    try:
        app.complete_task(1)
        app.list_tasks()
        print("[PASS] Toggle complete\n")
    except Exception as e:
        print(f"[FAIL] Toggle complete - {e}\n")
        return False

    # Test 6: Delete task
    print("TEST 6: Deleting task")
    try:
        app.delete_task(2)
        app.list_tasks()
        print("[PASS] Delete task\n")
    except Exception as e:
        print(f"[FAIL] Delete task - {e}\n")
        return False

    # Test 7: Error handling - empty title
    print("TEST 7: Error handling - empty title")
    try:
        app.add_task("")
        print("[FAIL] Error handling - Should have raised ValueError\n")
        return False
    except ValueError as e:
        print(f"[PASS] Error handling - Caught: {e}\n")

    # Test 8: Error handling - task not found
    print("TEST 8: Error handling - task not found")
    try:
        app.delete_task(999)
        print("[FAIL] Error handling - Should have raised ValueError\n")
        return False
    except ValueError as e:
        print(f"[PASS] Error handling - Caught: {e}\n")

    # Test 9: Final state
    print("TEST 9: Final task list")
    app.list_tasks()
    print("[PASS] All tests\n")

    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_todo_app()
    exit(0 if success else 1)
