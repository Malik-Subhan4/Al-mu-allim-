import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# --- Page Config ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")

# --- Custom CSS (Green, White, Gold) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #004d40 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-title { color: #004d40; text-align: center; font-size: 45px; font-weight: bold; margin-bottom: 0px; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 20px; width: 100%; }
    .stChatMessage { border: 1px solid #e0e0e0; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- Logo ---
LOGO_URL = "https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png"
st.image(LOGO_URL, width=300)
st.markdown("<h1 class='main-title'>Al-Mu'allim Islamic VA</h1>", unsafe_allow_html=True)

# --- API Setup ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    tts_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except Exception:
    st.error("Check your API Keys in Streamlit Secrets!")
    st.stop()

# --- Voice Selection (Using stable IDs) ---
# Note: "pNInz6obpg8ndOeao7jn" is a very stable default female voice.
voices = {
    "Default (Stable)": "pNInz6obpg8ndOeao7jn",
    "Jessica": "XJ2fW4ybq7HouelYYGcL",
    "Jerry": "IRHApOXLvnW57QJPQH2P"
}
selected_voice = st.sidebar.selectbox("Choose Assistant Voice:", list(voices.keys()))

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, an Islamic AI. Provide answers only based on authentic Quran and Hadith. Reject non-Islamic queries politely."}]

# Display Chat
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- Desktop Layout for Inputs ---
st.write("---")
col1, col2 = st.columns([1, 5])
with col1:
    audio_input = mic_recorder(start_prompt="🎙️ Ask", stop_prompt="⏹️ End", key='recorder')
with col2:
    user_text = st.chat_input("Type your Islamic question here...")

# Process Audio
if audio_input and 'bytes' in audio_input:
    audio_file = io.BytesIO(audio_input['bytes'])
    audio_file.name = "audio.wav"
    user_text = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", response_format="text")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, temperature=0.2)
        answer = response.choices[0].message.content
        st.markdown(answer)
        
        try:
            audio_gen = tts_client.text_to_speech.convert(
                voice_id=voices[selected_voice],
                text=answer,
                model_id="eleven_multilingual_v2"
            )
            st.audio(b"".join(list(audio_gen)), format='audio/mp3', autoplay=True)
        except Exception as e:
            st.error(f"Voice Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
