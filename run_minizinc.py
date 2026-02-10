from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import networkx as nx

s=0
t=4
k=4
nodes=[1,2,3,4,5,6,7,8,9,10]
edges = [  (1, 2, 7),  (2, 1, 7),  (1, 4, 23),  (4, 1, 23),  (1, 5, 4),  (5, 1, 4),  (1, 7, 3),  (7, 1, 3),  (1, 8, 5),  (8, 1, 5),  (1, 9, 1),  (9, 1, 1),  (2, 4, 10),  (4, 2, 10),  (2, 5, 30),  (5, 2, 30),  (2, 7, 11),  (7, 2, 11),  (2, 8, 1),  (8, 2, 1),  (2, 9, 4),  (9, 2, 4),  (2, 10, 6),  (10, 2, 6),  (3, 8, 6),  (8, 3, 6),  (4, 9, 22),  (9, 4, 22),  (4, 10, 30),  (10, 4, 30),  (5, 7, 6),  (7, 5, 6),  (5, 8, 7),  (8, 5, 7),  (5, 9, 2),  (9, 5, 2),  (6, 7, 20),  (7, 6, 20),  (7, 8, 30),  (8, 7, 30),  (8, 9, 11),  (9, 8, 11)]
tail, head, c = map(list, zip(*edges))
mini = min(c)
new_c=[e+abs(mini)+1 for e in c]

new_edges=list(zip(tail, head, new_c))
print(new_edges)

b= [0 for e in range(len(nodes))]
b[s]=1
b[t]=-1

# Load a solver (Gecode is bundled with MiniZinc)
solver = Solver.lookup("highs")

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
# removed = [x for x, m in zip(new_edges, result["x"]) if m]
# remaining = [x for x, m in zip(new_edges, result["x"]) if not m]
removed = [x for x, m in zip(edges, result["x"]) if m]
remaining = [x for x, m in zip(edges, result["x"]) if not m]
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
# G.add_weighted_edges_from(new_edges)
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
