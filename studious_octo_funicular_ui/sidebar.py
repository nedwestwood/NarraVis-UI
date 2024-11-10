import json
from datetime import datetime
from itertools import chain
from pathlib import Path

import networkx as nx
import streamlit as st

from studious_octo_funicular_ui.constants import OUTPUT_DATA_DIR, VIDEO_DATA_DIR


def get_cluster_relevant_nodes(nodes, louvain_clusters=None, multimodal_clusters=None):
    if louvain_clusters:
        return [node for node in nodes if node[1]["louvain_cluster"] in louvain_clusters]
    elif multimodal_clusters := set(multimodal_clusters):
        return [node for node in nodes if set(node[1]["multimodal_cluster"]) & multimodal_clusters]
    return nodes


def get_date_relevant_nodes(edges, shortlist_videos):
    if not shortlist_videos:
        return edges

    return [edge for edge in edges if set(edge[2]["relation_explanation"].keys()) & set(shortlist_videos)]


def get_subgraph_with_cluster_adjustment(graph, filtered_nodes, louvain_clusters=None, multimodal_clusters=None):
    if not louvain_clusters and not multimodal_clusters:
        return graph

    graph = graph.subgraph(nodes=(node_label for node_label, _ in filtered_nodes)).copy()

    if multimodal_clusters:
        for node in graph.nodes:
            graph.nodes[node]["multimodal_cluster"] = {
                vid_id: count
                for vid_id, count in graph.nodes[node]["multimodal_cluster"].items()
                if vid_id in multimodal_clusters
            }
            graph.nodes[node]["weight"] = sum(graph.nodes[node]["multimodal_cluster"].values())

        for edge in graph.edges:
            graph.edges[edge]["multimodal_cluster"] = {
                vid_id: count
                for vid_id, count in graph.edges[edge]["multimodal_cluster"].items()
                if vid_id in multimodal_clusters
            }
            graph.edges[edge]["weight"] = sum(graph.edges[edge]["multimodal_cluster"].values())
    return graph


def get_subgraph_with_time_adjustment(graph, shortlist_videos, filtered_edges):
    if not shortlist_videos:
        return graph

    sub_graph = graph.edge_subgraph(edges=((src, dest) for src, dest, _ in filtered_edges)).copy()

    # Remove isolates
    sub_graph.remove_nodes_from(list(nx.isolates(sub_graph)))

    for node in sub_graph.nodes:
        if "character_description" in sub_graph.nodes[node]:
            sub_graph.nodes[node]["character_description"] = {
                vid_id: exp
                for vid_id, exp in sub_graph.nodes[node]["character_description"].items()
                if vid_id in shortlist_videos
            }
            sub_graph.nodes[node]["weight"] = len(sub_graph.nodes[node]["character_description"])
            continue

        sub_graph.nodes[node]["weight"] = sub_graph.degree(node)

    for edge in sub_graph.edges:
        sub_graph.edges[edge]["relation_explanation"] = {
            vid_id: exp
            for vid_id, exp in sub_graph.edges[edge]["relation_explanation"].items()
            if vid_id in shortlist_videos
        }
        sub_graph.edges[edge]["weight"] = len(sub_graph.edges[edge]["relation_explanation"])

    return sub_graph


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
        metadata = [{"id": video["id"], "date": datetime.fromtimestamp(video["createTime"])} for video in json.load(f)]

    if len(metadata) > 1:
        metadata.sort(key=lambda x: x["date"], reverse=False)
        min_date = metadata[0]["date"]
        max_date = metadata[-1]["date"]

        with st.sidebar.container():
            date = st.sidebar.slider(
                label="Post Date",
                min_value=min_date,
                max_value=max_date,
                value=max_date,
            )
            shortlist_videos = [video["id"] for video in metadata if video["date"] <= date]
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
                sorted({details["louvain_cluster"] for _, details in nodes}),
                key="louvain_cluster",
            )
    elif cluster_type_selection == 1:
        st.session_state.louvain_cluster = []

        with st.sidebar.container():
            st.sidebar.multiselect(
                "Multimodal Cluster(s)",
                sorted({cluster for _, details in nodes for cluster in details["multimodal_cluster"]}),
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


def filter_graph_lens(lens, graph):
    if lens == "All":
        return graph
    return nx.subgraph_view(
        graph,
        filter_node=lambda node: graph.nodes[node].get(f'ff_{"_".join(lens.split(" ")).lower()}', False),
    )


def filter_graph_nodes(entity_node_labels, event_node_labels, graph):
    if not entity_node_labels and not event_node_labels:
        return graph

    try:
        all_nodes = (
            neighbor for node in chain(entity_node_labels, event_node_labels) for neighbor in graph.neighbors(node)
        )  # TODO: Maybe on top of neighbours, can go by associated videos as well, so can see entities and events that appeared in the same video as well
    except nx.NetworkXError:
        return nx.Graph()  # node (represented by label) not in graph

    return graph.subgraph(nodes=chain(all_nodes, entity_node_labels, event_node_labels))


def apply_filters(entity_node_labels, event_node_labels, lens, graph):
    return filter_graph_lens(lens, filter_graph_nodes(entity_node_labels, event_node_labels, graph))
