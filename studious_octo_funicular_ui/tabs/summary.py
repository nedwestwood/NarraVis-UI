import pandas as pd
import streamlit as st


def build_summary(selected_nodes, subgraph_nodes):
    with st.container():
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
            with st.expander("Entities"):
                entities_df = (
                    pd.DataFrame.from_records(entities)
                    .drop(["id", "value", "name"], axis=1)
                    .sort_values("weight", ascending=False)
                    .reset_index(drop=True)
                )

                st.dataframe(
                    entities_df[
                        entities_df.columns.difference(["louvain_cluster", "multimodal_cluster", "topic"]).append(
                            pd.Index(["louvain_cluster", "multimodal_cluster", "topic"])
                        )
                    ]
                )

        if events:
            with st.expander("Events"):
                events_df = (
                    pd.DataFrame.from_records(events)
                    .drop(["id", "value", "name"], axis=1)
                    .sort_values("weight", ascending=False)
                    .reset_index(drop=True)
                )

                st.dataframe(
                    events_df[
                        events_df.columns.difference(["louvain_cluster", "multimodal_cluster", "topic"]).append(
                            pd.Index(["louvain_cluster", "multimodal_cluster", "topic"])
                        )
                    ]
                )
