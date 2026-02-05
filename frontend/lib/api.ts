/**
 * API client for backend communication
 */

import { getAuthToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreateData {
  title: string;
  description?: string;
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Token expired or invalid
    throw new Error('Authentication failed. Please login again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * List all tasks for the authenticated user
 */
export async function listTasks(status: 'all' | 'pending' | 'completed' = 'all'): Promise<{ tasks: Task[]; total: number; filter: string }> {
  return apiRequest(`/api/v1/tasks?status=${status}`);
}

/**
 * Create a new task
 */
export async function createTask(data: TaskCreateData): Promise<{ task_id: number; status: string; title: string }> {
  return apiRequest('/api/v1/tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get a single task
 */
export async function getTask(taskId: number): Promise<Task> {
  return apiRequest(`/api/v1/tasks/${taskId}`);
}

/**
 * Update a task
 */
export async function updateTask(taskId: number, data: TaskUpdateData): Promise<{ task_id: number; status: string; title: string }> {
  return apiRequest(`/api/v1/tasks/${taskId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Toggle task completion
 */
export async function toggleTaskComplete(taskId: number): Promise<{ task_id: number; status: string; title: string }> {
  return apiRequest(`/api/v1/tasks/${taskId}/complete`, {
    method: 'PATCH',
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: number): Promise<{ message: string; task_id: number; title: string }> {
  return apiRequest(`/api/v1/tasks/${taskId}`, {
    method: 'DELETE',
  });
}
