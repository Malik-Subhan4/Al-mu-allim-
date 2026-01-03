import streamlit as st
from groq import Groq
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder
import io

# Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
tts_client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])

st.title("Al-Mu'allim VA (Multi-Voice Edition)")

# --- VOICE SELECTION ---
# یہاں وہ تمام آوازیں ہیں جو آپ نے مانگی تھیں
voices = {
    "Adam": "6xIsTj2HwM6VR4iXFCw",
    "Jessica": "XJ2fW4ybq7HouelYYGcL",
    "Jerry": "IRHApOXLvnW57QJPQH2P",
    "Hoor": "1it2J1u0gF5RhXGlpRpW" # Purani voice
}
selected_voice = st.selectbox("Apni pasand ki awaz chunein:", list(voices.keys()))
voice_id = voices[selected_voice]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Mike Input
audio_input = mic_recorder(start_prompt="🎙️ Bolne ke liye click karein", stop_prompt="⏹️ Stop", key='recorder')
user_text = st.chat_input("Ya type karein...")

if audio_input and 'bytes' in audio_input:
    audio_file = io.BytesIO(audio_input['bytes'])
    audio_file.name = "audio.wav"
    user_text = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", response_format="text")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"): st.markdown(user_text)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
        answer = response.choices[0].message.content
        st.markdown(answer)
        
        # Voice Output with Selected Voice ID
        try:
            audio_gen = tts_client.text_to_speech.convert(
                voice_id=voice_id,
                text=answer,
                model_id="eleven_multilingual_v2"
            )
            st.audio(b"".join(list(audio_gen)), format='audio/mp3', autoplay=True)
        except Exception as e:
            st.error(f"Voice Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": answer})
      
