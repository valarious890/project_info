import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Music vs Thriller Comparison", layout="wide")
st.markdown(
    "<h1 style='text-align: center; padding-top: 10px; font-size: 60px;'>Music or Thriller ?</div>", 
    unsafe_allow_html=True
)

# --- Dark Toggle Style ---
st.markdown("""
<style>
div[data-baseweb="radio"] > div {
    flex-direction: row !important;
    justify-content: center;
}
div[role="radiogroup"] > div {
    margin-right: 1rem;
    border: 1px solid #444;
    padding: 0.5rem 1.5rem;
    border-radius: 10px;
    background-color: #202020;
    font-weight: bold;
    color: white;
    cursor: pointer;
}
div[role="radiogroup"] > div[data-selected="true"] {
    background-color: #5bc0de;
    color: black;
    border: 2px solid #4aa4c4;
}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
genre_url = "https://drive.google.com/uc?export=download&id=1DkCDAFLUMP3wqioDJEa8aL3YldkQ4nWt"
df = pd.read_csv(genre_url)
df["genre_label"] = df["genre_label"].str.strip().str.lower()
df["videoNumber"] = df["index"].astype(int)

gaze = pd.read_csv("https://huggingface.co/datasets/valarious890/info/resolve/main/fixation_eye_tracking.csv")
gaze = gaze[gaze["missing"] == 0]
gaze = gaze[(gaze['x'] >= 0) & (gaze['y'] >= 0)]
gaze["videoNumber"] = gaze["videoNumber"].astype(int)
gaze = gaze.merge(df[["videoNumber", "genre_label", "movie name"]], on="videoNumber", how="left")

x_min, x_max = gaze["x"].min(), gaze["x"].max()
y_min, y_max = gaze["y"].min(), gaze["y"].max()

# === Radar Chart ===
st.subheader("Visual and Audio Feature Importance")

radar_cols = ["faces (0-5)", "human figures (0-5)", "nature (0-5)",
              "man-made objects (0-5)", "light (0-5)", "aud. Info"]
radar_summary = df.groupby("genre_label")[radar_cols].mean().reset_index()
radar_summary = radar_summary.rename(columns={
    "genre_label": "Genre", "faces (0-5)": "Faces", "human figures (0-5)": "Humans",
    "nature (0-5)": "Nature", "man-made objects (0-5)": "Objects",
    "light (0-5)": "Light", "aud. Info": "Audio"
})
melted_radar = radar_summary.melt(id_vars="Genre", var_name="Feature", value_name="Average Score")
color_map = {"music": "#71C8E2", "thriller": "#F14C2E"}

fig_radar = px.line_polar(
    melted_radar, r="Average Score", theta="Feature", color="Genre",
    line_close=True, markers=True,
    range_r=[0, 5],
    color_discrete_map=color_map
)
fig_radar.update_layout(
    title_text="",
    legend_title_text="Genre",
    height=500,
    width=650,
    margin=dict(t=50, b=50, l=50, r=50),
    font=dict(color="white"),
    polar=dict(
        angularaxis=dict(tickfont=dict(color="white")),
        radialaxis=dict(tickfont=dict(color="black"), gridcolor="#444", linecolor="black")
    )
)
left, center, right = st.columns([1, 10, 1])
with center:
    st.plotly_chart(fig_radar, use_container_width=True)

# === Light Category Plot ===
st.subheader("Light Category Distribution")

# Create full grid of genre x category
genres = df["genre_label"].unique()
light_levels = ["low", "medium", "high"]

# Create base DataFrame with all combinations
base = pd.DataFrame([(g, l) for g in genres for l in light_levels], columns=["genre_label", "light category"])

# Get actual counts
actual = df.dropna(subset=["light category"]).groupby(["genre_label", "light category"]).size().reset_index(name="Count")

# Merge with base to ensure all combinations exist
light_counts = pd.merge(base, actual, on=["genre_label", "light category"], how="left").fillna(0)
light_counts["Count"] = light_counts["Count"].astype(int)

# Format columns for plotting
light_counts["Genre"] = light_counts["genre_label"]
light_counts["Light Category"] = light_counts["light category"].str.capitalize()
light_counts["Light Category"] = pd.Categorical(
    light_counts["Light Category"], categories=["Low", "Medium", "High"], ordered=True
)

# Plot
fig3 = px.bar(
    light_counts, x="Light Category", y="Count", color="Genre",
    barmode="group",
    color_discrete_map=color_map
)
st.plotly_chart(fig3, use_container_width=True)


# === Environment Plot ===
st.subheader("Environment Distribution")
env_counts = df.groupby(["genre_label", "environment"]).size().reset_index(name="Count")
env_counts["Genre"] = env_counts["genre_label"]
env_counts["Environment"] = env_counts["environment"].str.capitalize()
fig4 = px.bar(
    env_counts, x="Environment", y="Count", color="Genre",
    barmode="group",
    color_discrete_map=color_map
)
fig4.update_layout(title_text="")
st.plotly_chart(fig4, use_container_width=True)

# === Box Plot for # Cuts ===
st.subheader("Shot Frequency (Number of Cuts)")
df["Genre"] = df["genre_label"]
fig_box = px.box(
    df,
    x="Genre",
    y="# cuts",
    color="Genre",
    category_orders={"Genre": ["music", "thriller"]},
    color_discrete_map=color_map
)
fig_box.update_layout(title_text="", 
                      xaxis_title="Genre", 
                      yaxis_title="Number of Cuts",
                      showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

# === Fixation Viewer ===
st.subheader("Gaze and Fixation")
genre_selected = st.radio(
    "Genre",
    options=["music", "thriller"],
    index=0,
    horizontal=True,
    key="genre_selected"
)

video_options = sorted(gaze[gaze["genre_label"] == genre_selected]["videoNumber"].unique())
selected_video = st.selectbox("Select Video Number", video_options)

video_obs = sorted(gaze[gaze["videoNumber"] == selected_video]["observer"].unique())
observer_map = {orig: str(i+1) for i, orig in enumerate(video_obs)}
gaze["observer_mapped"] = gaze["observer"].map(observer_map)

mapped_obs_options = sorted(observer_map.values(), key=int)
selected_mapped = st.selectbox("Select Observer", mapped_obs_options)
reverse_map = {v: k for k, v in observer_map.items()}
selected_observer = reverse_map[selected_mapped]

fixation_filtered = gaze[(gaze["videoNumber"] == selected_video) & (gaze["observer"] == selected_observer)]

if fixation_filtered.empty:
    st.warning("No fixation data available for this combination.")
else:
    movie_name = df[df["videoNumber"] == selected_video]["movie name"].values[0]

    st.markdown("<h4 style='margin-top: 1.5em;'>Gaze Plot by Timestamp</h4>", unsafe_allow_html=True)

    fig_gaze = px.scatter(
        fixation_filtered,
        x="x", y="y", color="timestamp",
        color_continuous_scale="Viridis",  # Or choose another like Plasma
        labels={"timestamp": "Timestamp"},
        height=600
    )

    fig_gaze.update_layout(
        title_text="",
        xaxis=dict(
            title="X",
            side="top",  # Move X-axis to the top
            range=[x_min, x_max]
        ),
        yaxis=dict(
            title="Y",
            autorange="reversed",  # Flip Y axis
            range=[y_max, y_min]
        ),
        coloraxis_colorbar=dict(
            orientation='h',
            y=-0.3,  # Move legend below chart
            x=0.5,
            xanchor='center',
            title="Timestamp"
        )
    )

    st.plotly_chart(fig_gaze, use_container_width=True)



    fixation_only = fixation_filtered[fixation_filtered["fixation_label"] == "fixation"]
    if not fixation_only.empty:
        st.markdown("<h4 style='margin-top: 1.5em;'>Average Fixation Centroids</h4>", unsafe_allow_html=True)

        # Choose color based on genre
        genre_color = "#71C8E2" if genre_selected == "music" else "#F14C2E"
 
        fig_avg = px.scatter(
            fixation_only,
            x="avg_x", y="avg_y",
            size="duration",
            color_discrete_sequence=["white"],  # all points white-filled
            labels={"avg_x": "Average X", "avg_y": "Average Y", "duration": "Duration (s)"},
            height=600
        )

        # Flip Y, keep layout clean, white borders
        fig_avg.update_traces(
            marker=dict(
                color=genre_color,              # genre-based fill color
                line=dict(width=1.5, color="white")  # white border
            )
        )

        fig_avg.update_layout(
            title_text="",
            xaxis=dict(title="Average X", side="top", range=[x_min, x_max]),
            yaxis=dict(title="Average Y", autorange="reversed", range=[y_max, y_min]),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )    

        # Add annotation
        fig_avg.add_annotation(
            text="Point size reflects fixation duration",
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(color="white", size=20),
            xanchor="center"
        )

st.plotly_chart(fig_avg, use_container_width=True)
