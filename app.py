import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.title("Music vs Thriller")

# === Section 1: Static Genre Images ===
#st.subheader("🎞️ Sample Frames")
#col1, col2 = st.columns(2)
#with col1:
    #st.image("https://via.placeholder.com/300x200.png?text=Music+Scene", caption="Music Scene")
#with col2:
    #st.image("https://via.placeholder.com/300x200.png?text=Thriller+Scene", caption="Thriller Scene")

# === Section 2: Load and Prepare Data ===
# Genre metadata
genre_url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"
df = pd.read_csv(genre_url)
df["genre_label"] = df["genre_label"].str.strip().str.lower()
#st.write("Gaze Data Columns:", df.columns.tolist())

# Gaze data
gaze = pd.read_csv("https://huggingface.co/datasets/valarious890/genre_eye_tracking/resolve/main/genre_eye_tracking.csv")

gaze = gaze[gaze["missing"] == 0]
gaze["t_sec"] = gaze["t"] / 1000

df["videoNumber"] = df["index"]
df["videoNumber"] = df["videoNumber"].astype(int)
gaze["videoNumber"] = gaze["videoNumber"].astype(int)

#merge gaze data
gaze = gaze.merge(df[["videoNumber", "genre_label"]], on="videoNumber", how="left")

# === Section 3: Feature Comparison (Bar + Radar) ===
st.header("📊 Visual & Audio Feature Comparison")
feature_cols = ["# cuts", "faces (0-5)", "human figures (0-5)", "nature (0-5)",
                "man-made objects (0-5)", "light (0-5)", "aud. Info"]
genre_summary = df.groupby("genre_label")[feature_cols].mean().reset_index()

melted = genre_summary.melt(id_vars="genre_label", var_name="feature", value_name="average_score")
fig1 = px.bar(
    melted, x="feature", y="average_score", color="genre_label",
    barmode="group", title="🔍 Average Visual & Audio Features: Music vs Thriller",
    labels={"average_score": "Avg Score", "feature": "Feature", "genre_label": "Genre"}
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

st.header("📈 Radar Chart: Feature Profiles")
radar_cols = ["faces (0-5)", "human figures (0-5)", "nature (0-5)",
              "man-made objects (0-5)", "light (0-5)", "aud. Info"]
radar_summary = df.groupby("genre_label")[radar_cols].mean().reset_index()
radar_summary = radar_summary.rename(columns={
    "faces (0-5)": "Faces", "human figures (0-5)": "Humans", "nature (0-5)": "Nature",
    "man-made objects (0-5)": "Objects", "light (0-5)": "Light", "aud. Info": "Audio"
})
melted_radar = radar_summary.melt(id_vars="genre_label", var_name="Feature", value_name="Average Score")
fig2 = px.line_polar(
    melted_radar, r="Average Score", theta="Feature", color="genre_label",
    line_close=True, markers=True, title="🎯 Feature Comparison: Music vs Thriller"
)
st.plotly_chart(fig2, use_container_width=True)

# === Section 4: Visual Style ===
st.header("🎥 Genre Visual Style Analysis")
light_counts = df.groupby(["genre_label", "light category"]).size().reset_index(name="count")
fig3 = px.bar(light_counts, x="light category", y="count", color="genre_label",
              barmode="group", title="💡 Light Category Frequency by Genre")
st.plotly_chart(fig3, use_container_width=True)

env_counts = df.groupby(["genre_label", "environment"]).size().reset_index(name="count")
fig4 = px.bar(env_counts, x="environment", y="count", color="genre_label",
              barmode="group", title="🌍 Environment Frequency by Genre")
st.plotly_chart(fig4, use_container_width=True)

# === Section 5: Fixation & Gaze Viewer ===
st.header("👁️ Fixation & Gaze Visualization")

# === Genre Selector ===
genre_selected = st.radio(
    "Select Genre",
    options=gaze["genre_label"].dropna().unique().tolist(),
    index=0,
    horizontal=True
)

# === Filter video numbers based on selected genre (from gaze data) ===
video_options = sorted(gaze[gaze["genre_label"] == genre_selected]["videoNumber"].unique())
selected_video = st.selectbox("🎞️ Select Video Number", video_options)

# === Observer options filtered by video number ===
observer_options = sorted(gaze[(gaze["videoNumber"] == selected_video)]["observer"].unique())
selected_observer = st.selectbox("👁️ Select Observer", observer_options)

# === Filter gaze data ===
gaze_filtered = gaze[(gaze["videoNumber"] == selected_video) & (gaze["observer"] == selected_observer)]

# === Plot ===
if gaze_filtered.empty:
    st.warning("No gaze data available for this combination.")
else:
    fig_gaze = px.scatter(
        gaze_filtered, x="x", y="y", size="pa", color="t_sec", animation_frame="t_sec",
        title=f"Animated Fixation - {genre_selected.title()} | Video {selected_video}, Observer {selected_observer}",
        height=500, color_continuous_scale="Viridis"
    )
    fig_gaze.update_yaxes(autorange='reversed')
    fig_gaze.update_layout(xaxis_title="X Position", yaxis_title="Y Position")
    st.plotly_chart(fig_gaze, use_container_width=True)
