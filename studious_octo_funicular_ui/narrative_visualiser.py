import streamlit as st

from studious_octo_funicular_ui.graph import build_graph
from studious_octo_funicular_ui.sidebar import build_sidebar
from studious_octo_funicular_ui.tabs.details import build_graph_details_tabs

HEIGHT = 600

st.set_page_config(
    page_title="Narrative 2000",
    page_icon=":pizza:",
    layout="wide",
    # initial_sidebar_state="expanded",
)


def main():
    ## Select Data
    sidebar = build_sidebar()
    if sidebar is None:
        return st.error("Graph is empty!")

    graph, entity_node_label, events_node_labels, lens = sidebar
    selected_nodes, subgraph_nodes = build_graph(entity_node_label, events_node_labels, lens, HEIGHT, graph)

    # TODO: All associated images
    # TODO: Add graph metrics
    if subgraph_nodes:
        build_graph_details_tabs(selected_nodes, subgraph_nodes)


if __name__ == "__main__":
    main()
