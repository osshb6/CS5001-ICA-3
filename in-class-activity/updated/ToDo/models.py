class Task:
    """Represents a ToDo task."""
    
    def __init__(self, id=None, title='', description='', completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
    
    def to_dict(self):
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }


class TaskStore:
    """In-memory storage for tasks."""
    
    def __init__(self):
        self.tasks = []
        self.next_id = 1
    
    def add(self, task):
        """Add a new task."""
        task.id = self.next_id
        self.tasks.append(task)
        self.next_id += 1
    
    def get(self, task_id):
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all(self):
        """Get all tasks."""
        return self.tasks
    
    def delete(self, task_id):
        """Delete a task by ID."""
        self.tasks = [task for task in self.tasks if task.id != task_id]
