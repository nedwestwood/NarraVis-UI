import pandas as pd
import streamlit as st


def build_summary(selected_nodes, subgraph_nodes):
    with st.container():
        # st.write(
        #     "**Selected node(s)**:",
        #     {node: subgraph_nodes[node] for node in selected_nodes},
        # )
        # TODO: Separate tables for events and entities

        entities = []
        events = []

        display_nodes = (
            (subgraph_nodes[node] for node in selected_nodes)
            if selected_nodes
            else [node_details for _, node_details in subgraph_nodes]
        )

        for node in display_nodes:
            if "event_type" in node:
                events.append(node)
            elif "character" in node:
                entities.append(node)

        if entities:
            st.text("Entities")
            st.dataframe(pd.DataFrame.from_records(entities).drop(["id", "value", "name"], axis=1))

        if events:
            st.text("Events")
            st.dataframe(pd.DataFrame.from_records(events).drop(["id", "value", "name"], axis=1))
