import streamlit as st


def build_summary(selected_nodes, subgraph_nodes):
    if not selected_nodes:
        st.info("Select node(s) of interest from the graph above")
        return

    with st.container():
        st.write(
            "**Selected node(s)**:",
            {node: subgraph_nodes[node] for node in selected_nodes},
        )
