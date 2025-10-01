import requests
import streamlit as st

API_KEY = st.secrets["petfinder"]["client_id"]
API_SECRET = st.secrets["petfinder"]["client_secret"]

def get_token():
    url = "https://api.petfinder.com/v2/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }
    r = requests.post(url, data=data)

    if r.status_code != 200:
        st.error(f"Failed to get token: {r.status_code} {r.text}")
        return None
    
    return r.json().get("access_token")
