import pandas as pd
from random_graph import show,determine_T

import random
import networkx as nx

def geometric_count(p):
    x = 0
    while random.random() < p:
        x += 1
    return x

def forest_fire_graph(n, p_f=0.3, p_b=0.25, seed=42):
    random.seed(seed)
    G = nx.DiGraph()
    G.add_node(0)

    for v in range(1, n):
        G.add_node(v)

        ambassador = random.choice(list(G.nodes - {v}))
        burned = {ambassador}
        frontier = [ambassador]

        while frontier:
            u = frontier.pop()
            G.add_edge(v, u)
            G.add_edge(u, v)

            forward = list(G.successors(u))
            backward = list(G.predecessors(u))

            random.shuffle(forward)
            random.shuffle(backward)

            x = geometric_count(p_f)
            y = geometric_count(p_b)

            for w in forward[:x]:
                if w not in burned:
                    burned.add(w)
                    frontier.append(w)

            for w in backward[:y]:
                if w not in burned:
                    burned.add(w)
                    frontier.append(w)
                    
                    
    copy=list(G.edges()).copy()
    for edge in copy:
        (i,j) = edge
        if i == j:
            G.remove_edge(i,j)
    return G


# n=500
# p_f=0.3
# p_b=0.25
# # G_ff = forest_fire_graph(n=n, p_f=p_f, p_b=p_b)
# # print(G_ff.number_of_nodes(), G_ff.number_of_edges())

# for pf in [0.2,0.25, 0.3, 0.35,0.40,0.45]:
#     for pb in [0.2,0.25, 0.3, 0.35,0.40,0.45]:
#         G =forest_fire_graph(n, pf, pb)

#         # forest_fire_graph(n, pf, pb)
#         G_undirected=set(G.edges())

#         for idx, edge in enumerate(set(G.edges())):
#             (i,j)=edge
            
#             if((j,i) not in G_undirected):
#                 print(idx)
        
        
        
#         print("edges=",list(G_undirected))    
#         print(pf, pb, len(G_undirected)/2)
        
#         show(n,G_undirected,[{n for n in range(n)}, {}, {},{}])
    

import igraph as ig
n = 500
for pf in [0.2, 0.25, 0.3, 0.35, 0.40, 0.45]:
    for pb in [0.2, 0.25, 0.3, 0.35, 0.40, 0.45]:

        g = ig.Graph.Forest_Fire(
            n=n,
            fw_prob=pf,
            bw_factor=pb,
            directed=True
        )

        # Convert igraph edge list to Python set of tuples
        G_edges = set(g.get_edgelist())

        # Optional: check whether every edge has reverse edge
        Final_edges=[]
        for idx, (i, j) in enumerate(G_edges):
            if (j, i) not in G_edges:
                Final_edges.append((i,j))
                Final_edges.append((j,i))

        # print("edges=", list(G_edges))
        print(pf, pb, len(G_edges))

        T=determine_T(Final_edges,[{i for i in range(n)}, {}, {}])
        print("len T= ",len(T))
        show(n, G_edges, [{i for i in range(n)}, {}, T])
