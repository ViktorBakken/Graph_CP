import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def show(n,edges, sets=None):
    if sets== None:
        sets=[{i for i in range(n)}, {},{},{}]
    colorStates = {"S": "green", "I": "red", "R":"black", "B":"yellow"}

    G = nx.Graph()
    for node in range(n): 
        G.add_node(node)
    
    for s in sets[0]:
        G.nodes[s]["state"]="S" 
    for i in sets[1]:
        G.nodes[i]["state"]="I"
    for r in sets[2]:
        G.nodes[r]["state"]="R"
    for r in sets[3]:
        G.nodes[r]["state"]="B"
    
    
    G.add_edges_from(edges)
    layout = nx.spring_layout(G)
    colors = [colorStates[G.nodes[n]["state"]] for n in G.nodes()]
    nx.draw(G, layout, node_color=colors, with_labels=True)
    plt.show()



def generate_graph(n=10, displ=False,):
    
    p=1/n
    edges =[]
    for i in range(n):
        for j in range(n):
            noise=np.random.normal(scale=0.05)
            # print("noise=",noise, ", p=",p+noise, "comp:", np.random.uniform(0,1))
            if i!=j and np.random.uniform(0,1) <= p+noise:
                edges.append((i,j)); edges.append((j,i))
    if displ:
        # show(n,edges)
        print("edges=",edges)
    return edges

# n=100
# print(1/n)
# for _ in range(1):
#     edges=generate_graph(n,True)
#     G = nx.Graph()
#     G.add_nodes_from(range(n))
#     G.add_edges_from(edges)
#     avg_degree = sum(d for _, d in G.degree()) / n
#     print(avg_degree)

#     if (avg_degree>3):
#         show(n,edges)


