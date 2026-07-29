import json
import requests
import os
import re
import time
from kivy.logger import Logger

GITHUB_JSON_URL_BASE = "https://raw.githubusercontent.com/mdarmandev-maker/ai-prompt-gallery/main/data/prompts.json"
GITHUB_IMAGE_BASE = "https://github.com/mdarmandev-maker/Apk-imges6/"


def _optimize_image_url(url):
    """
    Unsplash URLs ko chhoti size me convert karta hai (fast loading ke
    liye). Non-Unsplash URLs (jaise tumhari apni GitHub images) ko waise
    hi chhod deta hai, kyunki unpe ye query params kaam nahi karte.
    """
    if "images.unsplash.com" not in url:
        return url
    url = re.sub(r'([?&])w=\d+', r'\1w=500', url)
    url = re.sub(r'([?&])q=\d+', r'\1q=65', url)
    if "w=" not in url:
        url += ("&" if "?" in url else "?") + "w=500"
    if "q=" not in url:
        url += "&q=65"
    return url


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
            # Images ko live internet link mein badalna + size optimize karna
            for item in data:
                if "image" in item and not item["image"].startswith("http"):
                    item["image"] = GITHUB_IMAGE_BASE + item["image"]
                if "image" in item:
                    item["image"] = _optimize_image_url(item["image"])
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
