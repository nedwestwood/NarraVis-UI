import streamlit as st

from studious_octo_funicular_ui.tabs.media import build_media_gallery
from studious_octo_funicular_ui.tabs.summary import build_summary


def build_graph_details_tabs(selected_nodes, subgraph_nodes):
    tab1, tab2, tab3 = st.tabs(["Summary/Details", "Images", "Videos"])
    associated_videos = get_associated_videos(selected_nodes, subgraph_nodes)

    with tab1:
        build_summary(selected_nodes, subgraph_nodes)

    with tab2:
        build_media_gallery("image", associated_videos)

    with tab3:
        build_media_gallery("video", associated_videos)

    # TODO: Filter images and videos


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
