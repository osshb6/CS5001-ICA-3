Here's the implementation of the `ToDo.py` module following the comprehensive plan:

```python
"""
ToDo.py - Streamlit-based UI for the ToDo application.

This module provides the user interface for the ToDo application, interacting with
the Flask REST API to perform CRUD operations on tasks. The UI includes forms for
adding/editing tasks and displays a filtered list of tasks based on their status.

Dependencies:
    - streamlit: For the web UI
    - requests: For API communication
    - uuid: For task ID generation
    - datetime: For timestamp handling
"""

import streamlit as st
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import uuid

# Configuration
API_BASE_URL = "http://localhost:5000/tasks"

def validate_task_data(task_data: Dict) -> Tuple[bool, str]:
    """
    Validate task data before submission.

    Args:
        task_data: Dictionary containing task data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['title', 'status']
    for field in required_fields:
        if field not in task_data or not task_data[field]:
            return False, f"Missing required field: {field}"

    valid_statuses = ['todo', 'in_progress', 'done']
    if task_data['status'] not in valid_statuses:
        return False, f"Invalid status. Must be one of: {valid_statuses}"

    if len(task_data['title']) > 100:
        return False, "Title must be 100 characters or less"

    if 'description' in task_data and len(task_data['description']) > 500:
        return False, "Description must be 500 characters or less"

    return True, ""

def get_tasks(status_filter: Optional[str] = None) -> List[Dict]:
    """
    Fetch tasks from the API with optional status filtering.

    Args:
        status_filter: Optional status to filter by

    Returns:
        List of task dictionaries
    """
    params = {}
    if status_filter:
        params['status'] = status_filter

    try:
        response = requests.get(API_BASE_URL, params=params)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks: {str(e)}")
        return []

def create_task(task_data: Dict) -> Optional[Dict]:
    """
    Create a new task via the API.

    Args:
        task_data: Dictionary containing task data

    Returns:
        The created task dictionary if successful, None otherwise
    """
    try:
        response = requests.post(API_BASE_URL, json=task_data)
        response.raise_for_status()
        return response.json().get('data')
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating task: {str(e)}")
        return None

def update_task(task_id: str, updates: Dict) -> Optional[Dict]:
    """
    Update an existing task via the API.

    Args:
        task_id: ID of the task to update
        updates: Dictionary containing fields to update

    Returns:
        The updated task dictionary if successful, None otherwise
    """
    try:
        response = requests.put(f"{API_BASE_URL}/{task_id}", json=updates)
        response.raise_for_status()
        return response.json().get('data')
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating task: {str(e)}")
        return None

def delete_task(task_id: str) -> bool:
    """
    Delete a task via the API.

    Args:
        task_id: ID of the task to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        response = requests.delete(f"{API_BASE_URL}/{task_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting task: {str(e)}")
        return False

def display_task_form(task_data: Optional[Dict] = None) -> Optional[Dict]:
    """
    Display a form for creating or editing a task.

    Args:
        task_data: Optional existing task data to edit

    Returns:
        Dictionary of task data if form is submitted, None otherwise
    """
    with st.form("task_form"):
        # Determine default values
        title = task_data.get('title', '') if task_data else ''
        description = task_data.get('description', '') if task_data else ''
        status = task_data.get('status', 'todo') if task_data else 'todo'

        # Form fields
        st.text_input("Title", value=title, key="title")
        st.text_area("Description", value=description, key="description")
        status_option = st.selectbox(
            "Status",
            options=['todo', 'in_progress', 'done'],
            index=['todo', 'in_progress', 'done'].index(status)
        )

        submitted = st.form_submit_button("Save")

        if submitted:
            task_data = {
                'title': st.session_state.title,
                'description': st.session_state.description,
                'status': status_option
            }

            # Validate before submission
            is_valid, error_msg = validate_task_data(task_data)
            if not is_valid:
                st.error(error_msg)
                return None

            return task_data
    return None

def display_task_list(tasks: List[Dict]) -> None:
    """
    Display a list of tasks with options to edit or delete.

    Args:
        tasks: List of task dictionaries to display
    """
    if not tasks:
        st.info("No tasks found.")
        return

    for task in tasks:
        with st.expander(f"{task['title']} - {task['status'].replace('_', ' ').title()}"):
            st.write(f"**Description:** {task['description'] or 'No description'}")
            st.write(f"**Created:** {task['created_at']}")
            st.write(f"**Updated:** {task['updated_at']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{task['id']}"):
                    st.session_state['editing_task'] = task
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"delete_{task['id']}"):
                    if delete_task(task['id']):
                        st.success("Task deleted successfully!")
                        st.rerun()

def main() -> None:
    """
    Main function to run the Streamlit UI.
    """
    st.title("ToDo App")

    # Initialize session state
    if 'editing_task' not in st.session_state:
        st.session_state.editing_task = None

    # Sidebar for status filtering
    with st.sidebar:
        st.header("Filters")
        status_filter = st.selectbox(
            "Filter by status",
            options=['all', 'todo', 'in_progress', 'done'],
            index=0
        )

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        # Display task form
        if st.session_state.editing_task:
            st.header("Edit Task")
            task_data = display_task_form(st.session_state.editing_task)
            if task_data:
                if update_task(st.session_state.editing_task['id'], task_data):
                    st.success("Task updated successfully!")
                    st.session_state.editing_task = None
                    st.rerun()
        else:
            st.header("Add New Task")
            task_data = display_task_form()
            if task_data:
                created_task = create_task(task_data)
                if created_task:
                    st.success("Task created successfully!")
                    st.rerun()

    with col2:
        # Display task list
        st.header("Your Tasks")
        filter_status = status_filter if status_filter != 'all' else None
        tasks = get_tasks(filter_status)
        display_task_list(tasks)

if __name__ == "__main__":
    main()
```

This implementation includes:

1. **API Communication Functions**:
   - `get_tasks()` - Fetches tasks with optional status filtering
   - `create_task()` - Creates a new task
   - `update_task()` - Updates an existing task
   - `delete_task()` - Deletes a task

2. **Validation**:
   - `validate_task_data()` - Ensures task data meets requirements

3. **UI Components**:
   - `display_task_form()` - Shows form for creating/editing tasks
   - `display_task_list()` - Displays tasks with edit/delete options

4. **Main Application**:
   - `main()` - Orchestrates the UI flow with session state management

5. **Error Handling**:
   - Comprehensive error handling for API requests
   - User-friendly error messages

6. **Type Hints**:
   - All functions include proper type hints

7. **Documentation**:
   - Google-style docstrings for all functions
   - Clear comments explaining complex logic

The module is designed to work with the Flask API (api.py) and follows the architecture outlined in the implementation plan. The UI provides a complete CRUD interface for managing tasks with status filtering and form validation.
