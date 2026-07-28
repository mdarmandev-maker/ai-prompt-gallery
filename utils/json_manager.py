import json
import requests
import os
import time
from kivy.logger import Logger

# Yahan 'AAPKA_GITHUB_USERNAME' ko apne asli username se badle!
GITHUB_JSON_URL = "https://raw.githubusercontent.com/mdarmandev-maker/ai-prompt-gallery/main/data/prompts.json"
GITHUB_IMAGE_BASE = "https://github.com/mdarmandev-maker/Apk-imges6/"


def load_prompts():
    print("🌐 Internet se Live Prompts fetch kar rahe hain...")
    try:
        # Cache-busting: har call par URL ke end me current timestamp add
        # karte hain, taaki GitHub/network ka koi purana cached response
        # kabhi na mile - hamesha bilkul fresh data aaye.
        live_url = f"{GITHUB_JSON_URL_BASE}?t={int(time.time())}"

        # Internet se file download karne ki koshish (10 sec timeout)
        response = requests.get(live_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Images ko live internet link mein badalna
            for item in data:
                if "image" in item and not item["image"].startswith("http"):
                    item["image"] = GITHUB_IMAGE_BASE + item["image"]
            return data
        else:
            return load_local_prompts()
    except Exception as e:
        Logger.error(f"Internet Error: {e}")
        return load_local_prompts()

def load_local_prompts():
    local_path = os.path.join("data", "prompts.json")
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
