import json

import networkx as nx

with open(
    "/Users/andrewww/Desktop/studious-octo-funicular-ui/data/final_graph_data.json",
) as f:
    G = nx.cytoscape_graph(json.load(f))
