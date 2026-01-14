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
sys.path.insert(0, os.path.abspath('.'))

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
    st.session_state.last_subject = "English"
    st.session_state.last_year = 7

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

def fix_sentence_capitalization(text):
    """Fix lowercase letters after periods."""
    if not text:
        return text
    result = ""
    capitalize_next = True
    for char in text:
        if capitalize_next and char.isalpha():
            result += char.upper()
            capitalize_next = False
        else:
            result += char
        if char in ".!?":
            capitalize_next = True
    return result

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
    
    return text

# GENERATE COMMENT FUNCTION (unchanged)
def generate_comment(subject, year, name, gender, att, achieve, target, optional_text=None):
    # ... the same as your original generate_comment function ...
    # I will skip pasting the whole function here to save space
    # Assume it is fully included as in your original code
    pass

# STREAMLIT APP LAYOUT

# Sidebar for navigation
with st.sidebar:
    st.title("CommentCraft")
    st.caption("Your AI report writing assistant")
    
    app_mode = st.radio(
        "Choose Mode",
        ["Single Student", "Batch Upload", "Privacy Info"]
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
        st.session_state.last_subject = "English"
        st.session_state.last_year = 7
        st.success("All data cleared!")
        st.rerun()

# Main content area
st.title("CommentCraft")
st.warning("""
**Privacy Notice:** All data is processed in memory only. No files are stored on servers. 
Close browser tab to completely erase all data. For use with anonymized student data only.
""")

# -----------------------
# SINGLE STUDENT MODE
# -----------------------
if app_mode == "Single Student":
    st.subheader("Single Student Entry")
    
    with st.form("single_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            subject_options = ["English", "Maths", "Science", "ESL (IGCSE)", "Chemistry"]
            subject_index = subject_options.index(st.session_state.last_subject) if st.session_state.last_subject in subject_options else 0
            subject = st.selectbox("Subject", subject_options, index=subject_index)
            
            year_options = [5, 7, 8, 10, 11]
            year_index = year_options.index(st.session_state.last_year) if st.session_state.last_year in year_options else 1
            year = st.selectbox("Year", year_options, index=year_index)
            
            name = st.text_input("Student Name", placeholder="Enter first name only")
            gender = st.selectbox("Gender", ["Male", "Female"])
        
        with col2:
            att = st.selectbox("Attitude Band", options=[90,85,80,75,70,65,60,55,40], index=3)
            achieve = st.selectbox("Achievement Band", options=[90,85,80,75,70,65,60,55,40], index=3)
            target = st.selectbox("Target Band", options=[90,85,80,75,70,65,60,55,40], index=3)
        
        attitude_target = st.text_area("Optional Additional Comment", placeholder="Add any additional comments here...", height=60)
        submitted = st.form_submit_button("Generate Comment")

    if submitted and name:
        # ... rest of your single student processing remains unchanged ...
        pass

# -----------------------
# BATCH UPLOAD MODE
# -----------------------
# ... rest of your batch upload and privacy info sections remain unchanged ...
