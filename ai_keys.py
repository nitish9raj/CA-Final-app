"""
ai_keys.py — Manages API keys stored locally in a JSON file next to the app.
Keys are saved on the user's PC only, never transmitted anywhere except the respective AI APIs.
"""
import json, os

_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.json")

def load_keys():
    try:
        if os.path.exists(_KEY_FILE):
            with open(_KEY_FILE, "r") as f:
                return json.load(f)
    except: pass
    return {"anthropic": "", "openai": "", "gemini": ""}

def save_keys(keys: dict):
    with open(_KEY_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def get_key(provider: str) -> str:
    return load_keys().get(provider, "").strip()

def has_any_key() -> bool:
    k = load_keys()
    return any(v.strip() for v in k.values())
