from random_graph import generate_graph,show, determine_T
from Simulation import cascade
from run_minizinc import interdiction_minizinc
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
budget=23 # The interdiction budget
intervention_step=[5] # The steps in the simulation where interdiction occur
time_range=30 # The number of simulation steps
repr=15
mode="SI" # Infection model, SIR or SI 
interdiction_type="edge" # Naive interdiction model, node or edge or edge mzn
display=False # Should the simulation display each step
infected_nodes= {6} # Which nodes are infected at start
Run_single=False # Should the simulation run once or multiple time
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

# --- Graph --------------------------------------------------------------------------------------------------------------------------------------------------
# 15
# edges= [(12, 7), (7, 12),(5, 4), (4, 5),(4, 6), (6, 4),(8, 0), (0, 8),(9, 5), (5, 9),(11, 2), (2, 11),(11, 5), (5, 11),(9, 14), (14, 9),(13, 11), (11, 13),(7, 10), (10, 7),(6, 14), (14, 6),(4, 2), (2, 4),(3, 0), (0, 3),(9, 7), (7, 9),(5, 12), (12, 5),(11, 1), (1, 11),(11, 7), (7, 11),(1, 2), (2, 1),(0, 13), (13, 0),(13, 10), (10, 13),(8, 7), (7, 8),(9, 6), (6, 9)]
# 30
# edges= [(23, 4), (6, 18), (21, 16), (16, 29), (18, 26), (22, 17), (5, 10), (12, 25), (0, 5), (19, 18), (9, 17), (5, 28), (18, 19), (28, 5), (17, 14), (4, 23), (24, 19), (25, 18), (10, 29), (27, 8), (22, 21), (11, 0), (14, 17), (23, 29), (1, 19), (26, 18), (20, 17), (14, 10), (17, 9), (9, 5), (9, 14), (24, 5), (26, 2), (10, 15), (8, 27), (1, 21), (25, 22), (7, 16), (2, 29), (5, 0), (5, 9), (22, 25), (13, 7), (2, 13), (24, 25), (0, 25), (25, 24), (16, 21), (20, 3), (29, 15), (23, 8), (20, 21), (21, 20), (12, 26), (4, 22), (11, 27), (5, 4), (21, 22), (12, 19), (8, 6), (13, 2), (0, 11), (16, 7), (19, 24), (29, 1), (2, 26), (6, 8), (20, 7), (22, 4), (29, 10), (15, 29), (14, 9), (29, 28), (18, 25), (19, 8), (10, 5), (17, 20), (10, 14), (25, 12), (28, 29), (15, 22), (19, 1), (17, 22), (16, 2), (8, 19), (19, 28), (21, 1), (29, 23), (7, 20), (19, 12), (22, 1), (29, 16), (7, 13), (4, 5), (25, 0), (5, 24), (8, 23), (2, 16), (15, 10), (18, 6), (1, 29), (22, 15), (27, 11), (3, 20), (28, 19), (29, 2), (26, 12), (1, 22)]
# 100
edges= [(23, 4), (4, 23), (67, 4), (4, 67), (69, 1), (1, 69), (15, 30), (30, 15), (80, 65), (65, 80), (73, 26), (26, 73), (8, 0), (0, 8), (61, 70), (70, 61), (71, 38), (38, 71), (63, 34), (34, 63), (96, 67), (67, 96), (73, 35), (35, 73), (92, 79), (79, 92), (85, 73), (73, 85), (21, 37), (37, 21), (28, 30), (30, 28), (46, 66), (66, 46), (86, 47), (47, 86), (67, 98), (98, 67), (85, 27), (27, 85), (17, 94), (94, 17), (55, 50), (50, 55), (6, 11), (11, 6), (69, 49), (49, 69), (6, 75), (75, 6), (99, 93), (93, 99), (2, 32), (32, 2), (11, 44), (44, 11), (47, 18), (18, 47), (91, 18), (18, 91), (8, 11), (11, 8), (23, 27), (27, 23), (6, 41), (41, 6), (52, 8), (8, 52), (30, 75), (75, 30), (82, 58), (58, 82), (66, 7), (7, 66), (67, 27), (27, 67), (74, 84), (84, 74), (11, 80), (80, 11), (38, 64), (64, 38), (80, 88), (88, 80), (64, 0), (0, 64), (81, 16), (16, 81), (39, 10), (10, 39), (0, 46), (46, 0), (55, 79), (79, 55), (15, 46), (46, 15), (37, 28), (28, 37), (5, 23), (23, 5), (84, 45), (45, 84), (48, 58), (58, 48), (61, 22), (22, 61), (35, 67), (67, 35), (77, 48), (48, 77), (61, 31), (31, 61), (24, 21), (21, 24), (70, 43), (43, 70), (71, 72), (72, 71), (35, 85), (85, 35), (76, 31), (31, 76), (13, 94), (94, 13), (83, 0), (0, 83), (63, 31), (31, 63), (60, 16), (16, 60), (11, 66), (66, 11), (98, 9), (9, 98), (15, 66), (66, 15), (32, 27), (27, 32), (25, 22), (22, 25), (19, 36), (36, 19), (76, 88), (88, 76), (87, 70), (70, 87), (18, 80), (80, 18), (0, 96), (96, 0), (83, 48), (48, 83), (76, 97), (97, 76), (84, 86), (86, 84), (46, 47), (47, 46), (3, 21), (21, 3), (14, 21), (21, 14), (68, 1), (1, 68), (23, 33), (33, 23), (83, 84), (84, 83), (66, 77), (77, 66), (43, 20), (20, 43), (34, 48), (48, 34), (81, 77), (77, 81), (53, 6), (6, 53), (85, 93), (93, 85), (22, 0), (0, 22), (91, 54), (54, 91), (22, 73), (73, 22), (39, 89), (89, 39), (15, 34), (34, 15), (93, 69), (69, 93), (84, 97), (97, 84), (5, 84), (84, 5), (69, 87), (87, 69), (44, 12), (12, 44), (40, 81), (81, 40), (18, 50), (50, 18), (27, 28), (28, 27), (7, 59), (59, 7), (10, 85), (85, 10), (48, 69), (69, 48), (94, 36), (36, 94), (72, 90), (90, 72), (94, 72), (72, 94), (95, 92), (92, 95), (19, 72), (72, 19), (67, 39), (39, 67), (91, 88), (88, 91), (19, 81), (81, 19), (29, 3), (3, 29), (31, 18), (18, 31), (40, 94), (94, 40), (44, 64), (64, 44), (65, 62), (62, 65), (25, 78), (78, 25), (57, 76), (76, 57), (74, 83), (83, 74), (46, 85), (85, 46), (98, 31), (31, 98), (0, 42), (42, 0), (49, 90), (90, 49), (87, 74), (74, 87), (36, 37), (37, 36), (92, 91), (91, 92), (90, 56), (56, 90), (71, 70), (70, 71), (24, 77), (77, 24), (51, 6), (6, 51), (59, 51), (51, 59), (29, 4), (4, 29)]
if new_graph:
    edges=generate_graph(n)

for edge in edges:
    (i,j) = edge
    if i>=n or j>=n:
        raise Exception(f"WARNING: node i:{i} or j:{j}, exceed number of nodes n:{n}")


#--- Run Simulation -------------------------------------------------------------------------------------------------------------------------------------------
if Run_single:
    t, new_edges, sets,_=cascade(t=time_range,n=n,spread=spread,budget=budget,graph_edges=edges,init_infected=infected_nodes,
                        mode=mode,budget_type=interdiction_type,intervention_step=intervention_step,displ=display)

    #--- Stats ------------------------------------
    show(n,new_edges,sets) #Display graph after simulation

    print("Sim mode: ", mode)
    print("Sim steps: ", t)
    print("Num suceptible: ", len(sets[0]))
    print("Num infected: ", len(sets[1]))
    print("Num safe: ", len(sets[2]))

# ---Display multiple independent runs of simulation with varying simulaiton steps and varying budgets----------------------------------------------------------
if not Run_single:
    data_average=[]
    time_run=[]
    head_start=intervention_step[0]

    updated_intervention_steps=[0]
    if len(intervention_step)>1:
        updated_intervention_steps=[i-head_start for i in intervention_step]
    
    
    layout=None
    if display:layout=show(n,edges,[{n for n in range(n)}, {i for i in infected_nodes}, {},{}])
    
    # Let the Simulations have a common start before interdiction
    t=time.time()
    _, _, sets,head_start_infected=cascade(t=head_start,n=n,spread=spread,budget=0,graph_edges=edges,init_infected=infected_nodes, 
                                           mode=mode,budget_type="",intervention_step={},displ=False)
    time_run.append(time.time()-t)

    new_infected_nodes=sets[1]
    start=head_start_infected

   #Determine T
    T=[]
    if interdiction_type=="edge mzn":
        T=determine_T(edges,sets)
        sets[3]=T

    count=0
    for edge in edges:
        (i,j)=edge
        count+=1 if i in new_infected_nodes and j not in new_infected_nodes else 0

    print(count)

    #Run second time
    if display:show(n,edges,sets,layout)
    for b in range(budget+1):
        print("\nBUDGET:", b)
        data=[]
    
        # if interdiction_type == "edge mzn":
        #    print(len(edges))
        #    edges_new,_= interdiction_minizinc(num_nodes=n,budget=b,infected_nodes=head_start_infected,critical_nodes=T,interdiction_type="edge",solver_name="highs",displ=False)
        #    print(len(edges_new))
        t=time.time()
        for _ in range(repr):
            _, _, _,infected_over_time=cascade(t=time_range-head_start,n=n,spread=spread,budget=b,graph_edges=edges,init_infected=new_infected_nodes, 
                                           mode=mode,budget_type=interdiction_type,intervention_step=updated_intervention_steps,displ=False,T=T)
            data.append(infected_over_time)
        time_run.append((time.time()-t)/repr)
        #Determine the average of the runs and store the 
        means_over_run=np.mean(data,axis=0)
        combined_start_mean_data=[*start,*means_over_run]
        data_average.append(combined_start_mean_data)
    
    #--- Stats ------------------------------------
    df = pd.DataFrame(
        data_average,
        index=[f"budget = {b}" for b in range(budget+1)],
        columns=range(0, time_range)
    )
    df.to_csv("data")
    

    #--- Heat map ------------------------------------
    plt.figure(figsize=(10, 5))
    sns.heatmap(
        df,
        cmap="magma",
        annot=True,
        fmt=".0f",
        vmin=0,vmax=n,
        linewidths=0.514
    )

    plt.xlabel("Time step")
    plt.ylabel("Budget")
    plt.title(f"Infected nodes with spread {spread} after varying {interdiction_type} interdiction budgets at {intervention_step}")
    plt.show()  

    #--- Plot graph ------------------------------------
    plt.figure()
    plt.plot(time_run,label="time s")
    plt.show()

        # for k in range(len(df)):
        #     fig, ax = plt.subplots(figsize=(10, 4))
        #     df.iloc[:k+1].T.plot(ax=ax, legend=True)
        #     ax.set_xlabel("simulaiton steps")
        #     ax.set_ylabel("Number of infected nodes")
        #     ax.set_title(f"Infection model with varying max simulation steps and budgets")
        #     ax.grid(True)
        #     plt.show()