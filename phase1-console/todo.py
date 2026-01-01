"""Phase 1 In-Memory Console Todo Application."""

from task import Task


class TodoApp:
    """
    In-memory todo application with CLI interface.

    Attributes:
        tasks (dict): Dictionary mapping task_id to Task objects
        next_id (int): Counter for generating unique task IDs
    """

    def __init__(self):
        """Initialize the TodoApp with empty task storage."""
        self.tasks: dict[int, Task] = {}
        self.next_id: int = 1

    def add_task(self, title: str, description: str = "") -> None:
        """
        Create a new task.

        Args:
            title: Task title (required, cannot be empty)
            description: Optional task description

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        # Create and store task
        task = Task(self.next_id, title.strip(), description.strip())
        self.tasks[self.next_id] = task
        print(f"[OK] Task added successfully! (ID: {self.next_id})")

        # Increment ID for next task
        self.next_id += 1

    def list_tasks(self) -> None:
        """Display all tasks with their details."""
        print("\n=== Your Tasks ===")

        if not self.tasks:
            print("No tasks found.\n")
            return

        # Display tasks in order by ID
        for task_id in sorted(self.tasks.keys()):
            task = self.tasks[task_id]
            status_icon = "[X]" if task.completed else "[ ]"
            print(f"[{task.id}] {status_icon} {task.title}")

            if task.description:
                print(f"    Description: {task.description}")
            print()  # Blank line between tasks

        # Display summary
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.completed)
        pending = total - completed
        print(f"Total: {total} task{'s' if total != 1 else ''} "
              f"({completed} completed, {pending} pending)\n")

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> None:
        """
        Update an existing task's title and/or description.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Raises:
            ValueError: If task not found, no fields provided, or title is empty
        """
        # Validate task exists
        if task_id not in self.tasks:
            raise ValueError("Task not found")

        # Validate at least one field provided
        if title is None and description is None:
            raise ValueError("Nothing to update")

        # Validate title if provided
        if title is not None and (not title or not title.strip()):
            raise ValueError("Task title cannot be empty")

        # Update task
        task = self.tasks[task_id]
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip()

        print("[OK] Task updated successfully!")

    def complete_task(self, task_id: int) -> None:
        """
        Toggle a task's completion status.

        Args:
            task_id: ID of the task to toggle

        Raises:
            ValueError: If task not found
        """
        # Validate task exists
        if task_id not in self.tasks:
            raise ValueError("Task not found")

        # Toggle completion status
        task = self.tasks[task_id]
        task.completed = not task.completed

        status = "complete" if task.completed else "incomplete"
        print(f"[OK] Task marked as {status}: \"{task.title}\"")

    def delete_task(self, task_id: int) -> None:
        """
        Permanently delete a task.

        Args:
            task_id: ID of the task to delete

        Raises:
            ValueError: If task not found
        """
        # Validate task exists
        if task_id not in self.tasks:
            raise ValueError("Task not found")

        # Delete task and store title for confirmation
        task = self.tasks.pop(task_id)
        print(f"[OK] Task deleted: \"{task.title}\"")

    def _display_menu(self) -> None:
        """Display the main menu."""
        print("\n=== Todo App ===")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Update Task")
        print("4. Mark Complete")
        print("5. Delete Task")
        print("6. Exit")

    def _get_int_input(self, prompt: str) -> int:
        """
        Get integer input from user.

        Args:
            prompt: Prompt to display to user

        Returns:
            int: User's input as integer

        Raises:
            ValueError: If input is not a valid integer
        """
        value = input(prompt).strip()
        return int(value)

    def run(self) -> None:
        """Run the main CLI loop."""
        print("Welcome to Phase 1 Todo App!")
        print("All tasks are stored in memory and will be lost on exit.")

        while True:
            try:
                self._display_menu()
                choice = self._get_int_input("\nEnter your choice (1-6): ")

                if choice == 1:
                    # Add Task
                    title = input("Enter task title: ").strip()
                    description = input("Enter description (optional): ").strip()
                    self.add_task(title, description)

                elif choice == 2:
                    # List Tasks
                    self.list_tasks()

                elif choice == 3:
                    # Update Task
                    task_id = self._get_int_input("Enter task ID: ")
                    print("Enter new title (press Enter to skip): ", end="")
                    title = input().strip()
                    print("Enter new description (press Enter to skip): ", end="")
                    description = input().strip()

                    # Convert empty strings to None
                    title = title if title else None
                    description = description if description else None

                    self.update_task(task_id, title, description)

                elif choice == 4:
                    # Mark Complete
                    task_id = self._get_int_input("Enter task ID: ")
                    self.complete_task(task_id)

                elif choice == 5:
                    # Delete Task
                    task_id = self._get_int_input("Enter task ID: ")
                    self.delete_task(task_id)

                elif choice == 6:
                    # Exit
                    print("\nThank you for using Todo App. Goodbye!")
                    break

                else:
                    print("[ERROR] Invalid choice. Please enter 1-6.")

            except ValueError as e:
                print(f"[ERROR] {e}")
            except KeyboardInterrupt:
                print("\n\nExiting... Goodbye!")
                break
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")


def main():
    """Entry point for the application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
