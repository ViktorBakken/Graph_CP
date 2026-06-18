from minizinc import Instance, Model, Solver
from random_graph import determine_T, show, show_weighted
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from Generate_cost_edges import test
from Generate_cost_edges import node_edge_costs
import time


def interdiction_minizinc(
    num_nodes=50,
    budget=3,
    infected_nodes=None,
    infected_edges=None,
    critical_nodes=None,
    graph_edges=None,
    interdiction_type="edge",
    solver_name="highs",
    displ=0,
    layout=None,
    seed=42,
    node_b_weights=False,  # dict node->float (0-1), scales b[t] for targets
    M=0,
    influencer_set=None,
):
    k = budget
    n = num_nodes

    if infected_nodes == None:
        # 15
        S = {0,7,16}
        # 100
        # S = {0, 66, 34, 7, 8, 11, 46, 15, 80, 47, 52, 85}
    else:
        S = infected_nodes.copy()

    if graph_edges == None:
        # n=15
        # edges = [
        #     (12, 7, 4),
        #     (7, 12, 4),
        #     (5, 4, 90),
        #     (4, 5, 90),
        #     (4, 6, 56),
        #     (6, 4, 56),
        #     (8, 0, 34),
        #     (0, 8, 34),
        #     (9, 5, 55),
        #     (5, 9, 55),
        #     (11, 2, 43),
        #     (2, 11, 43),
        #     (11, 5, 39),
        #     (5, 11, 39),
        #     (9, 14, 33),
        #     (14, 9, 33),
        #     (13, 11, 50),
        #     (11, 13, 50),
        #     (7, 10, 81),
        #     (10, 7, 81),
        #     (6, 14, 76),
        #     (14, 6, 76),
        #     (4, 2, 54),
        #     (2, 4, 54),
        #     (3, 0, 30),
        #     (0, 3, 30),
        #     (9, 7, 76),
        #     (7, 9, 76),
        #     (5, 12, 68),
        #     (12, 5, 68),
        #     (11, 1, 35),
        #     (1, 11, 35),
        #     (11, 7, 41),
        #     (7, 11, 41),
        #     (1, 2, 97),
        #     (2, 1, 97),
        #     (0, 13, 5),
        #     (13, 0, 5),
        #     (13, 10, 66),
        #     (10, 13, 66),
        #     (8, 7, 24),
        #     (7, 8, 24),
        #     (9, 6, 63),
        #     (6, 9, 63),
        # ]
        edges= [(32, 37, 50), (4, 0, 91), (10, 34, 58), (21, 16, 91), (41, 31, 22), (34, 10, 58), (17, 3, 87), (20, 29, 35), (28, 21, 31), (8, 18, 55), (45, 37, 95), (12, 34, 89), (0, 14, 18), (13, 8, 93), (6, 2, 99), (4, 48, 60), (43, 30, 75), (7, 10, 82), (44, 47, 15), (34, 12, 89), (5, 3, 1), (17, 5, 38), (36, 18, 19), (48, 38, 58), (20, 31, 19), (0, 7, 18), (20, 40, 75), (32, 5, 25), (0, 16, 93), (13, 10, 92), (24, 19, 20), (7, 21, 45), (19, 4, 70), (3, 17, 87), (38, 48, 58), (5, 32, 25), (13, 12, 8), (35, 12, 27), (38, 11, 92), (8, 25, 71), (49, 11, 2), (8, 34, 54), (30, 43, 75), (9, 42, 74), (14, 1, 52), (29, 20, 35), (40, 20, 75), (0, 48, 51), (12, 13, 8), (40, 29, 87), (22, 23, 16), (21, 25, 41), (23, 22, 16), (0, 2, 43), (38, 4, 13), (10, 15, 81), (33, 17, 1), (41, 39, 85), (7, 16, 95), (29, 13, 7), (17, 2, 29), (34, 18, 58), (12, 15, 62), (4, 11, 14), (39, 41, 85), (11, 4, 14), (29, 40, 87), (3, 30, 22), (27, 15, 56), (10, 8, 12), (4, 38, 13), (6, 1, 72), (7, 0, 18), (1, 14, 52), (15, 13, 39), (17, 32,77), (2, 22, 95), (16, 21, 91), (22, 0, 31), (3, 5, 1), (15, 34, 47), (35, 46, 63), (12, 26, 3), (31, 39, 8), (4, 22, 61), (12, 35, 27), (8, 13, 93), (2, 6, 99), (25, 8, 71), (28, 25, 61), (22, 2, 95), (12, 10, 46), (15, 27, 56), (9, 2, 76), (4, 24, 47), (1, 0, 67), (10, 12, 46), (25, 10, 90), (16, 7, 95), (19, 24, 20), (2, 17, 29), (26, 12, 3), (25, 28, 61), (22, 4, 61), (11, 38, 92), (14, 0, 18), (46, 35, 63), (7, 25, 2), (18, 8, 55), (18, 34, 58), (1, 2, 39), (0, 4, 91), (2, 1, 39), (16, 0, 93), (24, 4, 47), (37, 32, 50), (0, 22, 31), (25, 21, 41), (3, 2, 89), (14, 2, 65), (11, 49, 2), (13, 34, 68), (32, 47, 58), (4, 19, 70), (18, 36, 19), (34, 20, 6), (8, 10, 12), (10, 7, 82), (2, 3, 89), (48, 0, 51), (10, 25, 90), (47, 44, 15), (31, 20, 19), (21, 28, 31), (34, 13, 68), (30, 3, 22), (34, 31, 99), (1,6, 72), (25, 7, 2), (31, 41, 22), (2, 14, 65), (17, 33, 1), (25, 16, 22), (37, 45, 95), (13, 20, 21), (6, 14, 88), (20, 13, 21), (44, 32, 80), (13, 29, 7), (14, 6, 88), (16, 25, 22), (34, 15, 47), (0, 1,67), (20, 34, 6), (31, 34, 99), (48, 4, 60), (32, 17, 77), (15, 10, 81), (32, 44, 80), (34, 8, 54), (39, 31, 8), (8, 7, 62), (42, 9, 74), (2, 0, 43), (5, 17, 38), (10, 13, 92), (47, 32, 58), (2, 9, 76), (13, 15, 39), (15, 12, 62), (7, 8, 62), (21, 7, 45)]        # print("edges=", sorted(edges, key=lambda e: e[2]))
        # edges,node_b_weights= node_edge_costs(edges, a=1)
        # edges=[(12, 7, 27), (7, 12, 5), (5, 4, 52), (4, 5, 62), (4, 6, 45), (6, 4, 49), (8, 0, 59), (0, 8, 63), (9, 5, 38), (5, 9, 34), (11, 2, 21), (2, 11, 35), (11, 5, 19), (5, 11, 26), (9, 14, 27), (14, 9, 55), (13, 11, 39), (11, 13, 10), (7, 10, 44), (10, 7, 76), (6, 14, 59), (14, 6, 77), (4, 2, 44), (2, 4, 41), (3, 0, 65), (0, 3, 61), (9, 7, 48), (7, 9, 41), (5, 12, 41), (12, 5, 59), (11, 1, 17), (1, 11, 49), (11, 7, 20), (7, 11, 24), (1, 2, 80), (2, 1, 62), (0, 13, 48), (13, 0, 31), (13, 10, 61), (10, 13, 68), (8, 7, 54), (7, 8, 15), (9, 6, 42), (6, 9, 52)]

        # 100
        # edges= [(23, 4), (4, 23), (67, 4), (4, 67), (69, 1), (1, 69), (15, 30), (30, 15), (80, 65), (65, 80), (73, 26), (26, 73), (8, 0), (0, 8), (61, 70), (70, 61), (71, 38), (38, 71), (63, 34), (34, 63), (96, 67), (67, 96), (73, 35), (35, 73), (92, 79), (79, 92), (85, 73), (73, 85), (21, 37), (37, 21), (28, 30), (30, 28), (46, 66), (66, 46), (86, 47), (47, 86), (67, 98), (98, 67), (85, 27), (27, 85), (17, 94), (94, 17), (55, 50), (50, 55), (6, 11), (11, 6), (69, 49), (49, 69), (6, 75), (75, 6), (99, 93), (93, 99), (2, 32), (32, 2), (11, 44), (44, 11), (47, 18), (18, 47), (91, 18), (18, 91), (8, 11), (11, 8), (23, 27), (27, 23), (6, 41), (41, 6), (52, 8), (8, 52), (30, 75), (75, 30), (82, 58), (58, 82), (66, 7), (7, 66), (67, 27), (27, 67), (74, 84), (84, 74), (11, 80), (80, 11), (38, 64), (64, 38), (80, 88), (88, 80), (64, 0), (0, 64), (81, 16), (16, 81), (39, 10), (10, 39), (0, 46), (46, 0), (55, 79), (79, 55), (15, 46), (46, 15), (37, 28), (28, 37), (5, 23), (23, 5), (84, 45), (45, 84), (48, 58), (58, 48), (61, 22), (22, 61), (35, 67), (67, 35), (77, 48), (48, 77), (61, 31), (31, 61), (24, 21), (21, 24), (70, 43), (43, 70), (71, 72), (72, 71), (35, 85), (85, 35), (76, 31), (31, 76), (13, 94), (94, 13), (83, 0), (0, 83), (63, 31), (31, 63), (60, 16), (16, 60), (11, 66), (66, 11), (98, 9), (9, 98), (15, 66), (66, 15), (32, 27), (27, 32), (25, 22), (22, 25), (19, 36), (36, 19), (76, 88), (88, 76), (87, 70), (70, 87), (18, 80), (80, 18), (0, 96), (96, 0), (83, 48), (48, 83), (76, 97), (97, 76), (84, 86), (86, 84), (46, 47), (47, 46), (3, 21), (21, 3), (14, 21), (21, 14), (68, 1), (1, 68), (23, 33), (33, 23), (83, 84), (84, 83), (66, 77), (77, 66), (43, 20), (20, 43), (34, 48), (48, 34), (81, 77), (77, 81), (53, 6), (6, 53), (85, 93), (93, 85), (22, 0), (0, 22), (91, 54), (54, 91), (22, 73), (73, 22), (39, 89), (89, 39), (15, 34), (34, 15), (93, 69), (69, 93), (84, 97), (97, 84), (5, 84), (84, 5), (69, 87), (87, 69), (44, 12), (12, 44), (40, 81), (81, 40), (18, 50), (50, 18), (27, 28), (28, 27), (7, 59), (59, 7), (10, 85), (85, 10), (48, 69), (69, 48), (94, 36), (36, 94), (72, 90), (90, 72), (94, 72), (72, 94), (95, 92), (92, 95), (19, 72), (72, 19), (67, 39), (39, 67), (91, 88), (88, 91), (19, 81), (81, 19), (29, 3), (3, 29), (31, 18), (18, 31), (40, 94), (94, 40), (44, 64), (64, 44), (65, 62), (62, 65), (25, 78), (78, 25), (57, 76), (76, 57), (74, 83), (83, 74), (46, 85), (85, 46), (98, 31), (31, 98), (0, 42), (42, 0), (49, 90), (90, 49), (87, 74), (74, 87), (36, 37), (37, 36), (92, 91), (91, 92), (90, 56), (56, 90), (71, 70), (70, 71), (24, 77), (77, 24), (51, 6), (6, 51), (59, 51), (51, 59), (29, 4), (4, 29)]
    else:
        edges = graph_edges.copy()

        # Search
    inf_edges = (
            [idx for idx, (i, j, _) in enumerate(edges) if i in S and j not in S]
            if infected_edges == None
            else [edges.index(edge) for edge in infected_edges]
    )
    # print(len(inf_edges), "infected edges:", [edges[i] for i in inf_edges])

    if interdiction_type == "edge" and (k <= 0 or len(inf_edges) == 0):
        return edges.copy()

    if critical_nodes == None:
       sets=[[i for i in range(n) if i not in S],S, {}]
       T= determine_T(edges, sets) - S
    else:
        T = critical_nodes.copy()
    nodes = [i for i in range(n)]

    tail, head, cost = map(list, zip(*edges))
   


    b = [0] * n
    for i in range(n):
        if i in S:
            b[i] = 1
        elif i in T:
            b[i] = -4 if (influencer_set is not None and i in influencer_set) else -1


    # Load a solver
    solver = Solver.lookup(solver_name)

    # Load the model
    model_choice = "Solver_2.mzn"
    # Create an instance
    instance = Instance(solver, Model(model_choice))

    if node_b_weights:
        cost=[1 for _ in cost] # ignore edge costs



    # Pass data from Python to MiniZinc
    instance["K"] = k
    instance["n"] = len(nodes)
    instance["m"] = len(edges)
    instance["i"] = tail
    instance["j"] = head
    instance["c"] = cost
    instance["b"] = b
    instance["idx_inf"] = inf_edges
    instance["inf"] = len(inf_edges)        
    instance["M"] = max(cost)*M # upperbound of beta, can be tuned for better performance
    
    # Solve
    # start_mzn= time.time()

    result = instance.solve(random_seed=seed, processes=1)
    # print("Minizinc interdiction time : ",time.time() - start_mzn,"s")
    # print(time.time() - start_mzn)
    # if budget==9: print(result) #if displ:
    # print(result,", bounds:[",min(result["pi"]),",",max(result["pi"]),"]")
    # if result.status=="UNBOUNDED":
    #     print("\n\n\n\n\nHIHIHIHIHIHI\n\n\n\n\n")


    interdicted_idxs = {edge_idx for edge_idx, sel in enumerate(result["x"]) if sel}
    edge_rem = [edges[i] for i in interdicted_idxs]

    edge_remaining = [edges[i] for i in range(len(edges)) if i not in interdicted_idxs]

    # if interdiction_type == "edge":
    #     # print(edge_remaining)
    #     for i, j, c in edge_rem:
    #         c_2=[cc for jj,ii,cc in edges if jj==j and ii==i][0]
    #         if (j, i, c_2) in edge_remaining:
    #             edge_remaining.remove((j, i, c_2))
    #         else:
    #             print("overflow or bad edge selection")

    # if displ:
    # if interdiction_type == "edge":
    #     print(
    #         "budget: ",
    #         k,
    #         "\nSelected edges to remove:",
    #         edge_rem,
    #         "\nMax removed?",
    #         len(edge_rem) == k,
    #         "\n",
    #     )
    

    if displ == 2:
        layout = show_weighted(n, edges, [nodes, S, T], layout=layout)
        show_weighted(n, edge_remaining, [nodes, S, T], layout=layout)


    return edge_remaining


if __name__ == "__main__":
    displ = 2
    sovl = ["cplex"]  #  "cbc", "highs", "coinbc", "coin-bc""cplex"
    for solver in sovl:
        print(solver)
        interdiction_minizinc(
            interdiction_type="edge", solver_name=solver, displ=displ, seed=42
        )  # np.random.randint(0,2**32-1)
