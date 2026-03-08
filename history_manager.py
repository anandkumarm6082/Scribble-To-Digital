import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    """Load history records from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_to_history(raw_text, corrected_text, todos):
    """Save a new record to the history JSON file."""
    history = load_history()
    
    # Create the new entry record
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_text": raw_text,
        "corrected_text": corrected_text,
        "todos": todos
    }
    
    # Prepend the newest entry to the start of the list
    history.insert(0, entry)
    
    # Keep only the last 20 entries to prevent the file from growing indefinitely
    history = history[:20]
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False
