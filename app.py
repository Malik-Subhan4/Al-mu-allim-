import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# --- Desktop Page Configuration ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")

# --- Authentic Islamic Styling (Green, White, Gold) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #013220 !important; }
    [data-testid="stSidebar"] * { color: #D4AF37 !important; }
    .main-title { color: #013220; text-align: center; font-family: 'Georgia', serif; font-size: 50px; margin-top: -50px; }
    .stChatMessage { border-radius: 20px; border: 1px solid #D4AF37; }
    .stChatInputContainer { border: 2px solid #013220 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Logo and Title ---
LOGO_URL = "https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png"
col_logo, col_empty = st.columns([1, 2])
with col_logo:
    st.image(LOGO_URL, width=250)
st.markdown("<h1 class='main-title'>Al-Mu'allim Islamic VA</h1>", unsafe_allow_html=True)

# --- API Setup ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    tts_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except Exception:
    st.error("Please add your GROQ_API_KEY and ELEVENLABS_API_KEY to Streamlit Secrets.")
    st.stop()

# --- Voice Settings ---
# If specific IDs fail, we use a more generic selection method
st.sidebar.header("Settings")
voice_choice = st.sidebar.selectbox("Choose Voice Profile:", ["Male (Adam)", "Female (Jessica)", "Male (Jerry)"])

voice_map = {
    "Male (Adam)": "6xIsTj2HwM6VR4iXFCw",
    "Female (Jessica)": "XJ2fW4ybq7HouelYYGcL",
    "Male (Jerry)": "IRHApOXLvnW57QJPQH2P"
}

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Al-Mu'allim, an authentic Islamic scholar AI. Only answer questions related to Islam using the Quran and Sahih Hadith. For non-Islamic topics, politely state you only provide religious guidance."
    }]

# --- Desktop Chat Display ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- Interaction Bar ---
st.write("---")
input_col, mic_col = st.columns([10, 1])

with mic_col:
    audio_input = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder')

with input_col:
    user_text = st.chat_input("Enter your Islamic query...")

# Process Audio Input
if audio_input and 'bytes' in audio_input:
    audio_file = io.BytesIO(audio_input['bytes'])

