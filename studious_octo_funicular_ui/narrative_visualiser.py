import streamlit as st

from studious_octo_funicular_ui.graph import build_graph
from studious_octo_funicular_ui.sample_graph_data import G
from studious_octo_funicular_ui.sidebar import build_sidebar

HEIGHT = 600

st.set_page_config(
    page_title="Narrative 2000",
    page_icon=":pizza:",
    layout="wide",
    # initial_sidebar_state="expanded",
)

st.title("Narrative 2000")

## Input Data
graph = G  # TODO: Replace with input graph file next time

entity_node_label, events_node_labels, lens = build_sidebar(graph.nodes(data=True))
selected_nodes, subgraph_nodes = build_graph(entity_node_label, events_node_labels, lens, HEIGHT, graph)

## Graph Details
if selected_nodes:
    with st.container():
        st.write(
            "**Selected nodes**:",
            {node: subgraph_nodes[node] for node in selected_nodes},
        )

# TODO: All associated videos
