import streamlit as st
import pandas as pd

st.set_page_config(page_title="Video Overview", layout="wide")
st.title("🎬 30s Video Segment Descriptions")

# Load video descriptions
desc = pd.read_csv("https://drive.google.com/uc?export=download&id=1_5OPeORG8vE2c40G-ceACmnQhwFaj9NQ")

# Clean videoNumber
desc = desc[desc["ch"].notna()]
desc["videoNumber"] = desc["ch"].astype(int)

# Let user select a video
selected_video = st.selectbox("🎞️ Select a video segment to view", sorted(desc["videoNumber"].unique()))

# Show segment metadata
selected_row = desc[desc["videoNumber"] == selected_video].iloc[0]
st.markdown(f"""
### 📝 {selected_row['movie name']}
⏱️ Duration: {selected_row['length']} seconds  
🌍 Environment: {selected_row['environment']}  
""")

# Save selected video to session state for next page
st.session_state["selected_video"] = selected_video

# Navigation button to viewer
st.page_link("pages/Gaze_Viewer.py", label="🔍 View Gaze Visualization", icon="🎯")
