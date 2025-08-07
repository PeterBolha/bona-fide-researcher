import os
import time

CACHE_FILE = "api_cache.json"
CACHE_EXPIRY = 3600  # 1 hour


def get_cached_data():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if time.time() - cache["timestamp"] < CACHE_EXPIRY:
                return cache["data"]
    return None