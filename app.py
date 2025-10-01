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
        height: 50px;
        font-size: 1.1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .circle-button {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: none;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        margin: 10px auto;
        display: block;
        transition: transform 0.2s;
    }
    .circle-button:hover {
        transform: scale(1.05);
    }
    .circle-yes {
        background-color: #90EE90;
        color: #006400;
    }
    .circle-maybe {
        background-color: #FFD700;
        color: #8B6914;
    }
    .circle-no {
        background-color: #FFB6C1;
        color: #8B0000;
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
    with st.spinner("Loading adorable dogs..."):
        try:
            token = get_token()
            if token:
                st.session_state.dogs = fetch_dogs(token, location="85004", limit=10)
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Rate Limit" in error_msg:
                st.error("⏰ **API Rate Limit Reached!**\n\nThe Petfinder API has a rate limit. Please try again in a few minutes, or click below to load sample data.")
                if st.button("Load Sample Dogs (Demo Mode)"):
                    # Load sample data for testing
                    st.session_state.dogs = [
                        {
                            "id": "sample1",
                            "name": "Buddy",
                            "breed": "Golden Retriever Mix",
                            "age": "Young",
                            "gender": "Male",
                            "size": "Large",
                            "photo": "https://images.unsplash.com/photo-1633722715463-d30f4f325e24?w=500",
                            "description": "Meet Buddy! This lovable golden boy is full of energy and ready to be your best friend. He loves long walks, playing fetch, and belly rubs!",
                            "url": "https://www.petfinder.com"
                        },
                        {
                            "id": "sample2",
                            "name": "Luna",
                            "breed": "Husky Mix",
                            "age": "Adult",
                            "gender": "Female",
                            "size": "Medium",
                            "photo": "https://images.unsplash.com/photo-1568572933382-74d440642117?w=500",
                            "description": "Luna is a beautiful husky mix with striking blue eyes. She's adventurous, loyal, and would love a home with a big yard to explore!",
                            "url": "https://www.petfinder.com"
                        },
                        {
                            "id": "sample3",
                            "name": "Max",
                            "breed": "Labrador Retriever",
                            "age": "Senior",
                            "gender": "Male",
                            "size": "Large",
                            "photo": "https://images.unsplash.com/photo-1527526029430-319f10814151?w=500",
                            "description": "Max is a gentle senior lab looking for a quiet home to spend his golden years. He's calm, well-trained, and loves to cuddle on the couch.",
                            "url": "https://www.petfinder.com"
                        }
                    ]
                    st.rerun()
            else:
                st.error(f"Error loading dogs: {error_msg}")
            st.stop()

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
    
    # Create three-column layout (left: image+nav, middle: buttons, right: info)
    col_left, col_middle, col_right = st.columns([2, 1, 2], gap="medium")
    
    with col_left:
        # Navigation arrows and image
        nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])
        with nav_col1:
            st.markdown('<div style="padding-top: 200px;">', unsafe_allow_html=True)
            if st.button("⬅️", key="prev", disabled=st.session_state.index == 0):
                prev_dog()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with nav_col2:
            st.image(dog["photo"], use_container_width=True)
        
        with nav_col3:
            st.markdown('<div style="padding-top: 200px;">', unsafe_allow_html=True)
            if st.button("➡️", key="next", disabled=st.session_state.index >= len(st.session_state.dogs) - 1):
                next_dog()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"<center>Dog {st.session_state.index + 1} of {len(st.session_state.dogs)}</center>", unsafe_allow_html=True)
    
    with col_middle:
        # Vertically stacked circular buttons in the middle
        st.markdown("<div style='padding-top: 150px;'>", unsafe_allow_html=True)
        
        # Yes button
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
        """, unsafe_allow_html=True)
        if st.button("✓\nYes", key=f"yes_{dog_id}", use_container_width=True, type="primary"):
            rank_dog("yes")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Maybe button
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
        """, unsafe_allow_html=True)
        if st.button("?\nMaybe", key=f"maybe_{dog_id}", use_container_width=True, type="secondary"):
            rank_dog("maybe")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # No button
        st.markdown("""
            <div style='text-align: center; margin-bottom: 20px;'>
        """, unsafe_allow_html=True)
        if st.button("✗\nNo", key=f"no_{dog_id}", use_container_width=True, type="secondary"):
            rank_dog("no")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
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
