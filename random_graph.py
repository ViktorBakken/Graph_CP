import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def show(n,edges, sets=None,layout=None):
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
    if(layout==None):
        layout = nx.spring_layout(G,seed=42)
    colors = [colorStates[G.nodes[n]["state"]] for n in G.nodes()]
    nx.draw(G, layout, node_color=colors, with_labels=True)
    plt.show()
    return layout



def generate_graph(n=10, displ=False,):
    
    p=1/n # The probability is set proportioinal to size of end graph
    edges =[]
    for i in range(n):
        for j in range(n):
            noise=np.random.normal(scale=0.03)
            if i!=j and np.random.uniform(0,1) <= p+noise:
                edges.append((i,j)); edges.append((j,i))
    if displ:
        show(n,edges)
    print("edges=",edges)
    return set(edges)


def filter_edges(nodes, edges):
    nodes_set=set(nodes)
    filtered_edges=[]
    for edge in edges:
        (i,j)=edge
        if i in nodes_set or j in nodes_set:
            filtered_edges.append((i,j))
            filtered_edges.append((j,i))
    return filtered_edges


def determine_T(edges, sets):
     #---Determine critical nodes ----------
    normal=sets[0]
    infected=sets[1]
    T=[None]

    filtered_edges=filter_edges(normal,edges)
    G=nx.Graph(filtered_edges)
    # Leaders (max degree nodes)
    # out=nx.degree_centrality(G)
    # max=np.max([degree for (node,degree) in out if node not in infected])
    # out=nx.degree(G,G.nodes)
    # max=np.max([degree for (node,degree) in out if node not in infected])
    # leading_nodes={node for (node,degree) in out if degree== max and node not in infected}
    leading_nodes=set(nx.voterank(G,1))
    # Bridging nodes
    bridging_nodes = set(nx.articulation_points(G))-infected

    T=leading_nodes.union(bridging_nodes)
    return T

if __name__=="__main__":
    n=100
    print(1/n)
    for _ in range(100):
        edges=generate_graph(n,False)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)
        avg_degree = sum(d for _, d in G.degree()) / n
        print(avg_degree)

        if (avg_degree>2.5 and avg_degree<3.2):
            show(n,edges)


