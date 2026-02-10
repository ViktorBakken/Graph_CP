import networkx as nx
import matplotlib.pyplot as plt

# Data
nodes=[1,2,3,4,5,6,7,8]
edges = [  (1, 7, 30),  (7, 1, 30),  (1, 8, 30),  (8, 1, 30),  (2, 7, 30),  (7, 2, 30),  (2, 8, 30),  (8, 2, 30),  (3, 7, 30),  (7, 3, 30),  (3, 8, 30),  (8, 3, 30),  (4, 5, 30),  (5, 4, 30),  (4, 6, 22),  (6, 4, 22),  (4, 7, 30),  (7, 4, 30),  (4, 8, 30),  (8, 4, 30),  (5, 7, 30),  (7, 5, 30),  (5, 8, 30),  (8, 5, 30),  (6, 7, 30),  (7, 6, 30),  (6, 8, 30),  (8, 6, 30),  (7, 8, 30),  (8, 7, 30)]
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

