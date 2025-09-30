import streamlit as st

# --- Demo Data (replace with PetFinder API later) ---
dogs = [
    {
        "id": 1,
        "name": "Rockwell",
        "age": "Baby",
        "gender": "Boy",
        "breed": ["Pit Bull Terrier", "Mix"],
        "size": "Small",
        "status": "Adoptable",
        "description": """Hi, I’m Rockwell, and I’m bursting with energy, joy, and goofy charm!
I’m the kind of pup who’s always ready for action, whether it’s chasing a ball, exploring new places, or inventing silly games to keep us laughing. Life with me will never be boring. I bring excitement and fun to every moment.

Because I’m such a lively guy, I’ll do best with someone who can match my enthusiasm and help guide me with a little basic training. I’m still learning, but with patience and structure, I’ll shine. Right now, my energy might be a bit too much for small children, though there are no age restrictions: I just need a family who understands my playful spirit.

I do need to be the only dog in the home, but that just means I’ll be free to give you all my love, attention, and endless tail wags. If you’re looking for an adventure buddy and a loyal best friend who’s always on the go, I’m your guy!""",
        "photo": "https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/78348145/1/?bust=1737910576&width=600"
    },
    {
        "id": 2,
        "name": "Bella",
        "age": "Young",
        "gender": "Girl",
        "breed": ["Labrador Retriever"],
        "size": "Medium",
        "status": "Adoptable",
        "description": "Bella is a sweet, playful lab who loves the outdoors and snuggling after long walks.",
        "photo": "https://placedog.net/500/400?id=43"
    }
]

# --- Track state ---
if "dog_index" not in st.session_state:
    st.session_state.dog_index = 0
if "choices" not in st.session_state:
    st.session_state.choices = {}

dog = dogs[st.session_state.dog_index]

# --- UI Layout ---
st.set_page_config(page_title="Pet Lights AI", page_icon="🐶", layout="centered")

st.title("🐾 Pet Lights AI")

col_left, col_center, col_right = st.columns([1, 3, 1])

with col_center:
    # Dog card
    st.image(dog["photo"], width=350)
    st.subheader(dog["name"])

    st.markdown(f"**Animal:** Dog")
    st.markdown(f"**Age:** {dog['age']}")
    st.markdown(f"**Gender:** {dog['gender']}")

    # Breed expandable if multiple
    if len(dog["breed"]) > 1:
        with st.expander("Breed Info"):
            st.markdown(", ".join(dog["breed"]))
    else:
        st.markdown(f"**Breed:** {dog['breed'][0]}")

    st.markdown(f"**Size:** {dog['size']}")
    st.markdown(f"**Status:** {dog['status']}")

    # Description preview with popup
    short_desc = dog["description"][:120] + "..."
    with st.expander("Read Full Description"):
        st.write(dog["description"])
    st.caption(short_desc)

    # Stoplight buttons
    col_yes, col_maybe, col_no = st.columns(3)
    with col_yes:
        if st.button("🟢 Yes"):
            st.session_state.choices[dog["id"]] = "yes"
    with col_maybe:
        if st.button("🟡 Maybe"):
            st.session_state.choices[dog["id"]] = "maybe"
    with col_no:
        if st.button("🔴 No"):
            st.session_state.choices[dog["id"]] = "no"

# --- Navigation Arrows ---
with col_left:
    if st.button("⬅️"):
        st.session_state.dog_index = (st.session_state.dog_index - 1) % len(dogs)
with col_right:
    if st.button("➡️"):
        st.session_state.dog_index = (st.session_state.dog_index + 1) % len(dogs)

# --- User Decisions ---
st.divider()
st.subheader("Your Choices")
st.json(st.session_state.choices)
