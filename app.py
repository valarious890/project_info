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

import plotly.express as px

st.header("📊 Visual & Audio Feature Comparison")

# Compute average values for each genre
feature_cols = [
    "faces (0-5)", "human figures (0-5)", "nature (0-5)",
    "man-made objects (0-5)", "light (0-5)", "aud. Info"
]
genre_summary = df.groupby("genre_label")[feature_cols].mean().reset_index()

# Melt data for plotting
melted = genre_summary.melt(id_vars="genre_label", var_name="feature", value_name="average_score")

# Plot as grouped bar chart
fig = px.bar(
    melted,
    x="feature",
    y="average_score",
    color="genre_label",
    barmode="group",
    title="🔍 Average Visual & Audio Features: Music vs Thriller",
    labels={"average_score": "Avg Score", "feature": "Feature", "genre_label": "Genre"}
)

fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

