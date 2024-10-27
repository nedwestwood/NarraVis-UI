import pandas as pd
import streamlit as st


def build_detected_objects(associated_videos):
    df = pd.read_csv(st.session_state.case / "scenes" / "detected_objects.csv")
    if "video_id" not in df.columns:
        st.write("Missing 'detected_objects.csv'")
        return

    st.dataframe(df[df.video_id.isin(associated_videos)].reset_index(drop=True))
