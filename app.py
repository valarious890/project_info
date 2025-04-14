import streamlit as st
import pandas as pd

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.title("🎬 Genre Comparison: Music vs Thriller")

# Load the filtered genre dataset
url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"  # replace if needed
df = pd.read_csv(url)

# Clean genre labels
df["genre_label"] = df["genre_label"].str.strip().str.lower()

# Filter genres
music_df = df[df["genre_label"] == "music"]
thriller_df = df[df["genre_label"] == "thriller"]

# Optional: Add videoNumber if missing (use 'ch' column)
df = df[pd.to_numeric(df["ch"], errors="coerce").notna()]
df["videoNumber"] = df["ch"].astype(float).astype(int)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎵 Music Segments")
    for _, row in music_df.iterrows():
        st.markdown(f"""
        **🎞️ {row['movie name']}**  
        ⏱️ Length: {row['length']}  
        🌍 Env: {row['environment']}  
        👁️ Video: `{int(row['ch'])}`  
        """)
        if st.button(f"🔍 View Gaze (Music {int(row['ch'])})", key=f"music-{row['ch']}"):
            st.session_state["selected_video"] = int(row["ch"])
            st.switch_page("pages/Gaze_Viewer.py")

with col2:
    st.subheader("🎬 Thriller Segments")
    for _, row in thriller_df.iterrows():
        st.markdown(f"""
        **🎞️ {row['movie name']}**  
        ⏱️ Length: {row['length']}  
        🌍 Env: {row['environment']}  
        👁️ Video: `{int(row['ch'])}`  
        """)
        if st.button(f"🔍 View Gaze (Thriller {int(row['ch'])})", key=f"thriller-{row['ch']}"):
            st.session_state["selected_video"] = int(row["ch"])
            st.switch_page("pages/Gaze_Viewer.py")


