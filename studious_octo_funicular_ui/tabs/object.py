import io

import boto3
import pandas as pd
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, S3_BUCKET, USE_S3

s3 = boto3.client("s3")


def load_object_data(run_id):
    if USE_S3:
        key = f"data/output/{run_id}/scenes/detected_objects.csv"
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(response["Body"].read()))
    else:
        path = OUTPUT_DATA_DIR / run_id / "scenes" / "detected_objects.csv"
        return pd.read_csv(path)


def build_detected_objects(associated_videos):
    run_id = st.session_state.case.name if not USE_S3 else str(st.session_state.case)
    df = load_object_data(run_id)

    if "video_id" not in df.columns:
        st.write("Missing 'detected_objects.csv'")
        return

    st.dataframe(df[df.video_id.isin(associated_videos)].reset_index(drop=True))
