import numpy as np
import networkx as nx

def test(edges,rng,n=100):
    chosen_edges=[]
    new_edges=[]
    #Determine edge costs
    for edge in edges:
        (i,j)=edge
        if (j,i) not in chosen_edges:
            cost = generate_cost(rng,n)
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))
        else:
            cost = next(c for (a,b,c) in new_edges if (a,b) == (j,i))
            chosen_edges.append((i,j))
            new_edges.append((i,j,cost))
    return new_edges

def node_edge_costs(edges, a=0, n=100):
    #Determine node cost
    node_cost= node_weights(edges)

    #Readjust edge weights
    def weight_to_procent(weight): return float(1-(weight/n))
    def procent_to_weight(procent): return max(int(((1-procent)*n)),1)
    def update_procent(node_procent, edge_procent):return max(min((node_procent*a)+(edge_procent*(1-a)),1),0)
    
    final_edges=[]
    for i,j,c in edges:
        p=weight_to_procent(c)
        new_p=update_procent(node_cost[j],p)
        new_c=procent_to_weight(new_p)
        final_edges.append((i,j,new_c))
        # print(f"({i},{j}): j_w={node_cost[j]} and e_w={p} <=> old c={c} != new c={new_c} ")
    # quit()
    return final_edges, node_cost

def generate_cost(rng,n=100):
    # return 1
    return(int(rng.integers(1,n)))

def node_weights(edges):
    unweighted_edges = [(i, j) for i, j, *_ in edges]
    G = nx.DiGraph(unweighted_edges)
    centrality = nx.eigenvector_centrality(G, max_iter=5000)
    n_nodes = G.number_of_nodes()
    nodes = sorted(G.nodes())

    # Lowest centrality first
    sorted_centrality = sorted(
        centrality.items(),
        key=lambda x: x[1],
        reverse=False
    )
    # print("Node centrality:", sorted_centrality)
    # print("Voterank:", nx.voterank(G, n_nodes))

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
    return r

    