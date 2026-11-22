import streamlit as st
import speech_recognition as sr
import hashlib
import io
from groq import Groq

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Multilingual AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Multilingual AI Voice Assistant")
st.subheader("Your Personal AI Assistant")

st.write(
    "Ask questions about studies, coding, AI, business, "
    "technology, shopping, career, or everyday life."
)

# ---------------- API CONNECTION ----------------

try:
    groq_client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )
except Exception:
    st.error("Groq API key is missing. Please add it in Streamlit Secrets.")
    st.stop()

# ---------------- LANGUAGE ----------------

language = st.selectbox(
    "Choose your language:",
    ["English", "Hindi", "Gujarati"]
)

language_codes = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Gujarati": "gu-IN"
}

# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

# ---------------- CLEAR CHAT ----------------

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.last_audio_hash = None
    st.rerun()

# ---------------- DISPLAY CHAT ----------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- AI RESPONSE FUNCTION ----------------

def get_ai_response(user_message):

    system_prompt = f"""
    You are a helpful multilingual AI voice assistant.

    Respond in {language}.

    You can help with:
    - Education and studies
    - Python programming and coding
    - Artificial Intelligence
    - Data Science and Data Analysis
    - Business and technology
    - Shopping
    - Career guidance
    - Finance
    - General knowledge
    - Everyday questions

    Give clear, useful and easy-to-understand answers.
    If the user asks in Hindi, respond in Hindi.
    If the user asks in Gujarati, respond in Gujarati.
    Keep answers reasonably concise.
    """

    recent_messages = st.session_state.messages[-8:]

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(recent_messages)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error connecting to AI: {e}"

# ---------------- TEXT CHAT ----------------

user_input = st.chat_input("Type your question here...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("AI is thinking..."):
            answer = get_ai_response(user_input)

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# ---------------- VOICE INPUT ----------------

st.divider()

st.subheader("🎤 Speak to your AI Assistant")

audio_file = st.audio_input("Record your question")

if audio_file:

    audio_bytes = audio_file.getvalue()

    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if audio_hash != st.session_state.last_audio_hash:

        st.session_state.last_audio_hash = audio_hash

        recognizer = sr.Recognizer()

        try:

            audio_data = sr.AudioFile(
                io.BytesIO(audio_bytes)
            )

            with audio_data as source:
                audio = recognizer.record(source)

            with st.spinner("Listening and converting speech to text..."):

                spoken_text = recognizer.recognize_google(
                    audio,
                    language=language_codes[language]
                )

            st.success("Speech recognized successfully!")

            st.write("*You said:*")
            st.write(spoken_text)

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": spoken_text
                }
            )

            with st.chat_message("assistant"):

                with st.spinner("AI is thinking..."):

                    answer = get_ai_response(spoken_text)

                st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your voice. Please try again.")

        except sr.RequestError:
            st.error("Speech recognition service is unavailable. Please try again.")

        except Exception as e:
            st.error(f"Voice error: {e}")
