import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "dogs_cache.json"
CACHE_DURATION = timedelta(hours=1)

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
            cache_time = datetime.fromisoformat(cache["timestamp"])
            if datetime.now() - cache_time < CACHE_DURATION:
                return cache["data"]
    return None

# In fetch_dogs(), check cache first:
def fetch_dogs(token, location, limit=10):
    cached = load_cache()
    if cached:
        return cached
    # ... existing API call code ...
    save_cache(dogs)
    return dogs
