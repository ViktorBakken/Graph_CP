from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import networkx as nx

s=0
t=2
k=4
n=20
nodes=[i+1 for i in range(n)]
print(nodes)
edges = [  (1, 2, 28),  (2, 1, 28),  (1, 5, 29),  (5, 1, 29),  (1, 6, 10),  (6, 1, 10),  (1, 10, 25),  (10, 1, 25),  (1, 13, 17),  (13, 1, 17),  (1, 14, 19),  (14, 1, 19),  (1, 17, 15),  (17, 1, 15),  (1, 20, 16),  (20, 1, 16),  (2, 3, 12),  (3, 2, 12),  (2, 4, 15),  (4, 2, 15),  (2, 8, 27),  (8, 2, 27),  (2, 10, 18),  (10, 2, 18),  (2, 12, 25),  (12, 2, 25),  (2, 14, 11),  (14, 2, 11),  (2, 15, 26),  (15, 2, 26),  (2, 17, 2),  (17, 2, 2),  (3, 6, 1),  (6, 3, 1),  (3, 20, 5),  (20, 3, 5),  (4, 5, 14),  (5, 4, 14),  (4, 9, 3),  (9, 4, 3),  (4, 10, 8),  (10, 4, 8),  (4, 11, 17),  (11, 4, 17),  (4, 14, 30),  (14, 4, 30),  (4, 16, 9),  (16, 4, 9),  (4, 19, 29),  (19, 4, 29),  (5, 6, 20),  (6, 5, 20),  (5, 7, 16),  (7, 5, 16),  (5, 8, 10),  (8, 5, 10),  (5, 14, 17),  (14, 5, 17),  (5, 15, 12),  (15, 5, 12),  (5, 17, 7),  (17, 5, 7),  (5, 18, 27),  (18, 5, 27),  (6, 8, 15),  (8, 6, 15),  (6, 10, 5),  (10, 6, 5),  (6, 14, 4),  (14, 6, 4),  (6, 15, 18),  (15, 6, 18),  (6, 16, 16),  (16, 6, 16),  (6, 17, 21),  (17, 6, 21),  (7, 9, 2),  (9, 7, 2),  (7, 10, 26),  (10, 7, 26),  (7, 17, 29),  (17, 7, 29),  (8, 10, 2),  (10, 8, 2),  (8, 11, 9),  (11, 8, 9),  (8, 14, 26),  (14, 8, 26),  (8, 17, 24),  (17, 8, 24),  (9, 14, 23),  (14, 9, 23),  (10, 11, 3),  (11, 10, 3),  (10, 14, 10),  (14, 10, 10),  (10, 15, 7),  (15, 10, 7),  (10, 17, 9),  (17, 10, 9),  (10, 18, 12),  (18, 10, 12),  (11, 14, 24),  (14, 11, 24),  (12, 14, 1),  (14, 12, 1),  (14, 15, 13),  (15, 14, 13),  (14, 17, 3),  (17, 14, 3),  (15, 17, 23),  (17, 15, 23),  (16, 17, 12),  (17, 16, 12)]
tail, head, c = map(list, zip(*edges))
mini = min(c)
new_c=[e+abs(mini)+1 for e in c]

new_edges=list(zip(tail, head, new_c))
print(new_edges)

b= [0 for e in range(len(nodes))]
b[s]=1
b[t]=-1

# Load a solver
solver = Solver.lookup("coin-bc")

# Load the model
model = Model("Solver.mzn")

# Create an instance
instance = Instance(solver, model)

# Pass data from Python to MiniZinc
instance["K"] = k*2
instance["s"] = s+1
instance["n"] = len(nodes)
instance["m"] = len(edges)
instance["i"] = tail
instance["j"] = head
instance["c"] = new_c
instance["b"] = b

# Solve
result = instance.solve()

print(result)
removed = [x for x, m in zip(new_edges, result["x"]) if m]
remaining = [x for x, m in zip(new_edges, result["x"]) if not m]
# removed = [x for x, m in zip(edges, result["x"]) if m]
# remaining = [x for x, m in zip(edges, result["x"]) if not m]
print("Selected edges to remove:")
print(removed)


#Print first graph
G = nx.DiGraph()
colorStates = {"I": "yellow", "S": "green", "B":"blue"}

for node in nodes: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 
    
G.nodes[s+1]["state"]="I" 
G.nodes[t+1]["state"]="B"
G.add_weighted_edges_from(new_edges)
# G.add_weighted_edges_from(edges)

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



#Print updated graph
G = nx.Graph()
colorStates = {"I": "yellow", "S": "green", "B":"blue"}

for node in nodes: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 
    
G.nodes[s+1]["state"]="I" 
G.nodes[t+1]["state"]="B"
G.add_weighted_edges_from(remaining)

colors = [colorStates[G.nodes[n]["state"]] for n in G.nodes()]

# Layout
layout = nx.spring_layout(G)
nx.draw(G, layout, node_color=colors,with_labels=True)
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, layout, edge_labels=edge_labels)


label_map = {"I": "Infected", "S": "Susceptible", "B": "Goal"}

legend_handles = [
    Patch(facecolor=color, edgecolor="black", label=label_map[state])
    for state, color in colorStates.items()
]

plt.legend(handles=legend_handles, title="State")
plt.show()
