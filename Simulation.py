from random_graph import show
from run_minizinc import interdiction_minizinc
import numpy as np
import time

def cascade(t=2, n=100,spread=0.2,budget=2,graph_edges=None, init_infected=None, mode="SI",budget_type="edge",intervention_step=None,displ=False,T=None, layout=None,solver="cbc"):
    # Initialization
    if graph_edges is None:
        edges= [(23, 4), (4, 23), (67, 4), (4, 67), (69, 1), (1, 69), (15, 30), (30, 15), (80, 65), (65, 80), (73, 26), (26, 73), (8, 0), (0, 8), (61, 70), (70, 61), (71, 38), (38, 71), (63, 34), (34, 63), (96, 67), (67, 96), (73, 35), (35, 73), (92, 79), (79, 92), (85, 73), (73, 85), (21, 37), (37, 21), (28, 30), (30, 28), (46, 66), (66, 46), (86, 47), (47, 86), (67, 98), (98, 67), (85, 27), (27, 85), (17, 94), (94, 17), (55, 50), (50, 55), (6, 11), (11, 6), (69, 49), (49, 69), (6, 75), (75, 6), (99, 93), (93, 99), (2, 32), (32, 2), (11, 44), (44, 11), (47, 18), (18, 47), (91, 18), (18, 91), (8, 11), (11, 8), (23, 27), (27, 23), (6, 41), (41, 6), (52, 8), (8, 52), (30, 75), (75, 30), (82, 58), (58, 82), (66, 7), (7, 66), (67, 27), (27, 67), (74, 84), (84, 74), (11, 80), (80, 11), (38, 64), (64, 38), (80, 88), (88, 80), (64, 0), (0, 64), (81, 16), (16, 81), (39, 10), (10, 39), (0, 46), (46, 0), (55, 79), (79, 55), (15, 46), (46, 15), (37, 28), (28, 37), (5, 23), (23, 5), (84, 45), (45, 84), (48, 58), (58, 48), (61, 22), (22, 61), (35, 67), (67, 35), (77, 48), (48, 77), (61, 31), (31, 61), (24, 21), (21, 24), (70, 43), (43, 70), (71, 72), (72, 71), (35, 85), (85, 35), (76, 31), (31, 76), (13, 94), (94, 13), (83, 0), (0, 83), (63, 31), (31, 63), (60, 16), (16, 60), (11, 66), (66, 11), (98, 9), (9, 98), (15, 66), (66, 15), (32, 27), (27, 32), (25, 22), (22, 25), (19, 36), (36, 19), (76, 88), (88, 76), (87, 70), (70, 87), (18, 80), (80, 18), (0, 96), (96, 0), (83, 48), (48, 83), (76, 97), (97, 76), (84, 86), (86, 84), (46, 47), (47, 46), (3, 21), (21, 3), (14, 21), (21, 14), (68, 1), (1, 68), (23, 33), (33, 23), (83, 84), (84, 83), (66, 77), (77, 66), (43, 20), (20, 43), (34, 48), (48, 34), (81, 77), (77, 81), (53, 6), (6, 53), (85, 93), (93, 85), (22, 0), (0, 22), (91, 54), (54, 91), (22, 73), (73, 22), (39, 89), (89, 39), (15, 34), (34, 15), (93, 69), (69, 93), (84, 97), (97, 84), (5, 84), (84, 5), (69, 87), (87, 69), (44, 12), (12, 44), (40, 81), (81, 40), (18, 50), (50, 18), (27, 28), (28, 27), (7, 59), (59, 7), (10, 85), (85, 10), (48, 69), (69, 48), (94, 36), (36, 94), (72, 90), (90, 72), (94, 72), (72, 94), (95, 92), (92, 95), (19, 72), (72, 19), (67, 39), (39, 67), (91, 88), (88, 91), (19, 81), (81, 19), (29, 3), (3, 29), (31, 18), (18, 31), (40, 94), (94, 40), (44, 64), (64, 44), (65, 62), (62, 65), (25, 78), (78, 25), (57, 76), (76, 57), (74, 83), (83, 74), (46, 85), (85, 46), (98, 31), (31, 98), (0, 42), (42, 0), (49, 90), (90, 49), (87, 74), (74, 87), (36, 37), (37, 36), (92, 91), (91, 92), (90, 56), (56, 90), (71, 70), (70, 71), (24, 77), (77, 24), (51, 6), (6, 51), (59, 51), (51, 59), (29, 4), (4, 29)]
    
    else:
        edges=graph_edges.copy()
    if init_infected is None:
        infected = {0, 66, 34, 7, 8, 11, 46, 15, 80, 47, 52, 85}
    else:
        infected=init_infected.copy()

    if intervention_step is None:
        intervention_step={0}
    else:
        intervention_step=set(intervention_step)

    suceptible={i for i in range(n)}
    for inf in infected:
        suceptible.remove(inf)

    safe=set()
    removed=set()
    infected_over_time=[]
    risk_edges=set()    

    #-------------------------------
    #---Spread model----------------
    #-------------------------------
    for time in range(t):
        infected_over_time.append(len(infected))
        if len(risk_edges)>0 or time==0:
            if displ:show(n=n,edges=edges,sets=[suceptible,infected,safe,removed],layout=layout)           

            # Interdiction mode: node
            if time in intervention_step and budget>0:
                match budget_type:
                    case "node":
                        if len(infected)> budget:
                            temp_infected=list(infected)
                            np.random.shuffle(temp_infected)
                            rem_nodes= set(temp_infected[:budget])
                            infected=set(temp_infected[budget:])
                        else:
                            rem_nodes=infected.copy()
                            infected.clear()
                        for node in rem_nodes:
                            removed.add(node)
                    case "edge mzn":
                        edges,_=interdiction_minizinc(solver_name=solver,num_nodes=n,budget=budget,infected_nodes=infected,critical_nodes=T, graph_edges=edges,interdiction_type="edge", displ=displ)                      
                        
            # Determine which edges are adjacent to infected nodes
            risk_edges.clear()
            for edge in edges:
                (i,j)=edge
                if i in infected and j in suceptible :
                    risk_edges.add(edge)
                        
            # Interdiction mode: edges
            if time in intervention_step and budget>0:
                match budget_type:
                    case "edge" :
                        temp_risk_edges=list(risk_edges)
                        np.random.shuffle(temp_risk_edges)
                        if(len(temp_risk_edges)>budget):
                            rem_edges= temp_risk_edges[:budget]
                            risk_edges=set(temp_risk_edges[budget:])
                        else:
                            rem_edges=risk_edges.copy()
                            risk_edges.clear()
                        for edge in rem_edges:
                            (i,j)=edge
                            edges.remove((i,j))
                            edges.remove((j,i))

            
            
            #Infection step
            if(mode=="SIR"):
                for inf_edge in risk_edges:
                    (i, j) = inf_edge
                    if j in suceptible:
                        if np.random.uniform(0,1)<=spread:
                            infected.add(j)
                        else:
                            safe.add(j)
                        suceptible.discard(j)

            if(mode=="SI"):
                for inf_edge in risk_edges:
                    (i, j) = inf_edge
                    if j in suceptible:
                        if np.random.uniform(0,1)<=spread:
                            infected.add(j)                   
                            suceptible.discard(j)
            
    return t, edges, [suceptible,infected,safe,removed], infected_over_time


def fix_edge(edges):
    fixed_edges=[]
    # edges=edges
    while len(edges)>0:
        edge=edges[0]
        (i,j)=edge
        fixed_edges.append(edge)
        fixed_edges.append((j,i))
        edges.remove(edge)
        edges.remove((j,i))
    return fixed_edges

if __name__=="__main__":
    displ=False
    sovl=["gurobi","highs","coinbc","coin-bc"]
    for solve in sovl:
        print(solve)
        start= time.time()
        cascade(solver =solve,displ=displ,budget_type="edge mzn")
        print(solve," run time: ",time.time() - start,"s\n")



    # t, edges, sets, infected_over_time =cascade(budget_type="edge mzn", displ=True)
#--- Stats ------------------------------------
    # show(3,edges,sets) #Display graph after simulation

    # print("Sim mode: ", "SI")
    # print("Sim steps: ", t)
    # print("Num suceptible: ", len(sets[0]))
    # print("Num infected: ", len(sets[1]))
    # print("Num safe: ", len(sets[2]))