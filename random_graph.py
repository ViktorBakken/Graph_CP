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
    
    p=1/n # The probability is set proportioinal to size of end graph
    edges =set()
    for i in range(n):
        for j in range(n):
            noise=np.random.normal(scale=0.09)
            if i!=j and np.random.uniform(0,1) <= p+noise:
                edges.add((i,j)); edges.add((j,i))
    if displ:
        show(n,edges)
    print("edges=",edges)
    return set(edges)

if __name__=="__main__":
    n=30
    print(1/n)
    for _ in range(20):
        edges=generate_graph(n,False)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)
        avg_degree = sum(d for _, d in G.degree()) / n
        print(avg_degree)

        if (avg_degree>2.5):
            show(n,edges)


