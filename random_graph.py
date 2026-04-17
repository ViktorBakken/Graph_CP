import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

import matplotlib.pyplot as plt
import networkx as nx

def show(n, edges, sets=None, layout=None):
    if sets is None:
        sets = [{i for i in range(n)}, {}, {}, {}]

    colorStates = {"S": "green", "I": "red", "R": "black", "B": "yellow"}

    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)

    # default state
    nx.set_node_attributes(G, {node: "S" for node in G.nodes()}, "state")

    for s in sets[0]:
        G.nodes[s]["state"] = "S"
    for i in sets[1]:
        G.nodes[i]["state"] = "I"
    for r in sets[2]:
        G.nodes[r]["state"] = "R"
    for b in sets[3]:
        G.nodes[b]["state"] = "B"

    if layout is None:
        layout = nx.spring_layout(G, seed=42)

    colors = [colorStates[G.nodes[node]["state"]] for node in G.nodes()]
    nx.draw(G, layout, node_color=colors, with_labels=True)
    plt.show()
    return layout


def generate_graph(n=10, seed=42,):
    # G=nx.barabasi_albert_graph(n,3,seed=seed)
    G=nx.newman_watts_strogatz_graph(n,4,0.2,seed=seed)
    # G = nx.karate_club_graph()
    # G=nx.erdos_renyi_graph(n,0.05,seed=seed)
    
    edges= list(G.edges())
    final_edges=edges.copy()
    for edge in edges:
        (i,j)=edge
        final_edges.append((j,i))

    return list(final_edges)


def filter_edges(nodes, edges, mode=0):
    nodes_set=set(nodes)
    filtered_edges=[]
    for edge in edges:
        (i,j)=edge
        if i in nodes_set and j in nodes_set and mode==0:
            filtered_edges.append((i,j))
            filtered_edges.append((j,i))
        if i in nodes_set and j not in nodes_set and mode==1:
            filtered_edges.append((i,j))
    return filtered_edges


def determine_T(edges, sets):
     #---Determine critical nodes ----------
    normal=sets[0]
    filtered_edges=filter_edges(normal,edges)
    G=nx.Graph(filtered_edges)
    T=set(nx.voterank(G,len(G.nodes)//5 ))
    return T

def determine_k_dangerous_edges(edges, risk_edges,sets,budget):
    healthyEdges=[]
    if sets[2]==set():
        healthyEdges=filter_edges(sets[0],edges)
    else:
        healthyEdges=filter_edges(set.union(sets[0],set(sets[3] - sets[1])),edges)
    high_risk_edges=[]
    if len(healthyEdges)>0:
        G=nx.Graph(healthyEdges)
        centrality = {}
        for component in nx.connected_components(G):
            H = G.subgraph(component)
            c = nx.eigenvector_centrality(H, max_iter=5000)
            centrality.update(c)
        high_risk_edges=sorted(risk_edges,key=lambda e: centrality.get(e[1],0),reverse=True)
    return set(high_risk_edges[:budget])

def analyse_graph(n,edges):
    G = nx.Graph(edges)
    avg_degree = sum(d for _, d in G.degree()) / n
    print(avg_degree)

    betweenness = nx.current_flow_betweenness_centrality(G)
    max=(0,0)
    for n in sorted(G.nodes()):
        t= betweenness[n]
        if max[1]< t:
            max=(n,t)
        # print(n,": ",t)
    print("current flow betweenness:",max)

    betweenness = nx.betweenness_centrality(G)
    max=(0,0)
    for n in sorted(G.nodes()):
        t= betweenness[n]
        if max[1]< t:
            max=(n,t)
        # print(n,": ",t)
    print("Shortest path:",max)

    betweenness = nx.eigenvector_centrality(G,max_iter=1000)
    max=(0,0)
    for n in sorted(G.nodes()):
        t= betweenness[n]
        if max[1]< t:
            max=(n,t)
        # print(n,": ",t)
    print("Eigenvector:",max)

    betweenness = nx.current_flow_closeness_centrality(G)
    max=(0,0)
    for n in sorted(G.nodes()):
        t= betweenness[n]
        if max[1]< t:
            max=(n,t)
        # print(n,": ",t)
    print("current flow closeness:",max)


    betweenness = nx.closeness_centrality(G)
    max=(0,0)
    for n in sorted(G.nodes()):
        t= betweenness[n]
        if max[1]< t:
            max=(n,t)
        # print(n,": ",t)
    print("closeness:",max)

if __name__=="__main__":
    n=100
    for _ in range(10):
        seed= np.random.randint(0,100)
        edges=generate_graph(n,seed)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)
        avg_degree = sum(d for _, d in G.degree()) / n
        print(avg_degree)
        print("edges=",edges)
        show(n,edges)

        # if (avg_degree>2.5):
        #     show(n,edges)


