import streamlit as st
from backend.gemini_api import query_gemini
from backend.langchain import generate_prompt
from gtts import gTTS
import re
from io import BytesIO

# App Configuration
st.set_page_config(
    page_title="Symphonic: Literature & Poetry Hub",
    page_icon="🎶",
    layout="wide"  # Centered layout for a more professional feel
)

# Initialize Session State for Responses and Audio
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'audio_files' not in st.session_state:
    st.session_state['audio_files'] = []

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the CSS file
load_css("Ui/Style.css")

# Remove special characters and improve formatting
def clean_text(text):
    # Retain alphabetic characters (both English and Hindi), numbers, punctuation, and spaces
    clean_text = re.sub(r'[^a-zA-Z0-9.,!?;:()\'" \n\u0900-\u097F]', '', text)
    return re.sub(r'\s+', ' ', clean_text).strip()

# Header Section
st.markdown(
    """
    <h1 class="main-title">🎶 Symphonic: Literature & Poetry Hub</h1>
    <p class="subtitle">✨ Experience the symphony of words, crafted uniquely for you ✨</p>
    <div class="divider"></div>
    """,
    unsafe_allow_html=True,
)

# About Project Section
st.markdown(
    """
    ### 📝 About This Project
    **Symphonic** is your gateway to personalized literature and poetry, blending the art of words with AI precision. 
    From timeless classics to creative modern renditions, Symphonic caters to your literary cravings. 

    **✨ Features:**
    - 🌐 **Multi-language Support**: Respond in **English**, **Hindi**, or **Odia**.
    - 🎭 **Custom Styles**: Choose between prose, poetry, narrative, or philosophical formats.
    - 🎨 **Dynamic Tones**: From neutral to contemplative, select your preferred tone.

    Perfect for enthusiasts, students, and professionals seeking inspiration or literary magic. 🪄
    """
)
st.divider()

# Layout Configuration
st.markdown("### 🎨 **Customize Your Response**")

# Language, Mode, Tone Selection
language = st.radio(
    "🌐 Select Language", 
    [
       "Hindi", "Odia", "English", 
        "Bengali", "Tamil", "Telugu", "Marathi", "Kannada", "Gujarati", "Punjabi"
    ], 
    horizontal=True
)

mode = st.selectbox(
    "✍️ **Response Format**", 
    [ 
        "Prose 🖋️",
        "Poetry 🎼", 
        "Narrative 📖", 
        "Philosophical 🧘‍♂️"
    ]
)

tone = st.selectbox(
    "🎭 **Tone of Response**", 
    [
        "Neutral 🤝 (निष्पक्ष)", 
        "Formal 🧑‍⚖️ (औपचारिक)", 
        "Casual 😊 (अनौपचारिक)", 
        "Passionate ❤️ (जोशीला)", 
        "Contemplative 🤔 (विचारशील)", 
        "Humorous 😄 (हास्य)", 
        "Romantic 💕 (रोमांटिक)", 
        "Inspirational 🌟 (प्रेरणादायक)", 
        "Optimistic 🌞 (आशावादी)", 
        "Serene 🌿 (शांत)", 
        "Excited 😆 (उत्साहित)", 
        "Melancholic 😔 (उदास)"
    ]
)

# User Input Query
st.markdown("### 🔍 **Enter Your Query**")
query = st.text_input("💡 Type your topic, theme, or idea (e.g., 'love', 'nature')")

# Generate Response Button
if st.button("🎤 **Generate Response**"):
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if query:
        with st.spinner("🎶 Composing your literary masterpiece..."):
            # Generate the prompt
            prompt = generate_prompt(
                query=query, 
                language=language.lower(), 
                mode=mode.split()[0].lower(),  # Extracting plain text mode
                tone=tone.split()[0].lower()  # Extracting plain text tone
            )
            # Query the Gemini API
            response = query_gemini(
                context=f"You are a literature and poetry expert, responding in {language}.", 
                prompt=prompt
            )

        # Display the Response
        if response:
            st.success("### 🎶 **Your Symphonic Creation**:")
            st.markdown(f"**{mode} in {language} ({tone}):**")
            st.write(response)

            # Clean the response text
            clean_response = clean_text(response)

            # Check if the cleaned response is valid (non-empty and not just whitespace)
            if clean_response and clean_response.strip():
                try:
                    # Proceed with text-to-speech if the cleaned response is valid
                    tts = gTTS(clean_response, lang='en', tld='co.in')
                    audio_file = BytesIO()
                    tts.write_to_fp(audio_file)
                    audio_file.seek(0)

                    # Store response and audio in session state
                    st.session_state['responses'].append(response)
                    st.session_state['audio_files'].append(audio_file)

                    # Play the generated audio
                    st.audio(audio_file, format='audio/mp3')
                except Exception as e:
                    st.error(f"⚠️ Error generating audio: {e}")
            else:
                st.error("⚠️ No valid text to convert to speech.")
        else:
            st.error("⚠️ No response received. Please try again later.")
    else:
        st.warning("⚠️ Please enter a query or select a famous work.")

# Display Previous Responses
st.markdown("### 📂 **Previous Responses**")
if st.session_state['responses']:
    for idx, (response, audio) in enumerate(zip(st.session_state['responses'], st.session_state['audio_files']), start=1):
        with st.expander(f"Response {idx}"):
            st.markdown(f"**Response {idx}:**")
            st.write(response)
            st.audio(audio, format='audio/mp3')
else:
    st.info("ℹ️ No previous responses to display.")

# Footer Section
st.markdown(
    """
    <div class="footer">
        Developed with ❤️ by <b>Aditya</b> | 
        <a href="https://www.linkedin.com/in/aditya-pandey-896109224/" target="_blank">
            LinkedIn
        </a> | © 2024 Symphonic🎶
    </div>
    """,
    unsafe_allow_html=True,
)
