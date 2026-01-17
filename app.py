import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from streamlit_mic_recorder import mic_recorder
import io
import os

# --- 1. Page Config & PWA Manifest Link ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")
# This link is essential for PWABuilder to recognize your app
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
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- 4. Sidebar: Voice & Language Controls ---
with st.sidebar:
    st.image("https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png", use_container_width=True)
    
    # Multilingual Voice Selector
    lang_display = st.selectbox("Speech Language", 
                                ["English (Male)", "English (Female)", "Arabic (Saudi)", "Urdu (Pakistan)", "Hindi (India)"])
    
    # Voice Mapping
    voice_map = {
        "English (Male)": "en-US-GuyNeural",
        "English (Female)": "en-US-AriaNeural",
        "Arabic (Saudi)": "ar-SA-HamedNeural",
        "Urdu (Pakistan)": "ur-PK-AsadNeural",
        "Hindi (India)": "hi-IN-MadhurNeural"
    }
    selected_voice = voice_map[lang_display]
    voice_on = st.toggle("Enable Voice Response", value=True)

# --- 5. Voice Function (Free Edge-TTS) ---
async def text_to_speech_edge(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("response.mp3")

# --- 6. Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, an Islamic AI. Answer using Quran and Sahih Hadith. Keep answers concise."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 7. Input Handling ---
user_query = st.chat_input("Ask an Islamic question...")
audio_data = mic_recorder(start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", key='recorder')

if audio_data and 'bytes' in audio_data:
    audio_bio = io.BytesIO(audio_data['bytes'])
    audio_bio.name = "audio.wav"
    user_query = groq_client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3-turbo", response_format="text")

# --- 8. Processing & Response ---
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    with st.chat_message("assistant"):
        # AI Text Response
        res = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
        ans = res.choices[0].message.content
        st.markdown(ans)
        
        # Audio Response
        if voice_on:
            with st.spinner("Generating voice..."):
                asyncio.run(text_to_speech_edge(ans, selected_voice))
                st.audio("response.mp3", format='audio/mp3', autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": ans})
