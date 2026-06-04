content = """import streamlit as st

st.set_page_config(
    page_title="Planer App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📋 Planer App")
st.write("Willkommen! Die App wird gerade aufgebaut.")
"""

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Gespeichert!")
