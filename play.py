import networkx as nx
import matplotlib.pyplot as plt

# Data
nodes=[1,2,3,4,5,6,7]
edges = [(1, 2, 21), (2, 1, 21), (1, 3, 4), (3, 1, 4), (2, 3, 1), (3, 2, 1), (4, 5, 24), (5, 4, 24), (4, 6, 9), (6, 4, 9), (5, 6, 8), (6, 5, 8), (7, 8, 8), (8, 7, 8), (7, 9, 5), (9, 7, 5), (8, 9, 24), (9, 8, 24), (1, 6, 24), (6, 1, 24), (3, 4, 19), (4, 3, 19), (5, 7, 1), (7, 5, 1), (4, 7, 8), (7, 4, 8)]
#Print first graph
G = nx.DiGraph()
colorStates = {"I": "yellow", "S": "green", "B":"blue"}

for node in nodes: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 
    
G.nodes[1]["state"]="I" 
G.nodes[3]["state"]="B"
G.add_weighted_edges_from(edges)

colors = [colorStates[G.nodes[n]["state"]] for n in G.nodes()]

# Layout
layout = nx.spring_layout(G)
nx.draw(G, layout, node_color=colors,with_labels=True)
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, layout, edge_labels=edge_labels)

from matplotlib.patches import Patch

label_map = {"I": "Infected", "S": "Susceptible", "B": "Goal"}

legend_handles = [
    Patch(facecolor=color, edgecolor="black", label=label_map[state])
    for state, color in colorStates.items()
]

plt.legend(handles=legend_handles, title="State")
plt.show()

