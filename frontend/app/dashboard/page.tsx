'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task, listTasks, createTask, updateTask, toggleTaskComplete, deleteTask } from '@/lib/api';
import AddTaskForm from '@/components/AddTaskForm';
import TaskItem from '@/components/TaskItem';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await listTasks(filter);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Add task
  const handleAddTask = async (title: string, description: string) => {
    await createTask({ title, description });
    await fetchTasks();
  };

  // Toggle task completion
  const handleToggleTask = async (taskId: number) => {
    await toggleTaskComplete(taskId);
    await fetchTasks();
  };

  // Update task
  const handleUpdateTask = async (taskId: number, title: string, description: string) => {
    await updateTask(taskId, { title, description });
    await fetchTasks();
  };

  // Delete task
  const handleDeleteTask = async (taskId: number) => {
    await deleteTask(taskId);
    await fetchTasks();
  };

  return (
    <div>
      {/* Add Task Form */}
      <AddTaskForm onAdd={handleAddTask} />

      {/* Filter Tabs */}
      <div className="bg-white shadow rounded-lg p-4 mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'pending'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filter === 'completed'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Completed
          </button>
        </div>
      </div>

      {/* Task List */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Your Tasks ({tasks.length})
        </h2>

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white shadow rounded-lg p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p className="mt-2 text-gray-600">Loading tasks...</p>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            <button
              onClick={fetchTasks}
              className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Try again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && tasks.length === 0 && (
          <div className="bg-white shadow rounded-lg p-8 text-center">
            <p className="text-gray-600">No tasks found.</p>
            <p className="text-sm text-gray-500 mt-1">
              Add your first task above to get started!
            </p>
          </div>
        )}

        {/* Task Items */}
        {!isLoading && !error && tasks.length > 0 && (
          <div>
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={handleToggleTask}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
