import io
from pathlib import Path

import boto3
import pandas as pd
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, S3_BUCKET, USE_S3
from studious_octo_funicular_ui.tabs.media import build_gallery

s3 = boto3.client("s3")


def load_face_details(run_id):
    if USE_S3:
        key = f"data/output/{run_id}/clustered_faces/face_details.csv"
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(response["Body"].read()))
    else:
        path = OUTPUT_DATA_DIR / run_id / "clustered_faces" / "face_details.csv"
        return pd.read_csv(path)


def build_detected_faces(associated_videos):
    run_id = st.session_state.case.name if not USE_S3 else str(st.session_state.case)
    df = load_face_details(run_id)

    df["video_id"] = df["image_path"].map(lambda path: str(Path(path).parent.name))
    clusters = df[df.video_id.isin(associated_videos)].cluster_label.unique()

    if USE_S3:
        from utils.s3 import build_s3_url

        image_urls = [
            build_s3_url(f"data/output/{run_id}/clustered_faces/{cluster}/collage.png") for cluster in clusters
        ]
        build_gallery(
            "image",
            image_urls,
            "face",
            lambda url: f"Cluster: {Path(url).parent.name}",
        )
    else:
        image_paths = [st.session_state.case / "clustered_faces" / str(cluster) / "collage.png" for cluster in clusters]
        build_gallery(
            "image",
            image_paths,
            "face",
            lambda path: f"Cluster: {path.parent.name}",
        )
