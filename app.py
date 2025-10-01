# app.py
import streamlit as st
from api_service import get_token, fetch_dogs

st.set_page_config(page_title="PetLights AI", page_icon="🐶", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #2c5f7c;
        margin-bottom: 2rem;
        font-family: 'Arial', sans-serif;
    }
    .dog-name {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c5f7c;
        margin-bottom: 1rem;
    }
    .info-label {
        font-weight: bold;
        color: #2c5f7c;
        font-size: 1.1rem;
    }
    .info-value {
        font-size: 1.1rem;
        color: #333;
    }
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 1.5rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .nav-button > button {
        width: 100%;
        height: 50px;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Session state setup ---
if "dogs" not in st.session_state:
    st.session_state.dogs = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "rankings" not in st.session_state:
    st.session_state.rankings = {}
if "show_breed_info" not in st.session_state:
    st.session_state.show_breed_info = False
if "show_description" not in st.session_state:
    st.session_state.show_description = False

# --- Load dogs ---
if not st.session_state.dogs:
    token = get_token()
    if token:
        st.session_state.dogs = fetch_dogs(token, location="85004", limit=10)

# --- Functions ---
def rank_dog(choice):
    dog = st.session_state.dogs[st.session_state.index]
    st.session_state.rankings[dog["id"]] = choice
    if st.session_state.index < len(st.session_state.dogs) - 1:
        st.session_state.index += 1
        st.session_state.show_breed_info = False
        st.session_state.show_description = False

def prev_dog():
    if st.session_state.index > 0:
        st.session_state.index -= 1
        st.session_state.show_breed_info = False
        st.session_state.show_description = False

def next_dog():
    if st.session_state.index < len(st.session_state.dogs) - 1:
        st.session_state.index += 1
        st.session_state.show_breed_info = False
        st.session_state.show_description = False

# --- Main Title ---
st.markdown('<div class="main-title">Pet Lights AI</div>', unsafe_allow_html=True)

# --- Display current dog ---
if st.session_state.dogs:
    dog = st.session_state.dogs[st.session_state.index]
    dog_id = dog["id"]
    
    # Create two-column layout
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        # Dog image
        st.image(dog["photo"], use_container_width=True)
        
        # Navigation arrows below image
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            st.markdown('<div class="nav-button">', unsafe_allow_html=True)
            if st.button("⬅️", key="prev", disabled=st.session_state.index == 0, use_container_width=True):
                prev_dog()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with nav_col2:
            st.markdown(f"<center style='padding-top: 10px;'>Dog {st.session_state.index + 1} of {len(st.session_state.dogs)}</center>", unsafe_allow_html=True)
        
        with nav_col3:
            st.markdown('<div class="nav-button">', unsafe_allow_html=True)
            if st.button("➡️", key="next", disabled=st.session_state.index >= len(st.session_state.dogs) - 1, use_container_width=True):
                next_dog()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        # Dog name
        st.markdown(f'<div class="dog-name">{dog["name"]}</div>', unsafe_allow_html=True)
        
        # Dog info
        st.markdown(f'<span class="info-label">Animal:</span> <span class="info-value">Dog</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="info-label">Age:</span> <span class="info-value">{dog["age"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="info-label">Gender:</span> <span class="info-value">{dog["gender"]}</span>', unsafe_allow_html=True)
        
        # Breed with expander
        breed_display = dog["breed"] if len(dog["breed"]) < 50 else dog["breed"][:47] + "..."
        if st.button(f"🔽 Breed: {breed_display}", key=f"breed_{dog_id}", use_container_width=True):
            st.session_state.show_breed_info = not st.session_state.show_breed_info
            st.rerun()
        
        if st.session_state.show_breed_info:
            st.info(f"**Full Breed Info:**\n\n{dog['breed']}\n\n*Click button again to close*")
        
        st.markdown(f'<span class="info-label">Size:</span> <span class="info-value">{dog.get("size", "Unknown")}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="info-label">Status:</span> <span class="info-value">ADOPTABLE</span>', unsafe_allow_html=True)
        
        # Description with expander
        description_preview = dog["description"][:100] + "..." if len(dog["description"]) > 100 else dog["description"]
        st.markdown(f'<span class="info-label">Description:</span>', unsafe_allow_html=True)
        st.write(description_preview)
        
        if st.button("📖 Click for full description", key=f"desc_{dog_id}", use_container_width=True):
            st.session_state.show_description = not st.session_state.show_description
            st.rerun()
        
        if st.session_state.show_description:
            with st.expander("Full Description", expanded=True):
                st.write(dog["description"])
        
        st.markdown("---")
        
        # Ranking buttons (traffic light style)
        rank_col1, rank_col2, rank_col3 = st.columns(3)
        
        with rank_col1:
            if st.button("🔴 No", key=f"no_{dog_id}", type="secondary"):
                rank_dog("no")
                st.rerun()
        
        with rank_col2:
            if st.button("🟡 Maybe", key=f"maybe_{dog_id}", type="secondary"):
                rank_dog("maybe")
                st.rerun()
        
        with rank_col3:
            if st.button("🟢 Yes", key=f"yes_{dog_id}", type="primary"):
                rank_dog("yes")
                st.rerun()
        
        # Link to Petfinder
        st.markdown(f"[View full profile on Petfinder →]({dog['url']})")

else:
    st.warning("No dogs found. Try refreshing or check your API credentials.")

# --- Sidebar: Saved rankings ---
st.sidebar.header("📋 Your Choices")
if st.session_state.rankings:
    yes_dogs = []
    maybe_dogs = []
    no_dogs = []
    
    for dog_id, choice in st.session_state.rankings.items():
        dog = next((d for d in st.session_state.dogs if d["id"] == dog_id), None)
        if dog:
            if choice == "yes":
                yes_dogs.append(dog["name"])
            elif choice == "maybe":
                maybe_dogs.append(dog["name"])
            else:
                no_dogs.append(dog["name"])
    
    if yes_dogs:
        st.sidebar.markdown("**🟢 Yes:**")
        for name in yes_dogs:
            st.sidebar.write(f"  • {name}")
    
    if maybe_dogs:
        st.sidebar.markdown("**🟡 Maybe:**")
        for name in maybe_dogs:
            st.sidebar.write(f"  • {name}")
    
    if no_dogs:
        st.sidebar.markdown("**🔴 No:**")
        for name in no_dogs:
            st.sidebar.write(f"  • {name}")
else:
    st.sidebar.write("No choices yet. Start swiping!")
