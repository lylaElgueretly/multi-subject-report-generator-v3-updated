import streamlit as st
import os
import sys

st.title("ROOT CAUSE DIAGNOSTIC")

# 1. Show where we are
st.write("### Current working directory:", os.getcwd())

# 2. Show ALL files recursively
st.write("### ALL FILES (recursive):")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            st.write(os.path.join(root, file))

# 3. Show Python path
st.write("### Python sys.path:")
for path in sys.path:
    st.write(path)

# 4. Try direct file read
st.write("### Can we READ the file directly?")
try:
    with open('statements_year5_Maths_NEW.py', 'r') as f:
        content = f.read(100)
        st.success(f"✓ Can read file: {content[:50]}...")
except Exception as e:
    st.error(f"✗ Cannot read file: {e}")

# 5. Try importing with different methods
st.write("### Import methods:")
import importlib.util

spec = importlib.util.spec_from_file_location(
    "maths_test", 
    "statements_year5_Maths_NEW.py"
)
if spec:
    st.success("✓ Can create spec from file")
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        st.success("✓ Can execute module")
    except Exception as e:
        st.error(f"✗ Cannot execute: {e}")
else:
    st.error("✗ Cannot create spec")
