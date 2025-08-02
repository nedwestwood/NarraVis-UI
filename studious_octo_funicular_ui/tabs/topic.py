import io
from pathlib import Path

import boto3
import pandas as pd
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, S3_BUCKET, USE_S3
from studious_octo_funicular_ui.tabs.media import build_gallery
from utils.s3 import build_s3_url

s3 = boto3.client("s3")


def load_topic_data(run_id):
    if USE_S3:
        key = f"data/output/{run_id}/scene_topics/image_topics.csv"
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(response["Body"].read()))
    else:
        path = OUTPUT_DATA_DIR / run_id / "scene_topics" / "image_topics.csv"
        return pd.read_csv(path)


def build_detected_topics(associated_videos):
    run_id = st.session_state.case.name if not USE_S3 else str(st.session_state.case)
    df = load_topic_data(run_id)

    df.Topic = df.Topic.astype(str)
    df["video_id"] = df["Image Path"].map(lambda path: str(Path(path).parent.name))
    clusters = df[df.video_id.isin(associated_videos)].drop_duplicates(subset=["Topic"])

    if USE_S3:
        image_urls = [build_s3_url(f"data/output/{run_id}/scene_topics/{cluster}.png") for cluster in clusters.Topic]
        build_gallery(
            "image",
            image_urls,
            "Topic",
            lambda url: f"Topic: {clusters[clusters['Topic'] == Path(url).stem].iloc[0]['Representation']}",
        )
    else:
        image_paths = [st.session_state.case / "scene_topics" / f"{cluster}.png" for cluster in clusters.Topic]
        build_gallery(
            "image",
            image_paths,
            "Topic",
            lambda path: f"Topic: {clusters[clusters['Topic'] == str(path.stem)].iloc[0]['Representation']}",
        )
