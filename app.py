import streamlit as st
import pandas as pd

st.set_page_config(page_title="Video Overview", layout="wide")
st.title("🎬 30s Video Segment Descriptions")

# Load descriptions
desc = pd.read_csv("https://drive.google.com/uc?export=download&id=1_5OPeORG8vE2c40G-ceACmnQhwFaj9NQ")

# Simulate or map to eye-tracking videoNumbers
desc["videoNumber"] = desc["ch"]  # Change this line if needed

# Display list of video segments with links to viewer page
for _, row in desc.iterrows():
    st.markdown(f"""
    ### 🎞️ {row['movie name']} - Segment {int(row['videoNumber'])}
    ⏱️ Duration: {row['length']}  
    🌍 Environment: {row['environment']}  
    👀 [View Gaze Visualization ▶️](Gaze_Viewer?video={int(row['videoNumber'])})
    ---
    """)
