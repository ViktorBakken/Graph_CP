from random_graph import generate_graph,show, determine_T, analyse_graph
from Simulation import cascade
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import time


# np.random.seed(42)
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#---Simulation parameters------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------
new_graph=False # Should the simulation generate a random graph of n nodes
n=100  # Number of nodes in graph
spread=0.2 # The chance an infection will spread through an edge
budget=27 # The interdiction budget
intervention_step={5} # The steps in the simulation where interdiction occur
early_stop=(True,10)
time_range=70 # The number of simulation steps
repr= 10
mode="SI" # Infection model, SIR or SI 
solver="coin-bc"
interdiction_type="semi edge" # Naive interdiction model, node or edge or edge mzn or semi edge
verbose=0 # Should the simulation display each step
infected_nodes= {11} # Which nodes are infected at start
Run_single=False
Double_trouble=False
#-------------------------------------------------------------------------------------------------------------------------------------------------
# 15
# edges= [(12, 7), (7, 12),(5, 4), (4, 5),(4, 6), (6, 4),(8, 0), (0, 8),(9, 5), (5, 9),(11, 2), (2, 11),(11, 5), (5, 11),(9, 14), (14, 9),(13, 11), (11, 13),(7, 10), (10, 7),(6, 14), (14, 6),(4, 2), (2, 4),(3, 0), (0, 3),(9, 7), (7, 9),(5, 12), (12, 5),(11, 1), (1, 11),(11, 7), (7, 11),(1, 2), (2, 1),(0, 13), (13, 0),(13, 10), (10, 13),(8, 7), (7, 8),(9, 6), (6, 9)]
# 30
# edges= [(23, 4), (6, 18), (21, 16), (16, 29), (18, 26), (22, 17), (5, 10), (12, 25), (0, 5), (19, 18), (9, 17), (5, 28), (18, 19), (28, 5), (17, 14), (4, 23), (24, 19), (25, 18), (10, 29), (27, 8), (22, 21), (11, 0), (14, 17), (23, 29), (1, 19), (26, 18), (20, 17), (14, 10), (17, 9), (9, 5), (9, 14), (24, 5), (26, 2), (10, 15), (8, 27), (1, 21), (25, 22), (7, 16), (2, 29), (5, 0), (5, 9), (22, 25), (13, 7), (2, 13), (24, 25), (0, 25), (25, 24), (16, 21), (20, 3), (29, 15), (23, 8), (20, 21), (21, 20), (12, 26), (4, 22), (11, 27), (5, 4), (21, 22), (12, 19), (8, 6), (13, 2), (0, 11), (16, 7), (19, 24), (29, 1), (2, 26), (6, 8), (20, 7), (22, 4), (29, 10), (15, 29), (14, 9), (29, 28), (18, 25), (19, 8), (10, 5), (17, 20), (10, 14), (25, 12), (28, 29), (15, 22), (19, 1), (17, 22), (16, 2), (8, 19), (19, 28), (21, 1), (29, 23), (7, 20), (19, 12), (22, 1), (29, 16), (7, 13), (4, 5), (25, 0), (5, 24), (8, 23), (2, 16), (15, 10), (18, 6), (1, 29), (22, 15), (27, 11), (3, 20), (28, 19), (29, 2), (26, 12), (1, 22)]
# 100
edges= [(23, 4), (4, 23), (67, 4), (4, 67), (69, 1), (1, 69), (15, 30), (30, 15), (80, 65), (65, 80), (73, 26), (26, 73), (8, 0), (0, 8), (61, 70), (70, 61), (71, 38), (38, 71), (63, 34), (34, 63), (96, 67), (67, 96), (73, 35), (35, 73), (92, 79), (79, 92), (85, 73), (73, 85), (21, 37), (37, 21), (28, 30), (30, 28), (46, 66), (66, 46), (86, 47), (47, 86), (67, 98), (98, 67), (85, 27), (27, 85), (17, 94), (94, 17), (55, 50), (50, 55), (6, 11), (11, 6), (69, 49), (49, 69), (6, 75), (75, 6), (99, 93), (93, 99), (2, 32), (32, 2), (11, 44), (44, 11), (47, 18), (18, 47), (91, 18), (18, 91), (8, 11), (11, 8), (23, 27), (27, 23), (6, 41), (41, 6), (52, 8), (8, 52), (30, 75), (75, 30), (82, 58), (58, 82), (66, 7), (7, 66), (67, 27), (27, 67), (74, 84), (84, 74), (11, 80), (80, 11), (38, 64), (64, 38), (80, 88), (88, 80), (64, 0), (0, 64), (81, 16), (16, 81), (39, 10), (10, 39), (0, 46), (46, 0), (55, 79), (79, 55), (15, 46), (46, 15), (37, 28), (28, 37), (5, 23), (23, 5), (84, 45), (45, 84), (48, 58), (58, 48), (61, 22), (22, 61), (35, 67), (67, 35), (77, 48), (48, 77), (61, 31), (31, 61), (24, 21), (21, 24), (70, 43), (43, 70), (71, 72), (72, 71), (35, 85), (85, 35), (76, 31), (31, 76), (13, 94), (94, 13), (83, 0), (0, 83), (63, 31), (31, 63), (60, 16), (16, 60), (11, 66), (66, 11), (98, 9), (9, 98), (15, 66), (66, 15), (32, 27), (27, 32), (25, 22), (22, 25), (19, 36), (36, 19), (76, 88), (88, 76), (87, 70), (70, 87), (18, 80), (80, 18), (0, 96), (96, 0), (83, 48), (48, 83), (76, 97), (97, 76), (84, 86), (86, 84), (46, 47), (47, 46), (3, 21), (21, 3), (14, 21), (21, 14), (68, 1), (1, 68), (23, 33), (33, 23), (83, 84), (84, 83), (66, 77), (77, 66), (43, 20), (20, 43), (34, 48), (48, 34), (81, 77), (77, 81), (53, 6), (6, 53), (85, 93), (93, 85), (22, 0), (0, 22), (91, 54), (54, 91), (22, 73), (73, 22), (39, 89), (89, 39), (15, 34), (34, 15), (93, 69), (69, 93), (84, 97), (97, 84), (5, 84), (84, 5), (69, 87), (87, 69), (44, 12), (12, 44), (40, 81), (81, 40), (18, 50), (50, 18), (27, 28), (28, 27), (7, 59), (59, 7), (10, 85), (85, 10), (48, 69), (69, 48), (94, 36), (36, 94), (72, 90), (90, 72), (94, 72), (72, 94), (95, 92), (92, 95), (19, 72), (72, 19), (67, 39), (39, 67), (91, 88), (88, 91), (19, 81), (81, 19), (29, 3), (3, 29), (31, 18), (18, 31), (40, 94), (94, 40), (44, 64), (64, 44), (65, 62), (62, 65), (25, 78), (78, 25), (57, 76), (76, 57), (74, 83), (83, 74), (46, 85), (85, 46), (98, 31), (31, 98), (0, 42), (42, 0), (49, 90), (90, 49), (87, 74), (74, 87), (36, 37), (37, 36), (92, 91), (91, 92), (90, 56), (56, 90), (71, 70), (70, 71), (24, 77), (77, 24), (51, 6), (6, 51), (59, 51), (51, 59), (29, 4), (4, 29)]
# 100 clustered
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
   
    # print(inf)

    #--- Stats ------------------------------------
    # css, max_css, S_glob_efficency, S_exposure, max_central = [list(col) for col in zip(*Data)]        
    # plt.plot(S_glob_efficency, label=f"budget={budget}")
    # plt.xlabel("Sim step")
    # plt.ylabel("Global Efficency")
    # plt.title(f"Global Efficency of suciptible nodes, varying {interdiction_type} interdiction  budgets at {intervention_step}")
    # plt.show()
    show(n,new_edges,sets) #Display graph after simulation

    print("Sim mode: ", mode)
    print("Sim steps: ", time_range)
    print("Num suceptible: ", len(sets[0]))
    print("Num infected: ", len(sets[1]))
    print("Num safe: ", len(sets[2]))

# ---Display multiple independent runs of simulation with varying simulaiton steps and varying budgets----------------------------------------------------------
if not Run_single:
    analyse_graph(n,edges)  

    runs= n-10 if Double_trouble else 1
    Reccomended=[]
    score=[]
    score_std=[]
    start_inf=[]
    for run in range(runs):
        print("run ", run+1)

        if Double_trouble:
            early_stop=(True,run+10)
        d=[]
        d_2=[]
        s=[]
        repeat = repr if Double_trouble else 1
        for _ in range(repeat):
            infected_nodes={int(np.random.randint(0,n))}

            data_average=[]
            Num_infected=[]
            time_run=[]


            # if Double_trouble:
            #     head_start=run+1
            #     updated_intervention_steps={0}
            # else:
            #     head_start=min(intervention_step)
            #     updated_intervention_steps={i-head_start for i in intervention_step}

            head_start=min(intervention_step)
            updated_intervention_steps={i-head_start for i in intervention_step}
            
            layout=None
            if verbose>=3:layout=show(n,edges,[{n for n in range(n)}, {}, {},{}])
            


            # Let the Simulations have a common start before interdiction
            t=time.time()
            _, sets,head_start_infected,Data_init=cascade(t=head_start,n=n,spread=spread,budget=0,graph_edges=edges,init_infected=infected_nodes, 
                                                mode=mode,budget_type="",intervention_step={},displ=False,early_stop=early_stop)   
            if early_stop[0]:
                head_start=Data_init[-1]
            time_run.append(time.time()-t)
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
            print("Infected percentage:",(len(sets[1])/n*100))
            d_2.append((len(sets[1])/n)*100)
            #Run second time
            if verbose>=2:show(n,edges,sets,layout)
            # Data_avg=[]
            for b in range(budget+1):
                # print("\nBUDGET:", b)
                data=[]
                inf=0
                extra_data=[]

                t=time.time()
                for _ in range(repr):
                    _, sets,infected_over_time,Data=cascade(solver=solver,t=time_range-head_start,n=n,spread=spread,budget=b,graph_edges=edges,init_infected=new_infected, 
                                                mode=mode,budget_type=interdiction_type,intervention_step=updated_intervention_steps,displ=verbose,T=T,layout=layout)
                    data.append(infected_over_time)
                    inf+=len(sets[1])
                    extra_data.append(Data)
                Data_avg=np.mean(extra_data,axis=0)

                time_run.append((time.time()-t)/repr)
                Num_infected.append(inf/repr)
                #Determine the average of the runs and store the 
                means_over_run=np.mean(data,axis=0)
                combined_start_mean_data=[*start,*means_over_run]
                data_average.append(combined_start_mean_data)

                # Experimental data
                if verbose>=1: #=="edge mzn" :
                    rows = list(Data_init) + list(Data_avg)
                    css, max_css, S_glob_efficency, S_exposure, max_central = [list(col) for col in zip(*rows)]        
                    # plt.plot(S_glob_efficency, label="Efficency")
                    # if b%2:
                    if b>=7 and b<=9:
                        plt.plot(S_exposure, label=f"budget={b}")
                        # plt.plot(np.array(combined_start_mean_data)/10,ls="--",label="Infected")
                        plt.xlabel("Sim step")
                        plt.ylabel("Efficency")
                        plt.title(f"Acceleration of infection rate over varying budgets")

                # plt.plot(S_glob_efficency, label="Efficency")
                # plt.plot(S_exposure,label="Exposure")
                # plt.plot(np.array(combined_start_mean_data)/10,ls="--",label="Infected")
                # plt.xlabel("Sim step")
                # plt.title(f"Global Efficency of suciptible nodes at {b}, varying {interdiction_type} interdiction  budgets at {intervention_step}")
                # # plt.legend()
                if verbose>=1:plt.savefig(f"new_test_data/{b}")  
                # # plt.clf()
                # # plt.show() 
            # plt.plot(data_average,ls="--",label="Infected")
            if verbose>=1:
                plt.legend()
            # plt.savefig(f"new_test_data/{b}")  
                plt.show()
            #--- Stats ------------------------------------
            if not Double_trouble:
                df = pd.DataFrame(
                    data_average,
                    index=[f"budget = {b}" for b in range(budget+1)],
                    columns=range(0, time_range)
                )
                df.to_csv("data")
            
            #--- Num infected given budget ----------------------
            if verbose>=1:
                plt.plot(Num_infected)
                plt.xlabel("Budget")
                plt.ylabel("Infected nodes")
                plt.title(f"Number of infected nodes at end of simulation (step {time_range}), with {spread} spread after varying {interdiction_type} interdiction  budgets at {intervention_step}")
                plt.show()

            if Num_infected[0] !=0:
                # Score 
                test = []
                for b, inf in enumerate(Num_infected):
                    if Num_infected[0] > 0:
                        test.append(1 - inf / Num_infected[0])
                    else:
                        test.append(0)
                
                if not Double_trouble:
                    plt.plot(test)
                    plt.xlabel("Budget")
                    plt.ylabel("effectiveness")
                    plt.title(f"Comparison of Effectiveness, with {spread} spread after varying {interdiction_type} interdiction  budgets at {intervention_step}")
                    plt.show()  


                # Effectiveness 
                delta=[0]
                for b in range(1,budget+1):
                    if(b>0):
                        delta.append(test[b]-test[b-1])
                
                # tau=0.01
                # b_star= next((b for b in range(1,len(delta)) if delta[b]<tau), len(delta)-1)
                b_star=delta.index(max(delta))
                print("b*:",b_star)
                # # d.append(b)
                s.append(test[b_star])

                if not Double_trouble:
                    plt.plot(delta)
                    plt.xlabel("Budget")
                    # plt.ylabel("effectiveness")
                    plt.title(f"Comparison of delta R, with {spread} spread after varying {interdiction_type} interdiction  budgets at {intervention_step}")
                    plt.show()
         




                # Area under number of infected over time
                budgetComparison=[0]
                for inf, b in zip(Num_infected,range(budget)):
                    if(b>0):
                        budgetComparison.append((Num_infected[0]-inf)/b)
                
                if not Double_trouble:
                    plt.plot(budgetComparison)
                    plt.xlabel("Budget")
                    plt.ylabel("Improvement given budget")
                    plt.title(f"Comparison of number of infected given baseline and budget, with {spread} spread after varying {interdiction_type} interdiction  budgets at {intervention_step}")
                    plt.show()  
                d.append(budgetComparison.index(max(budgetComparison)))



            #--- Heat map ------------------------------------
            if not Double_trouble:
                plt.figure(figsize=(10, 5))
                sns.heatmap(
                    df,
                    cmap="magma",
                    annot=True,
                    fmt=".0f",
                    vmin=0,vmax=n,
                    linewidths=0.514,
                )
                plt.xlabel("Time step")
                plt.ylabel("Budget")
                plt.title(f"Infected nodes with spread {spread} after varying {interdiction_type} interdiction budgets at {intervention_step}")
                plt.show()  
        # Reccomended.append(np.mean(d,axis=0))
        score.append(np.mean(s,axis=0))
        score_std.append(np.std(s,axis=0))
        start_inf.append(np.mean(d_2,axis=0))
    #--- Plot graph ------------------------------------
    from matplotlib.ticker import MaxNLocator
    print(score)
    print(score_std)
    print(start_inf)
    steps = range(len(score))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9, 6), dpi=150, sharex=True
    )

    ax1.fill_between(steps, np.array(score) - np.array(score_std), np.array(score) + np.array(score_std), alpha=0.2)    
    ax1.plot(steps, score, marker="o", linewidth=2)
    ax1.set_ylabel("Score")
    ax1.set_title(
        f"Interdiction analysis (spread={spread},  type={interdiction_type})"
    )
    ax1.grid(True, alpha=0.3)

    ax2.plot(steps, start_inf, marker="s", linestyle="--", linewidth=2)
    # ax2.set_xlabel("Interdiction step")
    ax2.set_ylabel("Percent infected (%)")
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()




    # plt.plot(Reccomended, label="Best cost effective budget")
    # plt.plot(start_inf, ls="--", label="Procent infected at interdiction")

    # # # --- Trendline ---
    # # x = np.arange(len(Reccomended))
    # # y = np.array(Reccomended)
    # # m, b = np.polyfit(x, y, 1)
    # # plt.plot(x, m*x + b, color='red', label="Trendline")

    # plt.xlabel("Interdiction step")
    # plt.title(f"Reccomended budget given interdiction step, with {spread} spread starting at {infected_nodes}, after varying {interdiction_type} interdiction budget")

    # plt.legend()
    # plt.show()