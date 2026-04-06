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

def analys_GF(edges, sets):
    G=nx.Graph(edges)
    Gf=nx.Graph(filter_edges(sets[1],edges,mode=1))
    exposure=len(filter_edges(sets[1],edges,mode=1))*0.2
    # print("infection exposure:",exposure)

    betweenes = nx.betweenness_centrality(G)
    avg_betweenness=[]
    for s in Gf.nodes():
        if s in (set.union(sets[0],sets[3])):
            avg_betweenness.append(betweenes[s])
            # print("node:", s, " ", betweenes[s])
    max_centrality=max(avg_betweenness) if len(avg_betweenness)>0 else 0
    # print("average betweenes in S nodes touching infected nodes:",average_centrality)
    # show(15,edges,sets)
    return [exposure,max_centrality]

def analys_Gh(edges, sets):
    healthyEdges=[]
    if sets[3]==set():
        healthyEdges=filter_edges(sets[0],edges)
    else:
        healthyEdges=filter_edges(set.union(sets[0],set(sets[3] - sets[1])),edges)
    Gh=nx.Graph(healthyEdges)
    # betweenes = nx.betweenness_centrality(G)
    ccs= nx.number_connected_components(Gh)
    # print("number of connected components",ccs)
    ccs_2=nx.connected_components(Gh)
    max=0
    for cc in ccs_2:
        max=max if len(cc)<max else len(cc)
    efficentcy=(nx.global_efficiency(Gh))/len(Gh.nodes()) if len(Gh.nodes())>0 else 0
    # print("efficency=", efficentcy)
    # eff=[betweenes[s] for s in set.union(sets[0],set(sets[3]-sets[1]))]
    # print("average efficency:",np.mean(eff))
    # for s in sets[0]:
    #     print("node:", s, " ", betweenes[s])

    # print("average connectivity:",nx.average_node_connectivity(Gh))
    # print("css_2=",max)
    return [ccs,max,efficentcy]

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
    if sets[3]==set():
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


