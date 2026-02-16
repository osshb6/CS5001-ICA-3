# ToDo App

A simple ToDo application with Flask backend and Streamlit frontend.

## Features

- Create, Read, Update, and Delete (CRUD) tasks
- Mark tasks as complete
- In-memory storage (tasks are lost when the server restarts)

## Requirements

- Python 3.6+
- Flask
- Streamlit
- Requests

## Installation

1. Clone this repository
2. Navigate to the `updated/ToDo` directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Run both servers manually

1. Start the Flask server in one terminal:
   ```bash
   python app.py
   ```

2. Start the Streamlit app in another terminal:
   ```bash
   streamlit run streamlit_app.py
   ```

### Option 2: Run both servers with the entry script

Run the following command:
```bash
python ToDo.py
```

This will start both the Flask server and Streamlit app automatically.

## Usage

1. Open your browser to `http://localhost:8501` to access the Streamlit app
2. Use the form to add new tasks
3. Click on a task to view, edit, or delete it
4. Mark tasks as complete by checking the checkbox

## API Endpoints

- `GET /tasks` - Get all tasks
- `POST /tasks` - Create a new task
- `GET /tasks/<id>` - Get a specific task
- `PUT /tasks/<id>` - Update a task
- `DELETE /tasks/<id>` - Delete a task
