
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Eye Fixation Viewer", layout="wide")
st.title("🎯 Eye Fixation Visualization")

uploaded_file = st.file_uploader("Upload Eye-Tracking CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df[df['missing'] == 0]
    df['t_sec'] = df['t'] / 1000

    st.sidebar.header("Filters")
    video_ids = df['videoNumber'].unique()
    selected_video = st.sidebar.selectbox("Select Video Number", sorted(video_ids))
    video_df = df[df['videoNumber'] == selected_video]

    start_time, end_time = st.slider("Select Time Range (seconds)", min_value=0, max_value=30, value=(0, 5))
    filtered_df = video_df[(video_df['t_sec'] >= start_time) & (video_df['t_sec'] <= end_time)]

    st.markdown(f"Showing **{len(filtered_df)}** fixations from second {start_time} to {end_time}")

    fig = px.scatter(
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
    fig.update_yaxes(autorange='reversed')
    fig.update_layout(xaxis_title='X Position', yaxis_title='Y Position')

    st.plotly_chart(fig, use_container_width=True)
