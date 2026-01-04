import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# --- Page Configuration ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F8F8; }
    [data-testid="stSidebar"] { background-color: #013220 !important; }
    .main-header { color: #013220; text-align: center; font-size: 35px; font-weight: bold; border-bottom: 2px solid #D4AF37; }
    .stChatMessage { border-radius: 10px; border: 1px solid #D4AF37; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Al-Mu'allim Islamic VA</h1>", unsafe_allow_html=True)

# --- API Initialization ---
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # Initialize ElevenLabs safely
    try:
        el_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
    except:
        el_client = None
except Exception:
    st.error("Missing API Keys in Secrets.")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.image("https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png", use_container_width=True)
    voice_on = st.checkbox("Enable Audio Response", value=True)
    st.info("Using standard quality voice for better stability.")

# --- Chat State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, an Islamic AI assistant. Answer using Quran and Sahih Hadith. Keep answers concise."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- Inputs ---
user_query = st.chat_input("Ask an Islamic question...")
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder')

if audio_data and 'bytes' in audio_data:
    audio_bio = io.BytesIO(audio_data['bytes'])
    audio_bio.name = "audio.wav"
    user_query = groq_client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3-turbo", response_format="text")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        # Generate Text Response
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
        ans = res.choices[0].message.content
        st.markdown(ans)
        
        # Audio Generation (Standard Voice)
        if voice_on and el_client:
            try:
                # 'cgSgSjS2KiW0W2uMQR7Ge' is a reliable default voice ID
                audio_stream = el_client.text_to_speech.convert(
                    voice_id="cgSgSjS2KiW0W2uMQR7Ge", 
                    text=ans[:300], # Keep it short for better reliability
                    model_id="eleven_multilingual_v2"
                )
                st.audio(b"".join(list(audio_stream)), format='audio/mp3', autoplay=True)
            except Exception:
                st.caption("Standard voice generation skipped due to account activity limits.")

    st.session_state.messages.append({"role": "assistant", "content": ans})
      
