from minizinc import Instance, Model, Solver
from random_graph import show
import matplotlib.pyplot as plt
import numpy as np
import time

def interdiction_minizinc(num_nodes=100,budget=4,infected_nodes=None,critical_nodes=None,graph_edges=None, interdiction_type="edge",solver_name="highs", displ=0,layout=None):
    k=budget

    n=num_nodes
    if infected_nodes==None:
        #15
        # S={11,5,6,7}
        #100
        S={0, 66, 34, 7, 8, 11, 46, 15, 80, 47, 52, 85}
    else:
        S=infected_nodes.copy()
    if graph_edges==None:
        # n=15
        # edges= [(12, 7), (7, 12),(5, 4), (4, 5),(4, 6), (6, 4),(8, 0), (0, 8),(9, 5), (5, 9),(11, 2), (2, 11),(11, 5), (5, 11),(9, 14), (14, 9),(13, 11), (11, 13),(7, 10), (10, 7),(6, 14), (14, 6),(4, 2), (2, 4),(3, 0), (0, 3),(9, 7), (7, 9),(5, 12), (12, 5),(11, 1), (1, 11),(11, 7), (7, 11),(1, 2), (2, 1),(0, 13), (13, 0),(13, 10), (10, 13),(8, 7), (7, 8),(9, 6), (6, 9)]
        # 100
        edges= [(23, 4), (4, 23), (67, 4), (4, 67), (69, 1), (1, 69), (15, 30), (30, 15), (80, 65), (65, 80), (73, 26), (26, 73), (8, 0), (0, 8), (61, 70), (70, 61), (71, 38), (38, 71), (63, 34), (34, 63), (96, 67), (67, 96), (73, 35), (35, 73), (92, 79), (79, 92), (85, 73), (73, 85), (21, 37), (37, 21), (28, 30), (30, 28), (46, 66), (66, 46), (86, 47), (47, 86), (67, 98), (98, 67), (85, 27), (27, 85), (17, 94), (94, 17), (55, 50), (50, 55), (6, 11), (11, 6), (69, 49), (49, 69), (6, 75), (75, 6), (99, 93), (93, 99), (2, 32), (32, 2), (11, 44), (44, 11), (47, 18), (18, 47), (91, 18), (18, 91), (8, 11), (11, 8), (23, 27), (27, 23), (6, 41), (41, 6), (52, 8), (8, 52), (30, 75), (75, 30), (82, 58), (58, 82), (66, 7), (7, 66), (67, 27), (27, 67), (74, 84), (84, 74), (11, 80), (80, 11), (38, 64), (64, 38), (80, 88), (88, 80), (64, 0), (0, 64), (81, 16), (16, 81), (39, 10), (10, 39), (0, 46), (46, 0), (55, 79), (79, 55), (15, 46), (46, 15), (37, 28), (28, 37), (5, 23), (23, 5), (84, 45), (45, 84), (48, 58), (58, 48), (61, 22), (22, 61), (35, 67), (67, 35), (77, 48), (48, 77), (61, 31), (31, 61), (24, 21), (21, 24), (70, 43), (43, 70), (71, 72), (72, 71), (35, 85), (85, 35), (76, 31), (31, 76), (13, 94), (94, 13), (83, 0), (0, 83), (63, 31), (31, 63), (60, 16), (16, 60), (11, 66), (66, 11), (98, 9), (9, 98), (15, 66), (66, 15), (32, 27), (27, 32), (25, 22), (22, 25), (19, 36), (36, 19), (76, 88), (88, 76), (87, 70), (70, 87), (18, 80), (80, 18), (0, 96), (96, 0), (83, 48), (48, 83), (76, 97), (97, 76), (84, 86), (86, 84), (46, 47), (47, 46), (3, 21), (21, 3), (14, 21), (21, 14), (68, 1), (1, 68), (23, 33), (33, 23), (83, 84), (84, 83), (66, 77), (77, 66), (43, 20), (20, 43), (34, 48), (48, 34), (81, 77), (77, 81), (53, 6), (6, 53), (85, 93), (93, 85), (22, 0), (0, 22), (91, 54), (54, 91), (22, 73), (73, 22), (39, 89), (89, 39), (15, 34), (34, 15), (93, 69), (69, 93), (84, 97), (97, 84), (5, 84), (84, 5), (69, 87), (87, 69), (44, 12), (12, 44), (40, 81), (81, 40), (18, 50), (50, 18), (27, 28), (28, 27), (7, 59), (59, 7), (10, 85), (85, 10), (48, 69), (69, 48), (94, 36), (36, 94), (72, 90), (90, 72), (94, 72), (72, 94), (95, 92), (92, 95), (19, 72), (72, 19), (67, 39), (39, 67), (91, 88), (88, 91), (19, 81), (81, 19), (29, 3), (3, 29), (31, 18), (18, 31), (40, 94), (94, 40), (44, 64), (64, 44), (65, 62), (62, 65), (25, 78), (78, 25), (57, 76), (76, 57), (74, 83), (83, 74), (46, 85), (85, 46), (98, 31), (31, 98), (0, 42), (42, 0), (49, 90), (90, 49), (87, 74), (74, 87), (36, 37), (37, 36), (92, 91), (91, 92), (90, 56), (56, 90), (71, 70), (70, 71), (24, 77), (77, 24), (51, 6), (6, 51), (59, 51), (51, 59), (29, 4), (4, 29)]
    else:
        edges=graph_edges.copy()
    if critical_nodes==None: 
        #15
        # T={0,1}
        #100
        T={1, 6, 16,21, 22, 23, 25, 27, 30, 73, 76, 77, 81, 84, 90, 91, 92, 93, 94, 98}
    else:
        T=critical_nodes.copy()
    nodes=[i for i in range(n)]
    tail, head = map(list, zip(*edges))
    
    b=[0]*n
    for i in range(n):
        if i in S:
            b[i]=1
        elif i in T:
            b[i]=-1

    
    # Load a solver
    solver = Solver.lookup(solver_name)

    # Load the model
    model_choice="Solver_node.mzn" if interdiction_type=="node" else "Solver.mzn"
    # Create an instance
    instance = Instance(solver, Model(model_choice))


    # Pass data from Python to MiniZinc
    instance["K"] = k
    instance["n"] = len(nodes)
    instance["m"] = len(edges)
    instance["i"] = tail
    instance["j"] = head
    instance["c"] = [1 for _ in range(len(edges))]
    instance["b"] = b

    # Solve
    start_mzn= time.time()
    rand_seed=np.random.randint(0,100)
    result = instance.solve(random_seed=rand_seed)
    # print("Minizinc interdiction time : ",time.time() - start_mzn,"s")
    # print(time.time() - start_mzn)
    # print(result) #if displ:
    # print(result,", bounds:[",min(result["pi"]),",",max(result["pi"]),"]")
    # if result.status=="UNBOUNDED":
    #     print("\n\n\n\n\nHIHIHIHIHIHI\n\n\n\n\n")
    node_removed = {node for node, selected in zip(nodes, result["z"]) if selected} 
    edge_remaining = {edge for edge, selected in zip(edges, result["x"]) if not selected}
    edge_rem = {edge for edge, selected in zip(edges, result["x"]) if selected}

    if interdiction_type=="edge":
        # print(edge_remaining)
        for edge in edge_rem:
            (i,j)=edge
            if((j,i) in edge_remaining):
                edge_remaining.remove((j,i))
            else:
                print("overflow or bad edge selection")

    if interdiction_type=="node":
        edge_remaining=edges.copy()
        for edge in edges:
            (i,j)=edge
            if(i in node_removed and (i,j) in edge_remaining):
                edge_remaining.remove((i,j))
                edge_remaining.remove((j,i))




    # if displ:
    # if interdiction_type=="edge":print("Selected edges to remove:",edge_rem,"\nMax removed?", len(edge_rem)==k,"\n")
    # if interdiction_type=="node":print("Selected nodes to remove:",node_removed)

    if displ>=2:
        layout=show(n,edges,[nodes, S,{},T],layout=layout)
        if interdiction_type=="edge":
            show(n,edge_remaining,[nodes, S,{},T],layout=layout)
        else:
            show(n,edge_remaining,[nodes, S,{},T],layout=layout)


    return edge_remaining, node_removed


if __name__=="__main__":
    displ=0
    sovl=["cbc","highs","coinbc","coin-bc"]
    for solver in sovl:
        print(solver)
        start= time.time()
        interdiction_minizinc(interdiction_type="node",solver_name=solver,displ=displ)
        print(solver," run time: ",time.time() - start,"s\n")

