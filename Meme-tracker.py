import networkx as nx
import pandas as pd

# Example expected CSV:
# phrase,frequency
# "palling around with terrorists",42   
# "he is palling around with terrorists who would target their own country",18

phrases = pd.read_csv("phrases.csv")

def token_overlap(short, long, k=5):
    s = short.lower().split()
    l = long.lower().split()
    if len(s) > len(l):
        return False
    joined_l = " ".join(l)
    return " ".join(s) in joined_l or any(
        " ".join(s[i:i+k]) in joined_l for i in range(max(1, len(s)-k+1))
    )

G_meme = nx.DiGraph()

for _, row in phrases.iterrows():
    G_meme.add_node(row["phrase"], frequency=row["frequency"])

plist = phrases["phrase"].tolist()

for p in plist:
    for q in plist:
        if p != q and len(p.split()) < len(q.split()):
            if token_overlap(p, q, k=5):
                G_meme.add_edge(p, q)

# Each weakly connected component is a rough meme / phrase cluster
clusters = list(nx.weakly_connected_components(G_meme))
print(len(clusters))