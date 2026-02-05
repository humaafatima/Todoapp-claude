# Full-Stack Todo App - Testing Guide

## Services Running

### Backend API
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Status**: ✅ Running

### Frontend
- **URL**: http://localhost:3000
- **Status**: ✅ Running

## Manual Testing Steps

### 1. Test Login Flow
1. Open http://localhost:3000 in your browser
2. You should be redirected to `/login`
3. Enter a username (e.g., "alice" or "bob")
4. Click "Sign in"
5. You should be redirected to `/dashboard`

### 2. Test Task Creation
1. On the dashboard, find the "Add New Task" form
2. Enter a task title (e.g., "Buy groceries")
3. Optionally add a description
4. Click "Add Task"
5. The task should appear in the list below

### 3. Test Task Operations
- **Toggle Complete**: Click the checkbox next to a task
- **Edit Task**: Click the "Edit" button, modify the task, click "Save"
- **Delete Task**: Click the "Delete" button, confirm deletion

### 4. Test Filtering
- Click the filter buttons (All, Pending, Completed) to filter tasks

### 5. Test Multi-User Isolation
1. Open a new incognito/private browser window
2. Login with a different username (e.g., "bob" if you used "alice" before)
3. Verify that this user cannot see the first user's tasks
4. Create tasks for this user
5. Switch back to the first window - verify tasks are isolated

### 6. Test Logout
1. Click the "Logout" button in the header
2. You should be redirected to `/login`
3. Try to access `/dashboard` directly - you should be redirected to login

## Expected Behavior

### Loading States
- ✅ Loading spinner when fetching tasks
- ✅ "Adding..." button text when creating a task
- ✅ Disabled buttons during operations

### Error States
- ✅ Error message if API request fails
- ✅ "Try again" button to retry failed requests

### Responsive Design
- ✅ Works on desktop
- ✅ Works on tablet (responsive layout)
- ✅ Works on mobile (responsive layout)

### Authentication
- ✅ Cannot access dashboard without login
- ✅ JWT token stored in localStorage
- ✅ Token sent with all API requests
- ✅ Logout clears token and redirects to login

## API Endpoints Used

All endpoints require JWT authentication:

1. `GET /api/v1/tasks?status={filter}` - List tasks
2. `POST /api/v1/tasks` - Create task
3. `GET /api/v1/tasks/{id}` - Get single task
4. `PUT /api/v1/tasks/{id}` - Update task
5. `PATCH /api/v1/tasks/{id}/complete` - Toggle completion
6. `DELETE /api/v1/tasks/{id}` - Delete task

## Common Issues & Solutions

### Issue: Frontend can't connect to backend
**Solution**: Ensure backend is running on port 8000

### Issue: CORS errors
**Solution**: Check that `ALLOWED_ORIGINS` in backend `.env` includes `http://localhost:3000`

### Issue: JWT authentication fails
**Solution**: Ensure `JWT_SECRET` in both frontend and backend `.env` files match

### Issue: Tasks not loading
**Solution**:
1. Open browser DevTools (F12)
2. Check Console for errors
3. Check Network tab for failed API requests
4. Verify backend is responding at http://localhost:8000

## Success Criteria

✅ All features implemented:
- User login (JWT-based)
- Task list display
- Create new tasks
- Edit existing tasks
- Toggle task completion
- Delete tasks
- Filter by status (all/pending/completed)
- Logout functionality

✅ Loading and error states displayed
✅ Responsive UI with Tailwind CSS
✅ Route protection (dashboard requires auth)
✅ Multi-tenant data isolation

## Next Steps

If all tests pass, the minimal but functional full-stack todo application is complete!

Optional enhancements:
- Add proper backend authentication (password validation)
- Add task due dates
- Add task categories/tags
- Add search functionality
- Add pagination for large task lists
- Add unit tests for frontend components
- Add E2E tests with Playwright
