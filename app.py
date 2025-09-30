"""
app.py - PetMatch Streamlit app
Features:
- Tinder-style browsing of Petfinder animals
- "Yes / Maybe / No" buttons plus keyboard shortcuts (Y/M/N)
- Save and export chosen pets, generate a report
- Adoption Resources tab with Q/A assistant (simple heuristics; optional OpenAI integration)
Notes:
- Install dependencies: streamlit, requests
- Set PETFINDER_BEARER_TOKEN in Streamlit secrets or env, or provide PETFINDER_KEY and PETFINDER_SECRET to fetch a token
- Optional: set OPENAI_API_KEY in secrets to use OpenAI for richer Q/A
"""

import streamlit as st
import requests
import time
import json
from typing import Dict, Any, List, Optional
import base64
import textwrap
import streamlit.components.v1 as components

# -----------------------------
# Configuration / Helpers
# -----------------------------
PETFINDER_TOKEN = st.secrets.get("PETFINDER_BEARER_TOKEN") or st.secrets.get("PETFINDER_TOKEN")
PETFINDER_KEY = st.secrets.get("PETFINDER_KEY")
PETFINDER_SECRET = st.secrets.get("PETFINDER_SECRET")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

PETFINDER_TOKEN_URL = "https://api.petfinder.com/v2/oauth2/token"
PETFINDER_ANIMALS_URL = "https://api.petfinder.com/v2/animals"

HEADERS = {}
if PETFINDER_TOKEN:
    HEADERS = {"Authorization": f"Bearer {PETFINDER_TOKEN}"}

st.set_page_config(page_title="PetMatch — Petfinder Tinder", layout="wide")

# -----------------------------
# Utility functions
# -----------------------------
def get_petfinder_token(key: str, secret: str) -> Optional[str]:
    """Exchange client id/secret for a bearer token (valid for a while)."""
    try:
        payload = {"grant_type": "client_credentials", "client_id": key, "client_secret": secret}
        r = requests.post(PETFINDER_TOKEN_URL, data=payload, timeout=10)
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        st.warning(f"Could not get Petfinder token: {e}")
        return None

def fetch_animals(page: int = 1, location: str = None, page_size: int = 12, type_: str = "dog") -> Dict[str, Any]:
    """Fetch animals from Petfinder. Returns JSON or empty dict on error."""
    global HEADERS
    if not HEADERS.get("Authorization") and PETFINDER_KEY and PETFINDER_SECRET:
        token = get_petfinder_token(PETFINDER_KEY, PETFINDER_SECRET)
        if token:
            HEADERS["Authorization"] = f"Bearer {token}"
    params = {"page": page, "limit": page_size, "type": type_}
    if location:
        params["location"] = location
    try:
        r = requests.get(PETFINDER_ANIMALS_URL, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Failed to fetch animals: {e}")
        return {}

def summarize_animal(an: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Petfinder animal JSON into a clean summary dict for display."""
    summary = {}
    summary["id"] = an.get("id")
    summary["name"] = an.get("name")
    summary["age"] = an.get("age")
    summary["size"] = an.get("size")
    summary["gender"] = an.get("gender")
    breeds = an.get("breeds", {})
    summary["breeds"] = ", ".join([b for b in [breeds.get("primary"), breeds.get("secondary")] if b])
    summary["photos"] = [p["medium"] for p in an.get("photos", []) if p.get("medium")]
    summary["primary_photo"] = summary["photos"][0] if summary["photos"] else None
    summary["description"] = an.get("description") or ""
    contact = an.get("contact", {})
    summary["city"] = contact.get("address", {}).get("city")
    summary["state"] = contact.get("address", {}).get("state")
    summary["email"] = contact.get("email")
    summary["phone"] = contact.get("phone")
    summary["status"] = an.get("status")
    attributes = an.get("attributes", {})
    # Common user-facing flags
    summary["good_with_kids"] = attributes.get("children")
    summary["good_with_dogs"] = attributes.get("dogs")
    summary["good_with_cats"] = attributes.get("cats")
    summary["house_trained"] = attributes.get("house_trained")
    summary["special_needs"] = an.get("status") == "adopted" and (an.get("attributes", {}).get("special_needs") or False)
    summary["url"] = an.get("url")
    summary["distance"] = an.get("distance")  # if search by location provided
    summary["tags"] = []
    # build tags
    if summary["age"]:
        summary["tags"].append(summary["age"])
    if summary["size"]:
        summary["tags"].append(summary["size"])
    if summary["breeds"]:
        summary["tags"].append(summary["breeds"].split(",")[0])
    return summary

def animal_card_markdown(s: Dict[str, Any]) -> str:
    """Return a markdown block showing the animal info succinctly."""
    parts = []
    header = f"### {s.get('name', 'Unknown')} — {s.get('breeds','')}"
    parts.append(header)
    meta = f"**Age:** {s.get('age','Unknown')}  \n**Size:** {s.get('size','Unknown')}  \n**Gender:** {s.get('gender','Unknown')}"
    parts.append(meta)
    loc = f"**Location:** {s.get('city','?')}, {s.get('state','?')}  "
    if s.get("distance"):
        loc += f"({s.get('distance')} miles)"
    parts.append(loc)
    tags = s.get("tags", [])
    if tags:
        parts.append("**Tags:** " + ", ".join(tags))
    if s.get("description"):
        desc = s["description"]
        # short preview
        parts.append("**About:** " + (desc if len(desc) < 350 else desc[:347] + "..."))
    contact = []
    if s.get("email"):
        contact.append(f"Email: {s['email']}")
    if s.get("phone"):
        contact.append(f"Phone: {s['phone']}")
    if contact:
        parts.append("**Contact:** " + " • ".join(contact))
    parts.append(f"[View on Petfinder]({s.get('url','')})")
    return "\n\n".join(parts)

def save_selection(selection: Dict[str, Any], bucket: str):
    """Save selection into st.session_state lists."""
    if "saved" not in st.session_state:
        st.session_state["saved"] = {"yes": [], "maybe": [], "no": []}
    st.session_state["saved"][bucket].append(selection)

def export_report() -> str:
    """Create a user-friendly report (markdown) and machine-readable JSON."""
    saved = st.session_state.get("saved", {"yes": [], "maybe": [], "no": []})
    md_lines = []
    md_lines.append("# PetMatch Report")
    md_lines.append(f"Generated: {time.ctime()}")
    md_lines.append("## Interested / Yes")
    for s in saved["yes"]:
        md_lines.append(f"- **{s.get('name')}** — {s.get('breeds','')}. Link: {s.get('url')}")
    md_lines.append("\n## Maybe")
    for s in saved["maybe"]:
        md_lines.append(f"- **{s.get('name')}** — {s.get('breeds','')}. Link: {s.get('url')}")
    md_lines.append("\n## No")
    for s in saved["no"]:
        md_lines.append(f"- **{s.get('name')}** — {s.get('breeds','')}. Link: {s.get('url')}")
    # user preferences
    prefs = st.session_state.get("prefs", {})
    if prefs:
        md_lines.append("\n## User Preferences")
        md_lines.append("Tags: " + ", ".join(prefs.get("tags", [])))
        md_lines.append("Notes: " + prefs.get("notes", ""))
    md_md = "\n\n".join(md_lines)
    report_json = {"meta": {"generated": time.time()}, "saved": saved, "prefs": prefs}
    st.session_state["_last_report"] = {"md": md_md, "json": report_json}
    return md_md

def download_string_as_file(content: str, filename: str) -> str:
    """Return a markdown link to download a string as a file."""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

# -----------------------------
# UI: Key capture (Y/M/N) with JS -> Streamlit
# -----------------------------
def key_capture_js():
    # Use a tiny JS snippet to capture keypresses and put them into a hidden input that Streamlit reads.
    js = """
    <script>
    const send = (k) => {
        const el = window.parent.document.querySelector('[data-keyfield]');
        if(el){
            el.value = k;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };
    document.addEventListener('keydown', (e) => {
        // Ignore if focus is on text input or textarea
        const active = document.activeElement;
        if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
            return;
        }
        if (e.key === 'y' || e.key === 'Y') send('y');
        if (e.key === 'm' || e.key === 'M') send('m');
        if (e.key === 'n' || e.key === 'N') send('n');
        if (e.key === 'd' || e.key === 'D') send('d');
        if (e.key === 's' || e.key === 'S') send('s');
    });
    </script>
    """
    components.html(js, height=0, scrolling=False)

# -----------------------------
# Main UI Layout
# -----------------------------
st.title("🐶 PetMatch — Find your next dog (Petfinder)")
st.write("Browse adoptable dogs in a Tinder-style interface. Use Y / M / N keys or the buttons to rate.")

# sidebar: search + prefs
with st.sidebar:
    st.header("Search & Preferences")
    location = st.text_input("Location (city, zip, or city, state)", value="Phoenix, AZ")
    page_size = st.slider("Cards per page", 6, 24, 12, 6)
    st.markdown("**Quick preferences (tags)** — add short words like: 'kid-friendly', 'apartment', 'active'")
    tags_str = st.text_input("Comma-separated tags", value="")
    notes = st.text_area("Short notes about what you want (optional)", value="", height=80)
    if "prefs" not in st.session_state:
        st.session_state["prefs"] = {"tags": [], "notes": ""}
    if st.button("Save preferences"):
        st.session_state["prefs"]["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
        st.session_state["prefs"]["notes"] = notes
        st.success("Preferences saved.")
    st.markdown("---")
    st.markdown("**Saved picks**")
    if st.button("Open saved picks"):
        st.experimental_set_query_params(tab="saved")
    if st.button("Export report (download)"):
        md = export_report()
        st.markdown(download_string_as_file(md, "petmatch_report.md"), unsafe_allow_html=True)
    st.markdown("**App notes**")
    st.markdown(textwrap.dedent("""
    - Keyboard shortcuts: Y = Yes, M = Maybe, N = No.
    - D = Download last report, S = open saved picks.
    - You must set a Petfinder token in Streamlit secrets as `PETFINDER_BEARER_TOKEN` or `PETFINDER_KEY`/`PETFINDER_SECRET`.
    - Optional: set `OPENAI_API_KEY` to enable richer Q/A (not required).
    """))

# Tabs
tab = st.sidebar.radio("Go to", ["Browse", "Resources", "Saved / Report", "Debug"])
if tab == "Browse":
    # fetch animals
    page = st.sidebar.number_input("API page", min_value=1, value=1)
    with st.spinner("Fetching animals..."):
        animals_json = fetch_animals(page=page, location=location, page_size=page_size)
    animals_list = animals_json.get("animals", []) if animals_json else []
    if not animals_list:
        st.info("No animals returned. Check your token or search criteria.")
    else:
        # set up session state index
        if "index" not in st.session_state:
            st.session_state["index"] = 0
        if "animals" not in st.session_state or st.session_state.get("_animals_page") != page:
            st.session_state["animals"] = [summarize_animal(a) for a in animals_list]
            st.session_state["_animals_page"] = page
            st.session_state["index"] = 0

        # hidden input for key capture
        if "keyfield" not in st.session_state:
            st.session_state["keyfield"] = ""
        # render key capture field
        key_html = '<input data-keyfield type="hidden" value="" />'
        components.html(key_html, height=0)
        key_capture_js()
        # read hidden value via streamlit text_input bound to session (workaround)
        # We use st.text_input linked to st.session_state['keyfield'] to receive JS writes.
        k = st.text_input("", key="keyfield", value="", label_visibility="collapsed")
        # process keyboard actions
        last_action = None
        if k:
            kk = k.lower().strip()
            # clear it to avoid repeated triggers
            st.session_state["keyfield"] = ""
            if kk == "y":
                last_action = "yes"
            elif kk == "m":
                last_action = "maybe"
            elif kk == "n":
                last_action = "no"
            elif kk == "d":
                # download report
                md = export_report()
                st.markdown(download_string_as_file(md, "petmatch_report.md"), unsafe_allow_html=True)
                last_action = None
            elif kk == "s":
                st.experimental_set_query_params(tab="saved")
                last_action = None

        # show current animal(s) card stack
        animals = st.session_state["animals"]
        idx = st.session_state["index"]
        if idx >= len(animals):
            st.info("You've reached the end of this page of animals. Change page or search to see more.")
        else:
            a = animals[idx]
            # layout: image left, info right
            cols = st.columns([1, 2])
            with cols[0]:
                if a.get("primary_photo"):
                    st.image(a["primary_photo"], use_column_width=True, caption=a.get("name"))
                else:
                    st.empty()
            with cols[1]:
                st.markdown(animal_card_markdown(a))
                st.markdown("---")
                st.write("Rate this pet:")
                c1, c2, c3 = st.columns([1,1,1])
                if c1.button("✅ Yes (Y)"):
                    last_action = "yes"
                if c2.button("🤔 Maybe (M)"):
                    last_action = "maybe"
                if c3.button("❌ No (N)"):
                    last_action = "no"

            # handle action
            if last_action in ("yes","maybe","no"):
                save_selection(a, last_action)
                st.success(f"Saved to '{last_action.upper()}'")
                st.session_state["index"] = st.session_state["index"] + 1

            # small quick preference entry
            with st.expander("Quick preference tags (used to refine recommendations)"):
                new_tags = st.text_input("Add tags (comma separated)", key=f"pref_newtags_{idx}")
                if st.button("Add tags to prefs", key=f"addtags_{idx}"):
                    toks = [t.strip() for t in new_tags.split(",") if t.strip()]
                    st.session_state.setdefault("prefs", {"tags": [], "notes": ""})
                    st.session_state["prefs"]["tags"] = list(set(st.session_state["prefs"]["tags"] + toks))
                    st.success("Tags added to preferences.")

if tab == "Resources":
    st.header("Adoption & Post-Adoption Resources")
    st.markdown("""
    Ask a question about preparing for adoption, training, health & care, house training, socialization, or behavior.
    - If you provide `OPENAI_API_KEY` in Streamlit secrets, the assistant will use it to generate more personalized answers.
    - Otherwise the assistant will use built-in curated guidance.
    """)

    question = st.text_area("Ask a question (example: 'My 8-month-old terrier is whining when I leave — what should I do?')", height=120)
    if st.button("Get help"):
        if not question.strip():
            st.info("Type a question first.")
        else:
            # if OPENAI_API_KEY is present, optionally call OpenAI (code left as comment for developer)
            if OPENAI_API_KEY:
                try:
                    import openai
                    openai.api_key = OPENAI_API_KEY
                    prompt = f"You are PetMatch, an empathetic adoption assistant. Provide concise actionable steps for this question:\n\n{question}\n\nInclude quick steps and when to seek a vet/behaviorist."
                    resp = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[{"role":"user","content":prompt}],
                        max_tokens=400,
                        temperature=0.7
                    )
                    answer = resp["choices"][0]["message"]["content"]
                    st.markdown("**AI Answer (OpenAI):**")
                    st.write(answer)
                except Exception as e:
                    st.error(f"OpenAI request failed: {e}")
                    st.markdown("**Fallback Guidance:**")
                    st.write(fallback_guidance(question))
            else:
                st.markdown("**Advice (built-in guidance):**")
                st.write(fallback_guidance(question))

    st.markdown("---")
    st.subheader("Quick Guides")
    st.markdown("""
    **House training quick steps**
    1. Set a schedule (every 2-3 hours, after meals, waking).
    2. Use a consistent cue and reward.
    3. Crate at night and when unsupervised.
    4. If accidents happen, clean enzymatically and avoid punishment.

    **Separation anxiety**
    - Start with short departures (minutes) and gradually increase.
    - Provide enrichment (puzzle toys) before leaving.
    - Avoid dramatic departures/arrivals.
    - If severe, consult a certified behaviorist.

    **Basic socialization**
    - Positive, controlled exposures to people, surfaces, and other dogs.
    - Focus on reward-based approaches.
    """)

if tab == "Saved / Report":
    st.header("Saved picks & Reports")
    saved = st.session_state.get("saved", {"yes": [], "maybe": [], "no": []})
    st.subheader("Yes / Interested")
    for s in saved["yes"]:
        st.markdown(f"- **{s.get('name')}** — {s.get('breeds')} — [Listing]({s.get('url')})")
    st.subheader("Maybe")
    for s in saved["maybe"]:
        st.markdown(f"- **{s.get('name')}** — {s.get('breeds')} — [Listing]({s.get('url')})")
    st.subheader("No")
    for s in saved["no"]:
        st.markdown(f"- **{s.get('name')}** — {s.get('breeds')} — [Listing]({s.get('url')})")

    if st.button("Generate report (preview)"):
        md = export_report()
        st.markdown("### Report Preview")
        st.markdown(md)
        st.markdown(download_string_as_file(md, "petmatch_report.md"), unsafe_allow_html=True)

    if st.button("Clear saved picks (all)"):
        st.session_state["saved"] = {"yes": [], "maybe": [], "no": []}
        st.success("Saved picks cleared.")

if tab == "Debug":
    st.header("Debug / Token Info")
    st.write("Petfinder token present:", bool(HEADERS.get("Authorization")))
    st.write("Optional OpenAI key present:", bool(OPENAI_API_KEY))
    st.write("Session state snapshot:")
    st.json({
        "index": st.session_state.get("index"),
        "animals_count": len(st.session_state.get("animals", [])),
        "saved": {k: len(v) for k,v in st.session_state.get("saved", {"yes":[],"maybe":[],"no":[]}).items()},
        "prefs": st.session_state.get("prefs")
    })


# -----------------------------
# Fallback simple guidance function
# -----------------------------
def fallback_guidance(question: str) -> str:
    """Return a simple rule-based guidance summary for common topics."""
    q = question.lower()
    out = []
    if "house" in q or "potty" in q or "bathroom" in q or "toilet" in q:
        out.append("House training steps: set hourly schedule, take outside after sleeping/eating/playing, reward immediately when they eliminate outside, supervise and crate when unsupervised. Use enzymatic cleaner on accidents.")
    if "separat" in q or "alone" in q or "whin" in q or "anxiety" in q:
        out.append("Separation anxiety: practice short departures, build up time away gradually, provide enrichment, remain low-key on leave/return, and consult a behaviorist if your dog's reaction is extreme (destructive behavior, self-harm).")
    if "chew" in q or "chewing" in q:
        out.append("Destructive chewing: ensure physical & mental exercise, redirect to chew-appropriate toys, use deterrents on dangerous items, crate for safety when unsupervised. If chewing is extreme, check for dental issues or anxiety.")
    if "food" in q or "eat" in q or "feeding" in q:
        out.append("Feeding: use recommended food for dog size & age, avoid overfeeding. If picky or losing weight, consult a vet.")
    if not out:
        out.append("General tip: describe the behavior, frequency, triggers, and environment. For medical concerns or severe behavior problems, contact your vet or a certified behaviorist. For practical help, ask about routines, exercise, feeding, or socialization and provide your dog's age, breed, and a short description.")
    return "\n\n".join(out)

# -----------------------------
# End of file
# -----------------------------
