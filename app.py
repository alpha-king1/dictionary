import streamlit as st
from nltk.corpus import wordnet as wn
from fuzzywuzzy import process
import nltk
import json
import speech_recognition as sr
import threading
import queue
import time

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Smart Thesaurus",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Download required NLTK data
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4')

# Custom CSS for Merriam-Webster style with background image
# Updated CSS with attractive black, white, blue color scheme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap');

    /* Beautiful gradient background */
    .main {
        background: linear-gradient(135deg, 
            #1e3a8a 0%,     /* Deep blue */
            #3b82f6 25%,    /* Blue */
            #1f2937 50%,    /* Dark gray */
            #111827 75%,    /* Almost black */
            #000000 100%    /* Black */
        );
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        color: #ffffff;
    }

    /* Main content container */
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #000000 0%, #1f2937 30%, #3b82f6 100%);
        color: #ffffff;
        padding: 3rem 0;
        margin: -2rem -2rem 2rem -2rem;
        text-align: center;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }

    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
    }

    .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }

    /* Search container */
    .search-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .search-container:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-right: 2px solid #cbd5e1;
    }

    /* Alphabetical section headers */
    .alphabet-header {
        background: linear-gradient(135deg, #000000 0%, #1f2937 50%, #3b82f6 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.4rem;
        text-align: center;
        padding: 1rem;
        margin: 1rem 0 0.5rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        letter-spacing: 3px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }

    /* Dropdown styling */
    .word-dropdown {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        max-height: 350px;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .dropdown-title {
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #1f2937;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }

    .word-item {
        display: block;
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 0.3rem 0;
        background: #ffffff;
        border: 2px solid transparent;
        border-radius: 8px;
        color: #1f2937;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .word-item:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        border-color: #3b82f6;
        color: #ffffff;
        text-decoration: none;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    .word-item:focus {
        outline: none;
        background: linear-gradient(135deg, #1e3a8a 0%, #000000 100%);
        border-color: #000000;
        color: #ffffff;
    }

    /* Word display styling */
    .word-display {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-left: 6px solid #3b82f6;
        border-radius: 0 15px 15px 0;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        position: relative;
    }

    .word-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 48%, rgba(59, 130, 246, 0.1) 50%, transparent 52%);
        border-radius: 0 15px 15px 0;
        pointer-events: none;
    }

    .matched-word {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #000000;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        position: relative;
        z-index: 1;
    }

    .phonetic {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #6b7280;
        font-style: italic;
        font-weight: 400;
    }

    .pos-tag {
        background: linear-gradient(135deg, #000000 0%, #374151 100%);
        color: #ffffff;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid #000000;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* Definition styling */
    .definition-section {
        background: #ffffff;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000;
        margin: 0 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        border-bottom: 3px solid #e5e7eb;
        padding-bottom: 0.75rem;
    }

    .definition-item {
        padding: 1rem 0;
        border-bottom: 1px solid #f3f4f6;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        color: #1f2937;
        font-size: 1rem;
    }

    .definition-item:last-child {
        border-bottom: none;
    }

    .definition-number {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: #ffffff;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-right: 1rem;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }

    /* Synonym/Antonym styling */
    .word-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .word-tag {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        color: #1e3a8a;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        border: 2px solid #3b82f6;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .word-tag:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    .antonym-tag {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: #991b1b;
        border-color: #ef4444;
    }

    .antonym-tag:hover {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
    }

    /* Error and info styling */
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #fecaca;
        color: #991b1b;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }

    .info-message {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #bae6fd;
        color: #1e3a8a;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }

    /* Speech button styling */
    .speech-button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: #ffffff;
        border: none;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        font-size: 1.75rem;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
        border: 3px solid #ffffff;
    }

    .speech-button:hover {
        transform: scale(1.1);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.6);
        background: linear-gradient(135deg, #1e3a8a 0%, #000000 100%);
    }

    /* Hide Streamlit branding */
    .css-1rs6os, .css-17ziqus {
        visibility: hidden;
    }

    /* Enhanced scrollbar styling */
    .word-dropdown::-webkit-scrollbar {
        width: 8px;
    }

    .word-dropdown::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }

    .word-dropdown::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        border-radius: 4px;
    }

    .word-dropdown::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #000000 100%);
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
        color: #1f2937;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #000000 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        .matched-word {
            font-size: 1.8rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .search-container, .word-display, .definition-section {
            padding: 1.2rem;
        }
        .block-container {
            padding: 1rem;
        }
        .main-header {
            padding: 2rem 0;
        }
    }

    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    .loading {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)


# Load word database with error handling
@st.cache_data
def load_word_database():
    """Load the generated word database from JSON file"""
    try:
        with open("meaningful_words_3k.json", "r", encoding='utf-8') as f:
            word_data = json.load(f)
            return word_data
    except FileNotFoundError:
        st.error("⚠️ Word database 'meaningful_words_3k.json' not found. Please run 'generate_word.py' first.")
        # Fallback to sample data
        return [
            {
                "word": "aberration",
                "definition": "a departure from what is normal, usual, or expected",
                "part_of_speech": "noun",
                "synonyms": ["deviation", "anomaly", "irregularity"],
                "antonyms": ["normality", "regularity"],
                "examples": ["The results were an aberration."]
            }
        ]
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON in word database file.")
        return []


def get_closest_word(input_word, word_database, threshold=70):
    """Find the closest matching word from the word database."""
    if not input_word or not word_database:
        return None

    word_list = [item['word'] for item in word_database]
    match, score = process.extractOne(input_word.lower().strip(), word_list)

    if score >= threshold:
        # Return the full word data
        for word_data in word_database:
            if word_data['word'] == match:
                return word_data
    return None


def search_words_starting_with(prefix, word_database):
    """Search for words that START with the given prefix"""
    if not prefix or not word_database:
        return []

    prefix_lower = prefix.lower().strip()
    matching_words = []

    for word_data in word_database:
        if word_data['word'].lower().startswith(prefix_lower):
            matching_words.append(word_data)

    return sorted(matching_words, key=lambda x: x['word'])


def group_words_by_letter(word_database):
    """Group words by their starting letter"""
    groups = {}
    for word_data in word_database:
        first_letter = word_data['word'][0].upper()
        if first_letter not in groups:
            groups[first_letter] = []
        groups[first_letter].append(word_data)

    # Sort each group
    for letter in groups:
        groups[letter].sort(key=lambda x: x['word'])

    return groups


def get_phonetic(word):
    """Get phonetic pronunciation (simplified)."""
    return f"/{word}/"


def display_word_info(word_data):
    """Display comprehensive word information using the database."""
    word = word_data['word']

    # Display matched word
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        phonetic = get_phonetic(word)
        st.markdown(f"""
        <div class="word-display">
            <h2 class="matched-word">
                {word}
                <span class="phonetic">{phonetic}</span>
                <span class="pos-tag">{word_data['part_of_speech']}</span>
            </h2>
        </div>
        """, unsafe_allow_html=True)

        # Definition section
        if word_data.get('definition'):
            st.markdown("""
            <div class="definition-section">
                <h3 class="section-title">📚 Definition</h3>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="definition-item">
                <span class="definition-number">1</span>
                {word_data['definition']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # Examples section
        if word_data.get('examples'):
            st.markdown("""
            <div class="definition-section">
                <h3 class="section-title">💡 Examples</h3>
            """, unsafe_allow_html=True)

            for i, example in enumerate(word_data['examples'], 1):
                st.markdown(f"""
                <div class="definition-item">
                    <span class="definition-number">{i}</span>
                    <em>"{example}"</em>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # Synonyms section
        if word_data.get('synonyms'):
            st.markdown("""
            <div class="definition-section">
                <h3 class="section-title">🔄 Synonyms</h3>
                <div class="word-list">
            """, unsafe_allow_html=True)

            for synonym in word_data['synonyms']:
                st.markdown(f"""
                <span class="word-tag">{synonym}</span>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        # Antonyms section
        if word_data.get('antonyms'):
            st.markdown("""
            <div class="definition-section">
                <h3 class="section-title">⚔️ Antonyms</h3>
                <div class="word-list">
            """, unsafe_allow_html=True)

            for antonym in word_data['antonyms']:
                st.markdown(f"""
                <span class="word-tag antonym-tag">{antonym}</span>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        # If no synonyms or antonyms found
        if not word_data.get('synonyms') and not word_data.get('antonyms'):
            st.markdown("""
            <div class="info-message">
                🔍 No synonyms or antonyms found for this word.
            </div>
            """, unsafe_allow_html=True)


# Load the word database
word_database = load_word_database()

# Initialize session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "listening" not in st.session_state:
    st.session_state.listening = False
if "selected_word" not in st.session_state:
    st.session_state.selected_word = ""

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">📘 Smart Thesaurus</h1>
    <p class="subtitle">Discover meanings, synonyms, and antonyms with intelligent word matching</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for speech input and word dropdown
with st.sidebar:
    st.markdown("### 🎙️ Voice Input")


    def speech_to_text_simple():
        """Simplified speech recognition."""
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎤 Listening... Please speak clearly.")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=5)

            text = r.recognize_google(audio)
            return text.lower().strip()
        except sr.WaitTimeoutError:
            st.error("⏰ Listening timeout. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"❌ Microphone error: {str(e)}")
            return None


    if st.button("🎤 Start Voice Input", key="voice_btn"):
        with st.spinner("🎧 Initializing microphone..."):
            recognized_text = speech_to_text_simple()
            if recognized_text:
                st.session_state.user_input = recognized_text
                st.session_state.selected_word = recognized_text
                st.success(f"✅ Recognized: **{recognized_text}**")
                st.rerun()

    # Word search and dropdown
    st.markdown("### 🔍 Word Search")

    # Search input for words starting with prefix
    search_prefix = st.text_input("Search words starting with:", placeholder="Type letters...", key="word_search")

    if search_prefix:
        matching_words = search_words_starting_with(search_prefix, word_database)

        if matching_words:
            st.markdown(f"**Found {len(matching_words)} words starting with '{search_prefix}':**")

            # Display matching words (limit to 15 for performance)
            for word_data in matching_words[:15]:
                if st.button(word_data['word'], key=f"search_btn_{word_data['word']}",
                             help=f"Click to explore '{word_data['word']}'"):
                    st.session_state.selected_word = word_data['word']
                    st.session_state.user_input = word_data['word']
                    st.rerun()

            if len(matching_words) > 15:
                st.markdown(f"<small>... and {len(matching_words) - 15} more words</small>", unsafe_allow_html=True)
        else:
            st.markdown(f"❌ No words found starting with '{search_prefix}'")

    # Alphabetical word browser
    st.markdown("### 📖 Browse by Letter")

    # Group words by starting letter
    word_groups = group_words_by_letter(word_database)

    # Create tabs or sections for each letter
    available_letters = sorted(word_groups.keys())

    # Let user select a letter
    selected_letter = st.selectbox("Choose a letter:", options=[""] + available_letters, key="letter_selector")

    if selected_letter and selected_letter in word_groups:
        st.markdown(f"""
        <div class="alphabet-header">
            {selected_letter}
        </div>
        """, unsafe_allow_html=True)

        words_in_letter = word_groups[selected_letter]

        st.markdown('<div class="word-dropdown">', unsafe_allow_html=True)
        st.markdown(f'<div class="dropdown-title">{len(words_in_letter)} words starting with {selected_letter}</div>',
                    unsafe_allow_html=True)

        # Display words for selected letter (limit to 20 for performance)
        for word_data in words_in_letter[:20]:
            if st.button(word_data['word'], key=f"letter_btn_{word_data['word']}",
                         help=f"Click to explore '{word_data['word']}'"):
                st.session_state.selected_word = word_data['word']
                st.session_state.user_input = word_data['word']
                st.rerun()

        if len(words_in_letter) > 20:
            st.markdown(f"<small>... and {len(words_in_letter) - 20} more words</small>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# Main search interface
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("""
    <div class="search-container">
    """, unsafe_allow_html=True)

    user_input = st.text_input(
        "Enter a word to explore",
        value=st.session_state.user_input,
        placeholder="Type any word...",
        label_visibility="collapsed",
        key="main_search"
    )

    st.markdown("</div>", unsafe_allow_html=True)

# Process input (from search box or dropdown selection)
current_word = user_input or st.session_state.selected_word

if current_word:
    word_data = get_closest_word(current_word, word_database)

    if word_data:
        display_word_info(word_data)
    else:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(f"""
            <div class="error-message">
                ❌ No similar word found for "<strong>{current_word}</strong>" in our dictionary.
                <br><small>Try checking your spelling or using a different word.</small>
            </div>
            """, unsafe_allow_html=True)

# Footer with instructions
if not current_word:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        **💡 How to use:**
        - Type any word in the search box
        - Use voice input from the sidebar
        - Search words starting with specific letters
        - Browse {len(word_database)} words alphabetically
        """)

    with col2:
        st.markdown("""
        **🎯 Features:**
        - Intelligent word matching
        - Rich definitions and examples
        - Related words discovery
        - Voice recognition support
        """)

    with col3:
        st.markdown("""
        **🔧 Tips:**
        - Try partial spellings for fuzzy matching
        - Use voice for hands-free search
        - Browse by letter for discovery
        - Click any word to explore instantly
        """)

# Display database stats
if st.sidebar.button("📊 Database Stats"):
    total_words = len(word_database)

    # Count by parts of speech
    pos_counts = {}
    for word_data in word_database:
        pos = word_data['part_of_speech']
        pos_counts[pos] = pos_counts.get(pos, 0) + 1

    st.sidebar.markdown(f"""
    **📈 Database Statistics:**
    - Total words: {total_words}
    - Letters covered: {len(word_groups)}

    **Parts of Speech:**
    """)

    for pos, count in sorted(pos_counts.items()):
        percentage = (count / total_words) * 100
        st.sidebar.markdown(f"- {pos.title()}: {count} ({percentage:.1f}%)")