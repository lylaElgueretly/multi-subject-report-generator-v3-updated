import streamlit as st

st.title("Import Test - All Years")

st.subheader("Year 5 Maths")
try:
    from statements_year5_Maths import maths_bank as y5_maths
    st.success("Year 5 SUCCESS")
except ImportError as e:
    st.error(f"Year 5 failed: {e}")

st.subheader("Year 7 Maths")
try:
    from statements_year7_Maths import maths_bank as y7_maths
    st.success("Year 7 SUCCESS")
except ImportError as e:
    st.error(f"Year 7 failed: {e}")

st.subheader("Year 8 Maths")
try:
    from statements_year8_Maths import maths_bank as y8_maths
    st.success("Year 8 SUCCESS")
except ImportError as e:
    st.error(f"Year 8 failed: {e}")
