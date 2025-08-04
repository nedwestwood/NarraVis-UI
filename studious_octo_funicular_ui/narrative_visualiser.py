import time

import streamlit as st

from studious_octo_funicular_ui.graph import build_graph
from studious_octo_funicular_ui.sidebar import build_sidebar
from studious_octo_funicular_ui.tabs.details import build_graph_details_tabs

HEIGHT = 600

st.set_page_config(
    page_title="NarraVis",
    page_icon=":book:",
    layout="wide",
)


def main():
    full_start = time.time()  # total app load timer

    # Step 1: Build Sidebar
    sidebar_start = time.time()
    sidebar = build_sidebar()
    st.sidebar.write(f"⚙️ Sidebar built in {time.time() - sidebar_start:.2f}s")

    if sidebar is None:
        return st.error("Graph is empty!")

    graph, entity_node_label, events_node_labels, lens = sidebar

    # Step 2: Build Graph
    graph_start = time.time()
    selected_nodes, subgraph_nodes = build_graph(entity_node_label, events_node_labels, lens, HEIGHT, graph)
    st.sidebar.write(f"📊 Graph visualization built in {time.time() - graph_start:.2f}s")

    # Step 3: Show Tabs with Subgraph Details
    if subgraph_nodes:
        detail_start = time.time()
        build_graph_details_tabs(selected_nodes, subgraph_nodes)
        st.sidebar.write(f"🧾 Graph detail tabs rendered in {time.time() - detail_start:.2f}s")

    # Optional: Total load time
    st.sidebar.write(f"🚀 Total app load time: {time.time() - full_start:.2f}s")


if __name__ == "__main__":
    main()
