import json
import os
import requests

# GitHub/jsDelivr live link
LIVE_JSON_URL = "https://cdn.jsdelivr.net/gh/mdarmandev-maker/ai-prompt-gallery@main/data/prompts.json"
LOCAL_CACHE_FILE = "data/prompts.json" # Local backup file ka path

def load_prompts():
    # 1. Pehle online data try karo
    try:
        response = requests.get(LIVE_JSON_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Online data mil gaya, toh ise local cache mein save kar lo (Backup ke liye)
            save_prompts(data)
            return data
    except Exception as e:
        print(f"Internet connection issue: {e}")
    
    # 2. Agar internet nahi chala, toh local backup file se dikhao
    if os.path.exists(LOCAL_CACHE_FILE):
        try:
            with open(LOCAL_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
            
    return [] # Kuch bhi nahi mila toh khali list

def save_prompts(data):
    # Backup file update karna
    os.makedirs(os.path.dirname(LOCAL_CACHE_FILE), exist_ok=True)
    with open(LOCAL_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
