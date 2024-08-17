from studious_octo_funicular_ui.constants import PALETTE

edge_weight_scale = lambda edge_weight: edge_weight * 5  # Larger numbers -> Bigger nodes


def get_node_color(node_details):
    if "event" in node_details:
        return PALETTE["event"]
    return PALETTE[node_details.get("character", "default")]


def parse_nodes_for_cytograph(nodes):
    return (
        ({
            "data": {
                "id": node_label,
                "name": node_label,
                "weight": edge_weight_scale(details["weight"]),
                "node_type": "entity" if "character" in details else "event",
                "color": get_node_color(details),
                "cluster": details["cluster"],
                "group": "nodes",
            },
            "selectable": True,
        })
        for node_label, details in nodes
    )


def parse_edges_for_cytograph(edges):
    return (
        ({
            "data": {
                "id": f"{entity}➞{event}",
                "name": details["relation_type"],
                "weight": details["weight"],
                "source": (event if details["relation_type"] == "affected by" else entity),
                "target": (entity if details["relation_type"] == "affected by" else event),
                "color": (PALETTE["event"] if details["relation_type"] == "affected by" else get_node_color(details)),
                "group": "edges",
            },
            "selectable": False,
        })
        for entity, event, details in edges
    )
