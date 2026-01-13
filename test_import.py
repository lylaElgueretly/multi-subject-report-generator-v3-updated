import streamlit as st

st.title("Import Test")

try:
    from statements_year5_Maths import maths_bank
    st.success("SUCCESS! Imported maths_bank")
    st.write("Sample value:", maths_bank.get(90, "Not found"))
except ImportError as e:
    st.error(f"Failed to import maths_bank: {e}")

try:
    from statements_year5_Maths import number_bank
    st.warning("PROBLEM! Found old number_bank variable")
except ImportError:
    st.success("Good - number_bank doesn't exist (as expected)")

import statements_year5_Maths
st.write("All variables in file:", [x for x in dir(statements_year5_Maths) if not x.startswith('_')])
