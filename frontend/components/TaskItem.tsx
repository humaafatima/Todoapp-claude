'use client';

import { useState } from 'react';
import { Task } from '@/lib/api';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: number) => Promise<void>;
  onUpdate: (taskId: number, title: string, description: string) => Promise<void>;
  onDelete: (taskId: number) => Promise<void>;
}

export default function TaskItem({ task, onToggle, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      await onToggle(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editTitle.trim()) return;

    setIsLoading(true);
    try {
      await onUpdate(task.id, editTitle.trim(), editDescription.trim());
      setIsEditing(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    setIsLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="bg-white shadow rounded-lg p-4 mb-3">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            placeholder="Task title"
            disabled={isLoading}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            rows={2}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
            placeholder="Task description"
            disabled={isLoading}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md disabled:opacity-50"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-3">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          disabled={isLoading}
          className="mt-1 h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
        />

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-sm font-medium ${
              task.completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`text-sm mt-1 ${
                task.completed ? 'line-through text-gray-400' : 'text-gray-600'
              }`}
            >
              {task.description}
            </p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            Created: {new Date(task.created_at).toLocaleString()}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
            className="px-3 py-1 text-sm font-medium text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isLoading}
            className="px-3 py-1 text-sm font-medium text-red-600 hover:text-red-800 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
