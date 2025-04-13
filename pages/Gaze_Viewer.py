import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gaze Viewer", layout="wide")
st.title("🎯 Eye Fixation Visualization")

# Load eye-tracking data
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?export=download&id=1-2S_SRfuh702J-8dsFGFekYSb142TG8y"
    df = pd.read_csv(url)
    df = df[df["missing"] == 0]
    df["t_sec"] = df["t"] / 1000
    df["t_sec"] = df["t_sec"].round(1)
    return df

df = load_data()

# Get videoNumber from session state
video_id = st.session_state.get("selected_video", None)

if video_id is None:
    st.warning("⚠️ Please select a video from the homepage.")
    st.page_link("app.py", label="⬅️ Go to Homepage")
    st.stop()

st.header(f"📽️ Gaze Data for Video {video_id}")
video_df = df[df["videoNumber"] == video_id]

# Time range slider
t_min = int(video_df["t_sec"].min())
t_max = int(video_df["t_sec"].max())

start_time, end_time = st.slider(
    "⏲️ Select Time Range (seconds)",
    min_value=t_min,
    max_value=t_max,
    value=(t_min, min(t_min + 5, t_max))
)

filtered_df = video_df[
    (video_df["t_sec"] >= start_time) &
    (video_df["t_sec"] <= end_time)
]

st.markdown(f"Showing **{len(filtered_df)}** fixations from **{start_time} to {end_time} seconds**")
st.dataframe(filtered_df.head())

if not filtered_df.empty:
    st.subheader("📍 Fixation Map")
    fig1 = px.scatter(filtered_df, x='x', y='y', size='pa', color='t_sec',
                      color_continuous_scale='Viridis', height=600)
    fig1.update_yaxes(autorange='reversed')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📈 Gaze Position Over Time")
    fig2 = px.line(filtered_df.sort_values("t_sec"), x="t_sec", y=["x", "y"],
                   labels={"value": "Gaze Position", "t_sec": "Time (s)"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🎬 Animated Fixation Playback")
    fig3 = px.scatter(filtered_df, x='x', y='y', size='pa', color='t_sec',
                      animation_frame='t_sec', color_continuous_scale='Viridis', height=600)
    fig3.update_yaxes(autorange='reversed')
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ No data found for this time range.")
