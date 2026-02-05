"""Simple script to test the API with JWT authentication."""

import jwt
from datetime import datetime, timedelta
import json

# Generate a test JWT token
def generate_test_token(user_id: str = "test_user_123") -> str:
    """Generate a JWT token for testing."""
    secret = "your-super-secret-key-change-in-production-12345678"
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

if __name__ == "__main__":
    token = generate_test_token()
    print("Generated JWT Token:")
    print(token)
    print("\nUse this in your HTTP requests:")
    print(f"Authorization: Bearer {token}")
    print("\nTest commands:")
    print(f'\ncurl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/tasks')
    print(f'\ncurl -X POST -H "Authorization: Bearer {token}" -H "Content-Type: application/json" -d \'{{"title": "Test Task", "description": "Test description"}}\' http://localhost:8000/api/v1/tasks')
