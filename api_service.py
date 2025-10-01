# api_service.py
import requests

API_KEY = "your_client_id"
API_SECRET = "your_client_secret"

# get token
def get_token():
    url = "https://api.petfinder.com/v2/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

# get adoptable dogs
def get_dogs(token, limit=10):
    url = f"https://api.petfinder.com/v2/animals?type=dog&limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return r.json()["animals"]
