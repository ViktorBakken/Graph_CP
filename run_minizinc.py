from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import networkx as nx

nodes = [1, 2, 3, 4]
edges = [(1, 2, 25), (2, 1, 25),(2, 3, 16),(3, 2, 16), (3, 4, 1), (4, 3, 1),(4, 1, 10),  (1, 4, 10)]
tail, head, c = map(list, zip(*edges))
b= [1,0,-1,0]
k=2
print(tail)
print(head)
print(c)
# Load a solver (Gecode is bundled with MiniZinc)
solver = Solver.lookup("gecode")

# Load the model
model = Model("Solver.mzn")

# Create an instance
instance = Instance(solver, model)

# Pass data from Python to MiniZinc
instance["K"] = k*2
instance["n"] = len(nodes)
instance["m"] = len(edges)
instance["i"] = tail
instance["j"] = head
instance["c"] = c
instance["b"] = b

# Solve
# result = instance.solve()

# print(result)
removed = [x for x, m in zip(edges, [0, 0, 1, 1, 1, 1, 0, 0]) if m]
remaining = [x for x, m in zip(edges, [0, 0, 1, 1, 1, 1, 0, 0]) if not m]

print("Selected edges to remove:")
print(removed)


#Print first graph
G = nx.Graph()
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



#Print updated graph
G = nx.Graph()
colorStates = {"I": "yellow", "S": "green", "B":"blue"}

for node in nodes: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 
    
G.nodes[1]["state"]="I" 
G.nodes[3]["state"]="B"
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
