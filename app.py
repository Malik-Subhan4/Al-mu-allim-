import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# 1. Page Config (Must be the very first Streamlit command)
st.set_page_config(page_title="Al-Mu'allim VA", page_icon="🕌", layout="wide")

# 2. Advanced Professional CSS
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    [data-testid="stSidebar"] { background-color: #013220 !important; border-right: 3px solid #D4AF37; }
    .main-header { color: #013220; text-align: center; font-family: 'Times New Roman', serif; font-size: 40px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
    .stChatMessage { background-color: white; border-radius: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); border-left: 5px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Branding
with st.sidebar:
    st.image("https://i.ibb.co/L952f4Y/Al-Muallim-Islamic-VA.png", use_container_width=True)
    st.markdown("<h2 style='color: #D4AF37; text-align: center;'>Al-Mu'allim</h2>", unsafe_allow_html=True)
    voice_on = st.toggle("Enable Voice Output", value=True)
    st.info("Ask any Islamic question from Quran and Hadith.")

st.markdown("<h1 class='main-header'>Al-Mu'allim Islamic Assistant</h1>", unsafe_allow_html=True)

# 4. Secure API Connection
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # If ElevenLabs fails, the app will still run
    try:
        el_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
    except:
        el_client = None
except Exception as e:
    st.error("API Secret Key Missing. Please check your Streamlit Settings.")
    st.stop()

# 5. Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are Al-Mu'allim, a specialized Islamic AI. Provide answers ONLY from authentic Quran and Sahih Hadith. Refuse non-Islamic topics."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

# 6. Optimized Input Bar
st.write("---")
col_text, col_mic = st.columns([10, 1])
with col_mic:
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder')
with col_text:
    user_input = st.chat_input("Enter your query...")

# Handle Input
if audio_data and 'bytes' in audio_data:
    with st.spinner("Transcribing..."):
        audio_bio = io.BytesIO(audio_data['bytes'])
        audio_bio.name = "audio.wav"
        user_input = groq_client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3-turbo", response_format="text")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        # Text Response
        chat_completion = groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, temperature=0.2)
        ans = chat_completion.choices[0].message.content
        st.markdown(ans)
        
        # Safe Voice Execution
        if voice_on and el_client:
            try:
                audio_stream = el_client.text_to_speech.convert(
                    voice_id="JBFqnCBv7vy9vWCvUCYd", # Using a highly available default voice
                    text=ans[:500],
                    model_id="eleven_multilingual_v2"
                )
                st.audio(b"".join(list(audio_stream)), format='audio/mp3', autoplay=True)
            except:
                st.caption("Audio unavailable at this moment.")

    st.session_state.messages.append({"role": "assistant", "content": ans})
      
