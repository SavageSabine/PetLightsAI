import streamlit as st



from api_service import get_token

token = get_token()
if token is None:
    st.stop()  # Stop the app if auth failed


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
