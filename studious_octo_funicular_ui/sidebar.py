from itertools import chain

import networkx as nx
import streamlit as st


# Sidebar
def build_sidebar(nodes):
    # TODO: Add an apply button?
    st.sidebar.header("Choose your Filter/Lens")

    ## Filters
    ### Entities
    # TODO: Add node type in graph on the other repo
    entity_node_labels = st.sidebar.multiselect(
        "Entities of Interest",
        sorted((node for node, details in nodes if "character" in details)),
    )

    ### Events
    events_node_labels = st.sidebar.multiselect(
        "Events of Interest",
        sorted((node for node, details in nodes if "event_type" in details)),
    )

    ## Lens
    lens = st.sidebar.selectbox(
        "Select the Lens Type:",
        options=[
            "All",
            "Define Problem",
            "Causal Diagnosis",
            "Treatment Recommendation",
            "Moral Evaluation",
        ],
    )
    return entity_node_labels, events_node_labels, lens


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
        )
    except nx.NetworkXError:
        return nx.Graph()  # node (represented by label) not in graph

    return graph.subgraph(nodes=chain(all_nodes, entity_node_labels, event_node_labels))


def apply_filters(entity_node_labels, event_node_labels, lens, graph):
    return filter_graph_lens(lens, filter_graph_nodes(entity_node_labels, event_node_labels, graph))


# TODO: Filter by cluster/topic
