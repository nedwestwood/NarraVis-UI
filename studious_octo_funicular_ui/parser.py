from studious_octo_funicular_ui.constants import PALETTE

edge_weight_scale = lambda edge_weight: edge_weight * 5  # Larger numbers -> Bigger nodes


def parse_nodes_for_cytograph(nodes):
    return (
        ({
            "data": {
                "id": node_label,
                "name": node_label,
                "weight": edge_weight_scale(details["weight"]),
                "node_type": "entity" if "character" in details else "event",
                "color": (PALETTE["entity"] if "character" in details else PALETTE["event"]),
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
                "source": entity,
                "target": event,
                "color": (
                    PALETTE["event"] if details["relation_type"] == "affected by" else PALETTE["entity"]
                ),  # "grey",
                "group": "edges",
            },
            "selectable": False,
        })
        for entity, event, details in edges
    )
