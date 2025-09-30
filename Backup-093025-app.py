import os
import requests
import streamlit as st

# --- API Setup ---
CLIENT_ID = os.getenv("PETFINDER_CLIENT_ID")
CLIENT_SECRET = os.getenv("PETFINDER_CLIENT_SECRET")

@st.cache_data
def get_access_token():
    """Fetch a new Petfinder access token."""
    url = "https://api.petfinder.com/v2/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_animals(token, type_filter="dog", limit=1):
    """Fetch animals from Petfinder API."""
    url = "https://api.petfinder.com/v2/animals"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"type": type_filter, "limit": limit}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# --- Streamlit UI ---
st.set_page_config(page_title="PetFinder Tinder", page_icon="🐶", layout="wide")

st.title("🐾 PetFinder Tinder")
st.write("Swipe through adoptable dogs and find your perfect match!")

token = get_access_token()
animals = get_animals(token, type_filter="dog", limit=5)["animals"]

if "seen" not in st.session_state:
    st.session_state.seen = []

for animal in animals:
    with st.container():
        st.subheader(animal["name"])
        if animal["photos"]:
            st.image(animal["photos"][0]["medium"], width=300)
        else:
            st.write("📷 No photo available")

        st.write(f"**Breed:** {animal['breeds']['primary']}")
        st.write(f"**Age:** {animal['age']}")
        st.write(f"**Gender:** {animal['gender']}")
        st.write(f"**Location:** {animal['contact']['address']['city']}, {animal['contact']['address']['state']}")
        st.write(animal["description"] or "No description provided.")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Yes", key=f"yes-{animal['id']}"):
                st.session_state.seen.append((animal["id"], "yes"))
        with col2:
            if st.button("🤔 Maybe", key=f"maybe-{animal['id']}"):
                st.session_state.seen.append((animal["id"], "maybe"))
        with col3:
            if st.button("❌ No", key=f"no-{animal['id']}"):
                st.session_state.seen.append((animal["id"], "no"))

st.write("---")
st.subheader("Your Decisions")
st.json(st.session_state.seen)
