from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import networkx as nx

S={1,2,8,7,27,26,22,16,14,18}
T={0,5,6,13,15,17,20,25,21}
k=2
n=29 
nodes=[i+1 for i in range(n)]
edges = [(1, 2, 21), (2, 1, 21), (1, 3, 4), (3, 1, 4), (1, 4, 1), (4, 1, 1), (1, 5, 24), (5, 1, 24), (1, 6, 9), (6, 1, 9), (1, 7, 8), (7, 1, 8), (1, 8, 8), (8, 1, 8), (1, 9, 5), (9, 1, 5), (1, 10, 24), (10, 1, 24), (2, 3, 4), (3, 2, 4), (2, 4, 22), (4, 2, 22), (2, 5, 24), (5, 2, 24), (2, 6, 29), (6, 2, 29), (2, 7, 18), (7, 2, 18), (2, 8, 3), (8, 2, 3), (2, 9, 19), (9, 2, 19), (2, 10, 14), (10, 2, 14), (3, 4, 2), (4, 3, 2), (3, 5, 1), (5, 3, 1), (3, 6, 3), (6, 3, 3), (3, 7, 7), (7, 3, 7), (3, 8, 8), (8, 3, 8), (3, 9, 17), (9, 3, 17), (3, 10, 20), (10, 3, 20), (4, 5, 1), (5, 4, 1), (4, 6, 18), (6, 4, 18), (4, 7, 7), (7, 4, 7), (4, 8, 23), (8, 4, 23), (4, 9, 21), (9, 4, 21), (4, 10, 23), (10, 4, 23), (5, 6, 18), (6, 5, 18), (5, 7, 14), (7, 5, 14), (5, 8, 8), (8, 5, 8), (5, 9, 15), (9, 5, 15), (5, 10, 19), (10, 5, 19), (6, 7, 9), (7, 6, 9), (6, 8, 26), (8, 6, 26), (6, 9, 28), (9, 6, 28), (6, 10, 1), (10, 6, 1), (7, 8, 25), (8, 7, 25), (7, 9, 26), (9, 7, 26), (7, 10, 6), (10, 7, 6), (8, 9, 23), (9, 8, 23), (8, 10, 14), (10, 8, 14), (9, 10, 11), (10, 9, 11), (11, 12, 9), (12, 11, 9), (11, 13, 5), (13, 11, 5), (11, 14, 7), (14, 11, 7), (11, 15, 25), (15, 11, 25), (11, 16, 11), (16, 11, 11), (11, 17, 4), (17, 11, 4), (11, 18, 3), (18, 11, 3), (11, 19, 13), (19, 11, 13), (11, 20, 4), (20, 11, 4), (12, 13, 12), (13, 12, 12), (12, 14, 28), (14, 12, 28), (12, 15, 12), (15, 12, 12), (12, 16, 20), (16, 12, 20), (12, 17, 9), (17, 12, 9), (12, 18, 26), (18, 12, 26), (12, 19, 2), (19, 12, 2), (12, 20, 24), (20, 12, 24), (13, 14, 15), (14, 13, 15), (13, 15, 18), (15, 13, 18), (13, 16, 4), (16, 13, 4), (13, 17, 30), (17, 13, 30), (13, 18, 13), (18, 13, 13), (13, 19, 3), (19, 13, 3), (13, 20, 18), (20, 13, 18), (14, 15, 10), (15, 14, 10), (14, 16, 27), (16, 14, 27), (14, 17, 21), (17, 14, 21), (14, 18, 20), (18, 14, 20), (14, 19, 29), (19, 14, 29), (14, 20, 28), (20, 14, 28), (15, 16, 12), (16, 15, 12), (15, 17, 19), (17, 15, 19), (15, 18, 7), (18, 15, 7), (15, 19, 23), (19, 15, 23), (15, 20, 3), (20, 15, 3), (16, 17, 2), (17, 16, 2), (16, 18, 22), (18, 16, 22), (16, 19, 8), (19, 16, 8), (16, 20, 25), (20, 16, 25), (17, 18, 10), (18, 17, 10), (17, 19, 3), (19, 17, 3), (17, 20, 28), (20, 17, 28), (18, 19, 8), (19, 18, 8), (18, 20, 28), (20, 18, 28), (19, 20, 4), (20, 19, 4), (21, 22, 13), (22, 21, 13), (21, 23, 9), (23, 21, 9), (21, 24, 15), (24, 21, 15), (21, 25, 21), (25, 21, 21), (21, 26, 27), (26, 21, 27), (21, 27, 12), (27, 21, 12), (21, 28, 6), (28, 21, 6), (21, 29, 12), (29, 21, 12), (22, 23, 12), (23, 22, 12), (22, 24, 7), (24, 22, 7), (22, 25, 22), (25, 22, 22), (22, 26, 9), (26, 22, 9), (22, 27, 23), (27, 22, 23), (22, 28, 30), (28, 22, 30), (22, 29, 22), (29, 22, 22), (23, 24, 21), (24, 23, 21), (23, 25, 3), (25, 23, 3), (23, 26, 20), (26, 23, 20), (23, 27, 21), (27, 23, 21), (23, 28, 6), (28, 23, 6), (23, 29, 18), (29, 23, 18), (24, 25, 24), (25, 24, 24), (24, 26, 8), (26, 24, 8), (24, 27, 6), (27, 24, 6), (24, 28, 15), (28, 24, 15), (24, 29, 13), (29, 24, 13), (25, 26, 9), (26, 25, 9), (25, 27, 30), (27, 25, 30), (25, 28, 21), (28, 25, 21), (25, 29, 23), (29, 25, 23), (26, 27, 18), (27, 26, 18), (26, 28, 8), (28, 26, 8), (26, 29, 22), (29, 26, 22), (27, 28, 11), (28, 27, 11), (27, 29, 27), (29, 27, 27), (28, 29, 25), (29, 28, 25), (1, 14, 27), (14, 1, 27), (1, 16, 13), (16, 1, 13), (15, 22, 7), (22, 15, 7), (20, 26, 7), (26, 20, 7)]
tail, head, c = map(list, zip(*edges))
mini = min(c)
new_c=[e+abs(mini)+1 for e in c]

new_edges=list(zip(tail, head, new_c))

b=[0]*n
for i in range(n):
    if i in S:
        b[i]=1
    elif i in T:
        b[i]=-1

# Load a solver
solver = Solver.lookup("coin-bc")

# Load the model
model = Model("Solver_node.mzn")

# Create an instance
instance = Instance(solver, model)

# Pass data from Python to MiniZinc
instance["K"] = k
instance["n"] = len(nodes)
instance["m"] = len(edges)
instance["i"] = tail
instance["j"] = head
instance["c"] = new_c
instance["b"] = b

# Solve
result = instance.solve()
print(result)

node_removed = [z for z, m in zip(nodes, result["z"]) if m]
node_remaining = [z for z, m in zip(nodes, result["z"]) if not m]

infected_remaining=[s for s in S if (s+1) not in node_removed]

edge_removed = [x for x, m in zip(new_edges, result["x"]) if m]
edge_remaining = [x for x, m in zip(new_edges, result["x"]) if not m]

# removed = [x for x, m in zip(edges, result["x"]) if m]
# remaining = [x for x, m in zip(edges, result["x"]) if not m]
print("Selected nodes to remove:")
print(node_removed)
print("Selected edges to remove:")
print(edge_removed)


#Print first graph
G = nx.DiGraph()
colorStates = {"I": "yellow", "S": "green", "B":"blue"}

for node in nodes: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 
    
for s in S:
    G.nodes[s+1]["state"]="I" 
for t in T:
    G.nodes[t+1]["state"]="B"
G.add_weighted_edges_from(new_edges)
# G.add_weighted_edges_from(edges)

colors = [colorStates[G.nodes[n]["state"]] for n in G.nodes()]

# Layout
layout = nx.spring_layout(G,seed=42)
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

for node in node_remaining: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 

for s in infected_remaining:
    G.nodes[s+1]["state"]="I" 
for t in T:
    G.nodes[t+1]["state"]="B"
G.add_weighted_edges_from(edge_remaining)

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
