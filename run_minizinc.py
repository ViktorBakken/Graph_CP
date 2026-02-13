from minizinc import Instance, Model, Solver
import matplotlib.pyplot as plt
import networkx as nx

S=[0,1,5]
t=6
k=1

n=7
nodes=[i+1 for i in range(n)]
edges = [(1, 2, 21), (2, 1, 21), (1, 3, 4), (3, 1, 4), (1, 4, 1), (4, 1, 1), (2, 3, 24), (3, 2, 24), (2, 4, 9), (4, 2, 9), (3, 4, 8), (4, 3, 8), (5, 6, 8), (6, 5, 8), (5, 7, 5), (7, 5, 5), (6, 7, 24), (7, 6, 24), (1, 7, 24), (7, 1, 24)]

tail, head, c = map(list, zip(*edges))
mini = min(c)
new_c=[e+abs(mini)+1 for e in c]

new_edges=list(zip(tail, head, new_c))

b= [1 if(e in S) else 0 for e in range(len(nodes))]
b[t]=-1

# Load a solver
solver = Solver.lookup("chuffed")

# Load the model
model = Model("Solver_node.mzn")

# Create an instance
instance = Instance(solver, model)

# Pass data from Python to MiniZinc
instance["K"] = k
instance["t"] = t+1
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

for node in node_remaining: 
    G.add_node(node) 
    G.nodes[node]["state"]="S" 

for s in infected_remaining:
    if(len(S)>0):
        G.nodes[s+1]["state"]="I" 
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
