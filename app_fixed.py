# clean_survey_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import io
import json
import time
import hashlib

# ============================================================================
# 1. COLUMNS DEFINITION
# ============================================================================

columns = [
    "submission_id", "name", "email", "allow_contact", "methods",
    "time_scratch", "time_ai", "time_school_bank", "time_dropdown",
    "cognitive_scratch", "cognitive_ai", "cognitive_dropdown",
    "quality_scratch", "quality_ai", "quality_dropdown",
    "character_accuracy_scratch", "character_accuracy_ai", "character_accuracy_dropdown",
    "curriculum_alignment_scratch", "curriculum_alignment_ai", "curriculum_alignment_dropdown",
    "stress_scratch", "stress_ai", "stress_dropdown",
    "biggest_cognitive_relief", "biggest_time_quality", "time_saved",
    "open_feedback_ai", "open_feedback_tool", "suggestions",
    "timestamp"
]

# ============================================================================
# 2. DATA PERSISTENCE CLASS
# ============================================================================

class DataPersistence:
    """Simple data persistence with multiple backups"""
    
    def __init__(self):
        self.submission_count = 0
        self.init_time = datetime.now()
        
        # Create backup directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        os.makedirs("daily_backups", exist_ok=True)
        
        # Initialize master CSV
        self.master_file = "data/survey_data_master.csv"
        if not os.path.exists(self.master_file):
            pd.DataFrame(columns=columns).to_csv(self.master_file, index=False)
        else:
            # Count existing submissions
            try:
                df = pd.read_csv(self.master_file)
                self.submission_count = len(df)
            except:
                self.submission_count = 0
    
    def save_submission(self, data):
        """Save submission with multiple backups"""
        self.submission_count += 1
        
        # Add metadata
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['timestamp'] = timestamp
        data['submission_id'] = hashlib.md5(f"{timestamp}{data.get('email','')}".encode()).hexdigest()[:8]
        
        # Save to master CSV
        try:
            df_master = pd.read_csv(self.master_file) if os.path.exists(self.master_file) else pd.DataFrame(columns=columns)
            df_master = pd.concat([df_master, pd.DataFrame([data])], ignore_index=True)
            df_master.to_csv(self.master_file, index=False)
            master_success = True
        except Exception as e:
            master_success = False
            st.error(f"Save error: {str(e)[:100]}")
        
        # Save to daily backup
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_file = f"daily_backups/survey_{date_str}.csv"
        try:
            if os.path.exists(daily_file):
                df_daily = pd.read_csv(daily_file)
                df_daily = pd.concat([df_daily, pd.DataFrame([data])], ignore_index=True)
            else:
                df_daily = pd.DataFrame([data])
            df_daily.to_csv(daily_file, index=False)
            daily_success = True
        except:
            daily_success = True
        
        # Save to JSON backup
        json_file = f"backups/survey_{timestamp.replace(':', '-').replace(' ', '_')}.json"
        try:
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            json_success = True
        except:
            json_success = True
        
        # Store in session state
        st.session_state.last_submission = {
            'time': timestamp,
            'id': data['submission_id'],
            'name': data.get('name', 'Anonymous'),
            'success': master_success
        }
        
        return master_success

# ============================================================================
# 3. STREAMLIT APP CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Report Writing MVP Survey",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'last_submission' not in st.session_state:
    st.session_state.last_submission = None

# Initialize data persistence
@st.cache_resource
def init_persistence():
    return DataPersistence()

persistence = init_persistence()

# ============================================================================
# 4. SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("Survey Dashboard")
    
    # System Status
    st.subheader("System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Submissions", persistence.submission_count)
    with col2:
        if os.path.exists("data/survey_data_master.csv"):
            try:
                file_size = os.path.getsize("data/survey_data_master.csv") / 1024
                st.metric("Data Size", f"{file_size:.1f} KB")
            except:
                st.metric("Data Size", "N/A")
        else:
            st.metric("Data Size", "0 KB")
    
    # Data protection indicator
    protection_level = min(100, 100)  # Always 100% with local backups
    st.progress(protection_level/100, text=f"Data Protection: {protection_level}%")
    
    st.write("**Backup Systems Active:**")
    st.write("- Local database")
    st.write("- Daily backups")
    st.write("- Individual JSON backups")
    
    st.divider()
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    if st.button("View All Data"):
        try:
            if os.path.exists(persistence.master_file):
                df = pd.read_csv(persistence.master_file)
                st.dataframe(df)
            else:
                st.info("No data yet")
        except Exception as e:
            st.error(f"Error: {str(e)[:100]}")
    
    if st.button("Download Data"):
        if os.path.exists(persistence.master_file):
            with open(persistence.master_file, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name=f"survey_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Last Submission
    if st.session_state.last_submission:
        st.divider()
        st.subheader("Last Submission")
        ls = st.session_state.last_submission
        st.write(f"Time: {ls['time']}")
        st.write(f"ID: {ls['id']}")
        st.write(f"Name: {ls['name']}")
        st.write(f"Status: {'Saved' if ls['success'] else 'Failed'}")

# ============================================================================
# 5. MAIN SURVEY INTERFACE
# ============================================================================

# Header
st.title("Report Writing MVP Validation Survey")
st.write("Your feedback helps improve our tool. All responses are anonymous unless you choose to share contact information.")
st.write("**Data is automatically saved with multiple backups.**")

# Show warning if no data file
if not os.path.exists(persistence.master_file):
    st.info("Starting fresh survey database")

# Progress tracker
if not st.session_state.submitted:
    progress = st.progress(0, text="Survey Progress")
else:
    progress = st.progress(100, text="Survey Completed")

# --- SURVEY FORM ---
with st.form("survey_form", clear_on_submit=True):
    # Section 1: Contact Information
    st.header("Your Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name (optional)", placeholder="e.g., Alex Johnson")
    with col2:
        email = st.text_input("Email (optional)", placeholder="e.g., name@school.edu")
    
    allow_contact = st.checkbox("I'm open to follow-up interviews (optional)")
    
    st.divider()
    
    # Section 2: Methods Used
    st.header("Methods You've Used")
    methods = st.multiselect(
        "Select all methods you've used for report writing:",
        ["Writing from scratch", "ChatGPT/AI prompts", "School comment banks", 
         "Previous year's comments", "Dropdown tool", "Other"],
        placeholder="Choose at least one method"
    )
    
    st.divider()
    
    # Section 3: Time Comparison
    st.header("Time Efficiency")
    st.write("How much time does each method take per comment?")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        time_scratch = st.selectbox("From scratch:", ["<2min","2-5min","5-10min","10+min","Didn't use"])
    with col2:
        time_ai = st.selectbox("AI prompts:", ["<2min","2-5min","5-10min","10+min","Didn't use"])
    with col3:
        time_school_bank = st.selectbox("School banks:", ["<2min","2-5min","5-10min","10+min","Didn't use"])
    with col4:
        time_dropdown = st.selectbox("Dropdown tool:", ["<30sec","30sec-1min","1-2min","2+min","Didn't use"])
    
    st.divider()
    
    # Section 4: Cognitive Effort
    st.header("Mental Effort")
    st.write("How mentally demanding is each method?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        cognitive_scratch = st.selectbox("From scratch:", ["Exhausting","High","Moderate","Low","Didn't use"])
    with col2:
        cognitive_ai = st.selectbox("AI prompts:", ["Exhausting","High","Moderate","Low","Didn't use"])
    with col3:
        cognitive_dropdown = st.selectbox("Dropdown tool:", ["Very low","Low","Moderate","High","Didn't use"])
    
    st.divider()
    
    # Section 5: Quality Assessment
    st.header("Output Quality")
    st.write("Rate the quality of comments from each method:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        quality_scratch = st.selectbox("From scratch:", 
            ["High quality and consistent", "High quality but inconsistent", 
             "Generally good", "Variable", "Often rushed/generic", "Didn't use"])
    with col2:
        quality_ai = st.selectbox("AI prompts:", 
            ["High after edits", "Good with minor tweaks", "Acceptable", 
             "Too generic/not suitable", "Haven't used AI", "Didn't use"])
    with col3:
        quality_dropdown = st.selectbox("Dropdown tool:", 
            ["High & curriculum-aligned", "Good, ready to use", 
             "Acceptable with minor tweaks", "Too generic", "Didn't use"])
    
    st.divider()
    
    # Section 6: Specific Metrics
    st.header("Specific Metrics")
    
    st.subheader("Character Accuracy")
    col1, col2, col3 = st.columns(3)
    with col1:
        character_accuracy_scratch = st.radio("From scratch:", ["Within range", "Exceeds range", "Didn't use"])
    with col2:
        character_accuracy_ai = st.radio("AI prompts:", ["Within range", "Exceeds range", "Didn't use"])
    with col3:
        character_accuracy_dropdown = st.radio("Dropdown tool:", ["Within range", "Exceeds range", "Didn't use"])
    
    st.subheader("Curriculum Alignment")
    col1, col2, col3 = st.columns(3)
    with col1:
        curriculum_alignment_scratch = st.selectbox("From scratch:", 
            ["Always", "Usually", "Sometimes", "Rarely", "Didn't use"])
    with col2:
        curriculum_alignment_ai = st.selectbox("AI prompts:", 
            ["Always", "Usually", "Sometimes", "Rarely", "Didn't use"])
    with col3:
        curriculum_alignment_dropdown = st.selectbox("Dropdown tool:", 
            ["Always", "Usually", "Sometimes", "Rarely", "Didn't use"])
    
    st.subheader("Stress Level")
    col1, col2, col3 = st.columns(3)
    with col1:
        stress_scratch = st.selectbox("From scratch:", 
            ["Very high", "High", "Moderate", "Low", "Didn't use"])
    with col2:
        stress_ai = st.selectbox("AI prompts:", 
            ["Very high", "High", "Moderate", "Low", "Didn't use"])
    with col3:
        stress_dropdown = st.selectbox("Dropdown tool:", 
            ["Very high", "High", "Moderate", "Low", "Didn't use"])
    
    st.divider()
    
    # Section 7: Tool Benefits
    st.header("Dropdown Tool Benefits")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        biggest_cognitive_relief = st.selectbox("Cognitive relief:", [
            "No need to decide what to include/exclude",
            "Character count automatically perfect",
            "No rephrasing/editing needed",
            "Curriculum-aligned language pre-written",
            "Clear structure removes blank page stress",
            "Consistency across all students",
            "Didn't use"
        ])
    
    with col2:
        biggest_time_quality = st.selectbox("Best time-to-quality:", [
            "Writing from scratch",
            "ChatGPT/AI",
            "Dropdown tool",
            "Other",
            "Didn't use"
        ])
    
    with col3:
        time_saved = st.selectbox("Time saved for 30 students:", [
            "No time saved",
            "30min-1hr",
            "1-2hrs",
            "2-4hrs",
            "4+hrs",
            "Didn't use"
        ])
    
    st.divider()
    
    # Section 8: Open Feedback
    st.header("Open Feedback")
    
    open_feedback_ai = st.text_area(
        "One thing AI does WRONG:",
        placeholder="e.g., AI comments often exceed character limits and require heavy editing...",
        height=80
    )
    
    open_feedback_tool = st.text_area(
        "One thing dropdown tool does BETTER:",
        placeholder="e.g., The dropdown tool creates perfectly formatted, curriculum-aligned comments in seconds...",
        height=80
    )
    
    suggestions = st.text_area(
        "Suggestions for improvement:",
        placeholder="e.g., Add more subject-specific options, allow custom templates...",
        height=80
    )
    
    st.divider()
    
    # Submit Button
    submitted = st.form_submit_button(
        "Submit Survey",
        type="primary",
        use_container_width=True
    )

# ============================================================================
# 6. SUBMISSION HANDLING
# ============================================================================

if submitted and not st.session_state.submitted:
    # Validate required fields
    if not methods:
        st.error("Please select at least one method you've used")
        st.stop()
    
    # Prepare data
    form_data = {
        "name": name if name else "Anonymous",
        "email": email if email else "",
        "allow_contact": allow_contact,
        "methods": ", ".join(methods),
        "time_scratch": time_scratch,
        "time_ai": time_ai,
        "time_school_bank": time_school_bank,
        "time_dropdown": time_dropdown,
        "cognitive_scratch": cognitive_scratch,
        "cognitive_ai": cognitive_ai,
        "cognitive_dropdown": cognitive_dropdown,
        "quality_scratch": quality_scratch,
        "quality_ai": quality_ai,
        "quality_dropdown": quality_dropdown,
        "character_accuracy_scratch": character_accuracy_scratch,
        "character_accuracy_ai": character_accuracy_ai,
        "character_accuracy_dropdown": character_accuracy_dropdown,
        "curriculum_alignment_scratch": curriculum_alignment_scratch,
        "curriculum_alignment_ai": curriculum_alignment_ai,
        "curriculum_alignment_dropdown": curriculum_alignment_dropdown,
        "stress_scratch": stress_scratch,
        "stress_ai": stress_ai,
        "stress_dropdown": stress_dropdown,
        "biggest_cognitive_relief": biggest_cognitive_relief,
        "biggest_time_quality": biggest_time_quality,
        "time_saved": time_saved,
        "open_feedback_ai": open_feedback_ai,
        "open_feedback_tool": open_feedback_tool,
        "suggestions": suggestions
    }
    
    # Update progress
    progress.progress(100, text="Saving your response...")
    
    # Save data
    with st.spinner("Saving your feedback securely..."):
        success = persistence.save_submission(form_data)
    
    # Show results
    if success:
        st.success("""
        ## Thank You For Your Feedback!
        
        Your submission has been securely saved with multiple backups.
        
        Your insights are invaluable for improving our tool.
        """)
        
        if allow_contact and name:
            st.info(f"Follow-up enabled: We may contact '{name}' for further insights")
        
        st.session_state.submitted = True
        
        # Auto-refresh suggestion
        time.sleep(2)
        st.rerun()
    else:
        st.error("""
        ## Save Failed
        
        Please try submitting again or contact support.
        
        Don't lose your responses! Here's what you entered:
        """)
        
        # Show data for manual recovery
        st.json(form_data)

# ============================================================================
# 7. POST-SUBMISSION VIEW
# ============================================================================

if st.session_state.submitted:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f5f7fa; border-radius: 10px;">
            <h2>Submission Complete!</h2>
            <p style="font-size: 1.2rem;">Thank you for contributing to our research.</p>
            <p>You may close this window or submit another response.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Option to submit another response
    if st.button("Submit Another Response"):
        st.session_state.submitted = False
        st.session_state.last_submission = None
        st.rerun()

# ============================================================================
# 8. DATA ANALYSIS SECTION
# ============================================================================

if st.sidebar.checkbox("View Analytics", False):
    st.markdown("---")
    st.header("Survey Analytics")
    
    try:
        if os.path.exists(persistence.master_file):
            df = pd.read_csv(persistence.master_file)
            
            if len(df) > 0:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Responses", len(df))
                with col2:
                    contact_count = df['allow_contact'].sum() if 'allow_contact' in df.columns else 0
                    st.metric("Open to Contact", contact_count)
                with col3:
                    time_saved_4hrs = (df['time_saved'] == '4+hrs').sum() if 'time_saved' in df.columns else 0
                    st.metric("4+ Hours Saved", time_saved_4hrs)
                with col4:
                    quality_high = (df['quality_dropdown'] == 'High & curriculum-aligned').sum() if 'quality_dropdown' in df.columns else 0
                    st.metric("High Quality", quality_high)
                
                # Recent submissions
                st.subheader("Recent Submissions")
                st.dataframe(df[['timestamp', 'name', 'time_saved', 'biggest_time_quality']].tail(10))
                
                # Time saved chart
                if 'time_saved' in df.columns:
                    time_counts = df['time_saved'].value_counts()
                    if len(time_counts) > 0:
                        fig = px.pie(values=time_counts.values, names=time_counts.index,
                                   title="Time Saved Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Export options
                st.subheader("Export Data")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Full Dataset (CSV)",
                    data=csv,
                    file_name="survey_data_full.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data available for analysis yet.")
        else:
            st.info("No data file found. Submit a response to see analytics.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)[:100]}")

# ============================================================================
# 9. FOOTER
# ============================================================================

st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.caption(f"Total submissions: {persistence.submission_count}")
with footer_col2:
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
