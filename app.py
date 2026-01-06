import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from streamlit_mic_recorder import mic_recorder
import io
import os

# --- 1. Page Config & PWA Manifest ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")
# This link helps PWABuilder find your manifest file in the static folder
st.markdown('<link rel="manifest" href="/app/static/manifest.json">', unsafe_allow_html=True)

# --- 2. Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F8F8; }
    [data-testid="stSidebar"] { background-color: #013220 !important; }
    .main-header { color: #013220; text-align: center; font-size: 32px; font-weight: bold; border-bottom: 2px solid #D4AF37; }
    .stChatMessage { border-radius: 10px; border: 1px solid #D4AF37; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Al-Mu'allim Islamic VA</h1>", unsafe_allow_html=True)

# --- 3. API Initialization ---
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# --- 4. Voice Function (Free Edge-TTS) ---
async def text_to_speech_edge(text):
    # 'en-US-GuyNeural' is a professional, free Microsoft voice
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save("response.mp3")

# --- 5. Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, an Islamic AI. Answer using Quran and Sahih Hadith. Keep answers concise."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 6. User Inputs (Voice & Text) ---
user_query = st.chat_input("Ask an Islamic question...")
audio_data = mic_recorder(start_prompt="🎙️ Click to Speak", stop_prompt="⏹️ Stop", key='recorder')

if audio_data and 'bytes' in audio_data:
    audio_bio = io.BytesIO(audio_data['bytes'])
    audio_bio.name = "audio.wav"
    user_query = groq_client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3-turbo", response_format="text")

# --- 7. Response Logic ---
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        # Text Generation
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
        ans = res.choices[0].message.content
        st.markdown(ans)
        
        # Audio Generation (Free & Unlimited)
        with st.spinner("Preparing voice..."):
            asyncio.run(text_to_speech_edge(ans))
            st.audio("response.mp3", format='audio/mp3', autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": ans})
                                 
