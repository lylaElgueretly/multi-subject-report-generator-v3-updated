import streamlit as st
import os

st.title("What's Actually Deployed?")

st.write("### All files in directory:")
for file in sorted(os.listdir('.')):
    if 'Maths' in file or 'maths' in file:
        st.write(f"**{file}**")
    else:
        st.write(file)

st.write("### Trying to import...")
try:
    import statements_year5_Maths_NEW
    st.success("✓ Can import statements_year5_Maths_NEW")
except Exception as e:
    st.error(f"✗ Cannot import: {e}")

# Try to find ANY Maths files
st.write("### Searching for Maths files...")
import glob
maths_files = glob.glob("*Maths*") + glob.glob("*maths*")
for f in maths_files:
    st.write(f"- {f}")
