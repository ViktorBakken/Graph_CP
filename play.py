import igraph as ig
import matplotlib.pyplot as plt

# Data
nodes = ["A", "B", "C", "D"]
edges = [
    ("A", "B", 1), ("B", "C", 4), ("C", "D", 3), ("D", "A", 2),
    ("B", "A", 3), ("C", "B", 2), ("D", "C", 3), ("A", "D", 3)
]
colorStates = {"I": "yellow", "S": "green"}

g = ig.Graph(directed=True)
g.add_vertices(nodes)

# Vertex attributes (state)
g.vs["state"] = ["S"] * g.vcount()
g.vs.find(name="A")["state"] = "I"

# Edges + weights
g.add_edges([(u, v) for (u, v, _) in edges])
g.es["weight"] = [w for (_, _, w) in edges]

vertex_colors = [colorStates[s] for s in g.vs["state"]]

# Layout
layout = g.layout("fr")

fig, ax = plt.subplots(figsize=(7, 4))

ig.plot(
    g,
    target=ax,
    layout=layout,
    bbox=(700, 700),     # larger drawing box
    margin=30,           # extra padding so labels don't hit the border
    vertex_color=vertex_colors,
    vertex_label=g.vs["name"],
    edge_label=g.es["weight"],
    autocurve=True,      # nicer for opposite-direction edges
    edge_arrow_size=0.6,
    edge_label_dist=0.8  # push labels a bit away from the edges
)

# Disable clipping for labels (weights + vertex labels) so nothing gets cut off
for t in ax.texts:
    t.set_clip_on(False)

ax.set_axis_off()
plt.tight_layout()
plt.show()



# Data
nodes = ["A", "B", "C", "D"]
edges = [("A", "B", 25), ("B", "C", 16), ("C", "D", 1), ("D", "A", 10)]
colorStates = {"I": "yellow", "S": "green"}

g = ig.Graph(directed=False)
g.add_vertices(nodes)

# Vertex attributes (state)
g.vs["state"] = ["S"] * g.vcount()
g.vs.find(name="A")["state"] = "I"

# Edges + weights
g.add_edges([(u, v) for (u, v, _) in edges])
g.es["weight"] = [w for (_, _, w) in edges]

vertex_colors = [colorStates[s] for s in g.vs["state"]]

# Layout
layout = g.layout("fr")

fig, ax = plt.subplots(figsize=(7, 4))

ig.plot(
    g,
    target=ax,
    layout=layout,
    bbox=(700, 400),     # larger drawing box
    margin=10,           # extra padding so labels don't hit the border
    vertex_color=vertex_colors,
    vertex_label=g.vs["name"],
    edge_label=g.es["weight"],
    autocurve=True,      # nicer for opposite-direction edges
    edge_arrow_size=0.6,
    edge_label_dist=0.3  # push labels a bit away from the edges
)

# Disable clipping for labels (weights + vertex labels) so nothing gets cut off
for t in ax.texts:
    t.set_clip_on(False)

# ax.set_axis_off()
plt.tight_layout()
plt.show()

# Data
nodes = ["A", "B", "C", "D"]
edges = [("A", "B", 25), ("B", "C", 16), ("C", "D", 1.2)]
colorStates = {"I": "yellow", "S": "green"}

g = ig.Graph(directed=False)
g.add_vertices(nodes)

# Vertex attributes (state)
g.vs["state"] = ["S"] * g.vcount()
g.vs.find(name="A")["state"] = "I"

# Edges + weights
g.add_edges([(u, v) for (u, v, _) in edges])
g.es["weight"] = [w for (_, _, w) in edges]

vertex_colors = [colorStates[s] for s in g.vs["state"]]

# Layout
layout = g.layout("fr")

fig, ax = plt.subplots(figsize=(7, 4))

ig.plot(
    g,
    target=ax,
    layout=layout,
    bbox=(700, 400),     # larger drawing box
    margin=70,           # extra padding so labels don't hit the border
    vertex_color=vertex_colors,
    vertex_label=g.vs["name"],
    edge_label=g.es["weight"],
    autocurve=True,      # nicer for opposite-direction edges
    edge_arrow_size=0.6,
    edge_label_dist=0.8  # push labels a bit away from the edges
)

# Disable clipping for labels (weights + vertex labels) so nothing gets cut off
for t in ax.texts:
    t.set_clip_on(False)

ax.set_axis_off()
plt.tight_layout()
plt.show()

