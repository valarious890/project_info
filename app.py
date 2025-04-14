import streamlit as st
import pandas as pd

st.set_page_config(page_title="Music vs Thriller", layout="wide")
st.title("🎬 Genre Comparison: Music vs Thriller")

# Load video descriptions
desc = pd.read_csv("https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt")

# Keep only rows where 'ch' is a number
desc = desc[pd.to_numeric(desc["ch"], errors="coerce").notna()]
desc["videoNumber"] = desc["ch"].astype(float).astype(int)

# Clean genre column (optional: make lowercase, strip spaces)
desc["genre"] = desc["genre"].str.strip().str.lower()

# Define the two genres to compare
genre1 = "music"
genre2 = "thriller"

# Filter segments by genre
music_df = desc[desc["genre"] == genre1]
thriller_df = desc[desc["genre"] == genre2]

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎵 Music Segments")
    for _, row in music_df.iterrows():
        st.markdown(f"""
        **🎞️ {row['movie name']}**  
        ⏱️ Duration: {row['length']}s  
        🌍 Env: {row['environment']}  
        👁️ Video: `{int(row['videoNumber'])}`  
        """)
        if st.button(f"🔍 View Gaze: Music {int(row['videoNumber'])}", key=f"music-{row['videoNumber']}"):
            st.session_state["selected_video"] = int(row["videoNumber"])
            st.switch_page("pages/Gaze_Viewer.py")

with col2:
    st.subheader("🎬 Thriller Segments")
    for _, row in thriller_df.iterrows():
        st.markdown(f"""
        **🎞️ {row['movie name']}**  
        ⏱️ Duration: {row['length']}s  
        🌍 Env: {row['environment']}  
        👁️ Video: `{int(row['videoNumber'])}`  
        """)
        if st.button(f"🔍 View Gaze: Thriller {int(row['videoNumber'])}", key=f"thriller-{row['videoNumber']}"):
            st.session_state["selected_video"] = int(row["videoNumber"])
            st.switch_page("pages/Gaze_Viewer.py")


