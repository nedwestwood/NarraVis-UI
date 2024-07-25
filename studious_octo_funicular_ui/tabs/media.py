from math import ceil
from pathlib import Path

import streamlit as st

from studious_octo_funicular_ui.constants import IMAGE_DATA_DIR, VIDEO_DATA_DIR


def build_media_gallery(media_type, media_ids=None):
    if media_type not in ["image", "video"]:
        return

    if media_type == "image":
        build_gallery("image", list(Path(IMAGE_DATA_DIR).glob("*.jpeg")))  # TODO: Change extension
    elif media_type == "video":
        if media_ids:
            build_gallery(
                "video",
                [(Path(VIDEO_DATA_DIR) / media_id).with_suffix(".mp4") for media_id in media_ids],
            )
        else:
            build_gallery("video", list(Path(VIDEO_DATA_DIR).glob("*.mp4")))


def build_gallery(media_type, media):
    page_grid = st.columns([0.9, 0.1])
    with page_grid[0]:
        row_size = st.select_slider(f"{media_type.capitalize()}s per page:", range(2, 11), value=5)
    with page_grid[1]:
        page = st.selectbox("Page", range(1, ceil(len(media) / row_size) + 1), key=media_type)

    media_batch = media[(page - 1) * row_size : page * row_size]

    media_grid = st.columns(row_size, vertical_alignment="center")
    for idx, medium in enumerate(media_batch):
        with media_grid[idx]:
            if media_type == "image":
                build_image(medium)
            elif media_type == "video":
                build_video(medium)


def build_video(video_path):
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
    st.video(video_bytes)
    st.markdown(f"**Video**: {video_path.stem}")


def build_image(image_path):
    st.image(str(image_path), caption=f"Image: {image_path.stem!s}")
