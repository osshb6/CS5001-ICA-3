import streamlit as st
import requests

# Flask API endpoint
API_URL = "http://localhost:5000/tasks"


def fetch_tasks():
    """Fetch tasks from Flask API."""
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch tasks: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return []


def add_task(title, description, completed):
    """Add a new task via Flask API."""
    try:
        response = requests.post(API_URL, json={
            'title': title,
            'description': description,
            'completed': completed
        })
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Failed to add task: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def update_task(task_id, title, description, completed):
    """Update a task via Flask API."""
    try:
        response = requests.put(f"{API_URL}/{task_id}", json={
            'title': title,
            'description': description,
            'completed': completed
        })
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to update task: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def delete_task(task_id):
    """Delete a task via Flask API."""
    try:
        response = requests.delete(f"{API_URL}/{task_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to delete task: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return False


def main():
    """Main Streamlit app."""
    st.title("ToDo App")
    
    # Fetch tasks
    tasks = fetch_tasks()
    
    # Add new task
    with st.form("new_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        completed = st.checkbox("Completed")
        submitted = st.form_submit_button("Add Task")
        
        if submitted and title:
            new_task = add_task(title, description, completed)
            if new_task:
                st.success("Task added successfully!")
                st.experimental_rerun()
    
    # Display tasks
    st.subheader("Your Tasks")
    for task in tasks:
        with st.expander(f"{task['title']} - {'✅' if task['completed'] else '❌'}"):
            st.write(f"**Description:** {task['description']}")
            
            # Edit task
            with st.form(f"edit_task_form_{task['id']}"):
                new_title = st.text_input("Title", value=task['title'])
                new_description = st.text_area("Description", value=task['description'])
                new_completed = st.checkbox("Completed", value=task['completed'])
                edit_submitted = st.form_submit_button("Update Task")
                
                if edit_submitted:
                    updated_task = update_task(task['id'], new_title, new_description, new_completed)
                    if updated_task:
                        st.success("Task updated successfully!")
                        st.experimental_rerun()
            
            # Delete task
            if st.button(f"Delete Task {task['id']}"):
                if delete_task(task['id']):
                    st.success("Task deleted successfully!")
                    st.experimental_rerun()


if __name__ == "__main__":
    main()
