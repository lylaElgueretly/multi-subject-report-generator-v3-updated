# MULTI-SUBJECT REPORT COMMENT GENERATOR - With Actual Imports
# Supports: English, Maths, Science, ESL, Chemistry

import streamlit as st
import tempfile
import os
import pandas as pd
import io
import random
import re
from datetime import datetime
from docx import Document

# PAGE CONFIG
st.set_page_config(
    page_title="Report Comment Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SESSION STATE INIT
if 'all_comments' not in st.session_state:
    st.session_state.all_comments = []

# HELPER FUNCTIONS
def get_pronouns(gender):
    gender = gender.lower()
    if gender == "male":
        return "he", "his"
    elif gender == "female":
        return "she", "her"
    return "they", "their"

def sanitize_input(text, max_length=100):
    if not text:
        return ""
    sanitized = ''.join(c for c in text if c.isalnum() or c in " .'-")
    return sanitized[:max_length].strip().title()

def lowercase_first(text):
    return text[0].lower() + text[1:] if text else ""

def fix_pronouns_in_text(text, pronoun, possessive):
    if not text:
        return text
    
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

def truncate_comment(comment, target=500):
    if len(comment) <= target:
        return comment
    truncated = comment[:target].rstrip(" ,;.")
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

def ensure_proper_capitalization(text):
    """Ensure sentences start with capital letters"""
    if not text:
        return text
    text = text.strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text

# IMPORT ALL STATEMENT FILES
try:
    # English imports
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

    # Science imports
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

    # Maths imports
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
    
    # ESL (IGCSE) import
    from statements_igcse_0510_esl import (
        opening_phrases as opening_esl,
        attitude_bank as attitude_esl,
        reading_bank as reading_esl,
        writing_bank as writing_esl,
        speaking_bank as speaking_esl,
        listening_bank as listening_esl,
        reading_target_bank as target_reading_esl,
        writing_target_bank as target_write_esl,
        closer_bank as closer_esl
    )

    # Chemistry import
    from statements_igcse_0620_chemistry import (
        opening_phrases as opening_chem,
        attitude_bank as attitude_chem,
        chemistry_bank as chemistry_chem,
        target_bank as target_chem,
        closer_bank as closer_chem
    )
    
    st.success("✓ All statement files imported successfully!")
    
except ImportError as e:
    st.error(f"❌ Missing statement files: {e}")
    st.error("Please make sure all statement files are in the same directory.")
    st.stop()

def generate_comment(subject, year, name, gender, att, achieve, target, optional_text=None):
    """Generate a report comment using imported statement banks"""
    p, p_poss = get_pronouns(gender)
    name = sanitize_input(name)
    
    comment_parts = []
    
    # Get closest band value (in case exact match not found)
    def get_closest_band(value, available_bands):
        if value in available_bands:
            return value
        # Find closest band
        bands = [90, 85, 80, 75, 70, 65, 60, 55, 40]
        closest = min(bands, key=lambda x: abs(x - value))
        return closest
    
    try:
        # ENGLISH
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
                    writing_target_sentence
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
                    writing_target_sentence
                ]
                
            elif year == 8:
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
                    writing_target_sentence
                ]
            else:
                raise ValueError(f"Year {year} not supported for English")
        
        # MATHS
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
                    target_sentence
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
                    target_sentence
                ]
                
            elif year == 8:
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
                    target_sentence
                ]
            else:
                raise ValueError(f"Year {year} not supported for Maths")
        
        # SCIENCE
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
                    target_sentence
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
                    target_sentence
                ]
                
            elif year == 8:
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
                    target_sentence
                ]
            else:
                raise ValueError(f"Year {year} not supported for Science")
        
        # ESL (IGCSE)
        elif subject == "ESL (IGCSE)":
            if year in [10, 11]:
                opening = random.choice(opening_esl)
                attitude_text = fix_pronouns_in_text(attitude_esl[att], p, p_poss)
                attitude_sentence = f"{opening} {name} {attitude_text}"
                
                reading_text = fix_pronouns_in_text(reading_esl[achieve], p, p_poss)
                reading_text = ensure_proper_capitalization(reading_text)
                if reading_text[0].islower():
                    reading_text = f"{p.capitalize()} {reading_text}"
                reading_sentence = f"In reading, {lowercase_first(reading_text)}"
                
                writing_text = fix_pronouns_in_text(writing_esl[achieve], p, p_poss)
                writing_text = ensure_proper_capitalization(writing_text)
                if writing_text[0].islower():
                    writing_text = f"{p.capitalize()} {writing_text}"
                writing_sentence = f"In writing, {lowercase_first(writing_text)}"
                
                speaking_text = fix_pronouns_in_text(speaking_esl[achieve], p, p_poss)
                speaking_text = ensure_proper_capitalization(speaking_text)
                if speaking_text[0].islower():
                    speaking_text = f"{p.capitalize()} {speaking_text}"
                speaking_sentence = f"In speaking, {lowercase_first(speaking_text)}"
                
                listening_text = fix_pronouns_in_text(listening_esl[achieve], p, p_poss)
                listening_text = ensure_proper_capitalization(listening_text)
                if listening_text[0].islower():
                    listening_text = f"{p.capitalize()} {listening_text}"
                listening_sentence = f"In listening, {lowercase_first(listening_text)}"
                
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
                    writing_target_sentence
                ]
            else:
                raise ValueError("ESL (IGCSE) is only for Years 10-11")
        
        # CHEMISTRY
        elif subject == "Chemistry":
            if year in [10, 11]:
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
                    target_sentence
                ]
            else:
                raise ValueError("Chemistry is only for Years 10-11")
        
        else:
            raise ValueError(f"Subject '{subject}' not supported")
        
        # ADD OPTIONAL TEXT
        if optional_text and str(optional_text).strip():
            optional_text_clean = str(optional_text).strip()
            optional_text_clean = sanitize_input(optional_text_clean, max_length=200)
            
            if optional_text_clean:
                if optional_text_clean[0].islower():
                    optional_text_clean = optional_text_clean[0].upper() + optional_text_clean[1:]
                
                optional_sentence = f"Additionally, {lowercase_first(optional_text_clean)}"
                if not optional_sentence.endswith('.'):
                    optional_sentence += '.'
                
                # Add optional sentence before closer
                comment_parts.append(optional_sentence)
        
        # ADD CLOSER SENTENCE
        # Determine which closer to use based on subject and year
        if subject == "English":
            if year == 5:
                comment_parts.append(random.choice(closer_5_eng))
            elif year == 7:
                comment_parts.append(random.choice(closer_7_eng))
            elif year == 8:
                comment_parts.append(random.choice(closer_8_eng))
        elif subject == "Maths":
            if year == 5:
                comment_parts.append(random.choice(closer_5_math))
            elif year == 7:
                comment_parts.append(random.choice(closer_7_math))
            elif year == 8:
                comment_parts.append(random.choice(closer_8_math))
        elif subject == "Science":
            if year == 5:
                comment_parts.append(random.choice(closer_5_sci))
            elif year == 7:
                comment_parts.append(random.choice(closer_7_sci))
            elif year == 8:
                comment_parts.append(random.choice(closer_8_sci))
        elif subject == "ESL (IGCSE)":
            comment_parts.append(random.choice(closer_esl))
        elif subject == "Chemistry":
            comment_parts.append(random.choice(closer_chem))
        
        # Ensure all sentences end with period
        for i in range(len(comment_parts)):
            if not comment_parts[i].endswith('.'):
                comment_parts[i] += '.'
        
        # Join comment parts
        comment = " ".join([c for c in comment_parts if c])
        
        # Truncate to target length
        comment = truncate_comment(comment, 500)
        
        # Ensure comment ends with period
        if not comment.endswith('.'):
            comment = comment.rstrip(' ,;') + '.'
        
        return comment
        
    except KeyError as e:
        st.error(f"Key error: Band value {e} not found in statement banks")
        return f"Error: Band value {e} not found. Please use standard band values: 90,85,80,75,70,65,60,55,40"
    except Exception as e:
        st.error(f"Error generating comment: {str(e)}")
        return f"Error generating comment. Please check subject/year combination is valid."

# APP LAYOUT
with st.sidebar:
    st.title("📚 Report Generator")
    app_mode = st.radio("Mode", ["Single Student", "Batch Upload", "Help"], key="mode_radio")
    
    st.markdown("---")
    if st.button("Clear All Data", use_container_width=True, key="sidebar_clear"):
        st.session_state.all_comments = []
        st.rerun()

# MAIN CONTENT
st.title("Report Comment Generator")
st.caption("Generate personalized report comments quickly and easily")

if app_mode == "Single Student":
    st.subheader("👤 Single Student Entry")
    
    with st.form("student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox("Subject", ["English", "Maths", "Science", "ESL (IGCSE)", "Chemistry"], key="subject_select")
            name = st.text_input("Student Name", placeholder="Enter student name", key="name_input")
            gender = st.selectbox("Gender", ["Male", "Female"], key="gender_select")
        
        with col2:
            # Show appropriate years based on subject
            if subject in ["ESL (IGCSE)", "Chemistry"]:
                year_options = [10, 11]
            else:
                year_options = [5, 7, 8]
            
            year = st.selectbox("Year", year_options, key="year_select")
            att = st.selectbox("Attitude", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="att_select")
            achieve = st.selectbox("Achievement", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="achieve_select")
            target = st.selectbox("Target", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="target_select")
        
        optional_comment = st.text_area(
            "Optional Additional Comment (Optional)",
            placeholder="Add any extra comments here...",
            height=60,
            key="optional_text"
        )
        
        submitted = st.form_submit_button("🚀 Generate Comment", use_container_width=True, key="generate_btn")
    
    if submitted and name:
        with st.spinner("Generating comment..."):
            comment = generate_comment(
                subject=subject,
                year=year,
                name=name,
                gender=gender,
                att=att,
                achieve=achieve,
                target=target,
                optional_text=optional_comment
            )
            
            # Display comment
            st.subheader("📝 Generated Comment")
            st.text_area("", comment, height=200, key="display_comment")
            
            # Stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Characters", len(comment))
            with col2:
                st.metric("Words", len(comment.split()))
            
            # Store in session
            st.session_state.all_comments.append({
                'name': name,
                'subject': subject,
                'year': year,
                'comment': comment
            })
            
            st.success("✓ Comment generated successfully!")

elif app_mode == "Batch Upload":
    st.subheader("📁 Batch Upload")
    
    st.info("Upload a CSV file with columns: Student Name, Gender, Subject, Year, Attitude, Achievement, Target")
    
    example_csv = """Student Name,Gender,Subject,Year,Attitude,Achievement,Target
John Smith,Male,English,7,75,80,85
Sarah Jones,Female,Maths,5,80,75,80
Ali Khan,Male,ESL (IGCSE),10,85,90,85
Maria Garcia,Female,Chemistry,11,80,85,80"""
    
    st.download_button("📥 Download Example CSV", example_csv, "example.csv", "text/csv", key="example_download")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="csv_uploader")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} students")
            
            if st.button("Generate All Comments", type="primary", key="batch_generate"):
                new_comments = []
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    try:
                        comment = generate_comment(
                            subject=str(row.get('Subject', 'English')),
                            year=int(row.get('Year', 7)),
                            name=str(row.get('Student Name', '')),
                            gender=str(row.get('Gender', 'Male')),
                            att=int(row.get('Attitude', 75)),
                            achieve=int(row.get('Achievement', 75)),
                            target=int(row.get('Target', 75))
                        )
                        
                        new_comments.append({
                            'name': str(row.get('Student Name', '')),
                            'subject': str(row.get('Subject', 'English')),
                            'year': int(row.get('Year', 7)),
                            'comment': comment
                        })
                        
                    except Exception as e:
                        st.warning(f"Row {idx+1}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                progress_bar.empty()
                st.session_state.all_comments.extend(new_comments)
                st.success(f"✓ Generated {len(new_comments)} comments!")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

else:  # Help mode
    st.subheader("❓ Help & Instructions")
    st.markdown("""
    ### How to Use:
    1. **Single Student**: Fill in the form to generate one comment
    2. **Batch Upload**: Upload a CSV file for multiple students
    
    ### CSV Format:
    ```
    Student Name,Gender,Subject,Year,Attitude,Achievement,Target
    John Doe,Male,English,7,75,80,85
    ```
    
    ### Band Values:
    - 90: Excellent
    - 85: Very Good
    - 80: Good
    - 75: Satisfactory
    - 70: Basic
    - 65: Developing
    - 60: Needs Improvement
    - 55: Significant Support Needed
    - 40: Intensive Support Required
    
    ### Subjects & Years:
    - **English**: Years 5, 7, 8
    - **Maths**: Years 5, 7, 8
    - **Science**: Years 5, 7, 8
    - **ESL (IGCSE)**: Years 10, 11
    - **Chemistry**: Years 10, 11
    
    ### Optional Comments:
    Add any additional comments in the optional field. These will be included before the closing sentence.
    """)

# DOWNLOAD SECTION
if st.session_state.all_comments:
    st.markdown("---")
    st.subheader("📥 Download Options")
    
    total = len(st.session_state.all_comments)
    st.info(f"You have {total} generated comment(s)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download as Word Document", key="word_btn"):
            doc = Document()
            doc.add_heading('Report Comments', 0)
            
            for entry in st.session_state.all_comments:
                doc.add_heading(f"{entry['name']} - {entry['subject']} Year {entry['year']}", level=2)
                doc.add_paragraph(entry['comment'])
                doc.add_paragraph()
            
            bio = io.BytesIO()
            doc.save(bio)
            
            st.download_button(
                "⬇️ Download Word File",
                bio.getvalue(),
                f"comments_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="word_download"
            )
    
    with col2:
        if st.button("Download as CSV", key="csv_btn"):
            csv_data = []
            for entry in st.session_state.all_comments:
                csv_data.append({
                    'Student Name': entry['name'],
                    'Subject': entry['subject'],
                    'Year': entry['year'],
                    'Comment': entry['comment']
                })
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                "⬇️ Download CSV",
                csv,
                f"comments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                key="csv_download"
            )
    
    with col3:
        if st.button("🔄 Clear All", type="secondary", key="clear_btn"):
            st.session_state.all_comments = []
            st.rerun()

st.markdown("---")
st.caption("Report Generator • Uses imported statement files • Includes optional comments")
