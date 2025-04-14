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

