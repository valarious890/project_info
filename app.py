import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Eye Fixation Viewer", layout="wide")
st.title("🎯 Eye Fixation Visualization")

# Load CSV from Google Drive
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?export=download&id=1-2S_SRfuh702J-8dsFGFekYSb142TG8y"
    df = pd.read_csv(url)
    df = df[df['missing'] == 0]
    df['t_sec'] = df['t'] / 1000  # Convert ms to seconds
    df['t_sec'] = df['t_sec'].round(1)  # Round to 0.1s for animation
    return df

df = load_data()

# ========== Sidebar Filters ==========
st.sidebar.header("Filters")

video_ids = df['videoNumber'].unique()
selected_video = st.sidebar.selectbox("🎞️ Select Video Number", sorted(video_ids))

video_df = df[df['videoNumber'] == selected_video]

# Show basic video info
st.write(f"📊 Total fixations for video {selected_video}: {len(video_df)}")
st.write(f"⏱️ Time range: {video_df['t_sec'].min()}s to {video_df['t_sec'].max()}s")

# Dynamically adjust slider range to available time
t_min = int(video_df['t_sec'].min())
t_max = int(video_df['t_sec'].max())

start_time, end_time = st.slider(
    "Select Time Range (seconds)",
    min_value=t_min,
    max_value=t_max,
    value=(t_min, min(t_min + 5, t_max))
)

filtered_df = video_df[
    (video_df['t_sec'] >= start_time) &
    (video_df['t_sec'] <= end_time)
]

st.markdown(f"Showing **{len(filtered_df)}** fixations from **{start_time} to {end_time} seconds**")

# Show first few records (for debugging)
st.dataframe(filtered_df.head())

# ========== Fixation Map ==========
if not filtered_df.empty:
    st.subheader("📍 Fixation Map")
    fig1 = px.scatter(
        filtered_df,
        x='x',
        y='y',
        size='pa',
        color='t_sec',
        color_continuous_scale='Viridis',
        title=f'Fixations for Video {selected_video}',
        labels={'t_sec': 'Time (s)', 'pa': 'Pupil Area'},
        height=600
    )
    fig1.update_yaxes(autorange='reversed')
    fig1.update_layout(xaxis_title='X Position', yaxis_title='Y Position')
    st.plotly_chart(fig1, use_container_width=True)

    # ========== Gaze Line Plot ==========
    st.subheader("📈 Gaze Position Over Time")
    fig2 = px.line(
        filtered_df.sort_values("t_sec"),
        x="t_sec",
        y=["x", "y"],
        labels={"value": "Gaze Position", "t_sec": "Time (s)", "variable": "Axis"},
        title="Gaze Movement Over Time"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ========== Animated Fixation Plot ==========
    st.subheader("🎬 Animated Fixation Playback")
    fig3 = px.scatter(
        filtered_df,
        x='x',
        y='y',
        size='pa',
        color='t_sec',
        animation_frame='t_sec',
        color_continuous_scale='Viridis',
        title=f"Animated Fixation (Video {selected_video})",
        height=600
    )
    fig3.update_yaxes(autorange='reversed')
    fig3.update_layout(xaxis_title='X Position', yaxis_title='Y Position')
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("⚠️ No fixations found for this video and time range. Try adjusting filters.")


