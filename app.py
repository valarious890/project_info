import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.title("Music vs Thriller")

# --- Load Data ---
genre_url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"
df = pd.read_csv(genre_url)
df["genre_label"] = df["genre_label"].str.strip().str.lower()
df["videoNumber"] = df["index"].astype(int)

gaze = pd.read_csv("https://huggingface.co/datasets/valarious890/genre_eye_tracking/resolve/main/genre_eye_tracking.csv")
gaze = gaze[gaze["missing"] == 0]
gaze["t_sec"] = gaze["t"] / 1000
gaze["videoNumber"] = gaze["videoNumber"].astype(int)

# Merge genre label into gaze data
gaze = gaze.merge(df[["videoNumber", "genre_label"]], on="videoNumber", how="left")

# --- Section 1: Feature Comparison ---
st.header("📊 Visual & Audio Feature Comparison")
feature_cols = ["# cuts", "faces (0-5)", "human figures (0-5)", "nature (0-5)",
                "man-made objects (0-5)", "light (0-5)", "aud. Info"]
genre_summary = df.groupby("genre_label")[feature_cols].mean().reset_index()
melted = genre_summary.melt(id_vars="genre_label", var_name="feature", value_name="average_score")

fig1 = px.bar(
    melted, x="feature", y="average_score", color="genre_label",
    barmode="group", title="🔍 Average Visual & Audio Features",
    labels={"average_score": "Avg Score", "feature": "Feature", "genre_label": "Genre"}
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# --- Section 2: Radar Chart ---
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

# --- Section 3: Visual Style Analysis ---
st.header("🎥 Genre Visual Style Analysis")

light_counts = df.groupby(["genre_label", "light category"]).size().reset_index(name="count")
fig3 = px.bar(
    light_counts, x="light category", y="count", color="genre_label",
    barmode="group", title="💡 Light Category Frequency"
)
st.plotly_chart(fig3, use_container_width=True)

env_counts = df.groupby(["genre_label", "environment"]).size().reset_index(name="count")
fig4 = px.bar(
    env_counts, x="environment", y="count", color="genre_label",
    barmode="group", title="🌍 Environment Frequency"
)
st.plotly_chart(fig4, use_container_width=True)

# --- Section 4: Fixation & Gaze Viewer ---
st.header("👁️ Fixation & Gaze Visualization")

# --- Styled Toggle Selector for Genre ---
st.markdown("""
<style>
.toggle-container {
    display: flex;
    justify-content: center;
    margin-bottom: 1rem;
}
.toggle-button {
    flex: 1;
    padding: 0.75rem;
    text-align: center;
    font-weight: bold;
    background-color: #ccc;
    color: black;
    border: none;
    cursor: pointer;
}
.toggle-button.selected {
    background-color: #5bc0de;
}
</style>
""", unsafe_allow_html=True)

# --- Genre Selector Logic ---
if "genre_selected" not in st.session_state:
    st.session_state.genre_selected = "music"

selected_genre = st.session_state.genre_selected

col1, col2 = st.columns(2)
with col1:
    if st.button("music"):
        st.session_state.genre_selected = "music"
with col2:
    if st.button("thriller"):
        st.session_state.genre_selected = "thriller"

# --- Toggle Highlight (force refresh with rerun) ---
st.markdown(f"""
<div class="toggle-container">
    <div class="toggle-button {'selected' if st.session_state.genre_selected == 'music' else ''}">music</div>
    <div class="toggle-button {'selected' if st.session_state.genre_selected == 'thriller' else ''}">thriller</div>
</div>
""", unsafe_allow_html=True)

# Use the selected genre
genre_selected = st.session_state.genre_selected


# --- Filter video numbers ---
video_options = sorted(gaze[gaze["genre_label"] == genre_selected]["videoNumber"].unique())
selected_video = st.selectbox("🎞️ Select Video Number", video_options)

# --- Observer Mapping (1,2,3...) ---
video_obs = gaze[gaze["videoNumber"] == selected_video]["observer"].unique()
observer_map = {orig: f"{i+1}" for i, orig in enumerate(sorted(video_obs))}
gaze["observer_mapped"] = gaze["observer"].map(observer_map)
selected_mapped = st.selectbox("👁️ Select Observer", sorted(observer_map.values()))
selected_observer = {v: k for k, v in observer_map.items()}[selected_mapped]

# --- Filter and Plot ---
gaze_filtered = gaze[(gaze["videoNumber"] == selected_video) & (gaze["observer"] == selected_observer)]

if gaze_filtered.empty:
    st.warning("No gaze data available for this combination.")
else:
    fig_gaze = px.scatter(
        gaze_filtered, x="x", y="y", size="pa", color="t_sec", animation_frame="t_sec",
        title=f"Fixation Plot - {genre_selected.title()} | Video {selected_video}, Observer {selected_mapped}",
        height=500, color_continuous_scale="Viridis"
    )
    fig_gaze.update_yaxes(autorange='reversed')
    fig_gaze.update_layout(xaxis_title="X", yaxis_title="Y")
    st.plotly_chart(fig_gaze, use_container_width=True)

