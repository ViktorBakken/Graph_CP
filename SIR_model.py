from random_graph import generate_graph, show, determine_T, analyse_graph, determine_k_dangerous_edges
from run_minizinc import interdiction_minizinc
from Simulation import cascade
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import time


np.random.seed(42)
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#---Simulation parameters------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------
new_graph=False # Should the simulation generate a random graph of n nodes
n=100  # Number of nodes in graph
spread=0.2 # The chance an infection will spread through an edge
budget=60 # The interdiction budget
intervention_step={4} # The steps in the simulation where interdiction occur
early_stop=(True,10)
time_range=20 # The number of simulation steps
repr= 50
mode="SI" # Infection model, SIR or SI 
solver="coin-bc"
interdiction_type="edge mzn" # Naive interdiction model, node or edge or edge mzn or semi edge
verbose=0 # Should the simulation display each step
infected_nodes= {6} # Which nodes are infected at start
Run_single=False
new_start=False
Double_trouble=False
#-------------------------------------------------------------------------------------------------------------------------------------------------
# 15
# edges= [(12, 7), (7, 12),(5, 4), (4, 5),(4, 6), (6, 4),(8, 0), (0, 8),(9, 5), (5, 9),(11, 2), (2, 11),(11, 5), (5, 11),(9, 14), (14, 9),(13, 11), (11, 13),(7, 10), (10, 7),(6, 14), (14, 6),(4, 2), (2, 4),(3, 0), (0, 3),(9, 7), (7, 9),(5, 12), (12, 5),(11, 1), (1, 11),(11, 7), (7, 11),(1, 2), (2, 1),(0, 13), (13, 0),(13, 10), (10, 13),(8, 7), (7, 8),(9, 6), (6, 9)]
# 30
# edges= [(23, 4), (6, 18), (21, 16), (16, 29), (18, 26), (22, 17), (5, 10), (12, 25), (0, 5), (19, 18), (9, 17), (5, 28), (18, 19), (28, 5), (17, 14), (4, 23), (24, 19), (25, 18), (10, 29), (27, 8), (22, 21), (11, 0), (14, 17), (23, 29), (1, 19), (26, 18), (20, 17), (14, 10), (17, 9), (9, 5), (9, 14), (24, 5), (26, 2), (10, 15), (8, 27), (1, 21), (25, 22), (7, 16), (2, 29), (5, 0), (5, 9), (22, 25), (13, 7), (2, 13), (24, 25), (0, 25), (25, 24), (16, 21), (20, 3), (29, 15), (23, 8), (20, 21), (21, 20), (12, 26), (4, 22), (11, 27), (5, 4), (21, 22), (12, 19), (8, 6), (13, 2), (0, 11), (16, 7), (19, 24), (29, 1), (2, 26), (6, 8), (20, 7), (22, 4), (29, 10), (15, 29), (14, 9), (29, 28), (18, 25), (19, 8), (10, 5), (17, 20), (10, 14), (25, 12), (28, 29), (15, 22), (19, 1), (17, 22), (16, 2), (8, 19), (19, 28), (21, 1), (29, 23), (7, 20), (19, 12), (22, 1), (29, 16), (7, 13), (4, 5), (25, 0), (5, 24), (8, 23), (2, 16), (15, 10), (18, 6), (1, 29), (22, 15), (27, 11), (3, 20), (28, 19), (29, 2), (26, 12), (1, 22)]
# 100
edges= [(55, 57), (96, 95), (80, 1), (18, 17), (67, 68), (78, 77), (98, 55), (8, 9), (40, 41), (48, 54), (19, 18), (63, 61), (41, 42), (81, 78), (73, 74), (4, 2), (52, 51), (85, 57), (14, 15), (99, 1), (74, 75), (37, 35), (85, 84), (15, 16), (38, 18), (90, 19), (7, 12), (47, 48), (26, 25), (88, 86), (1, 99), (70, 68), (29, 27), (77, 76), (48, 49), (71, 51), (80, 81), (11, 9), (50, 86), (62, 60), (93, 38), (72, 15), (19, 98), (81, 82), (93, 47), (44, 42), (81, 91), (3, 1), (51, 50), (2, 45), (22, 23), (51, 59), (95, 93), (98, 0), (36, 34), (26, 11), (55, 56), (96, 94), (88, 90), (18, 16), (29, 31), (69, 67), (10, 8), (62, 64), (25, 24), (45, 2), (0, 98), (3, 5), (43, 41), (56, 20), (95, 97), (97, 48), (36, 38), (16, 69), (78, 53), (1, 80), (96, 98), (40, 8), (38, 93), (21, 22), (77, 75), (69, 71), (77, 84), (73, 41), (10, 12), (54, 55), (51, 49), (43, 45), (84, 83), (23, 76), (23, 85), (87, 88), (67, 39), (28, 29), (76, 78), (88, 89), (99, 98), (58, 57), (29, 30), (77, 79), (61, 62), (61, 71), (33, 0), (93, 14), (91, 81), (8, 74), (2, 3), (10, 16), (91, 90), (62, 63), (94, 95), (73, 72), (32, 31), (3, 4), (51, 53), (35, 36), (4, 76), (95, 96), (17, 15), (65, 64), (9, 11), (88, 66), (57, 60), (36, 37), (68, 69), (47, 46), (6, 5), (15, 72), (57, 87), (50, 48), (68, 96), (98, 97), (42, 44), (69, 70), (80, 79), (39, 38), (10, 11), (83, 81), (66, 10), (85, 23), (24, 22), (72, 71), (16, 18), (53, 67), (43, 44), (84, 82), (95, 82), (1, 38), (17, 19), (57, 55), (76, 68), (49, 51), (14, 93), (76, 77), (58, 56), (50, 52), (90, 88), (11, 51), (31, 29), (23, 25), (32, 3), (91, 89), (83, 85), (20, 56), (12, 52), (32, 30), (24, 26), (64, 62), (84, 77), (2, 96), (5, 3), (5, 12), (65, 63), (9, 10), (57, 59), (97, 95), (6, 4), (69, 42), (98, 96), (42, 43), (90, 92), (39, 37), (31, 33), (51, 11), (91, 93), (75, 76), (94, 89), (13, 12), (72, 70), (16, 17), (24, 30), (64, 66), (5, 7), (46, 45), (65, 67), (49, 50), (97, 99), (69, 28), (80, 37), (27, 31), (19, 27), (79, 78), (50, 51), (82, 83), (20, 19), (39, 41), (23, 24), (63, 97), (74, 8), (75, 62), (83, 84), (53, 52), (24, 25), (72, 74), (56, 57), (38, 36), (86, 85), (37, 80), (15, 43), (78, 81), (57, 58), (7, 39), (89, 90), (70, 86), (27, 26), (47, 93), (30, 31), (71, 69), (63, 65), (8, 40), (90, 91), (12, 10), (60, 59), (4, 6), (31, 32), (4, 24), (41, 73), (1, 0), (13, 11), (45, 43), (93, 92), (37, 39), (64, 65), (88, 32), (2, 90), (5, 6), (46, 44), (86, 80), (38, 40), (78, 76), (70, 72), (97, 98), (89, 94), (19, 17), (11, 13), (79, 77), (71, 73), (12, 5), (20, 18), (12, 14), (52, 50), (44, 46), (53, 33), (99, 0), (10, 62), (53, 51), (3, 32), (45, 47), (85, 83), (66, 88), (67, 53), (26, 24), (18, 20), (59, 58), (86, 84), (78, 80), (50, 9), (18, 38), (27, 25), (19, 21), (92, 91), (11, 26), (63, 64), (41, 36), (33, 32), (60, 58), (4, 5), (52, 54), (84, 34), (10, 66), (34, 33), (66, 65), (93, 91), (37, 38), (85, 87), (14, 45), (7, 6), (86, 70), (26, 28), (67, 66), (70, 71), (8, 7), (40, 39), (11, 12), (41, 40), (25, 23), (44, 45), (54, 86), (14, 13), (37, 24), (10, 70), (51, 71), (74, 73), (15, 14), (96, 97), (18, 19), (59, 57), (36, 64), (55, 86), (28, 69), (48, 47), (21, 39), (92, 90), (33, 31), (81, 80), (25, 27), (54, 72), (45, 14), (22, 21), (56, 32), (66, 64), (85, 86), (36, 41), (7, 5), (55, 54), (67, 65), (90, 30), (59, 61), (99, 97), (27, 1), (5, 62), (77, 78), (0, 2), (40, 38), (52, 12), (92, 94), (41, 39), (33, 35), (73, 71), (20, 74), (51, 52), (84, 86), (14, 12), (74, 72), (66, 68), (15, 13), (7, 9), (47, 45), (58, 60), (21, 20), (48, 46), (40, 42), (80, 78), (54, 53), (81, 79), (25, 26), (62, 75), (73, 75), (93, 53), (32, 34), (22, 20), (14, 16), (87, 86), (53, 93), (17, 18), (90, 2), (28, 27), (55, 53), (47, 49), (88, 87), (6, 8), (9, 50), (29, 28), (61, 60), (80, 82), (2, 1), (54, 48), (62, 61), (19, 90), (30, 90), (94, 93), (23, 51), (39, 77), (3, 2), (35, 34), (84, 85), (70, 10), (32, 56), (95, 94), (34, 84), (96, 68), (36, 35), (68, 67), (68, 76), (57, 85), (58, 59), (38, 90), (21, 19), (69, 68), (80, 86), (42, 69), (10, 9), (91, 92), (54, 52), (43, 15), (0, 81), (23, 46), (32, 33), (0, 99), (1, 27), (43, 42), (87, 85), (65, 66), (28, 26), (76, 75), (6, 7), (40, 18), (98, 99), (21, 23), (61, 59), (31, 27), (39, 40), (2, 0), (51, 23), (54, 56), (94, 92), (39, 67), (13, 15), (72, 73), (35, 33), (53, 78), (87, 89), (46, 48), (9, 8), (28, 30), (68, 66), (79, 81), (62, 10), (42, 41), (61, 63), (82, 95), (20, 22), (2, 4), (74, 20), (75, 74), (94, 96), (53, 55), (87, 57), (16, 15), (24, 37), (35, 37), (38, 39), (86, 88), (17, 16), (49, 48), (76, 74), (77, 39), (68, 70), (81, 0), (27, 29), (62, 5), (71, 72), (50, 49), (82, 81), (26, 91), (39, 21), (12, 13), (48, 97), (60, 62), (23, 22), (83, 82), (1, 3), (72, 54), (13, 14), (45, 46), (16, 10), (93, 95), (24, 23), (56, 55), (46, 47), (78, 79), (9, 7), (57, 56), (89, 88), (19, 20), (30, 29), (79, 80), (39, 7), (42, 40), (90, 89), (20, 21), (60, 57), (52, 53), (31, 30), (75, 73), (64, 36), (60, 84), (34, 32), (84, 60), (53, 54), (16, 14), (64, 63), (26, 27), (5, 4), (86, 87), (69, 16), (49, 47), (97, 96), (8, 6), (27, 19), (8, 15), (27, 28), (30, 24), (82, 80), (60, 61), (23, 21), (33, 53), (96, 2), (75, 77), (1, 2), (24, 4), (34, 36), (93, 94), (76, 23), (56, 54), (86, 55), (67, 69), (89, 87), (8, 10), (91, 26), (30, 28), (63, 62), (0, 33), (82, 84), (41, 43), (12, 7), (4, 3), (74, 76), (37, 36), (38, 1), (86, 50), (15, 8), (56, 58), (46, 23), (32, 88), (15, 17), (59, 51), (59, 60), (38, 37), (90, 38), (70, 69), (18, 40), (89, 91), (0, 1), (48, 50), (55, 98), (11, 10), (71, 61), (92, 93), (30, 32), (71, 70), (33, 34), (81, 83), (12, 11), (44, 43), (22, 24), (76, 4), (34, 35), (66, 67), (45, 44), (86, 54), (98, 19), (97, 63), (7, 8)]# 100 clustered
# edges = [(83,8),(8,83),(1, 3), (3, 1), (1, 4), (4, 1), (1, 5), (5, 1), (1, 9), (9, 1), (2, 3), (3, 2), (2, 4), (4, 2), (2, 6), (6, 2), (2, 7), (7, 2), (2, 10), (10, 2), (3, 6), (6, 3), (3, 10), (10, 3), (4, 7), (7, 4), (4, 8), (8, 4), (7, 10), (10, 7), (8, 9), (9, 8), (8, 10), (10, 8), (9, 10), (10, 9), (11, 12), (12, 11), (11, 13), (13, 11), (11, 14), (14, 11), (11, 18), (18, 11), (11, 19), (19, 11), (12, 15), (15, 12), (12, 17), (17, 12), (13, 18), (18, 13), (13, 19), (19, 13), (14, 15), (15, 14), (14, 16), (16, 14), (15, 19), (19, 15), (15, 20), (20, 15), (16, 18), (18, 16), (17, 19), (19, 17), (18, 20), (20, 18), (19, 20), (20, 19), (21, 22), (22, 21), (21, 26), (26, 21), (22, 24), (24, 22), (22, 28), (28, 22), (22, 30), (30, 22), (23, 28), (28, 23), (23, 30), (30, 23), (24, 27), (27, 24), (24, 30), (30, 24), (25, 30), (30, 25), (26, 28), (28, 26), (27, 30), (30, 27), (29, 30), (30, 29), (31, 33), (33, 31), (31, 36), (36, 31), (31, 39), (39, 31), (32, 34), (34, 32), (32, 37), (37, 32), (33, 36), (36, 33), (33, 37), (37, 33), (33, 40), (40, 33), (34, 35), (35, 34), (34, 36), (36, 34), (34, 38), (38, 34), (35, 36), (36, 35), (35, 37), (37, 35), (35, 39), (39, 35), (35, 40), (40, 35), (37, 39), (39, 37), (37, 40), (40, 37), (41, 45), (45, 41), (41, 49), (49, 41), (41, 50), (50, 41), (42, 45), (45, 42), (42, 46), (46, 42), (43, 44), (44, 43), (43, 50), (50, 43), (44, 46), (46, 44), (44, 48), (48, 44), (45, 46), (46, 45), (46, 50), (50, 46), (47, 48), (48, 47), (49, 50), (50, 49), (51, 55), (55, 51), (51, 57), (57, 51), (51, 58), (58, 51), (52, 53), (53, 52), (52, 54), (54, 52), (52, 56), (56, 52), (53, 56), (56, 53), (53, 58), (58, 53), (54, 55), (55, 54), (54, 58), (58, 54), (55, 57), (57, 55), (55, 58), (58, 55), (55, 59), (59, 55), (56, 60), (60, 56), (59, 60), (60, 59), (61, 63), (63, 61), (61, 66), (66, 61), (61, 67), (67, 61), (61, 68), (68, 61), (61, 70), (70, 61), (62, 65), (65, 62), (62, 67), (67, 62), (63, 64), (64, 63), (63, 66), (66, 63), (63, 67), (67, 63), (63, 70), (70, 63), (64, 68), (68, 64), (64, 69), (69, 64), (65, 70), (70, 65), (66, 67), (67, 66), (67, 70), (70, 67), (68, 69), (69, 68), (68, 70), (70, 68), (71, 75), (75, 71), (72, 73), (73, 72), (72, 80), (80, 72), (73, 75), (75, 73), (73, 78), (78, 73), (74, 77), (77, 74), (74, 78), (78, 74), (74, 79), (79, 74), (75, 78), (78, 75), (76, 80), (80, 76), (77, 79), (79, 77), (78, 79), (79, 78), (78, 80), (80, 78), (81, 88), (88, 81), (81, 90), (90, 81), (82, 89), (89, 82), (84, 86), (86, 84), (84, 87), (87, 84), (85, 90), (90, 85), (86, 87), (87, 86), (87, 90), (90, 87), (91, 92), (92, 91), (91, 93), (93, 91), (91, 0), (0, 91), (92, 93), (93, 92), (92, 94), (94, 92), (92, 95), (95, 92), (92, 98), (98, 92), (93, 94), (94, 93), (93, 97), (97, 93), (93, 99), (99, 93), (94, 96), (96, 94), (94, 98), (98, 94), (95, 96), (96, 95), (95, 97), (97, 95), (3, 18), (18, 3), (8, 15), (15, 8), (14, 25), (25, 14), (19, 28), (28, 19), (24, 35), (35, 24), (28, 32), (32, 28), (35, 44), (44, 35), (35, 46), (46, 35), (46, 59), (59, 46), (42, 53), (53, 42), (53, 64), (64, 53), (57, 63), (63, 57), (64, 72), (72, 64), (67, 77), (77, 67), (76, 89), (89, 76), (78, 87), (87, 78), (81, 94), (94, 81), (87, 97), (97, 87)]


if new_graph:
    edges=generate_graph(n)

for edge in edges:
    (i,j) = edge
    if i>=n or j>=n:
        raise Exception(f"WARNING: node i:{i} or j:{j}, exceed number of nodes n:{n}")


#--- Run Simulation -------------------------------------------------------------------------------------------------------------------------------------------
if Run_single:
    T=set()
    if interdiction_type=="edge mzn" or interdiction_type=="node mzn":
        T=determine_T(edges,[{n for n in range(n)},infected_nodes,{},{}])
    new_edges, sets,inf,Data=cascade(solver=solver,t=time_range,n=n,spread=spread,budget=budget,graph_edges=edges,init_infected=infected_nodes,
                        mode=mode,budget_type=interdiction_type,intervention_step=intervention_step,displ=verbose,T=T)
   
    show(n,new_edges,sets) #Display graph after simulation

    print("Sim mode: ", mode)
    print("Sim steps: ", time_range)
    print("Num suceptible: ", len(sets[0]))
    print("Num infected: ", len(sets[1]))
    print("Num safe: ", len(sets[2]))

# ---Display multiple independent runs of simulation with varying simulaiton steps and varying budgets----------------------------------------------------------
if not Run_single:
    if verbose>=2:analyse_graph(n,edges)  

    runs= n-5 if Double_trouble else 1
    avg_heat=[]
    b_50_avg=[]
    b_70_avg=[]
    b_90_avg=[]

    for run in range(runs):
        print("run ", run+1)

        if Double_trouble:
            early_stop=(True,run+5)
    
        hm=[]
        b_50=[]
        b_70=[]
        b_90=[]

        repeat = repr if Double_trouble or new_start else 1
        for rep in range(repeat):
            #print("rep ", rep+1)

            if new_start or Double_trouble: infected_nodes={int(np.random.randint(0,n))}
            print(infected_nodes)
            data_average=[]

            head_start=min(intervention_step)
            updated_intervention_steps={i-head_start for i in intervention_step}
            print(updated_intervention_steps)
            layout=None
            if verbose>=3:layout=show(n,edges,[{n for n in range(n)}, {}, {},{}])
            


            # Let the Simulations have a common start before interdiction
            _, sets,head_start_infected,end_time_step=cascade(t=head_start,n=n,spread=spread,budget=0,graph_edges=edges,init_infected=infected_nodes, 
                                                mode=mode,budget_type="",intervention_step={},displ=False,early_stop=early_stop)   
            if early_stop[0]:
                head_start=end_time_step
            new_infected=sets[1]
            start=head_start_infected

            #Determine T
            T=set()
            if interdiction_type=="edge mzn" or interdiction_type=="node mzn":
                T=determine_T(edges,sets)
                sets[3]=T


            count=0
            for edge in edges:
                (i,j)=edge
                count+=1 if i in new_infected and j not in new_infected else 0
            print("Infected edges: ",count)
            infected_percentage=len(sets[1])/n*100
            print("Infected percentage:",(infected_percentage))


            #Run second time
            if verbose>=2:show(n,edges,sets,layout)
            for b in range(count+1):
                # print("\nBUDGET:", b)
                data=[]
                t=time_range-head_start
                new_edges=edges.copy() if interdiction_type!= "edge mzn" else []
                # Interdict
                for step in updated_intervention_steps:
                    if verbose>=1:show(n,edges,sets,layout)

                    match interdiction_type:
                        case "edge mzn":
                            T=determine_T(edges,sets)
                            T=set(T)-new_infected
                            new_edges,_=interdiction_minizinc(solver_name=solver,num_nodes=n,budget=b,infected_nodes=new_infected,critical_nodes=T, graph_edges=edges,interdiction_type="edge", displ=verbose)
                            
                        case "edge" :
                            
                            # Determine infected edges
                            risk_edges=set()
                            for edge in edges:
                                (i,j)=edge
                                if i in new_infected and j not in new_infected :
                                    risk_edges.add(edge)
                                
                            
                            temp_risk_edges=list(risk_edges)
                            np.random.shuffle(temp_risk_edges)
                            
                            if(len(temp_risk_edges)>b):
                                rem_edges= temp_risk_edges[:b]
                            else:
                                rem_edges=risk_edges.copy()
                            # Remove the selected edges
                            for edge in rem_edges:
                                (i,j)=edge
                                new_edges.remove((i,j))
                                new_edges.remove((j,i))
                                
                        case "semi edge":
                            # Determine infected edges
                            risk_edges=set()
                            for edge in edges:
                                (i,j)=edge
                                if i in new_infected and j not in new_infected :
                                    risk_edges.add(edge)
                                    
                            if(len(risk_edges)>b):
                                rem_edges= determine_k_dangerous_edges(edges,risk_edges,sets,b)
                            else:
                                rem_edges=risk_edges.copy()
                            
                            # Remove the selected edges
                            for edge in rem_edges:
                                (i,j)=edge
                                new_edges.remove((i,j))
                                new_edges.remove((j,i))

                    if verbose>=1:show(n,new_edges,sets,layout)
         
                    for _ in range(repr):
                        _, _ ,infected_over_time,_=cascade(solver=solver,t=t-step,n=n,spread=spread,budget=0,graph_edges=new_edges,init_infected=new_infected, 
                                                    mode=mode,budget_type="",intervention_step=None,displ=verbose,T=T,layout=layout)
                        data.append(infected_over_time)

                
                #Determine the average of the runs and store the 
                means_over_run=np.mean(data,axis=0)
                data_average.append([*start,*means_over_run])              
              
                
            # Pad remaining budgets with the last result (fully quarantined, no change)
            last = data_average[-1]
            data_average.extend([last] * (budget - count))  # fills up to budget+1 rows
            # ADD THIS: enforce fixed row count AND fixed row length
            target_rows = budget + 1
            target_cols = time_range  # your fixed time axis
            # Truncate or pad rows
            data_average = data_average[:target_rows]
            while len(data_average) < target_rows:
                data_average.append(data_average[-1])

            # Truncate or pad each row to fixed length
            data_average = [
                (row + [row[-1]] * target_cols)[:target_cols]
                for row in data_average
            ]
            data_average=np.array(data_average)
            
            #--- Stats ------------------------------------
            hm.append(data_average)
            num_infected = data_average[:,-1]
            reduction=1-num_infected/num_infected[0]
            len_b_50=len(b_50)
            len_b_70=len(b_70)
            len_b_90=len(b_90)
            for b, r in enumerate(reduction):
                if len(b_50)==len_b_50 and r>=0.5:
                    b_50.append(b)
                elif len(b_70)==len_b_70 and r>=0.7:
                    b_70.append(b)
                elif len(b_90)==len_b_90 and r>=0.9:
                    b_90.append(b)
        
        avg_heat.append(np.mean(hm,axis=0))
        b_50_avg.append(np.mean(b_50,axis=0))
        b_70_avg.append(np.mean(b_70,axis=0))
        b_90_avg.append(np.mean(b_90,axis=0))
    #--- Plot graph ------------------------------------
    # if new_start and not Double_trouble:
    print(b_50_avg)
    print("b 50: ", np.mean(b_50_avg,axis=0),"\nb 70: ", np.mean(b_70_avg,axis=0),"\nb 90: ", np.mean(b_90_avg,axis=0),)
    
    mean= np.mean(avg_heat,axis=0)
    print("hi")
    num_infected = mean[:,-1]
    final_outbreak=1-(num_infected/num_infected [0])
    exp=np.sum(mean,axis=1,dtype= float)
    exp_budget=1-(exp/exp[0])
    print("exp_budget=",exp_budget.tolist())
    print("final_outbreak=",final_outbreak.tolist())
    plt.plot(exp_budget, marker="o", linewidth=2)
    plt.xlabel("Budget")
    plt.ylabel("ExposureReduction")
    plt.title(f"ExposureReduction over varying {interdiction_type} interdiction budgets at {infected_percentage}% infection at interdiction")
    plt.grid(True, alpha=0.3)
                
    
    
    df = pd.DataFrame(
            mean,
            index=[f"budget = {b}" for b in range(budget+1)],
            columns=range(0, time_range)
            )
    df.to_csv(f"data_{interdiction_type}")
    
    # Heat map
    plt.figure(figsize=(10, 5))
    sns.heatmap(
        df,
        cmap="magma",
        annot=False,
        fmt=".0f",
        vmin=0,vmax=n,
        linewidths=0.514,
    )
    plt.xlabel("Time step")
    plt.ylabel("Budget")
    plt.title(f"Infected nodes with spread {spread} after varying {interdiction_type} interdiction budgets at {intervention_step}")
    plt.show()  
        
