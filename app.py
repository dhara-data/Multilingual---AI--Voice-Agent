import streamlit as st
import ollama
import speech_recognition as sr
import io
import hashlib

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Multilingual AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# ---------------- TITLE ----------------

st.title("🎙️ Multilingual AI Voice Assistant")
st.subheader("Your Personal AI Assistant")

st.write(
    "Ask me anything about studies, coding, AI, business, "
    "technology, shopping, career, or everyday life."
)

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_audio" not in st.session_state:
    st.session_state.processed_audio = None

if "voice_question" not in st.session_state:
    st.session_state.voice_question = None

# ---------------- SETTINGS ----------------

language = st.selectbox(
    "🌐 Choose your language",
    ["English", "Hindi", "Gujarati"]
)

model_name = st.text_input(
    "🤖 Ollama Model",
    value="qwen2.5:3b"
)

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.voice_question = None
    st.session_state.processed_audio = None
    st.rerun()

# ---------------- LANGUAGE INSTRUCTION ----------------

if language == "English":
    language_instruction = "Reply in English."

elif language == "Hindi":
    language_instruction = "Reply in Hindi."

else:
    language_instruction = "Reply in Gujarati."

# ---------------- SYSTEM PROMPT ----------------

system_prompt = f"""
You are a helpful multilingual AI assistant.

You can answer questions about:
Education, Python, AI, Data Science, Machine Learning,
Technology, Business, Shopping, Finance, Career,
General Knowledge and everyday life.

Do not restrict yourself to one topic.

{language_instruction}

Keep answers clear, useful and easy to understand.
Avoid unnecessary long answers unless the user requests detail.
For coding questions, provide working code.
"""

# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- VOICE INPUT ----------------

st.subheader("🎤 Voice Input")

audio = st.audio_input("Record your question")

if audio is not None:

    audio_bytes = audio.getvalue()

    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    # Process audio only once
    if audio_hash != st.session_state.processed_audio:

        st.session_state.processed_audio = audio_hash

        try:

            recognizer = sr.Recognizer()

            audio_file = sr.AudioFile(
                io.BytesIO(audio_bytes)
            )

            with audio_file as source:
                audio_data = recognizer.record(source)

            if language == "English":
                speech_language = "en-IN"

            elif language == "Hindi":
                speech_language = "hi-IN"

            else:
                speech_language = "gu-IN"

            with st.spinner("🎤 Understanding your voice..."):

                recognized_text = recognizer.recognize_google(
                    audio_data,
                    language=speech_language
                )

            st.success("Voice recognized!")

            st.write("Your question:")
            st.write(recognized_text)

            st.session_state.voice_question = recognized_text

        except sr.UnknownValueError:

            st.error("Sorry, I couldn't understand your voice.")

        except sr.RequestError:

            st.error("Speech recognition service is unavailable.")

        except Exception as e:

            st.error(f"Voice error: {e}")

# ---------------- TEXT INPUT ----------------

question = st.chat_input("Ask me anything...")

# Use voice question if available
if st.session_state.voice_question:

    question = st.session_state.voice_question

    st.session_state.voice_question = None

# ---------------- AI RESPONSE ----------------

if question:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Keep only recent messages to reduce processing
    recent_messages = st.session_state.messages[-8:]

    with st.chat_message("assistant"):

        with st.spinner("🤖 AI is thinking..."):

            try:

                response = ollama.chat(
                    model=model_name,

                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ] + recent_messages,

                    options={
                        "temperature": 0.3,
                        "num_predict": 256
                    }
                )

                answer = response["message"]["content"]

                st.markdown(answer)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(
                    "Unable to connect to Ollama. "
                    "Check whether Ollama is running "
                    "and whether the selected model is installed."
                )

                st.code(str(e))
