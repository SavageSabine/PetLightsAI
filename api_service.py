# api_service.py
import requests
import json
import os
from datetime import datetime, timedelta

# Petfinder API credentials - set these as environment variables
CLIENT_ID = os.getenv("PETFINDER_CLIENT_ID")
CLIENT_SECRET = os.getenv("PETFINDER_CLIENT_SECRET")

CACHE_FILE = "dogs_cache.json"
CACHE_DURATION = timedelta(hours=1)

def save_cache(data):
    """Save data to cache file with timestamp."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def load_cache():
    """Load cached data if it exists and is still valid."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache["timestamp"])
                if datetime.now() - cache_time < CACHE_DURATION:
                    return cache["data"]
        except Exception as e:
            print(f"Error loading cache: {e}")
    return None

def get_token():
    """Get OAuth token from Petfinder API."""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Warning: Petfinder API credentials not found in environment variables")
        return None
    
    url = "https://api.petfinder.com/v2/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting token: {e}")
        return None

def fetch_dogs(token, location="85004", limit=10):
    """Fetch dogs from Petfinder API with caching."""
    # Check cache first
    cached = load_cache()
    if cached:
        print("Using cached dog data")
        return cached
    
    if not token:
        print("No token provided")
        return []
    
    url = "https://api.petfinder.com/v2/animals"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "type": "dog",
        "location": location,
        "limit": limit,
        "status": "adoptable"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        dogs = []
        for animal in data.get("animals", []):
            # Get the best available photo
            photos = animal.get("photos", [])
            photo_url = photos[0]["large"] if photos else "https://via.placeholder.com/500?text=No+Photo"
            
            # Build breed string
            breeds = animal.get("breeds", {})
            breed_parts = []
            if breeds.get("primary"):
                breed_parts.append(breeds["primary"])
            if breeds.get("secondary"):
                breed_parts.append(breeds["secondary"])
            breed = ", ".join(breed_parts) if breed_parts else "Mixed Breed"
            
            dog = {
                "id": animal.get("id"),
                "name": animal.get("name", "Unknown"),
                "breed": breed,
                "age": animal.get("age", "Unknown"),
                "gender": animal.get("gender", "Unknown"),
                "size": animal.get("size", "Unknown"),
                "photo": photo_url,
                "description": animal.get("description", "No description available."),
                "url": animal.get("url", "https://www.petfinder.com")
            }
            dogs.append(dog)
        
        # Save to cache
        save_cache(dogs)
        print(f"Fetched {len(dogs)} dogs from API")
        return dogs
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if "429" in error_msg:
            raise Exception(f"Failed to fetch dogs: 429 Rate Limit Exceeded")
        else:
            raise Exception(f"Failed to fetch dogs: {error_msg}")
