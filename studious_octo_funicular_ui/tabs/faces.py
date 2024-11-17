from pathlib import Path

import pandas as pd
import streamlit as st

from studious_octo_funicular_ui.tabs.media import build_gallery


def build_detected_faces(associated_videos):
    df = pd.read_csv(st.session_state.case / "clustered_faces" / "face_details.csv")
    df["video_id"] = df["image_path"].map(lambda path: str(Path(path).parent.name))
    clusters = df[df.video_id.isin(associated_videos)].cluster_label.unique()

    build_gallery(
        "image",
        [st.session_state.case / "clustered_faces" / str(cluster) / "collage.png" for cluster in clusters],
        "face",
        lambda path: f"Cluster: {path.parent.name}",
    )
