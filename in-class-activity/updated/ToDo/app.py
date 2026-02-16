from flask import Flask, request, jsonify
from models import TaskStore, Task

app = Flask(__name__)
task_store = TaskStore()


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    tasks = task_store.get_all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )
    task_store.add(task)
    return jsonify(task.to_dict()), 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID."""
    task = task_store.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    task = task_store.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    
    return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    task = task_store.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task_store.delete(task_id)
    return jsonify({'message': 'Task deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
