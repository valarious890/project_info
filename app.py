import streamlit as st
import pandas as pd

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.title("Music vs Thriller")

# Genre page buttons (placed directly below the title)
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🎵 Go to Music Page"):
        st.switch_page("pages/Music_Only.py")  # Adjust this if your filename is different

with col2:
    if st.button("🎬 Go to Thriller Page"):
        st.switch_page("pages/Thriller_Only.py")

# Load the filtered genre dataset
url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"  # replace if needed
df = pd.read_csv(url)

# Clean genre labels
df["genre_label"] = df["genre_label"].str.strip().str.lower()

# Filter genres
music_df = df[df["genre_label"] == "music"]
thriller_df = df[df["genre_label"] == "thriller"]

import plotly.express as px

st.header("📊 Visual & Audio Feature Comparison")

# Compute average values for each genre
feature_cols = [
    "# cuts", "faces (0-5)", "human figures (0-5)", "nature (0-5)",
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

import plotly.express as px

st.header("📈 Radar Chart: Feature Profiles")

# Compute mean values for each genre
feature_cols = [
    "faces (0-5)", "human figures (0-5)", "nature (0-5)",
    "man-made objects (0-5)", "light (0-5)", "aud. Info"
]
genre_summary = df.groupby("genre_label")[feature_cols].mean().reset_index()

# Rename columns for readability
genre_summary = genre_summary.rename(columns={
    "faces (0-5)": "Faces",
    "human figures (0-5)": "Humans",
    "nature (0-5)": "Nature",
    "man-made objects (0-5)": "Objects",
    "light (0-5)": "Light",
    "aud. Info": "Audio"
})

# Melt for radar plot
melted = genre_summary.melt(id_vars="genre_label", var_name="Feature", value_name="Average Score")

# Radar plot
fig = px.line_polar(
    melted,
    r="Average Score",
    theta="Feature",
    color="genre_label",
    line_close=True,
    markers=True,
    title="🎯 Feature Comparison: Music vs Thriller"
)

st.plotly_chart(fig, use_container_width=True)

import plotly.express as px

st.header("🎥 Genre Visual Style Analysis")

# Light category frequency per genre
light_counts = df.groupby(["genre_label", "light category"]).size().reset_index(name="count")
light_fig = px.bar(
    light_counts,
    x="light category",
    y="count",
    color="genre_label",
    barmode="group",
    title="💡 Light Category Frequency by Genre",
    labels={"count": "Count", "light category": "Light Category", "genre_label": "Genre"}
)
st.plotly_chart(light_fig, use_container_width=True)

# Environment frequency per genre
env_counts = df.groupby(["genre_label", "environment"]).size().reset_index(name="count")
env_fig = px.bar(
    env_counts,
    x="environment",
    y="count",
    color="genre_label",
    barmode="group",
    title="🌍 Environment Frequency by Genre",
    labels={"count": "Count", "environment": "Environment", "genre_label": "Genre"}
)
st.plotly_chart(env_fig, use_container_width=True)

