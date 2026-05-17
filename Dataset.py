import pandas as pd
import networkx as nx
import numpy as np
from random_graph import analyse_graph, show_weighted

# Load CSV
# df = pd.read_csv("weighted_twitter_news_networks.csv")
df = pd.read_csv("weighted_edges.csv")

# Create directed weighted graph
G_string = nx.from_pandas_edgelist(
    df,
    source="source",
    target="target",
    edge_attr="weight",
    create_using=nx.DiGraph()
)

G = nx.convert_node_labels_to_integers(
    G_string,
    label_attribute="username"
)

def tie(cost_1, cost_2): return int(np.floor((cost_1 + cost_2)/(0.4*max(1,np.abs(cost_1-cost_2)))))
def weight(tie,global_max_tie): return global_max_tie-tie+1


n=len(G.nodes())
edges = [
    (u, v, d["weight"])
    for u, v, d in G.edges(data=True)
]
edge_pair={ (i,j) for i, j, _ in edges}

# Clean edges
for edge in edge_pair :
    i, j= edge
    if ((j,i) not in edge_pair) or (j,i)==(i,j):
        edges.remove((i,j,G[i][j]["weight"]))
    else:
        cost_1= G[i][j]["weight"]
        cost_2= G[j][i]["weight"]
        if cost_1 < 6 and cost_2 < 6:
            edges.remove((i,j,cost_1)) 

# Tie
seen = set()
new_edges = []

for i, j, c_1 in edges:
    if (j, i) not in seen :
        c_2 = G[j][i]["weight"]
        tie_score = tie(c_1, c_2)
        new_edges.append((i, j, tie_score))
        new_edges.append((j,i, tie_score))

        seen.add((i, j))
        seen.add((j, i))

G_test= nx.Graph()
G_test.add_weighted_edges_from(new_edges)
# after G_test has been created
remaining_nodes = sorted(G_test.nodes())
node_map = {
    old_id: new_id
    for new_id, old_id in enumerate(remaining_nodes)
}
renamed_edges = [
    (node_map[u], node_map[v], w)
    for u, v, w in G_test.edges(data="weight")
]



tie_bar=max({c for _,_,c in renamed_edges})
print(tie_bar)
final_edges=[]
for i,j,c in renamed_edges:
    final_edges.append((i,j,weight(c,tie_bar)))


G_reindexed = nx.Graph()
G_reindexed.add_weighted_edges_from(final_edges)

print("num edges: ",len(G_reindexed.edges()), "num nodes: ",len(G_reindexed.nodes()))


edge_pair={ (i,j) for i, j, _ in final_edges}

print(analyse_graph(n,edge_pair))
show_weighted(len(list(G_reindexed.nodes)),final_edges)

# print(final_edges)