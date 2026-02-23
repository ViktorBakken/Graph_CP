from random_graph import generate_graph,show
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
np.random.seed(0)

#Spread simulation
def cascade(t=100, n=2,spread=0.15,budget=0,edges=None, infected=None, mode="SIR",budget_type="edge",displ=False):
    # Initialization
    if edges is None:
        edges = {(0, 1), (1, 0)}
    else:
        edges = set(edges)
    if infected is None:
        infected = {0}
    suceptible={i for i in range(n)}
    for inf in infected:
        suceptible.remove(inf)
    safe=set()
    removed=set()

    # Determine which edges are adjacent to infected nodes
    risk_edges=set()    
    for edge in edges:
        i=edge[0]
        if i in infected:
            risk_edges.add(edge)

    #-------------------------------
    #---Spread model----------------
    #-------------------------------
    for time in range(t):
        #Stopp criteria
        if len(risk_edges)<=0:
            return time,edges, [suceptible,infected,safe,removed]
        if displ:show(n=n,edges=edges,sets=[suceptible,infected,safe,removed])

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

        # Interdiction mode: node        
        if budget_type=="node":
            if len(infected)> budget:
                np.random.shuffle(list(infected))
                rem_nodes= set(list(infected)[:budget])
                infected=set(list(infected)[budget:])
            else:
                rem_nodes=infected.copy()
                infected.clear()
            for node in rem_nodes:
                removed.add(node)
              
        # Update the list of edges which can conduct infection
        risk_edges.clear()
        for edge in edges:
            (i,j)=edge
            if i in infected and j in suceptible :
                risk_edges.add(edge)

        # Interdiction mode: edges
        if budget_type=="edge":
            np.random.shuffle(list(risk_edges))
            if(len(risk_edges)>budget):
                rem_edges= set(list(risk_edges)[:budget])
                risk_edges=set(list(risk_edges)[budget:])
            else:
                rem_edges=risk_edges.copy()
                risk_edges.clear()
            for edge in rem_edges:
                (i,j)=edge
                edges.discard((i,j))
                edges.discard((j,i))
        
    return t, edges, [suceptible,infected,safe,removed]


#------------------------------------------
#---Simulation parameters------------------
#------------------------------------------
new_graph=False # Should the simulation generate a random graph of n nodes
n=30  # Number of nodes in graph
spread=0.25 # The chance an infection will spread through an edge
budget=5 # The interdiction budget
time_range=15 # The number of simulation steps
mode="SI" # Infection model, SIR or SI 
interdiction_type="edge" # Naive interdiction model, node or edge
display=True # Should the simulation display each step
infected_nodes= {1,2} # Which nodes are infected at start
Run_single= False # Should the simulation run once or multiple time
#------------------------------------------

# --- Graph ----
edges= {(23, 4), (6, 18), (21, 16), (16, 29), (18, 26), (22, 17), (5, 10), (12, 25), (0, 5), (19, 18), (9, 17), (5, 28), (18, 19), (28, 5), (17, 14), (4, 23), (24, 19), (25, 18), (10, 29), (27, 8), (22, 21), (11, 0), (14, 17), (23, 29), (1, 19), (26, 18), (20, 17), (14, 10), (17, 9), (9, 5), (9, 14), (24, 5), (26, 2), (10, 15), (8, 27), (1, 21), (25, 22), (7, 16), (2, 29), (5, 0), (5, 9), (22, 25), (13, 7), (2, 13), (24, 25), (0, 25), (25, 24), (16, 21), (20, 3), (29, 15), (23, 8), (20, 21), (21, 20), (12, 26), (4, 22), (11, 27), (5, 4), (21, 22), (12, 19), (8, 6), (13, 2), (0, 11), (16, 7), (19, 24), (29, 1), (2, 26), (6, 8), (20, 7), (22, 4), (29, 10), (15, 29), (14, 9), (29, 28), (18, 25), (19, 8), (10, 5), (17, 20), (10, 14), (25, 12), (28, 29), (15, 22), (19, 1), (17, 22), (16, 2), (8, 19), (19, 28), (21, 1), (29, 23), (7, 20), (19, 12), (22, 1), (29, 16), (7, 13), (4, 5), (25, 0), (5, 24), (8, 23), (2, 16), (15, 10), (18, 6), (1, 29), (22, 15), (27, 11), (3, 20), (28, 19), (29, 2), (26, 12), (1, 22)}
if new_graph:
    edges=generate_graph(n)

#--- Run Simulation ---
if Run_single:
    t, edges, sets=cascade(n=n,spread=spread,budget=budget,edges=edges,infected=infected_nodes,
                        mode=mode,budget_type=interdiction_type,displ=display)
    show(n,edges,sets) #Display graph after simulation

    #--- Stats -------------
    print("Sim mode: ",mode)
    print("Sim steps: ", t)
    print("Num suceptible: ", len(sets[0]))
    print("Num infected: ", len(sets[1]))
    print("Num safe: ", len(sets[2]))

# ---Display multiple independent runs of simulation with varying simulaiton steps and varying budgets---
if not Run_single:
    data=[]
    for b in range(budget+1):
        row=[]
        for t in range(time_range):
            _, _, sets=cascade(t=t+1,n=n,spread=spread,budget=b,
                      edges=edges,infected={1,2}, mode=mode,budget_type=interdiction_type,displ=False)
            inf = len(sets[1])
            row.append(inf)
        data.append(row)

    # Store results
    df = pd.DataFrame(
        data,
        index=[f"budget = {b}" for b in range(budget+1)],
        columns=range(1, time_range+1)
    )

    print(tabulate(
        df.to_numpy(),
        headers=["max time step"] + [str(c) for c in df.columns],  # corner title + column headers
        showindex=list(df.index),
        tablefmt="fancy_grid",
        numalign="right",
        stralign="center"
    ))    

    # Plot the runs
    for k in range(len(df)):
        fig, ax = plt.subplots(figsize=(10, 4))
        df.iloc[:k+1].T.plot(ax=ax, legend=True)
        ax.set_xlabel("Max simulaiton steps")
        ax.set_ylabel("Number of infected nodes")
        ax.set_title(f"Infection model with varying max simulation steps and budgets")
        ax.grid(True)
        plt.show()