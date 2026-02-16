# Entry point for the ToDo application
# This module provides a simple CLI to start both Flask and Streamlit servers

import subprocess
import sys
import time
from threading import Thread


def start_flask():
    """Start the Flask server in a separate thread."""
    subprocess.run([sys.executable, "app.py"])


def start_streamlit():
    """Start the Streamlit app in a separate thread."""
    subprocess.run(["streamlit", "run", "streamlit_app.py"])


def main():
    """Main entry point to start both servers."""
    print("Starting Flask server...")
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Give Flask server a moment to start
    time.sleep(2)
    
    print("Starting Streamlit app...")
    start_streamlit()


if __name__ == "__main__":
    main()
