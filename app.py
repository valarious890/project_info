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

# === Genre Selector UI with Custom CSS ===
st.markdown("""
<style>
.genre-selector {
    display: flex;
    margin-bottom: 1rem;
}
.genre-tab {
    flex: 1;
    padding: 0.75rem;
    text-align: center;
    font-weight: bold;
    color: black;
    background-color: #ccc;
    cursor: pointer;
    border-radius: 0;
}
.genre-tab.selected {
    background-color: #5bc0de;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# === Genre Selection Logic ===
genres = ["music", "thriller"]
selected_genre = st.session_state.get("selected_genre", genres[0])

# Create fake buttons
genre_cols = st.columns(len(genres))
for i, g in enumerate(genres):
    if genre_cols[i].button(f"{g}", key=f"genre_{g}"):
        st.session_state.selected_genre = g
        selected_genre = g

# Load data (assuming already loaded above)
# genre_selected is now:
genre_selected = selected_genre

# === Filter video numbers based on selected genre ===
video_options = sorted(gaze[gaze["genre_label"] == genre_selected]["videoNumber"].unique())
selected_video = st.selectbox("🎞️ Select Video Number", video_options)

# === Observer mapping: assign 1, 2, 3… per video number ===
video_obs = gaze[gaze["videoNumber"] == selected_video]["observer"].unique()
observer_map = {orig: f"{i+1}" for i, orig in enumerate(sorted(video_obs))}
gaze["observer_mapped"] = gaze["observer"].map(observer_map)

# Select observer by 1, 2, 3
selected_mapped = st.selectbox("👁️ Select Observer", sorted(observer_map.values()))

# Get original observer name from mapped
reverse_map = {v: k for k, v in observer_map.items()}
selected_observer = reverse_map[selected_mapped]

# === Filter gaze data ===
gaze_filtered = gaze[(gaze["videoNumber"] == selected_video) & (gaze["observer"] == selected_observer)]

# === Plot ===
if gaze_filtered.empty:
    st.warning("No gaze data available for this combination.")
else:
    fig_gaze = px.scatter(
        gaze_filtered, x="x", y="y", size="pa", color="t_sec", animation_frame="t_sec",
        title=f"Animated Fixation - {genre_selected.title()} | Video {selected_video}, Observer {selected_mapped}",
        height=500, color_continuous_scale="Viridis"
    )
    fig_gaze.update_yaxes(autorange='reversed')
    fig_gaze.update_layout(xaxis_title="X Position", yaxis_title="Y Position")
    st.plotly_chart(fig_gaze, use_container_width=True)
