# api_service.py
import requests
import streamlit as st

API_KEY = st.secrets["PETFINDER_CLIENT_ID"]
API_SECRET = st.secrets["PETFINDER_CLIENT_SECRET"]

TOKEN_URL = "https://api.petfinder.com/v2/oauth2/token"
ANIMALS_URL = "https://api.petfinder.com/v2/animals"


def get_token():
    """Get an access token from Petfinder API."""
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET,
    }
    r = requests.post(TOKEN_URL, data=data)
    if r.status_code != 200:
        st.error(f"Failed to get token: {r.status_code} {r.text}")
        return None
    return r.json().get("access_token")


def fetch_dogs(token, location="85004", limit=10):
    """Fetch adoptable dogs from Petfinder and normalize results."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"type": "Dog", "location": location, "limit": limit}

    r = requests.get(ANIMALS_URL, headers=headers, params=params)
    if r.status_code != 200:
        st.error(f"Failed to fetch dogs: {r.status_code} {r.text}")
        return []

    animals = r.json().get("animals", [])

    # Normalize each dog into a flat dict
    dogs = []
    for a in animals:
        dogs.append(
            {
                "id": a.get("id"),
                "name": a.get("name", "Unknown"),
                "age": a.get("age", "Unknown"),
                "gender": a.get("gender", "Unknown"),
                "breed": a.get("breeds", {}).get("primary", "Unknown"),
                "description": a.get("description", "No description available."),
                "photo": (
                    a.get("photos")[0]["medium"]
                    if a.get("photos")
                    else "https://via.placeholder.com/350x350.png?text=No+Image"
                ),
                "url": a.get("url", "#"),
            }
        )

    return dogs
