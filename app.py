# app.py
import streamlit as st
from api_service import get_token, fetch_dogs

st.set_page_config(page_title="PetLights AI", page_icon="🐶", layout="centered")

st.title("🐾 PetLights AI - Find Your Perfect Dog")

# --- Session state setup ---
if "dogs" not in st.session_state:
    st.session_state.dogs = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "rankings" not in st.session_state:
    st.session_state.rankings = {}  # {dog_id: "yes/maybe/no"}

# --- Load dogs ---
if not st.session_state.dogs:
    token = get_token()
    if token:
        st.session_state.dogs = fetch_dogs(token, location="85004", limit=10)

# --- Navigation functions ---
def next_dog():
    if st.session_state.index < len(st.session_state.dogs) - 1:
        st.session_state.index += 1

def prev_dog():
    if st.session_state.index > 0:
        st.session_state.index -= 1

def rank_dog(choice):
    current_dog = st.session_state.dogs[st.session_state.index]
    st.session_state.rankings[current_dog["id"]] = choice
    next_dog()

# --- Display current dog ---
if st.session_state.dogs:
    dog = st.session_state.dogs[st.session_state.index]

    st.image(dog["photo"], width=350)
    st.subheader(dog["name"])
    st.write(f"**Breed:** {dog['breed']}")
    st.write(f"**Age:** {dog['age']}")
    st.write(f"**Gender:** {dog['gender']}")
    st.write(dog["description"])
    st.markdown(f"[View on Petfinder →]({dog['url']})")

    # Ranking buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❌ No", use_container_width=True):
            rank_dog("no")
    with col2:
        if st.button("🤔 Maybe", use_container_width=True):
            rank_dog("maybe")
    with col3:
        if st.button("✅ Yes", use_container_width=True):
            rank_dog("yes")

    # Navigation arrows
    col_left, col_mid, col_right = st.columns([1, 4, 1])
    with col_left:
        if st.button("⬅️ Prev"):
            prev_dog()
    with col_right:
        if st.button("➡️ Next"):
            next_dog()

    st.write(f"Viewing dog {st.session_state.index+1} of {len(st.session_state.dogs)}")

else:
    st.warning("No dogs found. Try refreshing or check your API credentials.")

# --- Saved rankings section ---
st.sidebar.header("📋 Your Choices")
if st.session_state.rankings:
    for dog_id, choice in st.session_state.rankings.items():
        dog = next(d for d in st.session_state.dogs if d["id"] == dog_id)
        st.sidebar.write(f"{dog['name']} → {choice}")
else:
    st.sidebar.write("No choices yet. Start swiping!")
