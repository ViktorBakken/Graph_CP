import numpy as np
import networkx as nx

def test(n,edges,rng):
    chosen_edges=[]
    new_edges=[]
    #Determine edge costs
    for edge in edges:
        (i,j)=edge
        if (j,i) not in chosen_edges:
            cost = generate_cost(rng)
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))
        else:
            cost = next(c for (a,b,c) in new_edges if (a,b) == (j,i))
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))


    #Determine node cost
    node_cost= node_weights(n,edges)

    #Readjust edge weights
    def weight_to_procent(weight): return 1-(weight/100)
    def procent_to_weight(procent): return (1-procent)*100
    def update_procent(node_procent, edge_procent,a=4):return max(min((node_procent*a)+(edge_procent*(1-a)),1),0)
    final_edges=[]

    for i,j,c in new_edges:
        p=weight_to_procent(c)
        new_p=update_procent(node_cost[i],p)
        new_c=procent_to_weight(new_p)
        final_edges.append((i,j,new_c))
        # print(f"edge:({i},{j},{c}), where i={node_cost[i]}, new c={new_c}")
    return new_edges

def generate_cost(rng):
    # return 1
    return(int(rng.integers(1,100)))

def node_weights(n,edges):

    G = nx.Graph(edges)
    avg_degree = sum(d for _, d in G.degree()) / n
    print("Average node degree: ", avg_degree)

    import numpy as np

    centrality = nx.eigenvector_centrality(G, max_iter=5000)

    n_nodes = G.number_of_nodes()
    nodes = sorted(G.nodes())

    # Lowest centrality first
    sorted_centrality = sorted(
        centrality.items(),
        key=lambda x: x[1],
        reverse=False
    )

    ranked_nodes = {}

    current_rank = 0
    previous_value = None

    for node, value in sorted_centrality:
        if previous_value is None or not value < previous_value:
            current_rank += 1
            previous_value = value

        ranked_nodes[node] = current_rank

    # Ranking ordered by node id / node order
    final_ranking = np.array([ranked_nodes[node] for node in nodes])

    # Same r formula:
    # lowest centrality -> r = 0
    # highest centrality -> r close to 1
    r = (final_ranking - 1) / (n_nodes - 1)
    # print(r[0])
    return r

    