import json
from itertools import chain
from pathlib import Path

import networkx as nx
import streamlit as st

from studious_octo_funicular_ui.constants import GRAPH_DATA_DIR


# Sidebar
def build_sidebar():
    # TODO: Add an apply button?
    st.sidebar.title("Narrative")
    only_frames = st.sidebar.toggle("Only Frames", value=True)
    st.sidebar.divider()

    ## Data
    options = Path(GRAPH_DATA_DIR).glob("*.json")
    with st.sidebar.container():
        graph_data_file = st.sidebar.selectbox(
            "Graph Data",
            options=sorted(options, key=lambda file: Path(file).lstat().st_mtime, reverse=True),
            format_func=lambda file: file.stem,
        )
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
    ### Clusters
    with st.sidebar.container():
        clusters = st.sidebar.multiselect(
            "Cluster(s)",
            sorted({details["cluster"] for _, details in nodes}),
        )
    ###

    filtered_nodes = [node for node in nodes if node[1]["cluster"] in clusters] if clusters else nodes

    ### Entities
    # TODO: Add node type in graph on the other repo
    with st.sidebar.container():
        entity_node_labels = st.sidebar.multiselect(
            "Entities",
            sorted((node for node, details in filtered_nodes if "character" in details)),
        )

        ### Events
        events_node_labels = st.sidebar.multiselect(
            "Events",
            sorted((node for node, details in filtered_nodes if "event_type" in details)),
        )
    st.sidebar.divider()

    ## Lens
    with st.sidebar.container():
        # lens = st.sidebar.selectbox(
        #     "Select the Lens Type:",
        #     options=[
        #         "All",
        #         "Define Problem",
        #         "Causal Diagnosis",
        #         "Treatment Recommendation",
        #         "Moral Evaluation",
        #     ],
        # )
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
        (graph.subgraph(nodes=(node_label for node_label, _ in filtered_nodes)) if clusters else graph),
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


# TODO: Filter by cluster/topic
