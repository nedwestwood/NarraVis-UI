import networkx as nx


def get_cluster_relevant_nodes(nodes, louvain_clusters=None, multimodal_clusters=None):
    if louvain_clusters:
        return [node for node in nodes if node[1]["louvain_cluster"] in louvain_clusters]
    elif multimodal_clusters := set(multimodal_clusters):
        return [node for node in nodes if set(node[1]["multimodal_cluster"]) & multimodal_clusters]
    return nodes


def get_date_relevant_nodes(edges, shortlist_videos):
    if not shortlist_videos:
        return edges

    return [edge for edge in edges if set(edge[2]["relation_explanation"].keys()) & set(shortlist_videos)]


def get_subgraph_with_cluster_adjustment(graph, filtered_nodes, louvain_clusters=None, multimodal_clusters=None):
    if not louvain_clusters and not multimodal_clusters:
        return graph

    graph = graph.subgraph(nodes=(node_label for node_label, _ in filtered_nodes)).copy()

    if multimodal_clusters:
        for node in graph.nodes:
            graph.nodes[node]["multimodal_cluster"] = {
                vid_id: count
                for vid_id, count in graph.nodes[node]["multimodal_cluster"].items()
                if vid_id in multimodal_clusters
            }
            graph.nodes[node]["weight"] = sum(graph.nodes[node]["multimodal_cluster"].values())

        for edge in graph.edges:
            graph.edges[edge]["multimodal_cluster"] = {
                vid_id: count
                for vid_id, count in graph.edges[edge]["multimodal_cluster"].items()
                if vid_id in multimodal_clusters
            }
            graph.edges[edge]["weight"] = sum(graph.edges[edge]["multimodal_cluster"].values())
    return graph


def get_subgraph_with_time_adjustment(graph, shortlist_videos, filtered_edges):
    if not shortlist_videos:
        return graph

    sub_graph = graph.edge_subgraph(edges=((src, dest) for src, dest, _ in filtered_edges)).copy()

    # Remove isolates
    sub_graph.remove_nodes_from(list(nx.isolates(sub_graph)))

    for node in sub_graph.nodes:
        if "character_description" in sub_graph.nodes[node]:
            sub_graph.nodes[node]["character_description"] = {
                vid_id: exp
                for vid_id, exp in sub_graph.nodes[node]["character_description"].items()
                if vid_id in shortlist_videos
            }
            sub_graph.nodes[node]["weight"] = len(sub_graph.nodes[node]["character_description"])
            continue

        sub_graph.nodes[node]["weight"] = sub_graph.degree(node)

    for edge in sub_graph.edges:
        sub_graph.edges[edge]["relation_explanation"] = {
            vid_id: exp
            for vid_id, exp in sub_graph.edges[edge]["relation_explanation"].items()
            if vid_id in shortlist_videos
        }
        sub_graph.edges[edge]["weight"] = len(sub_graph.edges[edge]["relation_explanation"])

    return sub_graph
