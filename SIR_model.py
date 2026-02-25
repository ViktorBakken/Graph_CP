from random_graph import generate_graph,show
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

np.random.seed(42)

#Spread simulation
def cascade(t=100, n=2,spread=0.15,budget=0,graph_edges=None, init_infected=None, mode="SIR",budget_type="edge",intervention_step=None,displ=False):
    # Initialization
    if graph_edges is None:
        edges = {(0, 1), (1, 0)}
    else:
        edges=graph_edges.copy()
        
    if init_infected is None:
        infected = {0}
    else:
        infected=init_infected.copy()

    if intervention_step is None:
        intervention_step={1}
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
            if displ:show(n=n,edges=edges,sets=[suceptible,infected,safe,removed])           

            # Interdiction mode: node
            if budget_type=="node" and time in intervention_step:
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
                
            # Determine which edges are adjacent to infected nodes

            risk_edges.clear()
            for edge in edges:
                (i,j)=edge
                if i in infected and j in suceptible :
                    risk_edges.add(edge)

            # Interdiction mode: edges
            if budget_type=="edge" and time in intervention_step:
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
                    edges.discard((i,j))
                    edges.discard((j,i))
            
            
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


#------------------------------------------------------------------------------------------------------------------------------------------------------------
#---Simulation parameters------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------
new_graph=False # Should the simulation generate a random graph of n nodes
n=100  # Number of nodes in graph
spread=0.2 # The chance an infection will spread through an edge
budget=17 # The interdiction budget
intervention_step=[4,6] # The simulation steps where the interdiction will happen
time_range=30 # The number of simulation steps
mode="SI" # Infection model, SIR or SI 
interdiction_type="edge" # Naive interdiction model, node or edge
display=True # Should the simulation display each step
infected_nodes= {11} # Which nodes are infected at start
Run_single=False # Should the simulation run once or multiple time
#-------------------------------------------------------------------------------------------------------------------------------------------------------------

# --- Graph --------------------------------------------------------------------------------------------------------------------------------------------------
# 15
# edges= {(12, 7), (5, 4), (4, 6), (8, 0), (9, 5), (11, 2), (11, 5), (9, 14), (0, 8), (2, 11), (13, 11), (7, 10), (6, 14), (4, 2), (3, 0), (14, 6), (4, 5), (14, 9), (5, 9), (9, 7), (5, 12), (11, 1), (11, 7), (2, 4), (1, 2), (2, 1), (1, 11), (0, 13), (11, 13), (13, 10), (6, 4), (7, 9), (7, 12), (12, 5), (5, 11), (8, 7), (9, 6), (0, 3), (10, 7), (13, 0), (10, 13), (7, 11), (6, 9), (7, 8)}
# 30
# edges= {(23, 4), (6, 18), (21, 16), (16, 29), (18, 26), (22, 17), (5, 10), (12, 25), (0, 5), (19, 18), (9, 17), (5, 28), (18, 19), (28, 5), (17, 14), (4, 23), (24, 19), (25, 18), (10, 29), (27, 8), (22, 21), (11, 0), (14, 17), (23, 29), (1, 19), (26, 18), (20, 17), (14, 10), (17, 9), (9, 5), (9, 14), (24, 5), (26, 2), (10, 15), (8, 27), (1, 21), (25, 22), (7, 16), (2, 29), (5, 0), (5, 9), (22, 25), (13, 7), (2, 13), (24, 25), (0, 25), (25, 24), (16, 21), (20, 3), (29, 15), (23, 8), (20, 21), (21, 20), (12, 26), (4, 22), (11, 27), (5, 4), (21, 22), (12, 19), (8, 6), (13, 2), (0, 11), (16, 7), (19, 24), (29, 1), (2, 26), (6, 8), (20, 7), (22, 4), (29, 10), (15, 29), (14, 9), (29, 28), (18, 25), (19, 8), (10, 5), (17, 20), (10, 14), (25, 12), (28, 29), (15, 22), (19, 1), (17, 22), (16, 2), (8, 19), (19, 28), (21, 1), (29, 23), (7, 20), (19, 12), (22, 1), (29, 16), (7, 13), (4, 5), (25, 0), (5, 24), (8, 23), (2, 16), (15, 10), (18, 6), (1, 29), (22, 15), (27, 11), (3, 20), (28, 19), (29, 2), (26, 12), (1, 22)}
# 100
edges= {(23, 4), (67, 4), (69, 1), (15, 30), (80, 65), (73, 26), (8, 0), (61, 70), (71, 38), (63, 34), (96, 67), (73, 35), (92, 79), (85, 73), (21, 37), (28, 30), (46, 66), (86, 47), (67, 98), (85, 27), (17, 94), (38, 71), (55, 50), (6, 11), (69, 49), (6, 75), (99, 93), (2, 32), (11, 44), (47, 18), (91, 18), (8, 11), (23, 27), (6, 41), (52, 8), (4, 23), (30, 75), (82, 58), (66, 7), (67, 27), (74, 84), (11, 80), (38, 64), (80, 88), (64, 0), (81, 16), (39, 10), (79, 92), (73, 85), (0, 46), (55, 79), (66, 46), (0, 64), (15, 46), (37, 28), (5, 23), (84, 45), (48, 58), (61, 22), (35, 67), (77, 48), (61, 31), (75, 30), (26, 73), (24, 21), (70, 43), (71, 72), (35, 85), (76, 31), (16, 81), (13, 94), (70, 61), (8, 52), (83, 0), (63, 31), (37, 21), (60, 16), (11, 66), (66, 11), (98, 9), (15, 66), (32, 27), (25, 22), (19, 36), (76, 88), (87, 70), (18, 80), (0, 96), (83, 48), (76, 97), (84, 86), (46, 47), (22, 25), (3, 21), (14, 21), (32, 2), (68, 1), (23, 33), (83, 84), (66, 77), (43, 20), (1, 69), (34, 48), (81, 77), (53, 6), (85, 93), (22, 0), (91, 54), (48, 83), (31, 76), (22, 73), (39, 89), (97, 76), (15, 34), (93, 69), (94, 13), (84, 97), (5, 84), (69, 87), (67, 35), (79, 55), (44, 12), (16, 60), (35, 73), (88, 76), (7, 66), (46, 15), (93, 99), (77, 66), (40, 81), (96, 0), (43, 70), (64, 38), (47, 86), (30, 15), (18, 50), (27, 28), (28, 27), (7, 59), (33, 23), (10, 85), (48, 69), (94, 36), (10, 39), (84, 74), (84, 83), (21, 24), (72, 90), (94, 72), (80, 18), (27, 67), (95, 92), (58, 82), (19, 72), (67, 39), (27, 85), (89, 39), (91, 88), (19, 81), (93, 85), (88, 80), (0, 22), (29, 3), (85, 35), (22, 61), (34, 63), (58, 48), (69, 48), (23, 5), (9, 98), (31, 18), (72, 19), (48, 34), (80, 11), (40, 94), (18, 91), (75, 6), (81, 40), (45, 84), (44, 64), (65, 62), (85, 10), (11, 6), (27, 23), (1, 68), (67, 96), (27, 32), (30, 28), (66, 15), (25, 78), (12, 44), (57, 76), (65, 80), (74, 83), (84, 5), (88, 91), (46, 85), (94, 40), (98, 31), (0, 42), (85, 46), (49, 90), (50, 55), (87, 74), (4, 67), (86, 84), (77, 81), (97, 84), (72, 94), (41, 6), (78, 25), (36, 19), (50, 18), (18, 47), (98, 67), (44, 11), (64, 44), (0, 8), (11, 8), (36, 37), (90, 72), (37, 36), (92, 91), (91, 92), (47, 46), (62, 65), (21, 3), (73, 22), (18, 31), (34, 15), (76, 57), (54, 91), (90, 56), (70, 87), (94, 17), (31, 98), (20, 43), (36, 94), (6, 53), (71, 70), (0, 83), (74, 87), (31, 61), (48, 77), (24, 77), (72, 71), (81, 19), (21, 14), (87, 69), (59, 7), (70, 71), (42, 0), (90, 49), (77, 24), (56, 90), (83, 74), (46, 0), (3, 29), (69, 93), (28, 37), (92, 95), (39, 67), (49, 69), (31, 63),(51,6),(6,51),(59,51),(51,59),(29,4),(4,29)}
if new_graph:
    edges=generate_graph(n)

#--- Run Simulation -------------------------------------------------------------------------------------------------------------------------------------------
if Run_single:
    t, new_edges, sets,_=cascade(t=time_range,n=n,spread=spread,budget=budget,graph_edges=edges,init_infected=infected_nodes,
                        mode=mode,budget_type=interdiction_type,intervention_step=intervention_step,displ=display)
    show(n,new_edges,sets) #Display graph after simulation

    #--- Stats -------------------------------------------------------------------------------------------------------------------------------------------------
    print("Sim mode: ", mode)
    print("Sim steps: ", t)
    print("Num suceptible: ", len(sets[0]))
    print("Num infected: ", len(sets[1]))
    print("Num safe: ", len(sets[2]))

# ---Display multiple independent runs of simulation with varying simulaiton steps and varying budgets----------------------------------------------------------
if not Run_single:
    data_average=[]
    head_start=intervention_step[0]
    print("head start: ", head_start)

    updated_intervention_steps=[0]
    if len(intervention_step)>1:
        updated_intervention_steps=[i-head_start for i in intervention_step]
    print("New intervention steps: ", updated_intervention_steps)

    show(n,edges,[{n for n in range(n)}, {i for i in infected_nodes}, {},{}])
    
    # Let the Simulations have a common start before interdiction
    _, _, sets,head_start_infected=cascade(t=head_start,n=n,spread=spread,budget=0,graph_edges=edges,init_infected={11}, 
                                           mode=mode,budget_type=interdiction_type,intervention_step=intervention_step,displ=False)
    new_infected_nodes=sets[1]
    start=head_start_infected
    show(n,edges,sets)

    for b in range(budget+1):
        data=[]
        for _ in range(30):
            _, _, _,infected_over_time=cascade(t=time_range-head_start,n=n,spread=spread,budget=b,graph_edges=edges,init_infected=new_infected_nodes, 
                                           mode=mode,budget_type=interdiction_type,intervention_step=updated_intervention_steps,displ=False)
            
            data.append(infected_over_time)
        #Determine the average of the runs and store the 
        means_over_run=np.mean(data,axis=0)
        combined_start_mean_data=[*start,*means_over_run]
        data_average.append(combined_start_mean_data)
    
    # Store results
    df = pd.DataFrame(
        data_average,
        index=[f"budget = {b}" for b in range(budget+1)],
        columns=range(0, time_range)
    )

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
    plt.title(f"Infected nodes after varying {interdiction_type} interdiction budgets at {intervention_step}")
    plt.show()  

    # Plot the runs
    if display:
        for k in range(len(df)):
            fig, ax = plt.subplots(figsize=(10, 4))
            df.iloc[:k+1].T.plot(ax=ax, legend=True)
            ax.set_xlabel("simulaiton steps")
            ax.set_ylabel("Number of infected nodes")
            ax.set_title(f"Infection model with varying max simulation steps and budgets")
            ax.grid(True)
            plt.show()