"""Test script for API endpoints with JWT authentication."""

import requests
import jwt
from datetime import datetime, timedelta, timezone

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
JWT_SECRET = "your-super-secret-key-change-in-production-12345678"

def generate_token(user_id="test_user_123"):
    """Generate a JWT token for testing."""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def test_api():
    """Run API endpoint tests."""
    token = generate_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("=" * 60)
    print("Testing Todo API Endpoints")
    print("=" * 60)

    # Test 1: List tasks (should be empty initially)
    print("\n1. GET /api/v1/tasks - List all tasks")
    r = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200, "Failed to list tasks"

    # Test 2: Create a task
    print("\n2. POST /api/v1/tasks - Create a new task")
    task_data = {"title": "Test Task 1", "description": "This is a test task"}
    r = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 201, "Failed to create task"
    task_id = r.json()["task_id"]

    # Test 3: Create another task
    print("\n3. POST /api/v1/tasks - Create another task")
    task_data2 = {"title": "Test Task 2", "description": "Another test"}
    r = requests.post(f"{BASE_URL}/tasks", json=task_data2, headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    task_id_2 = r.json()["task_id"]

    # Test 4: Get a single task
    print(f"\n4. GET /api/v1/tasks/{task_id} - Get single task")
    r = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200, "Failed to get task"

    # Test 5: Update a task
    print(f"\n5. PUT /api/v1/tasks/{task_id} - Update task")
    update_data = {"title": "Updated Test Task", "description": "Updated description"}
    r = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200, "Failed to update task"

    # Test 6: Toggle completion
    print(f"\n6. PATCH /api/v1/tasks/{task_id}/complete - Toggle completion")
    r = requests.patch(f"{BASE_URL}/tasks/{task_id}/complete", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200, "Failed to toggle completion"

    # Test 7: List tasks (should show both tasks)
    print("\n7. GET /api/v1/tasks - List all tasks (should show 2)")
    r = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print(f"   Status: {r.status_code}")
    data = r.json()
    print(f"   Total: {data['total']}")
    for task in data['tasks']:
        print(f"   - {task['id']}: {task['title']} (completed: {task['completed']})")

    # Test 8: Filter by status
    print("\n8. GET /api/v1/tasks?status=completed - Filter completed")
    r = requests.get(f"{BASE_URL}/tasks?status=completed", headers=headers)
    print(f"   Status: {r.status_code}")
    data = r.json()
    print(f"   Total: {data['total']}")

    # Test 9: Delete a task
    print(f"\n9. DELETE /api/v1/tasks/{task_id} - Delete task")
    r = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    assert r.status_code == 200, "Failed to delete task"

    # Test 10: Verify task was deleted
    print(f"\n10. GET /api/v1/tasks/{task_id} - Verify deletion (should 404)")
    r = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"    Status: {r.status_code}")
    assert r.status_code == 404, "Task should not exist"

    # Test 11: Test without auth (should fail)
    print("\n11. GET /api/v1/tasks - Test without auth (should 401)")
    r = requests.get(f"{BASE_URL}/tasks")
    print(f"    Status: {r.status_code}")
    assert r.status_code == 401, "Should require authentication"

    # Test 12: Test multi-tenant isolation
    print("\n12. Multi-tenant isolation test")
    print("    Creating task as user_a...")
    user_a_token = generate_token("user_a")
    user_a_headers = {"Authorization": f"Bearer {user_a_token}", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/tasks", json={"title": "User A's Task"}, headers=user_a_headers)
    user_a_task_id = r.json()["task_id"]

    print("    Listing tasks as user_b...")
    user_b_token = generate_token("user_b")
    user_b_headers = {"Authorization": f"Bearer {user_b_token}", "Content-Type": "application/json"}
    r = requests.get(f"{BASE_URL}/tasks", headers=user_b_headers)
    user_b_tasks = r.json()["tasks"]

    # User B should not see User A's task
    user_a_task_visible = any(t["id"] == user_a_task_id for t in user_b_tasks)
    print(f"    User A's task visible to User B: {user_a_task_visible}")
    assert not user_a_task_visible, "Multi-tenant isolation failed!"

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
