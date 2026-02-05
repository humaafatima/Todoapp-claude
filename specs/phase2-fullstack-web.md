# Phase 2: Full-Stack Web Todo Application

## Purpose
A production-ready, multi-user web application with persistent storage, authentication, and a responsive user interface. This phase transforms the console todo app into a complete full-stack system with secure user isolation, RESTful API, and modern web frontend.

## Overview
Phase 2 delivers a complete web-based todo application where users can:
- Sign up and log in with Better Auth
- Manage their personal todo tasks through a clean web interface
- Access their data from any device with persistent storage
- Enjoy complete data isolation from other users

The system uses JWT-based authentication, SQLite for local development (Neon PostgreSQL-ready for production), and a modern TypeScript stack.

## Location in Project
```
todo-app/
├── frontend/                    # Next.js 15 (App Router)
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/          # Login page
│   │   │   └── signup/         # Signup page
│   │   ├── dashboard/          # Authenticated dashboard
│   │   ├── api/auth/           # Better Auth API routes
│   │   └── layout.tsx          # Root layout
│   ├── components/
│   │   ├── auth/               # Auth-related components
│   │   ├── tasks/              # Task CRUD components
│   │   └── ui/                 # Shared UI components
│   ├── lib/
│   │   ├── auth.ts             # Better Auth client config
│   │   └── api.ts              # API client with JWT
│   └── package.json
│
├── backend/                     # FastAPI application
│   ├── src/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Environment config
│   │   ├── auth/
│   │   │   ├── middleware.py   # JWT verification middleware
│   │   │   └── models.py       # User auth models
│   │   ├── tasks/
│   │   │   ├── router.py       # Task REST endpoints
│   │   │   ├── service.py      # Business logic layer
│   │   │   └── models.py       # SQLModel Task definition
│   │   └── database.py         # Database connection
│   ├── tests/
│   │   ├── test_auth.py        # Auth middleware tests
│   │   ├── test_tasks.py       # Task endpoint tests
│   │   └── test_isolation.py   # Multi-tenant security tests
│   └── requirements.txt
│
└── specs/
    ├── phase1-console-app.md
    ├── phase2-fullstack-web.md  # This document
    ├── database/
    │   └── schema.md            # Task schema specification
    └── api/
        └── rest-endpoints.md    # REST API spec (to be created)
```

## Tech Stack

### Frontend
- **Framework**: Next.js 15.1 (App Router, React Server Components)
- **Language**: TypeScript 5.7
- **Styling**: Tailwind CSS 4.0
- **Authentication**: Better Auth (client-side SDK)
- **HTTP Client**: Native `fetch` with JWT header injection
- **UI Components**: Radix UI primitives + custom components
- **Form Handling**: React Hook Form + Zod validation
- **State Management**: React Context for auth state, local component state for tasks

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **Database ORM**: SQLModel 0.0.22+ (combines SQLAlchemy + Pydantic)
- **Database**: SQLite 3.x (local dev), Neon PostgreSQL (production)
- **Authentication**: JWT verification middleware (validating Better Auth tokens)
- **Validation**: Pydantic v2 models
- **Testing**: pytest + pytest-asyncio
- **CORS**: Configured for Next.js dev server (localhost:3000)

### Authentication
- **Provider**: Better Auth (https://www.better-auth.com/)
- **Flow**: Better Auth handles signup/login → issues JWT → backend verifies JWT
- **Token Format**: JWT with `sub` (user_id), `email`, `exp` claims
- **Storage**: HTTPOnly cookies (Better Auth default)
- **Middleware**: FastAPI dependency injection for auth verification

### Database
- **Development**: SQLite (`./data/todo.db`)
- **Production**: Neon PostgreSQL (serverless, auto-scaling)
- **Migrations**: SQLModel `create_all()` for dev, Alembic for production
- **Schema**: See `@specs/database/schema.md`

## User Stories

### Authentication
- As a new user, I want to sign up with email and password so I can create my account.
- As a returning user, I want to log in so I can access my tasks.
- As an authenticated user, I want to log out so I can secure my account.
- As a user, I want my session to persist so I don't have to log in on every visit.
- As a user, I want my password to be securely hashed so my credentials are protected.

### Task Management (All User-Scoped)
- As an authenticated user, I want to see all my tasks so I can track what needs to be done.
- As an authenticated user, I want to add a new task so I can remember something I need to do.
- As an authenticated user, I want to edit a task's title or description so I can update my todos.
- As an authenticated user, I want to mark a task as complete so I can track my progress.
- As an authenticated user, I want to delete a task so I can remove completed or irrelevant items.
- As an authenticated user, I want to filter tasks by status (all/pending/completed) so I can focus on what matters.

### Data Isolation
- As a user, I should only see my own tasks, never another user's tasks.
- As a user, I cannot modify or delete another user's tasks even if I know their task ID.

## Core Features

### 1. User Authentication

#### Sign Up
**Route**: `POST /api/auth/signup` (Better Auth handled)

**Frontend Form**:
- Email (required, validated)
- Password (required, min 8 chars, complexity rules)
- Confirm Password (must match)

**Flow**:
1. User submits signup form
2. Better Auth creates user account
3. Better Auth issues JWT token
4. Frontend stores token in HTTPOnly cookie
5. User redirected to dashboard

**Validation**:
- Email format validation
- Password strength (min 8 chars, 1 uppercase, 1 number, 1 special)
- Email uniqueness (handled by Better Auth)

#### Log In
**Route**: `POST /api/auth/login` (Better Auth handled)

**Frontend Form**:
- Email (required)
- Password (required)

**Flow**:
1. User submits login form
2. Better Auth verifies credentials
3. Better Auth issues JWT token
4. Frontend stores token in HTTPOnly cookie
5. User redirected to dashboard

**Errors**:
- Invalid credentials → "Invalid email or password"
- Account not found → "Invalid email or password" (don't reveal which)

#### Log Out
**Route**: `POST /api/auth/logout` (Better Auth handled)

**Flow**:
1. User clicks logout button
2. Better Auth revokes token/session
3. Frontend clears auth state
4. User redirected to login page

### 2. Task CRUD Operations

All task operations require authentication (JWT token in request headers).

#### List Tasks
**Endpoint**: `GET /api/tasks?status={all|pending|completed}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
| Parameter | Type   | Required | Default | Description                    |
|-----------|--------|----------|---------|--------------------------------|
| status    | string | No       | all     | Filter: all, pending, completed|

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 123,
      "user_id": "user_abc123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-30T10:30:00Z",
      "updated_at": "2025-12-30T10:30:00Z"
    }
  ],
  "total": 1,
  "filter": "all"
}
```

**Business Rules**:
- Only returns tasks for authenticated user (from JWT `sub` claim)
- Tasks ordered by `created_at` DESC (newest first)
- Empty array if no tasks match filter

---

#### Create Task
**Endpoint**: `POST /api/tasks`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Schema**:
| Field       | Type   | Required | Constraints      | Description          |
|-------------|--------|----------|------------------|----------------------|
| title       | string | Yes      | Max 200 chars    | Task title           |
| description | string | No       | Max 2000 chars   | Task description     |

**Response** (201 Created):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-30T10:30:00Z",
  "updated_at": "2025-12-30T10:30:00Z"
}
```

**Errors**:
- 400 Bad Request: Title empty or exceeds length
- 401 Unauthorized: Missing or invalid JWT
- 500 Internal Server Error: Database failure

---

#### Get Single Task
**Endpoint**: `GET /api/tasks/{task_id}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type    | Description       |
|-----------|---------|-------------------|
| task_id   | integer | Task ID to fetch  |

**Response** (200 OK):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-30T10:30:00Z",
  "updated_at": "2025-12-30T10:30:00Z"
}
```

**Errors**:
- 404 Not Found: Task doesn't exist or belongs to different user
- 401 Unauthorized: Missing or invalid JWT

---

#### Update Task
**Endpoint**: `PUT /api/tasks/{task_id}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type    | Description        |
|-----------|---------|--------------------|
| task_id   | integer | Task ID to update  |

**Request Body** (Partial update supported):
```json
{
  "title": "Buy organic milk",
  "description": "From Whole Foods"
}
```

**Request Schema**:
| Field       | Type   | Required | Constraints      | Description          |
|-------------|--------|----------|------------------|----------------------|
| title       | string | No       | Max 200 chars    | New task title       |
| description | string | No       | Max 2000 chars   | New task description |

**Response** (200 OK):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Buy organic milk",
  "description": "From Whole Foods",
  "completed": false,
  "created_at": "2025-12-30T10:30:00Z",
  "updated_at": "2025-12-31T08:15:00Z"
}
```

**Business Rules**:
- At least one field (title or description) must be provided
- `updated_at` automatically updated
- User can only update their own tasks

**Errors**:
- 400 Bad Request: No fields provided or validation failed
- 404 Not Found: Task doesn't exist or belongs to different user
- 401 Unauthorized: Missing or invalid JWT

---

#### Toggle Task Completion
**Endpoint**: `PATCH /api/tasks/{task_id}/complete`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type    | Description          |
|-----------|---------|----------------------|
| task_id   | integer | Task ID to complete  |

**Request Body**: None (toggle operation)

**Response** (200 OK):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-12-30T10:30:00Z",
  "updated_at": "2025-12-31T09:00:00Z"
}
```

**Business Rules**:
- Toggles `completed` status: false → true, true → false
- Idempotent operation
- `updated_at` automatically updated

**Errors**:
- 404 Not Found: Task doesn't exist or belongs to different user
- 401 Unauthorized: Missing or invalid JWT

---

#### Delete Task
**Endpoint**: `DELETE /api/tasks/{task_id}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type    | Description        |
|-----------|---------|--------------------|
| task_id   | integer | Task ID to delete  |

**Response** (200 OK):
```json
{
  "message": "Task deleted successfully",
  "task_id": 123,
  "title": "Buy groceries"
}
```

**Business Rules**:
- Hard delete (permanent removal)
- User can only delete their own tasks
- NOT idempotent (second delete returns 404)

**Errors**:
- 404 Not Found: Task doesn't exist or belongs to different user
- 401 Unauthorized: Missing or invalid JWT

---

## Authentication Flow

### JWT Token Structure
Better Auth issues JWTs with the following claims:

```json
{
  "sub": "user_abc123",        // User ID (used for database queries)
  "email": "user@example.com", // User email
  "iat": 1735567800,           // Issued at (Unix timestamp)
  "exp": 1735571400            // Expires at (Unix timestamp, +1 hour)
}
```

### Backend JWT Verification

**Middleware**: `backend/src/auth/middleware.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token and extract user_id.

    Returns:
        user_id (str): User ID from JWT 'sub' claim

    Raises:
        HTTPException 401: Invalid or expired token
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

**Usage in Endpoints**:
```python
@router.get("/tasks")
async def list_tasks(
    status: str = "all",
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # user_id automatically extracted from JWT
    # Use for database query filtering
    tasks = task_service.list_tasks(db, user_id, status)
    return {"tasks": tasks, "total": len(tasks), "filter": status}
```

### Frontend API Client

**File**: `frontend/lib/api.ts`

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  // Better Auth automatically includes JWT in cookies
  // Backend reads from Authorization header
  const token = await getAuthToken(); // Get from Better Auth session

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Include cookies
  });

  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const tasksApi = {
  list: (status = 'all') => fetchWithAuth(`/api/tasks?status=${status}`),
  create: (data: { title: string; description?: string }) =>
    fetchWithAuth('/api/tasks', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: number) => fetchWithAuth(`/api/tasks/${id}`),
  update: (id: number, data: { title?: string; description?: string }) =>
    fetchWithAuth(`/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  toggleComplete: (id: number) =>
    fetchWithAuth(`/api/tasks/${id}/complete`, { method: 'PATCH' }),
  delete: (id: number) =>
    fetchWithAuth(`/api/tasks/${id}`, { method: 'DELETE' }),
};
```

## Frontend Architecture

### Page Structure

#### 1. Login Page (`app/(auth)/login/page.tsx`)
- Email and password form
- "Sign up" link for new users
- Error message display (invalid credentials)
- Redirect to dashboard on success

#### 2. Signup Page (`app/(auth)/signup/page.tsx`)
- Email, password, and confirm password form
- Password strength indicator
- "Log in" link for existing users
- Redirect to dashboard on success

#### 3. Dashboard Page (`app/dashboard/page.tsx`)
- Protected route (requires authentication)
- Task list component
- Add task form (inline or modal)
- Filter tabs (All / Pending / Completed)
- Logout button in header

### Component Structure

#### `<TaskList />` Component
**Props**:
- `tasks: Task[]`
- `onToggleComplete: (id: number) => void`
- `onDelete: (id: number) => void`
- `onEdit: (task: Task) => void`

**Features**:
- Display tasks in a responsive grid/list
- Show completion status (checkbox or toggle)
- Edit button (opens modal or inline edit)
- Delete button (with confirmation)
- Empty state message ("No tasks found")

#### `<AddTaskForm />` Component
**Props**:
- `onSubmit: (data: { title: string; description: string }) => void`

**Features**:
- Title input (required, max 200 chars)
- Description textarea (optional, max 2000 chars)
- Character count indicators
- Submit button (disabled if invalid)
- Clear form on success

#### `<EditTaskModal />` Component
**Props**:
- `task: Task | null`
- `open: boolean`
- `onClose: () => void`
- `onSave: (id: number, data: Partial<Task>) => void`

**Features**:
- Pre-filled form with current task data
- Title and description editing
- Cancel and Save buttons
- Close on successful save

### Responsive Design
- **Mobile**: Stacked layout, hamburger menu, full-width task cards
- **Tablet**: 2-column grid for tasks, side navigation
- **Desktop**: 3-column grid for tasks, persistent sidebar

## Backend Architecture

### Project Structure
```
backend/
├── src/
│   ├── main.py              # FastAPI app initialization, CORS, routes
│   ├── config.py            # Environment variables (Pydantic Settings)
│   ├── database.py          # SQLModel engine, session dependency
│   ├── auth/
│   │   ├── middleware.py    # JWT verification, get_current_user
│   │   └── models.py        # User model (if needed, or rely on Better Auth)
│   └── tasks/
│       ├── router.py        # FastAPI router with all 6 endpoints
│       ├── service.py       # Business logic (CRUD operations)
│       ├── models.py        # Task SQLModel (from schema.md)
│       └── schemas.py       # Pydantic request/response schemas
├── tests/
│   ├── conftest.py          # Pytest fixtures (test DB, auth mock)
│   ├── test_tasks.py        # Task endpoint tests
│   ├── test_isolation.py    # Multi-tenant security tests
│   └── test_auth.py         # JWT middleware tests
└── requirements.txt
```

### FastAPI Main App (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.tasks.router import router as tasks_router
from src.database import engine
from src.tasks.models import Task
from sqlmodel import SQLModel

app = FastAPI(title="Todo API", version="2.0.0")

# CORS for Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Include routers
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
```

### Task Router (`tasks/router.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from src.database import get_db
from src.auth.middleware import get_current_user
from src.tasks import service, schemas

router = APIRouter()

@router.get("", response_model=schemas.TaskListResponse)
async def list_tasks(
    status: str = Query("all", regex="^(all|pending|completed)$"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = service.list_tasks(db, user_id, status)
    return {"tasks": tasks, "total": len(tasks), "filter": status}

@router.post("", response_model=schemas.TaskResponse, status_code=201)
async def create_task(
    data: schemas.TaskCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.create_task(db, user_id, data)

@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = service.get_task(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = service.update_task(db, user_id, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/complete", response_model=schemas.TaskResponse)
async def toggle_complete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = service.toggle_complete(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", response_model=schemas.TaskDeleteResponse)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = service.delete_task(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "message": "Task deleted successfully",
        "task_id": task.id,
        "title": task.title
    }
```

### Task Service (`tasks/service.py`)
```python
from sqlmodel import Session, select
from src.tasks.models import Task
from src.tasks.schemas import TaskCreate, TaskUpdate
from datetime import datetime

def list_tasks(db: Session, user_id: str, status: str = "all") -> list[Task]:
    """List tasks for user, filtered by status."""
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    return list(db.exec(query.order_by(Task.created_at.desc())))

def get_task(db: Session, user_id: str, task_id: int) -> Task | None:
    """Get single task by ID (user-scoped)."""
    return db.exec(
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == user_id)
    ).first()

def create_task(db: Session, user_id: str, data: TaskCreate) -> Task:
    """Create new task for user."""
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description or "",
        completed=False
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task(
    db: Session,
    user_id: str,
    task_id: int,
    data: TaskUpdate
) -> Task | None:
    """Update task fields (user-scoped)."""
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description

    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def toggle_complete(db: Session, user_id: str, task_id: int) -> Task | None:
    """Toggle task completion status (user-scoped)."""
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, user_id: str, task_id: int) -> Task | None:
    """Delete task (user-scoped)."""
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    db.delete(task)
    db.commit()
    return task
```

## Multi-Tenant Data Isolation

### Security Guarantees
Every backend endpoint MUST:
1. Extract `user_id` from JWT token (via `get_current_user` dependency)
2. Filter ALL database queries with `WHERE user_id = ?`
3. Return 404 (not 403) if task exists but belongs to different user
4. Never expose existence of other users' data

### Security Test Cases
**File**: `backend/tests/test_isolation.py`

```python
def test_list_tasks_isolation(test_db, user_a_token, user_b_token):
    """User A cannot see User B's tasks."""
    # User A creates task
    response_a = client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"title": "User A's secret task"}
    )
    assert response_a.status_code == 201

    # User B lists tasks
    response_b = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    assert response_b.status_code == 200
    tasks_b = response_b.json()["tasks"]
    assert len(tasks_b) == 0  # User B sees no tasks

def test_update_task_isolation(test_db, user_a_token, user_b_token):
    """User B cannot update User A's task."""
    # User A creates task
    task = client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"title": "Original"}
    ).json()

    # User B attempts to update
    response = client.put(
        f"/api/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {user_b_token}"},
        json={"title": "Hacked"}
    )
    assert response.status_code == 404  # Not 403, to prevent info leak

def test_delete_task_isolation(test_db, user_a_token, user_b_token):
    """User B cannot delete User A's task."""
    # User A creates task
    task = client.post(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"title": "Important"}
    ).json()

    # User B attempts to delete
    response = client.delete(
        f"/api/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    assert response.status_code == 404

    # Verify task still exists for User A
    response_a = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert len(response_a.json()["tasks"]) == 1
```

## Environment Configuration

### Frontend `.env.local`
```env
# Better Auth
BETTER_AUTH_SECRET=<random-secret-key>
BETTER_AUTH_URL=http://localhost:3000

# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database (Better Auth uses separate DB)
BETTER_AUTH_DATABASE_URL=postgresql://...
```

### Backend `.env`
```env
# JWT Secret (must match Better Auth secret)
JWT_SECRET=<random-secret-key>

# Database
DATABASE_URL=sqlite:///./data/todo.db
# Production: DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_db?sslmode=require

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Acceptance Criteria

### Feature Completeness
- [ ] User can sign up with email and password
- [ ] User can log in with email and password
- [ ] User can log out and session is cleared
- [ ] Authenticated user can view all their tasks
- [ ] Authenticated user can create a new task
- [ ] Authenticated user can edit task title/description
- [ ] Authenticated user can toggle task completion
- [ ] Authenticated user can delete a task
- [ ] User can filter tasks by status (all/pending/completed)
- [ ] Unauthenticated users are redirected to login

### Security & Data Isolation
- [ ] JWT tokens are verified on every API request
- [ ] Expired or invalid tokens return 401 Unauthorized
- [ ] User A cannot see User B's tasks
- [ ] User A cannot modify or delete User B's tasks
- [ ] Database queries always include `user_id` filter
- [ ] Multi-tenant isolation tests pass
- [ ] Passwords are hashed (handled by Better Auth)
- [ ] No sensitive data in error messages

### User Experience
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] Forms have client-side validation
- [ ] Error messages are clear and helpful
- [ ] Loading states shown during API calls
- [ ] Success feedback for all CRUD operations
- [ ] Smooth animations and transitions
- [ ] Accessible (keyboard navigation, ARIA labels)
- [ ] Empty states with helpful messages

### Technical Requirements
- [ ] Next.js 15 App Router with TypeScript
- [ ] Tailwind CSS for styling
- [ ] FastAPI backend with SQLModel ORM
- [ ] SQLite for local development
- [ ] Better Auth for authentication
- [ ] JWT middleware verifies tokens
- [ ] CORS configured correctly
- [ ] Environment variables for secrets
- [ ] Clean code structure (separation of concerns)

### Testing
- [ ] Backend unit tests for all service functions
- [ ] API endpoint tests (all 6 endpoints)
- [ ] Multi-tenant isolation security tests
- [ ] JWT middleware tests (valid, expired, invalid tokens)
- [ ] Frontend component tests (task list, forms)
- [ ] End-to-end test: signup → login → create task → logout

### Performance
- [ ] API endpoints respond in <200ms (p95, local dev)
- [ ] Frontend initial load <2s (production build)
- [ ] No unnecessary re-renders in React components
- [ ] Database queries use indexes (see schema.md)

## Non-Goals (Out of Scope for Phase 2)
- ❌ Task categories or tags
- ❌ Task priorities or due dates
- ❌ Recurring tasks
- ❌ Task search functionality
- ❌ Real-time collaboration (WebSockets)
- ❌ File attachments
- ❌ Email notifications
- ❌ Mobile native apps
- ❌ Social features (sharing tasks)
- ❌ Task history or audit log
- ❌ Soft deletes or trash functionality
- ❌ Password reset flow (Better Auth handles this)

## Deployment Strategy

### Development
- **Frontend**: `npm run dev` (Next.js dev server on port 3000)
- **Backend**: `uvicorn src.main:app --reload` (FastAPI on port 8000)
- **Database**: SQLite file at `./data/todo.db`

### Production (Future)
- **Frontend**: Vercel (automatic deployment from GitHub)
- **Backend**: Railway, Fly.io, or AWS Lambda
- **Database**: Neon PostgreSQL (serverless, auto-scaling)
- **Environment**: Separate `.env` files for prod
- **HTTPS**: Required for production (Vercel and Railway provide SSL)

## Success Metrics
- All 6 REST API endpoints functional and tested
- User signup → login → create task → logout workflow works end-to-end
- Multi-tenant isolation tests pass (no data leakage)
- Responsive UI works on mobile and desktop
- Zero authentication bypasses (all routes protected)
- Clean, maintainable codebase (passes linting, type checks)

## References

### Internal Specs
- `@specs/phase1-console-app.md` - Phase 1 console implementation
- `@specs/database/schema.md` - Task model schema and multi-tenant design
- `@specs/api/mcp-tools.md` - MCP tool signatures (basis for REST endpoints)
- `@specs/agents/crud-subagent.md` - CRUD subagent implementation

### External Documentation
- **Next.js**: https://nextjs.org/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Better Auth**: https://www.better-auth.com/docs
- **Neon PostgreSQL**: https://neon.tech/docs
- **Tailwind CSS**: https://tailwindcss.com/docs

---

**Version**: 1.0.0
**Created**: 2026-02-05
**Status**: Ready for Planning
**Estimated Effort**: 2-3 weeks (frontend + backend + testing)
