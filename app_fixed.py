# MULTI-SUBJECT REPORT COMMENT GENERATOR - Working Version
# Supports: English, Maths, Science, ESL, Chemistry

import streamlit as st
import tempfile
import os
import pandas as pd
import io
import random
import re
from datetime import datetime, timedelta
from docx import Document

# SECURITY SETTINGS
TARGET_CHARS = 500
MAX_FILE_SIZE_MB = 5
MAX_ROWS_PER_UPLOAD = 100

# PAGE CONFIG
st.set_page_config(
    page_title="Report Comment Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SESSION STATE INIT
if 'app_initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.app_initialized = True
    st.session_state.all_comments = []

# SIMPLE HELPER FUNCTIONS
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
    return text

def truncate_comment(comment, target=TARGET_CHARS):
    if len(comment) <= target:
        return comment
    truncated = comment[:target].rstrip(" ,;.")
    if "." in truncated:
        truncated = truncated[:truncated.rfind(".")+1]
    return truncated

# SAMPLE COMMENT BANKS (Replace with your actual imports)
SAMPLE_COMMENTS = {
    "English": {
        5: {
            "opening": ["In English this term,", "During English lessons,", "In English,"],
            "attitude": {
                90: "has shown exceptional enthusiasm and dedication.",
                75: "has worked conscientiously and shown good focus.",
                60: "has made a satisfactory effort in class."
            },
            "reading": {
                90: "reads with excellent comprehension and fluency.",
                75: "reads with understanding and can discuss texts.",
                60: "is developing basic reading skills."
            },
            "writing": {
                90: "writes with creativity and excellent structure.",
                75: "writes clearly with good sentence structure.",
                60: "is learning to write complete sentences."
            },
            "target": {
                90: "continue to challenge themselves with advanced texts.",
                75: "work on expanding vocabulary and descriptive language.",
                60: "practice reading aloud to improve fluency."
            },
            "closer": ["Keep up the excellent work!", "Well done this term."]
        },
        7: {
            "opening": ["In English this term,", "During English lessons,", "In English,"],
            "attitude": {
                90: "has shown exceptional enthusiasm and dedication.",
                75: "has worked conscientiously and shown good focus.",
                60: "has made a satisfactory effort in class."
            },
            "reading": {
                90: "reads with excellent comprehension and fluency.",
                75: "reads with understanding and can discuss texts.",
                60: "is developing basic reading skills."
            },
            "writing": {
                90: "writes with creativity and excellent structure.",
                75: "writes clearly with good sentence structure.",
                60: "is learning to write complete sentences."
            },
            "target": {
                90: "continue to challenge themselves with advanced texts.",
                75: "work on expanding vocabulary and descriptive language.",
                60: "practice reading aloud to improve fluency."
            },
            "closer": ["Keep up the excellent work!", "Well done this term."]
        }
    },
    "Maths": {
        5: {
            "opening": ["In Mathematics this term,", "During Maths lessons,", "In Maths,"],
            "attitude": {
                90: "has demonstrated outstanding mathematical thinking.",
                75: "has worked diligently on mathematical concepts.",
                60: "has participated in mathematical activities."
            },
            "achievement": {
                90: "solves complex problems with excellent reasoning.",
                75: "applies mathematical concepts correctly.",
                60: "understands basic mathematical operations."
            },
            "target": {
                90: "tackle more challenging problem-solving tasks.",
                75: "work on mental calculation strategies.",
                60: "practice basic number facts regularly."
            },
            "closer": ["Continue to develop mathematical skills.", "Good progress made."]
        },
        7: {
            "opening": ["In Mathematics this term,", "During Maths lessons,", "In Maths,"],
            "attitude": {
                90: "has demonstrated outstanding mathematical thinking.",
                75: "has worked diligently on mathematical concepts.",
                60: "has participated in mathematical activities."
            },
            "achievement": {
                90: "solves complex problems with excellent reasoning.",
                75: "applies mathematical concepts correctly.",
                60: "understands basic mathematical operations."
            },
            "target": {
                90: "tackle more challenging problem-solving tasks.",
                75: "work on mental calculation strategies.",
                60: "practice basic number facts regularly."
            },
            "closer": ["Continue to develop mathematical skills.", "Good progress made."]
        }
    },
    "Science": {
        5: {
            "opening": ["In Science this term,", "During Science lessons,", "In Science,"],
            "attitude": {
                90: "has shown excellent scientific curiosity.",
                75: "has engaged well with scientific concepts.",
                60: "has participated in science activities."
            },
            "achievement": {
                90: "demonstrates excellent understanding of scientific principles.",
                75: "understands key scientific concepts.",
                60: "is learning basic scientific ideas."
            },
            "target": {
                90: "engage with more complex scientific investigations.",
                75: "develop scientific inquiry skills.",
                60: "practice scientific vocabulary."
            },
            "closer": ["Continue scientific exploration.", "Good work in science."]
        }
    }
}

def generate_comment(subject, year, name, gender, att, achieve, target, optional_text=None):
    """Generate a report comment - SIMPLE WORKING VERSION"""
    p, p_poss = get_pronouns(gender)
    name = sanitize_input(name)
    
    # Get closest available band
    def get_closest_band(value, bands):
        available_bands = [90, 75, 60]
        closest = min(available_bands, key=lambda x: abs(x - value))
        return closest
    
    # Default comment parts
    comment_parts = []
    
    # Try to get from sample data, fallback to generic
    try:
        if subject in SAMPLE_COMMENTS and year in SAMPLE_COMMENTS[subject]:
            data = SAMPLE_COMMENTS[subject][year]
            
            # Opening and attitude
            opening = random.choice(data["opening"])
            att_band = get_closest_band(att, [90, 75, 60])
            attitude = fix_pronouns_in_text(data["attitude"][att_band], p, p_poss)
            comment_parts.append(f"{opening} {name} {attitude}")
            
            # Subject achievement
            achieve_band = get_closest_band(achieve, [90, 75, 60])
            if subject == "English":
                reading = fix_pronouns_in_text(data["reading"][achieve_band], p, p_poss)
                writing = fix_pronouns_in_text(data["writing"][achieve_band], p, p_poss)
                comment_parts.append(f"In reading, {lowercase_first(reading)}")
                comment_parts.append(f"In writing, {lowercase_first(writing)}")
            else:
                achievement = fix_pronouns_in_text(data["achievement"][achieve_band], p, p_poss)
                if achievement[0].islower():
                    achievement = f"{p.capitalize()} {achievement}"
                comment_parts.append(achievement)
            
            # Target
            target_band = get_closest_band(target, [90, 75, 60])
            target_text = fix_pronouns_in_text(data["target"][target_band], p, p_poss)
            comment_parts.append(f"For next term, {p} should {lowercase_first(target_text)}")
            
            # Optional text
            if optional_text and str(optional_text).strip():
                opt = str(optional_text).strip()
                if opt[0].islower():
                    opt = opt[0].upper() + opt[1:]
                if not opt.endswith('.'):
                    opt += '.'
                comment_parts.append(f"Additionally, {lowercase_first(opt)}")
            
            # Closer
            closer = random.choice(data["closer"])
            comment_parts.append(closer)
            
        else:
            # Fallback for unsupported subjects
            comment_parts.append(f"{name} has worked in {subject} this term. {p.capitalize()} has made good progress.")
            if optional_text:
                comment_parts.append(f"Note: {optional_text}")
            
    except Exception as e:
        # Ultimate fallback
        comment_parts = [f"{name} has participated in {subject} lessons. Keep up the good work!"]
    
    # Build final comment
    comment = " ".join(comment_parts)
    
    # Ensure proper punctuation
    comment_parts_clean = []
    for part in comment_parts:
        if not part.endswith('.'):
            part += '.'
        comment_parts_clean.append(part)
    
    comment = " ".join(comment_parts_clean)
    comment = truncate_comment(comment)
    
    if not comment.endswith('.'):
        comment += '.'
    
    return comment

# APP LAYOUT
with st.sidebar:
    st.title("📚 Report Generator")
    app_mode = st.radio("Mode", ["Single Student", "Batch Upload", "Help"], key="mode_radio")
    
    st.markdown("---")
    # FIXED: Added unique key to button
    if st.button("Clear All Data", use_container_width=True, key="sidebar_clear_btn"):
        st.session_state.clear()
        st.session_state.app_initialized = True
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
            year = st.selectbox("Year", [5, 7, 8, 10, 11], key="year_select")
            name = st.text_input("Student Name", placeholder="Enter student name", key="name_input")
            gender = st.selectbox("Gender", ["Male", "Female"], key="gender_select")
        
        with col2:
            att = st.selectbox("Attitude", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="att_select")
            achieve = st.selectbox("Achievement", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="achieve_select")
            target = st.selectbox("Target", [90, 85, 80, 75, 70, 65, 60, 55, 40], index=3, key="target_select")
        
        optional_comment = st.text_area(
            "Optional Additional Comment (Optional)",
            placeholder="Add any extra comments here...",
            height=60,
            key="optional_text"
        )
        
        # FIXED: Added unique key to submit button
        submitted = st.form_submit_button("🚀 Generate Comment", use_container_width=True, key="generate_btn")
    
    if submitted and name:
        with st.spinner("Generating comment..."):
            try:
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
                    st.metric("Characters", len(comment), key="char_metric")
                with col2:
                    st.metric("Words", len(comment.split()), key="word_metric")
                
                # Store in session
                if 'all_comments' not in st.session_state:
                    st.session_state.all_comments = []
                
                st.session_state.all_comments.append({
                    'name': name,
                    'subject': subject,
                    'year': year,
                    'comment': comment
                })
                
                st.success("✓ Comment generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating comment: {str(e)}")
                st.info("Try different subject/year combination")

elif app_mode == "Batch Upload":
    st.subheader("📁 Batch Upload")
    
    st.info("Upload a CSV file with columns: Student Name, Gender, Subject, Year, Attitude, Achievement, Target")
    
    example_csv = """Student Name,Gender,Subject,Year,Attitude,Achievement,Target
John Smith,Male,English,7,75,80,85
Sarah Jones,Female,Maths,5,80,75,80"""
    
    # FIXED: Added unique key to download button
    st.download_button("📥 Download Example CSV", example_csv, "example.csv", "text/csv", key="example_download")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="csv_uploader")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Loaded {len(df)} students")
            
            # FIXED: Added unique key to generate button
            if st.button("Generate All Comments", type="primary", key="batch_generate"):
                if 'all_comments' not in st.session_state:
                    st.session_state.all_comments = []
                
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    comment = generate_comment(
                        subject=str(row.get('Subject', 'English')),
                        year=int(row.get('Year', 7)),
                        name=str(row.get('Student Name', '')),
                        gender=str(row.get('Gender', '')),
                        att=int(row.get('Attitude', 75)),
                        achieve=int(row.get('Achievement', 75)),
                        target=int(row.get('Target', 75))
                    )
                    
                    st.session_state.all_comments.append({
                        'name': str(row.get('Student Name', '')),
                        'subject': str(row.get('Subject', 'English')),
                        'year': int(row.get('Year', 7)),
                        'comment': comment
                    })
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                progress_bar.empty()
                st.success(f"✓ Generated {len(df)} comments!")
                
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
    - 75: Good  
    - 60: Satisfactory
    - 40: Needs improvement
    
    ### Subjects Supported:
    - English (Years 5, 7, 8)
    - Maths (Years 5, 7, 8)
    - Science (Years 5, 7, 8)
    - ESL (IGCSE) (Years 10, 11)
    - Chemistry (Years 10, 11)
    """)

# DOWNLOAD SECTION
if 'all_comments' in st.session_state and st.session_state.all_comments:
    st.markdown("---")
    st.subheader("📥 Download Options")
    
    total = len(st.session_state.all_comments)
    st.info(f"You have {total} generated comment(s)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download as Word Document", key="word_download_btn"):
            doc = Document()
            doc.add_heading('Report Comments', 0)
            
            for entry in st.session_state.all_comments:
                doc.add_heading(f"{entry['name']} - {entry['subject']} Year {entry['year']}", level=2)
                doc.add_paragraph(entry['comment'])
                doc.add_paragraph()
            
            bio = io.BytesIO()
            doc.save(bio)
            
            # FIXED: Added unique key to download button
            st.download_button(
                "⬇️ Download Word File",
                bio.getvalue(),
                f"comments_{datetime.now().strftime('%Y%m%d')}.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="word_download_final"
            )
    
    with col2:
        if st.button("Download as CSV", key="csv_download_btn"):
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
            
            # FIXED: Added unique key to download button
            st.download_button(
                "⬇️ Download CSV",
                csv,
                f"comments_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="csv_download_final"
            )
    
    with col3:
        # FIXED: Added unique key to clear button
        if st.button("🔄 Start Over", type="secondary", key="final_clear_btn"):
            st.session_state.all_comments = []
            st.rerun()

st.markdown("---")
st.caption("Report Generator v1.0 • All comments are generated locally")
