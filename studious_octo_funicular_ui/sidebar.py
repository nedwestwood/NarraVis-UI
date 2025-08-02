import json
from datetime import datetime
from pathlib import Path

import boto3
import networkx as nx
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, S3_BUCKET, USE_S3, VIDEO_DATA_DIR
from studious_octo_funicular_ui.subgraph import (
    get_cluster_relevant_nodes,
    get_date_relevant_nodes,
    get_subgraph_with_cluster_adjustment,
    get_subgraph_with_time_adjustment,
)
from utils.s3 import list_s3_files

s3 = boto3.client("s3")


def load_combined_graph(run_id):
    if USE_S3:
        key = f"data/output/{run_id}/combined_data.json"
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return nx.cytoscape_graph(json.load(response["Body"]))
    else:
        with open(Path(OUTPUT_DATA_DIR) / run_id / "combined_data.json") as f:
            return nx.cytoscape_graph(json.load(f))


def load_video_metadata(run_id):
    if USE_S3:
        key = f"data/videos/{run_id}/metadata.json"
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return json.load(response["Body"])
    else:
        with open(Path(VIDEO_DATA_DIR) / run_id / "metadata.json") as f:
            return json.load(f)


def build_sidebar():
    st.sidebar.title("Narrative")
    only_frames = st.sidebar.toggle("Only Frames", value=True)
    st.sidebar.divider()

    if USE_S3:
        json_keys = list_s3_files(S3_BUCKET, "data/output/", suffix="combined_data.json")
        options = [key.split("/")[2] for key in json_keys]
    else:
        options = [p.parent.name for p in Path(OUTPUT_DATA_DIR).glob("*/combined_data.json")]

    with st.sidebar.container():
        graph_data_file = st.sidebar.selectbox(
            "Graph Data",
            options=sorted(options),
            format_func=lambda run_id: run_id,
        )

    if not graph_data_file:
        return nx.Graph(), [], [], "All"

    st.session_state.case = Path(graph_data_file)

    try:
        graph = load_combined_graph(graph_data_file)
        if only_frames:
            graph = graph.subgraph(
                nodes=[
                    node
                    for node, details in graph.nodes(data=True)
                    if any((
                        details.get("ff_define_problem"),
                        details.get("ff_causal_diagnosis"),
                        details.get("ff_treatment_recommendation"),
                        details.get("ff_moral_evaluation"),
                    ))
                ]
            )
    except json.JSONDecodeError:
        return

    st.sidebar.divider()

    nodes = graph.nodes(data=True)
    if nx.is_empty(graph):
        return

    metadata = load_video_metadata(graph_data_file)
    st.session_state.metadata = [
        {
            "video_id": video["video_id"],
            "date": datetime.fromtimestamp(video["createTime"]),
            "author": f"{video['author'].get('nickname', '')} ({video['author'].get('video_id', '')})",
        }
        for video in metadata
    ]

    if len(st.session_state.metadata) > 1:
        st.session_state.metadata.sort(key=lambda x: x["date"], reverse=False)
        min_date = st.session_state.metadata[0]["date"]
        max_date = st.session_state.metadata[-1]["date"]

        with st.sidebar.container():
            date = st.sidebar.slider(
                label="Post Date",
                min_value=min_date,
                max_value=max_date,
                value=max_date,
            )
            shortlist_videos = [video["video_id"] for video in st.session_state.metadata if video["date"] <= date]
    else:
        shortlist_videos = []

    st.sidebar.divider()

    option_map = {0: "Louvain", 1: "Multimodal"}

    with st.sidebar.container():
        cluster_type_selection = st.sidebar.segmented_control(
            "Clustering Mode",
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single",
        )

    if cluster_type_selection == 0:
        st.session_state.multimodal_cluster = []

        with st.sidebar.container():
            st.sidebar.multiselect(
                "Louvain Cluster(s)",
                sorted({details["louvain_cluster"] for _, details in nodes}, key=int),
                key="louvain_cluster",
            )
    elif cluster_type_selection == 1:
        st.session_state.louvain_cluster = []

        with st.sidebar.container():
            st.sidebar.multiselect(
                "Multimodal Cluster(s)",
                sorted(
                    {cluster for _, details in nodes for cluster in details["multimodal_cluster"]},
                    key=int,
                ),
                key="multimodal_cluster",
            )
    elif cluster_type_selection is None:
        st.session_state.louvain_cluster = []
        st.session_state.multimodal_cluster = []

    st.sidebar.divider()

    filtered_nodes = get_cluster_relevant_nodes(
        nodes,
        louvain_clusters=st.session_state.louvain_cluster,
        multimodal_clusters=st.session_state.multimodal_cluster,
    )
    subgraph_with_filtered_nodes = get_subgraph_with_cluster_adjustment(
        graph,
        filtered_nodes,
        louvain_clusters=st.session_state.louvain_cluster,
        multimodal_clusters=st.session_state.multimodal_cluster,
    )

    filtered_edges = get_date_relevant_nodes(subgraph_with_filtered_nodes.edges(data=True), shortlist_videos)
    subgraph = get_subgraph_with_time_adjustment(subgraph_with_filtered_nodes, shortlist_videos, filtered_edges)

    with st.sidebar.container():
        entity_node_labels = st.sidebar.multiselect(
            "Entities",
            sorted((node for node, details in subgraph.nodes(data=True) if "character" in details)),
        )

        events_node_labels = st.sidebar.multiselect(
            "Events",
            sorted((node for node, details in subgraph.nodes(data=True) if "event_type" in details)),
        )

    st.sidebar.divider()

    with st.sidebar.container():
        lens = st.radio(
            "Framing Function",
            options=[
                "All",
                "Define Problem",
                "Causal Diagnosis",
                "Treatment Recommendation",
                "Moral Evaluation",
            ],
        )

    return (
        subgraph,
        entity_node_labels,
        events_node_labels,
        lens,
    )
