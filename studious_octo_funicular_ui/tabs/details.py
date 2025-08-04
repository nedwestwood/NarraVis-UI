import time

import streamlit as st

from studious_octo_funicular_ui.tabs.faces import build_detected_faces
from studious_octo_funicular_ui.tabs.media import build_media_gallery
from studious_octo_funicular_ui.tabs.object import build_detected_objects
from studious_octo_funicular_ui.tabs.summary import build_summary
from studious_octo_funicular_ui.tabs.topic import build_detected_topics


def log_perf(msg):
    if "perf_log" not in st.session_state:
        st.session_state.perf_log = []
    st.session_state.perf_log.append(msg)


def build_graph_details_tabs(selected_nodes, subgraph_nodes):
    total_start = time.time()
    log_perf(f"⏱ Starting detail tab build for {len(subgraph_nodes)} subgraph nodes")

    assoc_start = time.time()
    associated_videos = get_associated_videos(selected_nodes, subgraph_nodes)
    log_perf(f"🔗 Associated {len(associated_videos)} videos in {time.time() - assoc_start:.2f}s")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Summary/Details",
        "Faces",
        "Images",
        "Image Topics",
        "Objects",
        "Videos",
    ])

    with tab1:
        start = time.time()
        build_summary(selected_nodes, subgraph_nodes)
        log_perf(f"📄 Summary tab built in {time.time() - start:.2f}s")

    with tab2:
        start = time.time()
        build_detected_faces(associated_videos)
        log_perf(f"👤 Faces tab built in {time.time() - start:.2f}s")

    with tab3:
        start = time.time()
        build_media_gallery("image", associated_videos)
        log_perf(f"🖼️ Image gallery tab built in {time.time() - start:.2f}s")

    with tab4:
        start = time.time()
        build_detected_topics(associated_videos)
        log_perf(f"🧠 Topics tab built in {time.time() - start:.2f}s")

    with tab5:
        start = time.time()
        build_detected_objects(associated_videos)
        log_perf(f"📦 Objects tab built in {time.time() - start:.2f}s")

    with tab6:
        start = time.time()
        build_media_gallery("video", associated_videos)
        log_perf(f"🎞️ Video gallery tab built in {time.time() - start:.2f}s")

    log_perf(f"✅ Total detail tabs built in {time.time() - total_start:.2f}s")


def get_associated_videos(selected_nodes, graph):
    associated_videos = set()
    for node, details in graph:
        if selected_nodes and node not in selected_nodes:
            continue

        associated_videos |= details.get("character_description", {}).keys()
        associated_videos |= details.get("ff_define_problem_explanation", {}).keys()
        associated_videos |= details.get("ff_causal_diagnosis_explanation", {}).keys()
        associated_videos |= details.get("ff_treatment_recommendation_explanation", {}).keys()
        associated_videos |= details.get("ff_moral_evaluation_explanation", {}).keys()

    return associated_videos
