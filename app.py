import streamlit as st
import ollama
import speech_recognition as sr
import io

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
    "Ask me anything! I can help with studies, coding, AI, business, technology, shopping, and more."
)

# ---------------- SIDEBAR ----------------


# ---------------- MAIN PAGE SETTINGS ----------------

language = st.selectbox(
"🌐 Choose your language",
["English", "Hindi", "Gujarati"]
)

model_name = st.text_input(
    "🤖 Ollama Model",
    value="phi3"
)

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# ---------------- LANGUAGE SETTINGS ----------------

if language == "English":
    language_instruction = "Answer in English."

elif language == "Hindi":
    language_instruction = "Answer in Hindi."

else:
    language_instruction = "Answer in Gujarati."

# ---------------- AI INSTRUCTIONS ----------------

system_prompt = f"""
You are a helpful multilingual AI assistant.

You can answer questions about any topic, including:

- Education and studies
- Python programming
- Artificial Intelligence
- Data Science
- Machine Learning
- Technology
- Business
- Shopping
- Finance
- General knowledge
- Career guidance
- Everyday questions

Do not restrict yourself to shopping questions.

{language_instruction}

Explain answers clearly and simply.
If the user asks for code, provide working code and explain it.
Be friendly, helpful, and accurate.
"""

# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ---------------- VOICE INPUT ----------------

st.subheader("🎤 Voice Input")

audio = st.audio_input("Record your question")

if audio is not None:

    try:

        recognizer = sr.Recognizer()

        audio_file = sr.AudioFile(
            io.BytesIO(audio.getvalue())
        )

        with audio_file as source:

            audio_data = recognizer.record(source)

        if language == "English":
            speech_language = "en-IN"

        elif language == "Hindi":
            speech_language = "hi-IN"

        else:
            speech_language = "gu-IN"

        recognized_text = recognizer.recognize_google(
            audio_data,
            language=speech_language
        )

        st.success("Speech recognized successfully!")

        st.write("Your question:")
        st.write(recognized_text)

        st.session_state.voice_question = recognized_text

    except sr.UnknownValueError:

        st.error("Sorry, I could not understand your voice.")

    except sr.RequestError:

        st.error("Speech recognition service is unavailable.")

    except Exception as e:

        st.error(f"Voice error: {e}")

# ---------------- TEXT INPUT ----------------

question = st.chat_input(
    "Ask me anything..."
)

# Voice question if available

if "voice_question" in st.session_state:

    question = st.session_state.voice_question

    del st.session_state.voice_question

# ---------------- AI RESPONSE ----------------

if question:

    # Display user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # AI response

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
                    ] + st.session_state.messages,

                )

                answer = response["message"]["content"]

                st.markdown(answer)

                # Save assistant response

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                st.error(
                    "Unable to connect to Ollama. "
                    "Make sure Ollama is running and "
                    "the selected model is installed."
                )

                st.code(str(e))