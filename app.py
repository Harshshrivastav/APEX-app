import google.generativeai as gen_ai
import os 
import streamlit as st
from gtts import gTTS
import threading
import tempfile
import pygame

st.set_page_config(
    page_title="APEX",
    page_icon="💀",
    layout="centered",
)

# Set the Google API key
GOOGLE_API_KEY = 'AIzaSyA6AK_T8QcOzV8i8ZyBgRUfalZ1wjD59sE'

gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-pro')

# Function to translate roles between Gemini Pro and Streamlit
def translate_role_for_streamlit(role):
    return "assistant" if role == "model" else role

# Initialize chat session if not already present
if "chat_session" not in st.session_state:
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error starting chat session: {e}")

# Initialize state for audio playback
if "speaking" not in st.session_state:
    st.session_state.speaking = False

# Styling for the container with hover effect
st.markdown(
    """
    <style>
    .container {
        background-image: url("https://cdn.pixabay.com/animation/2023/06/26/03/02/03-02-03-917_512.gif");
        background-size: cover;
        margin: 0;
        padding: 0;
        padding: 50px;
        border-radius: 5px;
        border: 1px solid #ddd;
        position: relative;
        overflow: hidden;
    }

    .container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background-color: #ddd;
        transition: width 0.5s ease;
        z-index: 0;
    }

    .container:hover::before {
        width: 100%;
    }

    .container h4,
    .container p {
        position: relative;
        z-index: 1;
        color: #fff;
        transition: color 0.5s ease;
    }

    .container:hover h4,
    .container:hover p {
        color: #000;
    }
    </style>
    
    <div class="container">
        <h4>APEX</h4>
        <p>Confused! Converse your thoughts with APEX</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display chat history
if "chat_session" in st.session_state:
    for message in st.session_state.chat_session.history:
        role = translate_role_for_streamlit(message.role)
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

# User input
user_prompt = st.chat_input('Ask APEX...')
if user_prompt:
    st.chat_message('harsh').markdown(user_prompt)
    
    # Get response from APEX (Gemini Pro)
    try:
        apex_response = st.session_state.chat_session.send_message(user_prompt)
        response_text = apex_response.text
    except Exception as e:
        st.error(f"Error getting response from APEX: {e}")
        response_text = None
    
    if response_text:
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        # Store the response text in session state for speaking out loud
        st.session_state.last_response = response_text

# Function to handle text-to-speech in a separate thread
def speak_text(text):
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_file_path = fp.name
            tts.save(temp_file_path)
        
        # Initialize pygame mixer and play the audio
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()
        
        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            continue
        
        # Delete the temporary file after playback is complete
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    except Exception as e:
        print(f"Error during text-to-speech: {e}")

# Function to toggle speaking state and manage the audio thread
def toggle_speaking():
    if st.session_state.speaking:
        st.session_state.speaking = False
        pygame.mixer.music.stop()
    else:
        st.session_state.speaking = True
        audio_thread = threading.Thread(target=speak_text, args=(st.session_state.last_response,))
        audio_thread.start()

# Show the "Speak Out Loud" button if there is a response to read
if "last_response" in st.session_state:
    if st.button("🔊"):
        toggle_speaking()
