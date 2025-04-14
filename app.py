import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.title("Music vs Thriller")

# Custom page background color
st.markdown("""
<style>
body {
    background-color: #312D2D !important;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
genre_url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"
df = pd.read_csv(genre_url)
df["genre_label"] = df["genre_label"].str.strip().str.lower()
df["videoNumber"] = df["index"].astype(int)

# Fixation data
gaze = pd.read_csv("https://huggingface.co/datasets/valarious890/genre_eye_tracking/resolve/main/fixation_eye_tracking.csv")

gaze = gaze[gaze["missing"] == 0]
gaze = gaze[(gaze['x'] >= 0) & (gaze['y'] >= 0)]
gaze["videoNumber"] = gaze["videoNumber"].astype(int)

# Merge genre info
gaze = gaze.merge(df[["videoNumber", "genre_label", "movie name"]], on="videoNumber", how="left")

# === Global x and y limits ===
x_min, x_max = gaze["x"].min(), gaze["x"].max()
y_min, y_max = gaze["y"].min(), gaze["y"].max()

# --- Section: Radar Chart ---
st.header("📈 Radar Chart: Feature Profiles")

radar_cols = ["faces (0-5)", "human figures (0-5)", "nature (0-5)",
              "man-made objects (0-5)", "light (0-5)", "aud. Info"]
radar_summary = df.groupby("genre_label")[radar_cols].mean().reset_index()
radar_summary = radar_summary.rename(columns={
    "faces (0-5)": "Faces", "human figures (0-5)": "Humans", "nature (0-5)": "Nature",
    "man-made objects (0-5)": "Objects", "light (0-5)": "Light", "aud. Info": "Audio"
})
melted_radar = radar_summary.melt(id_vars="genre_label", var_name="Feature", value_name="Average Score")

fig_radar = px.line_polar(
    melted_radar, r="Average Score", theta="Feature", color="genre_label",
    line_close=True, markers=True,
    title="🎯 Feature Comparison: Music vs Thriller",
    range_r=[0, 5],
    color_discrete_map={"music": "#71C8E2", "thriller": "#F14C2E"}
)
fig_radar.update_layout(plot_bgcolor="#312D2D", paper_bgcolor="#312D2D")
st.plotly_chart(fig_radar, use_container_width=True)

# --- Section: Visual Style ---
st.header("🎥 Genre Visual Style Analysis")
light_counts = df.groupby(["genre_label", "light category"]).size().reset_index(name="count")
fig3 = px.bar(light_counts, x="light category", y="count", color="genre_label",
              barmode="group", title="💡 Light Category Frequency",
              color_discrete_map={"music": "#71C8E2", "thriller": "#F14C2E"})
fig3.update_layout(plot_bgcolor="#312D2D", paper_bgcolor="#312D2D")
st.plotly_chart(fig3, use_container_width=True)

env_counts = df.groupby(["genre_label", "environment"]).size().reset_index(name="count")
fig4 = px.bar(env_counts, x="environment", y="count", color="genre_label",
              barmode="group", title="🌍 Environment Frequency",
              color_discrete_map={"music": "#71C8E2", "thriller": "#F14C2E"})
fig4.update_layout(plot_bgcolor="#312D2D", paper_bgcolor="#312D2D")
st.plotly_chart(fig4, use_container_width=True)

# --- Section: Fixation Viewer ---
st.header("👁️ Fixation & Gaze Visualization")

# Genre selector
st.markdown("""
<style>
div[data-baseweb="radio"] > div {
    flex-direction: row !important;
    justify-content: center;
}
div[role="radiogroup"] > div {
    margin-right: 1rem;
    border: 1px solid #999;
    padding: 0.5rem 1.5rem;
    border-radius: 10px;
    background-color: #ddd;
    font-weight: bold;
    color: black;
    cursor: pointer;
}
div[role="radiogroup"] > div[data-selected="true"] {
    background-color: #5bc0de;
    color: black;
    border: 2px solid #4aa4c4;
}
</style>
""", unsafe_allow_html=True)

genre_selected = st.radio(
    "🎵 Choose Genre",
    options=["music", "thriller"],
    index=0 if "genre_selected" not in st.session_state else ["music", "thriller"].index(st.session_state.genre_selected),
    horizontal=True,
    key="genre_selected"
)

video_options = sorted(gaze[gaze["genre_label"] == genre_selected]["videoNumber"].unique())
selected_video = st.selectbox("🎞️ Select Video Number", video_options)

# Observer mapping
video_obs = sorted(gaze[gaze["videoNumber"] == selected_video]["observer"].unique())
observer_map = {orig: str(i+1) for i, orig in enumerate(video_obs)}
gaze["observer_mapped"] = gaze["observer"].map(observer_map)

mapped_obs_options = sorted(observer_map.values(), key=int)
selected_mapped = st.selectbox("👁️ Select Observer", mapped_obs_options)
reverse_map = {v: k for k, v in observer_map.items()}
selected_observer = reverse_map[selected_mapped]

# Filter fixation data
fixation_filtered = gaze[
    (gaze["videoNumber"] == selected_video) & (gaze["observer"] == selected_observer)
]

if fixation_filtered.empty:
    st.warning("No fixation data available for this combination.")
else:
    movie_name = df[df["videoNumber"] == selected_video]["movie name"].values[0]

    fig_fix = px.scatter(
        fixation_filtered,
        x="x", y="y", color="fixation_label", size="duration",
        title=f"Fixation Plot - {genre_selected.title()} | {movie_name} | Video {selected_video}, Observer {selected_mapped}",
        height=500,
        color_discrete_map={"fixation": "#F14C2E", "non-fixation": "#AAAAAA"}
    )
    fig_fix.update_yaxes(autorange="reversed")
    fig_fix.update_layout(
        xaxis_range=[x_min, x_max], yaxis_range=[y_max, y_min],
        xaxis_title="X", yaxis_title="Y",
        plot_bgcolor="#312D2D", paper_bgcolor="#312D2D"
    )
    st.plotly_chart(fig_fix, use_container_width=True)

    fixation_only = fixation_filtered[fixation_filtered["fixation_label"] == "fixation"]
    if not fixation_only.empty:
        st.subheader("📍 Average Fixation Locations")
        fig_avg = px.scatter(
            fixation_only, x="avg_x", y="avg_y", color="duration", size="duration",
            color_continuous_scale="Plasma", title="Average Fixation Centroids",
            labels={"avg_x": "Avg X", "avg_y": "Avg Y"}
        )
        fig_avg.update_yaxes(autorange="reversed")
        fig_avg.update_layout(
            xaxis_range=[x_min, x_max], yaxis_range=[y_max, y_min],
            plot_bgcolor="#312D2D", paper_bgcolor="#312D2D"
        )
        st.plotly_chart(fig_avg, use_container_width=True)

