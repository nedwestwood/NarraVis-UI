from pathlib import Path

import pandas as pd
import streamlit as st

from studious_octo_funicular_ui.tabs.media import build_gallery


def build_detected_topics(associated_videos):
    df = pd.read_csv(st.session_state.case / "scene_topics" / "image_topics.csv")
    df.Topic = df.Topic.astype(str)
    df["video_id"] = df["Image Path"].map(lambda path: str(Path(path).parent.name))
    clusters = df[df.video_id.isin(associated_videos)].drop_duplicates(subset=["Topic"])

    build_gallery(
        "image",
        [st.session_state.case / "scene_topics" / f"{cluster!s}.png" for cluster in clusters.Topic],
        "Topic",
        lambda path: f"Topic: {clusters[clusters['Topic'] == str(path.stem)].iloc[0]['Representation']}",
    )
