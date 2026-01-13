# Version 2.0 - Cache buster
# MULTI-SUBJECT REPORT COMMENT GENERATOR
# Supports: English, Science, Maths, ESL, Chemistry

import streamlit as st
import tempfile
import os
import pandas as pd
import io
import random
import re
from datetime import datetime, timedelta
from docx import Document

import sys
sys.dont_write_bytecode = True

# Add this at the VERY TOP for import fixes
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Custom CSS to reduce space and remove colors
st.markdown("""
<style>
    /* Reduce space on top of the title */
    .stApp > header {
        padding-top: 1rem !important;
    }
    
    /* Reduce space between navigation bar and title */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Center the title and make it black */
    h1 {
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        color: #000000 !important;
    }
    
    /* Yellow background for privacy notice */
    div[data-testid="stAlert"]:has(svg[data-testid="WarningIcon"]) {
        background-color: #FFEB3B !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        margin-bottom: 1rem !important;
    }
    
    /* Make privacy notice fit on one line */
    div[data-testid="stAlert"]:has(svg[data-testid="WarningIcon"]) > div {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Remove all colored borders, shadows, boxes except yellow privacy */
    .stAlert:not(:has(svg[data-testid="WarningIcon"])), 
    .stWarning:not(:has(svg[data-testid="WarningIcon"])), 
    .stSuccess, 
    .stInfo, 
    .stError {
        border: none !important;
        box-shadow: none !important;
        background-color: #f8f8f8 !important;
    }
    
    /* Remove colored borders from buttons and inputs */
    .stButton > button, .stDownloadButton > button, .stFileUploader > div {
        border: 1px solid #cccccc !important;
        box-shadow: none !important;
    }
    
    /* Remove colored borders from radio buttons */
    .stRadio > div {
        border: none !important;
        background-color: white !important;
    }
    
    /* Remove colored highlights from inputs */
    .st-bb, .st-at, .st-af {
        border-color: #cccccc !important;
    }
    
    /* PURPLE BUTTONS - Consistent purple shade (#8A2BE2) */
    
    /* Main action buttons */
    .stButton > button:not(:has-text("Clear All Data")):not(:has-text("Clear All")):not([kind="secondary"]) {
        background-color: #8A2BE2 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Submit/Generate button */
    .stButton > button:has-text("Generate Comment"),
    .stButton > button:has-text("Generate All Comments") {
        background-color: #8A2BE2 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Add Another button */
    div[data-testid="stButton"] button:has-text("Add Another Student") {
        background-color: #8A2BE2 !important;
        color: white !important;
        border: none !important;
    }
    
    /* CSV download buttons */
    div[data-testid="stButton"] button:has-text("Download Example CSV"),
    div[data-testid="stDownloadButton"] button:has-text("Download CSV"),
    div[data-testid="stButton"] button:has-text("Download Word File") {
        background-color: #8A2BE2 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Make all backgrounds white */
    .main, .stApp {
        background-color: white !important;
    }
    
    /* Remove any gradient backgrounds */
    div[data-testid="stSidebar"],
    .css-1d391kg,
    .css-1lcbmhc,
    .css-18e3th9 {
        background-color: white !important;
    }
    
    /* Remove sidebar colors */
    .css-1lcbmhc {
        border-right: 1px solid #f0f0f0 !important;
    }
    
    /* Remove colored text in metrics */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #333333 !important;
    }
    
    /* Purple progress bars */
    .stProgress > div > div {
        background-color: #f0f0f0 !important;
    }
    
    .stProgress > div > div > div {
        background-color: #8A2BE2 !important;
    }
    
    /* Remove blue from selected radio button */
    .stRadio > div > label > div:first-child {
        background-color: white !important;
        border-color: #cccccc !important;
    }
    
    /* Purple for checked radio button */
    .stRadio > div > label > div:first-child > div {
        background-color: #8A2BE2 !important;
    }
    
    /* Remove blue from tabs/navigation */
    .stTabs [data-baseweb="tab"] {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Remove blue from selected tab */
    .stTabs [aria-selected="true"] {
        background-color: #f0f0f0 !important;
        color: #333333 !important;
        border-color: #cccccc !important;
    }
    
    /* Remove blue from select boxes */
    .stSelectbox > div > div {
        background-color: white !important;
        border-color: #cccccc !important;
    }
    
    /* Remove blue from text areas */
    .stTextArea > div > div {
        background-color: white !important;
        border-color: #cccccc !important;
    }
    
    /* Purple button hover effects */
    .stButton > button:not(:has-text("Clear All Data")):not(:has-text("Clear All")):not([kind="secondary"]):hover,
    .stButton > button:has-text("Generate Comment"):hover,
    .stButton > button:has-text("Generate All Comments"):hover,
    div[data-testid="stButton"] button:has-text("Add Another Student"):hover,
    div[data-testid="stButton"] button:has-text("Download Example CSV"):hover,
    div[data-testid="stDownloadButton"] button:has-text("Download CSV"):hover,
    div[data-testid="stButton"] button:has-text("Download Word File"):hover {
        background-color: #7a1bd2 !important;
    }
    
    /* Grey hover for clear buttons */
    .stButton > button:has-text("Clear All Data"):hover,
    .stButton > button:has-text("Clear All"):hover {
        background-color: #f0f0f0 !important;
        border-color: #cccccc !important;
    }
    
    /* Remove blue from form borders */
    .stForm {
        border-color: #cccccc !important;
    }
    
    /* Remove blue from expander headers */
    .streamlit-expanderHeader {
        background-color: white !important;
        border-color: #cccccc !important;
    }
    
    /* Remove blue from success/warning/info boxes */
    [data-testid="stAlert"]:not(:has(svg[data-testid="WarningIcon"])) {
        background-color: #f8f8f8 !important;
    }
    
    /* Remove any remaining blue backgrounds */
    .st-emotion-cache-1v0mbdj {
        background-color: white !important;
    }
    
    /* Fix sidebar radio button selected state */
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        border-color: #cccccc !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child > div {
        background-color: #8A2BE2 !important;
    }
    
    /* Remove blue from metric containers */
    [data-testid="stMetricContainer"] {
        border: none !important;
        background-color: white !important;
    }
    
    /* Make all form elements white */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: white !important;
    }
    
    /* Clear buttons styling (secondary buttons) */
    .stButton > button[kind="secondary"] {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Form submit button styling */
    [data-testid="baseButton-secondary"] {
        background-color: #8A2BE2 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# SECURITY & PRIVACY SETTINGS
TARGET_CHARS = 500
MAX_FILE_SIZE_MB = 5
MAX_ROWS_PER_UPLOAD = 100
RATE_LIMIT_SECONDS = 10

# PAGE CONFIGURATION
st.set_page_config(
    page_title="CommentCraft",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SECURITY INITIALIZATION
if 'app_initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.app_initialized = True
    st.session_state.upload_count = 0
    st.session_state.last_upload_time = datetime.now()
    st.session_state.generated_files = []
    
# Initialize session state for form persistence
if 'subject' not in st.session_state:
    st.session_state.subject = "English"
if 'year' not in st.session_state:
    st.session_state.year = 7
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'gender' not in st.session_state:
    st.session_state.gender = "Male"
if 'att' not in st.session_state:
    st.session_state.att = 75
if 'achieve' not in st.session_state:
    st.session_state.achieve = 75
if 'target' not in st.session_state:
    st.session_state.target = 75
if 'attitude_target' not in st.session_state:
    st.session_state.attitude_target = ""

# IMPORT STATEMENT FILES (directly from repository)
try:
    # English
    from statements_year5_English import (
        opening_phrases as opening_5_eng,
        attitude_bank as attitude_5_eng,
        reading_bank as reading_5_eng,
        writing_bank as writing_5_eng,
        reading_target_bank as target_5_eng,
        writing_target_bank as target_write_5_eng,
        closer_bank as closer_5_eng
    )
    
    from statements_year7_English import (
        opening_phrases as opening_7_eng,
        attitude_bank as attitude_7_eng,
        reading_bank as reading_7_eng,
        writing_bank as writing_7_eng,
        reading_target_bank as target_7_eng,
        writing_target_bank as target_write_7_eng,
        closer_bank as closer_7_eng
    )

    from statements_year8_English import (
        opening_phrases as opening_8_eng,
        attitude_bank as attitude_8_eng,
        reading_bank as reading_8_eng,
        writing_bank as writing_8_eng,
        reading_target_bank as target_8_eng,
        writing_target_bank as target_write_8_eng,
        closer_bank as closer_8_eng
    )

    # Science
    from statements_year5_Science import (
        opening_phrases as opening_5_sci,
        attitude_bank as attitude_5_sci,
        science_bank as science_5_sci,
        target_bank as target_5_sci,
        closer_bank as closer_5_sci
    )
    
    from statements_year7_science import (
        opening_phrases as opening_7_sci,
        attitude_bank as attitude_7_sci,
        science_bank as science_7_sci,
        target_bank as target_7_sci,
        closer_bank as closer_7_sci
    )

    from statements_year8_science import (
        opening_phrases as opening_8_sci,
        attitude_bank as attitude_8_sci,
        science_bank as science_8_sci,
        target_bank as target_8_sci,
        closer_bank as closer_8_sci
    )

    # Maths
    from statements_year5_Maths_NEW import (
        opening_phrases as opening_5_math,
        attitude_bank as attitude_5_math,
        maths_bank as maths_5_math,
        target_bank as target_5_math,
        closer_bank as closer_5_math
    )
    
    from statements_year7_Maths_NEW import (
        opening_phrases as opening_7_math,
        attitude_bank as attitude_7_math,
        maths_bank as maths_7_math,
        target_bank as target_7_math,
        closer_bank as closer_7_math
    )

    from statements_year8_Maths_NEW import (
        opening_phrases as opening_8_math,
        attitude_bank as attitude_8_math,
        maths_bank as maths_8_math,
        target_bank as target_8_math,
        closer_bank as closer_8_math
    )
    
    # ESL (IGCSE)
    from statements_igcse_0510_esl import (
        opening_phrases as opening_esl,
        attitude_bank as attitude_esl,
        reading_bank as reading_esl,
        writing_bank as writing_esl,
        speaking_bank as speaking_esl,
        listening_bank as listening_esl,
        reading_target_bank as target_reading_esl,
        writing_target_bank as target_write_esl,
        speaking_target_bank as target_speak_esl,
        listening_target_bank as target_listen_esl,
        closer_bank as closer_esl
    )

    # Chemistry
    from statements_igcse_0620_chemistry import (
        opening_phrases as opening_chem,
        attitude_bank as attitude_chem,
        chemistry_bank as chemistry_chem,
        target_bank as target_chem,
        closer_bank as closer_chem
    )

except ImportError as e:
    st.error(f"Missing required statement files: {e}")
    st.error("Please ensure all statement files are in the repository.")
    st.stop()

# SECURITY FUNCTIONS
def validate_upload_rate():
    """Prevent rapid-fire uploads/abuse"""
    time_since_last = datetime.now() - st.session_state.last_upload_time
    if time_since_last < timedelta(seconds=RATE_LIMIT_SECONDS):
        wait_time = RATE_LIMIT_SECONDS - time_since_last.seconds
        st.error(f"Please wait {wait_time} seconds before uploading again")
        return False
    return True

def sanitize_input(text, max_length=100):
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    sanitized = ''.join(c for c in text if c.isalnum() or c in " .'-")
    return sanitized[:max_length].strip().title()

def validate_file(file):
    """Validate uploaded file size and type"""
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large (max {MAX_FILE_SIZE_MB}MB)"
    
    if not file.name.lower().endswith('.csv'):
        return False, "Only CSV files allowed"
    
    return True, ""

def process_csv_securely(uploaded_file):
    """Process CSV with auto-cleanup of temp files"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
        tmp.write(uploaded_file.getvalue())
        temp_path = tmp.name
    
    try:
        df = pd.read_csv(temp_path, nrows=MAX_ROWS_PER_UPLOAD + 1)
        
        if len(df) > MAX_ROWS_PER_UPLOAD:
            st.warning(f"Only processing first {MAX_ROWS_PER_UPLOAD} rows")
            df = df.head(MAX_ROWS_PER_UPLOAD)
        
        if 'Student Name' in df.columns:
            df['Student Name'] = df['Student Name'].apply(lambda x: sanitize_input(str(x)))
        
        return df
        
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None
        
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

# HELPER FUNCTIONS
def get_pronouns(gender):
    gender = gender.lower()
    if gender == "male":
        return "he", "his"
    elif gender == "female":
        return "she", "her"
    return "they", "their"

def lowercase_first(text):
    return text[0].lower() + text[1:] if text else ""

def truncate_comment(comment, target=TARGET_CHARS):
    if len(comment) <= target:
        return comment
    truncated = comment[:target].rstrip(" ,;.")
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

def fix_pronouns_in_text(text, pronoun, possessive):
    """Fix gender pronouns in statement text"""
    if not text:
        return text
    
    # Fix pronouns with word boundaries
    text = re.sub(r'\bhe\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHe\b', pronoun.capitalize(), text)
    text = re.sub(r'\bshe\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bShe\b', pronoun.capitalize(), text)
    text = re.sub(r'\bhis\b', possessive, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHis\b', possessive.capitalize(), text)
    text = re.sub(r'\bher\b', possessive, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHer\b', possessive.capitalize(), text)
    text = re.sub(r'\bhim\b', pronoun, text, flags=re.IGNORECASE)
    text = re.sub(r'\bHim\b', pronoun.capitalize(), text)
    text = re.sub(r'\bhimself\b', f"{pronoun}self", text, flags=re.IGNORECASE)
    text = re.sub(r'\bherself\b', f"{pronoun}self", text, flags=re.IGNORECASE)
    
    # Additional British spelling conversions
    text = text.replace("color", "colour")
    text = text.replace("Color", "Colour")
    text = text.replace("behavior", "behaviour")
    text = text.replace("Behavior", "Behaviour")
    text = text.replace("favorite", "favourite")
    text = text.replace("Favorite", "Favourite")
    text = text.replace("organize", "organise")
    text = text.replace("Organize", "Organise")
    text = text.replace("realize", "realise")
    text = text.replace("Realize", "Realise")
    text = text.replace("recognize", "recognise")
    text = text.replace("Recognize", "Recognise")
    text = text.replace("analyze", "analyse")
    text = text.replace("Analyze", "Analyse")
    text = text.replace("center", "centre")
    text = text.replace("Center", "Centre")
    text = text.replace("meter", "metre")
    text = text.replace("Meter", "Metre")
    text = text.replace("liter", "litre")
    text = text.replace("Liter", "Litre")
    
    return text

def ensure_proper_capitalization(text):
    """Ensure sentences start with capital letters"""
    if not text:
        return text
    
    # Split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    capitalized_sentences = []
    
    for sentence in sentences:
        if sentence:
            # Capitalize first letter
            sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
            capitalized_sentences.append(sentence)
    
    return ' '.join(capitalized_sentences)

def generate_comment(subject, year, name, gender, att, achieve, target, optional_text=None):
    """Generate a report comment based on subject, year, and performance bands"""
    p, p_poss = get_pronouns(gender)
    name = sanitize_input(name)
    
    # Initialize comment parts
    comment_parts = []
    
    # Subject-specific comment generation
    if subject == "English":
        if year == 5:
            opening = random.choice(opening_5_eng)
            attitude_text = fix_pronouns_in_text(attitude_5_eng[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            reading_text = fix_pronouns_in_text(reading_5_eng[achieve], p, p_poss)
            reading_text = ensure_proper_capitalization(reading_text)
            if reading_text[0].islower():
                reading_text = f"{p.capitalize()} {reading_text}"
            reading_sentence = f"In reading, {lowercase_first(reading_text)}"
            
            writing_text = fix_pronouns_in_text(writing_5_eng[achieve], p, p_poss)
            writing_text = ensure_proper_capitalization(writing_text)
            if writing_text[0].islower():
                writing_text = f"{p.capitalize()} {writing_text}"
            writing_sentence = f"In writing, {lowercase_first(writing_text)}"
            
            reading_target_text = fix_pronouns_in_text(target_5_eng[target], p, p_poss)
            reading_target_text = ensure_proper_capitalization(reading_target_text)
            reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
            
            writing_target_text = fix_pronouns_in_text(target_write_5_eng[target], p, p_poss)
            writing_target_text = ensure_proper_capitalization(writing_target_text)
            writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
            
            closer_sentence = random.choice(closer_5_eng)
            
            comment_parts = [
                attitude_sentence,
                reading_sentence,
                writing_sentence,
                reading_target_sentence,
                writing_target_sentence,
                closer_sentence
            ]
            
        elif year == 7:
            opening = random.choice(opening_7_eng)
            attitude_text = fix_pronouns_in_text(attitude_7_eng[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            reading_text = fix_pronouns_in_text(reading_7_eng[achieve], p, p_poss)
            reading_text = ensure_proper_capitalization(reading_text)
            if reading_text[0].islower():
                reading_text = f"{p.capitalize()} {reading_text}"
            reading_sentence = f"In reading, {lowercase_first(reading_text)}"
            
            writing_text = fix_pronouns_in_text(writing_7_eng[achieve], p, p_poss)
            writing_text = ensure_proper_capitalization(writing_text)
            if writing_text[0].islower():
                writing_text = f"{p.capitalize()} {writing_text}"
            writing_sentence = f"In writing, {lowercase_first(writing_text)}"
            
            reading_target_text = fix_pronouns_in_text(target_7_eng[target], p, p_poss)
            reading_target_text = ensure_proper_capitalization(reading_target_text)
            reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
            
            writing_target_text = fix_pronouns_in_text(target_write_7_eng[target], p, p_poss)
            writing_target_text = ensure_proper_capitalization(writing_target_text)
            writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
            
            closer_sentence = random.choice(closer_7_eng)
            
            comment_parts = [
                attitude_sentence,
                reading_sentence,
                writing_sentence,
                reading_target_sentence,
                writing_target_sentence,
                closer_sentence
            ]
            
        else:  # Year 8
            opening = random.choice(opening_8_eng)
            attitude_text = fix_pronouns_in_text(attitude_8_eng[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            reading_text = fix_pronouns_in_text(reading_8_eng[achieve], p, p_poss)
            reading_text = ensure_proper_capitalization(reading_text)
            if reading_text[0].islower():
                reading_text = f"{p.capitalize()} {reading_text}"
            reading_sentence = f"In reading, {lowercase_first(reading_text)}"
            
            writing_text = fix_pronouns_in_text(writing_8_eng[achieve], p, p_poss)
            writing_text = ensure_proper_capitalization(writing_text)
            if writing_text[0].islower():
                writing_text = f"{p.capitalize()} {writing_text}"
            writing_sentence = f"In writing, {lowercase_first(writing_text)}"
            
            reading_target_text = fix_pronouns_in_text(target_8_eng[target], p, p_poss)
            reading_target_text = ensure_proper_capitalization(reading_target_text)
            reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
            
            writing_target_text = fix_pronouns_in_text(target_write_8_eng[target], p, p_poss)
            writing_target_text = ensure_proper_capitalization(writing_target_text)
            writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
            
            closer_sentence = random.choice(closer_8_eng)
            
            comment_parts = [
                attitude_sentence,
                reading_sentence,
                writing_sentence,
                reading_target_sentence,
                writing_target_sentence,
                closer_sentence
            ]
        
    elif subject == "Science":
        if year == 5:
            opening = random.choice(opening_5_sci)
            attitude_text = fix_pronouns_in_text(attitude_5_sci[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            science_text = fix_pronouns_in_text(science_5_sci[achieve], p, p_poss)
            science_text = ensure_proper_capitalization(science_text)
            if science_text[0].islower():
                science_text = f"{p.capitalize()} {science_text}"
            science_sentence = science_text
            
            target_text = fix_pronouns_in_text(target_5_sci[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_5_sci)
            
            comment_parts = [
                attitude_sentence,
                science_sentence,
                target_sentence,
                closer_sentence
            ]
            
        elif year == 7:
            opening = random.choice(opening_7_sci)
            attitude_text = fix_pronouns_in_text(attitude_7_sci[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            science_text = fix_pronouns_in_text(science_7_sci[achieve], p, p_poss)
            science_text = ensure_proper_capitalization(science_text)
            if science_text[0].islower():
                science_text = f"{p.capitalize()} {science_text}"
            science_sentence = science_text
            
            target_text = fix_pronouns_in_text(target_7_sci[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_7_sci)
            
            comment_parts = [
                attitude_sentence,
                science_sentence,
                target_sentence,
                closer_sentence
            ]
            
        else:  # Year 8
            opening = random.choice(opening_8_sci)
            attitude_text = fix_pronouns_in_text(attitude_8_sci[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            science_text = fix_pronouns_in_text(science_8_sci[achieve], p, p_poss)
            science_text = ensure_proper_capitalization(science_text)
            if science_text[0].islower():
                science_text = f"{p.capitalize()} {science_text}"
            science_sentence = science_text
            
            target_text = fix_pronouns_in_text(target_8_sci[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_8_sci)
            
            comment_parts = [
                attitude_sentence,
                science_sentence,
                target_sentence,
                closer_sentence
            ]
        
    elif subject == "Maths":
        if year == 5:
            opening = random.choice(opening_5_math)
            attitude_text = fix_pronouns_in_text(attitude_5_math[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            maths_text = fix_pronouns_in_text(maths_5_math[achieve], p, p_poss)
            maths_text = ensure_proper_capitalization(maths_text)
            if maths_text[0].islower():
                maths_text = f"{p.capitalize()} {maths_text}"
            maths_sentence = maths_text
            
            target_text = fix_pronouns_in_text(target_5_math[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_5_math)
            
            comment_parts = [
                attitude_sentence,
                maths_sentence,
                target_sentence,
                closer_sentence
            ]
            
        elif year == 7:
            opening = random.choice(opening_7_math)
            attitude_text = fix_pronouns_in_text(attitude_7_math[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            maths_text = fix_pronouns_in_text(maths_7_math[achieve], p, p_poss)
            maths_text = ensure_proper_capitalization(maths_text)
            if maths_text[0].islower():
                maths_text = f"{p.capitalize()} {maths_text}"
            maths_sentence = maths_text
            
            target_text = fix_pronouns_in_text(target_7_math[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_7_math)
            
            comment_parts = [
                attitude_sentence,
                maths_sentence,
                target_sentence,
                closer_sentence
            ]
            
        else:  # Year 8
            opening = random.choice(opening_8_math)
            attitude_text = fix_pronouns_in_text(attitude_8_math[att], p, p_poss)
            attitude_sentence = f"{opening} {name} {attitude_text}"
            
            maths_text = fix_pronouns_in_text(maths_8_math[achieve], p, p_poss)
            maths_text = ensure_proper_capitalization(maths_text)
            if maths_text[0].islower():
                maths_text = f"{p.capitalize()} {maths_text}"
            maths_sentence = maths_text
            
            target_text = fix_pronouns_in_text(target_8_math[target], p, p_poss)
            target_text = ensure_proper_capitalization(target_text)
            target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
            
            closer_sentence = random.choice(closer_8_math)
            
            comment_parts = [
                attitude_sentence,
                maths_sentence,
                target_sentence,
                closer_sentence
            ]
        
    elif subject == "ESL (IGCSE)":
        opening = random.choice(opening_esl)
        attitude_text = fix_pronouns_in_text(attitude_esl[att], p, p_poss)
        attitude_sentence = f"{opening} {name} {attitude_text}"
        
        # Reading
        reading_text = fix_pronouns_in_text(reading_esl[achieve], p, p_poss)
        reading_text = ensure_proper_capitalization(reading_text)
        if reading_text[0].islower():
            reading_text = f"{p.capitalize()} {reading_text}"
        reading_sentence = f"In reading, {lowercase_first(reading_text)}"
        
        # Writing
        writing_text = fix_pronouns_in_text(writing_esl[achieve], p, p_poss)
        writing_text = ensure_proper_capitalization(writing_text)
        if writing_text[0].islower():
            writing_text = f"{p.capitalize()} {writing_text}"
        writing_sentence = f"In writing, {lowercase_first(writing_text)}"
        
        # Speaking
        speaking_text = fix_pronouns_in_text(speaking_esl[achieve], p, p_poss)
        speaking_text = ensure_proper_capitalization(speaking_text)
        if speaking_text[0].islower():
            speaking_text = f"{p.capitalize()} {speaking_text}"
        speaking_sentence = f"In speaking, {lowercase_first(speaking_text)}"
        
        # Listening
        listening_text = fix_pronouns_in_text(listening_esl[achieve], p, p_poss)
        listening_text = ensure_proper_capitalization(listening_text)
        if listening_text[0].islower():
            listening_text = f"{p.capitalize()} {listening_text}"
        listening_sentence = f"In listening, {lowercase_first(listening_text)}"
        
        # Targets
        reading_target_text = fix_pronouns_in_text(target_reading_esl[target], p, p_poss)
        reading_target_text = ensure_proper_capitalization(reading_target_text)
        reading_target_sentence = f"For the next term, {p} should {lowercase_first(reading_target_text)}"
        
        writing_target_text = fix_pronouns_in_text(target_write_esl[target], p, p_poss)
        writing_target_text = ensure_proper_capitalization(writing_target_text)
        writing_target_sentence = f"Additionally, {p} should {lowercase_first(writing_target_text)}"
        
        closer_sentence = random.choice(closer_esl)
        
        comment_parts = [
            attitude_sentence,
            reading_sentence,
            writing_sentence,
            speaking_sentence,
            listening_sentence,
            reading_target_sentence,
            writing_target_sentence,
            closer_sentence
        ]
        
    elif subject == "Chemistry":
        opening = random.choice(opening_chem)
        attitude_text = fix_pronouns_in_text(attitude_chem[att], p, p_poss)
        attitude_sentence = f"{opening} {name} {attitude_text}"
        
        chemistry_text = fix_pronouns_in_text(chemistry_chem[achieve], p, p_poss)
        chemistry_text = ensure_proper_capitalization(chemistry_text)
        if chemistry_text[0].islower():
            chemistry_text = f"{p.capitalize()} {chemistry_text}"
        chemistry_sentence = chemistry_text
        
        target_text = fix_pronouns_in_text(target_chem[target], p, p_poss)
        target_text = ensure_proper_capitalization(target_text)
        target_sentence = f"For the next term, {p} should {lowercase_first(target_text)}"
        
        closer_sentence = random.choice(closer_chem)
        
        comment_parts = [
            attitude_sentence,
            chemistry_sentence,
            target_sentence,
            closer_sentence
        ]
    
    else:
        # Default fallback if subject not recognized
        comment_parts = [f"{name} has worked in {subject} this term."]
    
    # Ensure all sentences end with period
    for i in range(len(comment_parts)):
        if not comment_parts[i].endswith('.'):
            comment_parts[i] += '.'
    
    # Join comment parts
    comment = " ".join([c for c in comment_parts if c])
    
    # ADD OPTIONAL TEXT AT THE VERY END (AFTER EVERYTHING ELSE)
    if optional_text:
        optional_text = sanitize_input(optional_text)
        if optional_text:
            # Ensure optional text starts with capital letter and ends with period
            if not optional_text[0].isupper():
                optional_text = optional_text[0].upper() + optional_text[1:]
            if not optional_text.endswith('.'):
                optional_text += '.'
            
            # Add to the end of the comment with proper punctuation
            if comment.strip().endswith('.'):
                comment = comment.rstrip()
                comment = comment[:-1]  # Remove the last period
                comment += f". Additionally, {lowercase_first(optional_text)}"
            else:
                comment += f". Additionally, {lowercase_first(optional_text)}"
    
    # Truncate after adding optional text
    comment = truncate_comment(comment, TARGET_CHARS)
    
    # Ensure comment ends with period
    if not comment.endswith('.'):
        comment = comment.rstrip(' ,;') + '.'
    
    # Final capitalization check
    comment = ensure_proper_capitalization(comment)
    
    return comment

# STREAMLIT APP LAYOUT

# Sidebar for navigation
with st.sidebar:
    st.title("CommentCraft")
    st.caption("Your AI report writing assistant")
    
    app_mode = st.radio(
        "Choose Mode",
        ["Single Student", "Batch Upload", "Privacy Info"],
        key="app_mode"
    )
    
    st.markdown("---")
    st.markdown("### Privacy Features")
    st.info("""
    - No data stored on servers
    - All processing in memory
    - Auto-deletion of temp files
    - Input sanitization
    - Rate limiting enabled
    """)
    
    if st.button("Clear All Data", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.session_state.app_initialized = True
        st.session_state.upload_count = 0
        st.session_state.last_upload_time = datetime.now()
        # Reinitialize session state for form persistence
        st.session_state.subject = "English"
        st.session_state.year = 7
        st.session_state.name = ""
        st.session_state.gender = "Male"
        st.session_state.att = 75
        st.session_state.achieve = 75
        st.session_state.target = 75
        st.session_state.attitude_target = ""
        st.success("All data cleared!")
        st.rerun()

# Main content area - CENTERED BLACK TITLE
st.markdown("<h1>CommentCraft</h1>", unsafe_allow_html=True)

# Privacy notice - YELLOW BACKGROUND, ONE LINE
st.warning("**Privacy Notice:** All data is processed in memory only. No files are stored on servers. Close browser tab to completely erase all data. For use with anonymized student data only.")

# SINGLE STUDENT MODE
if app_mode == "Single Student":
    st.subheader("Single Student Entry")
    
    with st.form("single_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox(
                "Subject", 
                ["English", "Maths", "Science", "ESL (IGCSE)", "Chemistry"],
                index=["English", "Maths", "Science", "ESL (IGCSE)", "Chemistry"].index(st.session_state.subject) 
                if st.session_state.subject in ["English", "Maths", "Science", "ESL (IGCSE)", "Chemistry"] 
                else 0,
                key="subject_select"
            )
            
            year = st.selectbox(
                "Year", 
                [5, 7, 8, 10, 11],
                index=[5, 7, 8, 10, 11].index(st.session_state.year) if st.session_state.year in [5, 7, 8, 10, 11] else 1,
                key="year_select"
            )
            
            name = st.text_input(
                "Student Name", 
                placeholder="Enter first name only",
                value=st.session_state.name,
                key="name_input"
            )
            
            gender = st.selectbox(
                "Gender", 
                ["Male", "Female"],
                index=0 if st.session_state.gender == "Male" else 1,
                key="gender_select"
            )
        
        with col2:
            att = st.selectbox(
                "Attitude Band", 
                options=[90,85,80,75,70,65,60,55,40],
                index=[90,85,80,75,70,65,60,55,40].index(st.session_state.att) if st.session_state.att in [90,85,80,75,70,65,60,55,40] else 3,
                key="att_select"
            )
            
            achieve = st.selectbox(
                "Achievement Band",
                options=[90,85,80,75,70,65,60,55,40],
                index=[90,85,80,75,70,65,60,55,40].index(st.session_state.achieve) if st.session_state.achieve in [90,85,80,75,70,65,60,55,40] else 3,
                key="achieve_select"
            )
            
            target = st.selectbox(
                "Target Band",
                options=[90,85,80,75,70,65,60,55,40],
                index=[90,85,80,75,70,65,60,55,40].index(st.session_state.target) if st.session_state.target in [90,85,80,75,70,65,60,55,40] else 3,
                key="target_select"
            )
        
        attitude_target = st.text_area(
            "Optional Additional Comment",
            placeholder="Add any additional comments here...",
            height=60,
            value=st.session_state.attitude_target,
            key="optional_text_area"
        )
        
        submitted = st.form_submit_button("Generate Comment")
        
        if submitted:
            # Update session state with current values
            st.session_state.subject = subject
            st.session_state.year = year
            st.session_state.name = name
            st.session_state.gender = gender
            st.session_state.att = att
            st.session_state.achieve = achieve
            st.session_state.target = target
            st.session_state.attitude_target = attitude_target
    
    if submitted and name:
        if not validate_upload_rate():
            st.stop()
        
        name = sanitize_input(name)
        
        with st.spinner("Generating comment..."):
            comment = generate_comment(
                subject=subject,
                year=year,
                name=name,
                gender=gender,
                att=att,
                achieve=achieve,
                target=target,
                optional_text=attitude_target
            )
            char_count = len(comment)
        
        # Display comment
        st.subheader("Generated Comment")
        st.text_area("", comment, height=200, key="generated_comment")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Character Count", f"{char_count}/500")
        with col2:
            st.metric("Words", len(comment.split()))
        with col3:
            if char_count < 450:
                st.success("Good length")
            else:
                st.warning("Near limit")
        
        # Store in session
        if 'all_comments' not in st.session_state:
            st.session_state.all_comments = []
        
        student_entry = {
            'name': name,
            'subject': subject,
            'year': year,
            'comment': comment,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.all_comments.append(student_entry)
        
        # Add another button - PURPLE BACKGROUND
        if st.button("Add Another Student"):
            # Keep the current subject and year, but clear other fields
            st.session_state.name = ""
            st.session_state.attitude_target = ""
            st.rerun()

# BATCH UPLOAD MODE
elif app_mode == "Batch Upload":
    st.subheader("Batch Upload (CSV)")
    
    st.info("""
    **CSV Format Required:**
    - Columns: Student Name, Gender, Subject, Year, Attitude, Achievement, Target
    - Gender: Male/Female
    - Subject: English/Maths/Science/ESL (IGCSE)/Chemistry
    - Year: 5,7,8,10,11
    - Bands: 90,85,80,75,70,65,60,55,40
    """)
    
    # Example CSV
    example_csv = """Student Name,Gender,Subject,Year,Attitude,Achievement,Target
John,Male,English,7,75,80,85
Sarah,Female,Maths,5,80,75,80
Ahmed,Male,ESL (IGCSE),10,85,90,85
Maria,Female,Chemistry,11,80,85,80"""
    
    # CSV download button with purple background
    st.download_button(
        label="Download Example CSV",
        data=example_csv,
        file_name="example_students.csv",
        mime="text/csv"
    )
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        if not validate_upload_rate():
            st.stop()
        
        is_valid, msg = validate_file(uploaded_file)
        if not is_valid:
            st.error(msg)
            st.stop()
        
        with st.spinner("Processing CSV..."):
            df = process_csv_securely(uploaded_file)
        
        if df is not None:
            st.success(f"Processed {len(df)} students")
            
            with st.expander("Preview Data"):
                st.dataframe(df.head())
            
            if st.button("Generate All Comments"):
                if 'all_comments' not in st.session_state:
                    st.session_state.all_comments = []
                
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    progress = (idx + 1) / len(df)
                    progress_bar.progress(progress)
                    
                    try:
                        comment = generate_comment(
                            subject=str(row.get('Subject', 'English')),
                            year=int(row.get('Year', 7)),
                            name=str(row.get('Student Name', '')),
                            gender=str(row.get('Gender', '')),
                            att=int(row.get('Attitude', 75)),
                            achieve=int(row.get('Achievement', 75)),
                            target=int(row.get('Target', 75))
                        )
                        
                        student_entry = {
                            'name': sanitize_input(str(row.get('Student Name', ''))),
                            'subject': str(row.get('Subject', 'English')),
                            'year': int(row.get('Year', 7)),
                            'comment': comment,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state.all_comments.append(student_entry)
                        
                    except Exception as e:
                        st.error(f"Error processing row {idx + 1}: {e}")
                
                progress_bar.empty()
                st.success(f"Generated {len(df)} comments!")
                st.session_state.last_upload_time = datetime.now()

# PRIVACY INFO MODE
elif app_mode == "Privacy Info":
    st.subheader("Privacy & Security Information")
    
    st.markdown("""
    ### Data Protection
    
    **How we handle data:**
    - All processing occurs in your browser's memory
    - No student data is sent to external servers
    - Temporary files are created and immediately deleted
    - No database or persistent storage is used
    
    **Security features:**
    1. **Input Sanitization** - Removes special characters
    2. **Rate Limiting** - Prevents system abuse
    3. **File Validation** - Checks file size and type
    4. **Auto-Cleanup** - Temporary files automatically deleted
    5. **Memory Clearing** - All data erased on browser close
    
    **Best practices:**
    - Use only first names or student IDs
    - Close browser tab when finished
    - Download reports immediately
    - Use on school-managed devices for maximum privacy
    """)

# DOWNLOAD SECTION
if 'all_comments' in st.session_state and st.session_state.all_comments:
    st.markdown("---")
    st.subheader("Download Reports")
    
    total_comments = len(st.session_state.all_comments)
    st.info(f"You have {total_comments} generated comment(s)")
    
    # Preview
    with st.expander(f"Preview Comments ({total_comments})"):
        for idx, entry in enumerate(st.session_state.all_comments, 1):
            st.markdown(f"**{idx}. {entry['name']}** ({entry['subject']} Year {entry['year']})")
            st.write(entry['comment'])
            st.markdown("---")
    
    # Download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Word Document"):
            doc = Document()
            doc.add_heading('Report Comments', 0)
            doc.add_paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
            doc.add_paragraph(f'Total Students: {total_comments}')
            doc.add_paragraph('')
            
            for entry in st.session_state.all_comments:
                doc.add_heading(f"{entry['name']} - {entry['subject']} Year {entry['year']}", level=2)
                doc.add_paragraph(entry['comment'])
                doc.add_paragraph('')
            
            bio = io.BytesIO()
            doc.save(bio)
            
            st.download_button(
                label="Download Word File",
                data=bio.getvalue(),
                file_name=f"report_comments_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    
    with col2:
        if st.button("CSV Export"):
            csv_data = []
            for entry in st.session_state.all_comments:
                csv_data.append({
                    'Student Name': entry['name'],
                    'Subject': entry['subject'],
                    'Year': entry['year'],
                    'Comment': entry['comment'],
                    'Generated': entry['timestamp']
                })
            
            df_export = pd.DataFrame(csv_data)
            csv_bytes = df_export.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name=f"report_comments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Clear All", type="secondary"):
            st.session_state.all_comments = []
            st.success("All comments cleared!")
            st.rerun()

# FOOTER
st.markdown("---")
st.caption("CommentCraft v4.0 • Secure & Private • British English")
