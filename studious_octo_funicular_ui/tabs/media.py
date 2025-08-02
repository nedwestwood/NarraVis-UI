from math import ceil
from pathlib import Path

import streamlit as st

from studious_octo_funicular_ui.constants import (
    S3_BASE_URL,
    S3_BUCKET,
    USE_S3,
    VIDEO_DATA_DIR,
)
from utils.s3 import build_s3_url, list_s3_files


def build_media_gallery(media_type, media_ids=None):
    if media_type not in ["image", "video"]:
        return

    case_name = st.session_state.case.name

    if media_type == "image":
        handle_image_gallery(case_name, media_ids)
    elif media_type == "video":
        handle_video_gallery(case_name, media_ids)


def handle_image_gallery(case_name, media_ids):
    if USE_S3:
        image_urls = []
        if media_ids:
            for media_id in media_ids:
                s3_prefix = f"data/output/{case_name}/scenes/{media_id.strip('.mp4')}/"
                jpg_keys = list_s3_files(S3_BUCKET, s3_prefix, suffix=".jpg")
                image_urls.extend([build_s3_url(k) for k in jpg_keys])
        else:
            s3_prefix = f"data/output/{case_name}/scenes/"
            jpg_keys = list_s3_files(S3_BUCKET, s3_prefix, suffix=".jpg")
            image_urls = [build_s3_url(k) for k in jpg_keys]
        build_gallery("image", image_urls, "image")
    else:
        image_path = st.session_state.case / "scenes"
        paths = (
            [img_path for media_id in media_ids for img_path in (image_path / media_id.strip(".mp4")).glob("*.jpg")]
            if media_ids
            else list(image_path.glob("*/*.jpg"))
        )
        build_gallery("image", paths, "image")


def handle_video_gallery(case_name, media_ids):
    if USE_S3:
        videos = [f"{media_id}.mp4" for media_id in media_ids] if media_ids else []
        build_gallery("video", videos, "video")
    else:
        video_path = Path(VIDEO_DATA_DIR) / case_name
        videos = (
            [(video_path / media_id).with_suffix(".mp4") for media_id in media_ids]
            if media_ids
            else list(video_path.glob("*.mp4"))
        )
        build_gallery("video", videos, "video")


def image_caption_formatter(image_path):
    return f"Image: {image_path.parent.stem!s}/{image_path.stem!s}"


def build_gallery(media_type, media, name, _image_caption_formatter=image_caption_formatter):
    page_grid = st.columns([0.9, 0.1])

    if len(media) == 0:
        st.write(f"No {media_type}s found.")
        return

    with page_grid[0]:
        row_size = st.select_slider(
            f"{media_type.capitalize()}s per page:",
            list(range(2, 11)),
            value=5,
            key=f"{name}_slider",
        )

    with page_grid[1]:
        page = st.selectbox(
            "Page",
            list(range(1, ceil(len(media) / row_size) + 1)),
            index=None,
            placeholder="View Page",
            key=f"{name}_box",
        )

    if page is None:
        return

    media_batch = media[(page - 1) * row_size : page * row_size]
    media_grid = st.columns(row_size, vertical_alignment="center")

    for idx, medium in enumerate(media_batch):
        with media_grid[idx]:
            if media_type == "image":
                build_image(medium, _image_caption_formatter)
            elif media_type == "video":
                build_video(medium)


def build_video(video_ref):
    case_name = st.session_state.case.name

    if USE_S3:
        video_id = Path(video_ref).stem
        s3_url = f"{S3_BASE_URL}/data/videos/{case_name}/{video_id}.mp4"
        st.video(s3_url)
    else:
        try:
            video_id = video_ref.stem
            with open(video_ref, "rb") as video_file:
                video_bytes = video_file.read()
            st.video(video_bytes)
        except FileNotFoundError:
            st.write(f"**Missing video**: {video_ref}")
            return

    st.markdown(f"**Video**: {video_id}")
    for video in st.session_state.metadata:
        if video["video_id"] == video_id:
            st.markdown(f"**Author**: {video['author']}")
            break


def build_image(image_ref, _formatter):
    if USE_S3:
        st.image(
            image_ref,
            caption=image_ref.split("/")[-2] + "/" + Path(image_ref).stem,
            use_container_width=True,
        )
    else:
        st.image(
            str(image_ref),
            caption=_formatter(image_ref),
            use_container_width=True,
        )
