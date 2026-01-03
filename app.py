import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# --- Page Config ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="centered")

# --- Custom CSS for Green, Gold, and White Theme ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #004d40;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    h1 {
        color: #004d40;
        text-align: center;
        font-family: 'Serif';
    }
    .stButton>button {
        background-color: #D4AF37;
        color: white;
        border-radius: 20px;
        border: 1px solid #C0A12A;
    }
    .stChatMessage {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logo ---
# Replace this URL with your actual hosted logo link
LOGO_URL = "https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png"
st.image(LOGO_URL, use_container_width=True)

# --- API Setup ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    tts_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except Exception as e:
    st.error("API Keys missing in Secrets!")
    st.stop()

# --- Voice Selection ---
voices = {
    "Adam": "6xIsTj2HwM6VR4iXFCw",
    "Jessica": "XJ2fW4ybq7HouelYYGcL",
    "Jerry": "IRHApOXLvnW57QJPQH2P"
}
selected_voice = st.sidebar.selectbox("Select Voice:", list(voices.keys()))

# --- Chat Logic & Islamic System Prompt ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are Al-Mu'allim, an authentic Islamic AI. Only answer questions related to Islam using Quran, Sahih Hadith, and scholarly debates. If asked about non-Islamic topics, politely say you only provide Islamic guidance."
    }]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- Input Section ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", key='recorder')
user_text = st.chat_input("Ask an Islamic question...")

# Process Speech-to-Text
if audio_input and 'bytes' in audio_input:
    audio_file = io.BytesIO(audio_input['bytes'])
    audio_file.name = "audio.wav"
    user_text = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", response_format="text")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)

    with st.chat_message("assistant"):
        # AI Text Generation
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=st.session_state.messages,
            temperature=0.3
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        
        # Audio Generation
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
      
