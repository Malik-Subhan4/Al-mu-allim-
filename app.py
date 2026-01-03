import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# --- Page Config ---
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #013220 !important; }
    .main-title { color: #013220; text-align: center; font-size: 40px; font-weight: bold; }
    .stChatMessage { border: 1px solid #D4AF37; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Al-Mu'allim Islamic VA</h1>", unsafe_allow_html=True)

# --- API Setup ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    tts_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
except Exception:
    st.error("Check your API Keys in Streamlit Secrets!")
    st.stop()

# --- Voice Settings ---
st.sidebar.header("Settings")
# Adding an option to disable voice if errors persist
use_voice = st.sidebar.toggle("Enable Voice Output", value=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, an Islamic AI. Provide answers ONLY from Quran and Sahih Hadith. Politely refuse non-Islamic topics."}]

# Display Chat
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- Inputs ---
st.write("---")
audio_input = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder')
user_text = st.chat_input("Enter your Islamic query...")

# Process Speech-to-Text
if audio_input and 'bytes' in audio_input:
    audio_file = io.BytesIO(audio_input['bytes'])
    audio_file.name = "audio.wav"
    user_text = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", response_format="text")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)

    with st.chat_message("assistant"):
        # 1. Generate Text Answer (This will work even if voice fails)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=st.session_state.messages,
            temperature=0.2
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
        
        # 2. Try Voice Output
        if use_voice:
            try:
                # Using a generic voice ID that is usually available by default
                audio_gen = tts_client.text_to_speech.convert(
                    voice_id="JBFqnCBv7vy9vWCvUCYd", # Changed to a default 'Chris' voice ID
                    text=answer,
                    model_id="eleven_multilingual_v2"
                )
                st.audio(b"".join(list(audio_gen)), format='audio/mp3', autoplay=True)
            except Exception as e:
                st.warning("Voice could not be played, but the answer is shown above.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
                                      
