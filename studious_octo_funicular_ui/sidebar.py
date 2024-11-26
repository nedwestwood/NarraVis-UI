import json
from datetime import datetime
from pathlib import Path

import networkx as nx
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, VIDEO_DATA_DIR
from studious_octo_funicular_ui.subgraph import (
    get_cluster_relevant_nodes,
    get_date_relevant_nodes,
    get_subgraph_with_cluster_adjustment,
    get_subgraph_with_time_adjustment,
)


# Sidebar
def build_sidebar():
    # TODO: Add an apply button?
    st.sidebar.title("Narrative")
    only_frames = st.sidebar.toggle("Only Frames", value=True)
    st.sidebar.divider()

    ## Data
    options = Path(OUTPUT_DATA_DIR).glob("*/combined_data.json")
    with st.sidebar.container():
        graph_data_file = st.sidebar.selectbox(
            "Graph Data",
            options=sorted(options, key=lambda file: Path(file).lstat().st_mtime, reverse=True),
            format_func=lambda file: file.parent.name,
        )
    st.session_state.case = graph_data_file.parent

    if not graph_data_file:
        return nx.Graph(), [], [], "All"

    try:
        with open(graph_data_file) as f:
            graph = nx.cytoscape_graph(json.load(f))

            if only_frames:
                graph = graph.subgraph(
                    nodes=[
                        node
                        for node, details in graph.nodes(data=True)
                        if any((
                            details["ff_define_problem"],
                            details["ff_causal_diagnosis"],
                            details["ff_treatment_recommendation"],
                            details["ff_moral_evaluation"],
                        ))
                    ]
                )
    except json.JSONDecodeError:
        return

    st.sidebar.divider()

    nodes = graph.nodes(data=True)
    if nx.is_empty(graph):
        return

    ## Filters
    ### Date
    with open(VIDEO_DATA_DIR / st.session_state.case.name / "metadata.json") as f:
        st.session_state.metadata = [
            {
                "id": video["id"],
                "date": datetime.fromtimestamp(video["createTime"]),
                "author": f"{video['author'].get('nickname', '')} ({video['author'].get('id', '')})",
            }
            for video in json.load(f)
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
            shortlist_videos = [video["id"] for video in st.session_state.metadata if video["date"] <= date]
    else:
        shortlist_videos = []

    st.sidebar.divider()

    ### Clusters
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

    #### Apply cluster and date filters
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

    ### Entities
    with st.sidebar.container():
        entity_node_labels = st.sidebar.multiselect(
            "Entities",
            sorted((node for node, details in subgraph.nodes(data=True) if "character" in details)),
        )

        ### Events
        events_node_labels = st.sidebar.multiselect(
            "Events",
            sorted((node for node, details in subgraph.nodes(data=True) if "event_type" in details)),
        )

    st.sidebar.divider()

    ## TODO: Link text topics

    ## Lens
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
