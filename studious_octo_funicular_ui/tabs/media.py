from math import ceil
from pathlib import Path

import streamlit as st

from studious_octo_funicular_ui.constants import VIDEO_DATA_DIR


def build_media_gallery(media_type, media_ids=None):
    if media_type not in ["image", "video"]:
        return

    if media_type == "image":
        image_path = st.session_state.case / "scenes"
        if media_ids:
            build_gallery(
                "image",
                [img_path for media_id in media_ids for img_path in image_path.glob(f"{media_id.strip('.mp4')}/*.jpg")],
                "image",
            )
        else:
            build_gallery("image", list(image_path.glob("*/*.jpg")), "image")
    elif media_type == "video":
        video_path = Path(VIDEO_DATA_DIR) / st.session_state.case.name
        if media_ids:
            build_gallery(
                "video",
                [(video_path / media_id).with_suffix(".mp4") for media_id in media_ids],
                "video",
            )
        else:
            build_gallery("video", list(video_path.glob("*.mp4")), "video")


def image_caption_formatter(image_path):
    return f"Image: {image_path.parent.stem!s}/{image_path.stem!s}"


def build_gallery(media_type, media, name, _image_caption_formatter=image_caption_formatter):
    page_grid = st.columns([0.9, 0.1])

    if len(media) == 0:
        st.write(f"No {media_type} found.")
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


def build_video(video_path):
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)

        video_id = video_path.stem
        st.markdown(f"**Video**: {video_id}")

        for video in st.session_state.metadata:
            if video["id"] == video_id:
                st.markdown(f"**Author**: {video['author']}")
                break
    except FileNotFoundError:
        st.write(f"**Missing video**: {video_path.stem}")


def build_image(image_path, _formatter):
    st.image(
        str(image_path),
        caption=_formatter(image_path),
        use_container_width=True,
    )
