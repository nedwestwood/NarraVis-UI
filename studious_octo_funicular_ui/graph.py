from itertools import chain

import networkx as nx
import streamlit as st
from st_cytoscape import cytoscape

from studious_octo_funicular_ui.parser import (
    parse_edges_for_cytograph,
    parse_nodes_for_cytograph,
)
from studious_octo_funicular_ui.sidebar import apply_filters


def get_element(nodes, edges):
    return list(
        chain(
            parse_nodes_for_cytograph(nodes),
            parse_edges_for_cytograph(edges),
        )
    )


def get_stylesheet():
    node_styles = {
        "selector": "node",
        "style": {
            "font-size": "data(weight)",
            "label": "data(name)",
            # "text-valign": "center",
            "text-halign": "center",
            "background-color": "data(color)",
            "height": "data(weight)",
            "width": "data(weight)",
            "shape": "circle",
        },
    }
    edge_styles = {
        "selector": "edge",
        "css": {
            # TODO: Add edge label
            # "font-size": "data(weight)",
            # "color": "white",
            # "label": "data(name)",
            "height": "data(weight)",
            "width": "data(weight)",
            "line-color": "data(color)",
            # "line-fill": "linear-gradient",
            # "line-gradient-stop-colors": "function(edge) { return `edge.data.get(source_color) edge.data.get(target_color)`",
            # "line-gradient-stop-positions": "60% 80%",
            "opacity": 0.5,
            "curve-style": "unbundled-bezier",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "data(color)",
            "arrow-scale": 0.5,
        },
    }
    return [node_styles, edge_styles]


def get_layout():
    # layout["alignmentConstraint"] = {"horizontal": [["X", "Y"]]}
    # layout["relativePlacementConstraint"] = [{"top": "Z", "bottom": "X"}]
    # layout["relativePlacementConstraint"] = [{"left": "X", "right": "Y"}]
    return {
        "name": "fcose",
        "quality": "proof",
        "animate": False,
        "animationDuration": 0,
        "fit": True,
        "padding": 5,
        "nodeRepulsion": 100,
        "gravity": 1,
        "avoidOverlap": True,
        "nodeDimensionsIncludeLabels": True,
        "uniformNodeDimensions": True,
        "numIter": 100,
    }


def build_graph(entity_node_label, events_node_labels, lens, height, graph):
    subgraph = apply_filters(entity_node_label, events_node_labels, lens, graph)
    if nx.is_empty(subgraph):
        st.info("Empty Graph - Nothing to see here!")
        return [], []

    subgraph_nodes = subgraph.nodes(data=True)
    subgraph_edges = subgraph.edges(data=True)

    with st.container(height=height):
        selected = cytoscape(
            elements=get_element(subgraph_nodes, subgraph_edges),
            stylesheet=get_stylesheet(),
            layout=get_layout(),
            width="100%",
            height=f"{height - 35}px",
            key="graph",
        )
    return selected["nodes"], subgraph_nodes
