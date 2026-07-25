import json
import os

# Create absolute path for reliability on Android
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.json')

def load_prompts():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return []

def save_prompts(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)