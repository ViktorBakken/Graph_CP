from random_graph import show,determine_k_dangerous_edges,analys_GF,analys_Gh, determine_T
from run_minizinc import interdiction_minizinc
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def cascade(t=4, n=100,spread=0.2,budget=8,graph_edges=None, init_infected=None, mode="SI",budget_type="edge",intervention_step=None,displ=0,T=set(), layout=None,solver="cbc", early_stop=(False,0)):
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

    if T==set(): 
        #15
        # T={0,1}
        #100
        T={69, 6, 48,21, 18,88, 22, 23, 25, 27, 30, 73, 76, 77, 81, 84, 90, 91, 92, 93, 94, 98}
        # T=set()
        # T=determine_T(edges,[])
    else:
        T=T.copy()

    suceptible={i for i in range(n)}
    for inf in infected:
        suceptible.remove(inf)

    safe=set()
    removed=set()
    risk_edges=set()    


    infected_over_time=[]
    DATA=[]
    sets=[{},{},{},{}]
    #-------------------------------
    #---Spread model----------------
    #-------------------------------
    if early_stop[0]: 
        t=100000
    for time in range(t):
        if early_stop[0] and (len(infected)/n)*100  >=early_stop[1]: 
            if displ>=1: print("stopping")
            t=time
            break
        sets=[suceptible,infected,safe,removed]
        infected_over_time.append(len(infected))
        # if budget_type=="edge mzn":
        if displ>=1:DATA.append([*analys_Gh(edges,sets),*analys_GF(edges,sets)])


        if len(risk_edges)>0 or time==0:
            if displ>=3:show(n=n,edges=edges,sets=sets,layout=layout)           

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
                        if len(intervention_step)>1:
                            T=determine_T(edges,sets)
                        T=set(T)-infected
                        edges,_=interdiction_minizinc(solver_name=solver,num_nodes=n,budget=budget,infected_nodes=infected,critical_nodes=T, graph_edges=edges,interdiction_type="edge", displ=displ)    
                    case "node mzn":
                        T=T-infected
                        edges,rem_nodes=interdiction_minizinc(solver_name=solver,num_nodes=n,budget=budget,infected_nodes=infected,critical_nodes=T, graph_edges=edges,interdiction_type="node", displ=displ)                      
                        for node in rem_nodes:
                            removed.add(node)
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
                    case "semi edge":
                        if(len(risk_edges)>budget):
                            rem_edges= determine_k_dangerous_edges(edges,risk_edges,sets,budget)
                            risk_edges-=rem_edges
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
            
    return edges, sets, infected_over_time, [*DATA,t]

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
    # np.random.seed(42)
    # intervention_step={1,2}
    # displ=0
    # sovl=["gurobi","highs","coinbc","coin-bc"]
    # for solve in sovl:
    #     print(solve)
    #     start= time.time()
    #     cascade(solver =solve,displ=displ,budget_type="edge mzn",intervention_step=intervention_step)
    #     print(solve," run time: ",time.time() - start,"s\n")
# --------------------------------------------------------
    from matplotlib.ticker import MaxNLocator
    spread=0.2
    interdiction_type="edge"

    score=[np.float64(0.012413627254508985), np.float64(0.034399999999999986), np.float64(0.008800000000000007), np.float64(0.0015999999999999793), np.float64(0.038799999999999966), np.float64(0.006399999999999984), np.float64(0.015999999999999993), np.float64(0.02679999999999998), np.float64(0.04280000000000002), np.float64(0.06280000000000004), np.float64(0.09999999999999998), np.float64(0.078), np.float64(0.0972), np.float64(0.02679999999999998), np.float64(0.03361683366733468), np.float64(0.056059318637274536), np.float64(0.07840000000000003), np.float64(0.1456), np.float64(0.044399999999999995), np.float64(0.0811017543859649), np.float64(0.11999999999999997), np.float64(0.10800000000000001), np.float64(0.15), np.float64(0.06721207243460765), np.float64(0.08880000000000002), np.float64(0.16160000000000002), np.float64(0.07119999999999997), np.float64(0.12799999999999995), np.float64(0.076), np.float64(0.11200000000000002), np.float64(0.134), np.float64(0.152), np.float64(0.1232), np.float64(0.18480000000000002), np.float64(0.16967054108216434), np.float64(0.11359999999999996), np.float64(0.15839999999999999), np.float64(0.1728), np.float64(0.20919999999999997), np.float64(0.1252), np.float64(0.11920000000000001), np.float64(0.22080000000000002), np.float64(0.1256), np.float64(0.17440000000000005), np.float64(0.14044328657314628), np.float64(0.0696), np.float64(0.08640000000000003), np.float64(0.14880000000000002), np.float64(0.15839999999999996), np.float64(0.12457831325301198), np.float64(0.1564), np.float64(0.05720000000000001), np.float64(0.076), np.float64(0.122), np.float64(0.08759999999999998), np.float64(0.10559999999999999), np.float64(0.11919999999999997), np.float64(0.08039999999999999), np.float64(0.13919999999999993), np.float64(0.08119999999999994), np.float64(0.07559999999999996), np.float64(0.06999999999999998), np.float64(0.06080000000000001), np.float64(0.1024), np.float64(0.0508), np.float64(0.036800000000000034), np.float64(0.09559999999999998), np.float64(0.048), np.float64(0.04479999999999999), np.float64(0.03599999999999996), np.float64(0.04040000000000001), np.float64(0.03519999999999999), np.float64(0.03159999999999998), np.float64(0.021999999999999974), np.float64(0.01200000000000001), np.float64(0.021599999999999998), np.float64(0.01479999999999999), np.float64(0.009199999999999986), np.float64(0.0), np.float64(0.006399999999999984), np.float64(0.015599999999999992), np.float64(0.0028000000000000026), np.float64(0.0), np.float64(0.0), np.float64(0.004800000000000004), np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0)]
    score_std=[np.float64(0.012248650546205104), np.float64(0.031759093186046736), np.float64(0.0067646138101151105), np.float64(0.0023323807579380806), np.float64(0.043847006739343115), np.float64(0.004630334761116096), np.float64(0.008099382692526668), np.float64(0.012998461447417531), np.float64(0.03671729837556134), np.float64(0.0344), np.float64(0.06841052550594824), np.float64(0.08260750571225355), np.float64(0.06693997311024262), np.float64(0.00854166260162503), np.float64(0.023919112422927515), np.float64(0.05140942232763782), np.float64(0.038354139281177965), np.float64(0.14282520785911712), np.float64(0.02214136400495687), np.float64(0.05715500019595138), np.float64(0.08590227005149514), np.float64(0.08114185110040319), np.float64(0.08855280910281729), np.float64(0.056720185969860816), np.float64(0.11381810049372636), np.float64(0.11846619771057058), np.float64(0.04844130468928347), np.float64(0.13277951649256753), np.float64(0.05577096018538678), np.float64(0.054243893665554675), np.float64(0.08027951170753346), np.float64(0.1419971830706511), np.float64(0.10726117657381914), np.float64(0.06336686831460113), np.float64(0.09286529400173561), np.float64(0.04832225160316934), np.float64(0.1084686129716795), np.float64(0.12459598709428808), np.float64(0.08361435283490504), np.float64(0.0432037035449509), np.float64(0.07041136271937933), np.float64(0.13880979792507447), np.float64(0.06925200358112392), np.float64(0.05492394741822553), np.float64(0.08005649583244188), np.float64(0.05058695484015615), np.float64(0.10824712467312932), np.float64(0.08039502472168289), np.float64(0.07100873185742725), np.float64(0.06009637201572777), np.float64(0.07039772723604079), np.float64(0.02306859336847392), np.float64(0.033538038106007334), np.float64(0.05916755867872196), np.float64(0.0390978260265197), np.float64(0.06692563036684822), np.float64(0.05146804834069389), np.float64(0.055054881709072835), np.float64(0.043517352860669274), np.float64(0.0604728038046856), np.float64(0.04310730796512346), np.float64(0.04618224767158915), np.float64(0.03218943926196912), np.float64(0.0257806128709152), np.float64(0.025317187837514625), np.float64(0.028187940683916616), np.float64(0.045824011173183035), np.float64(0.03961817764612601), np.float64(0.048192945541852876), np.float64(0.025518620652378508), np.float64(0.02740510901273706), np.float64(0.029680970334542662), np.float64(0.052890830963409866), np.float64(0.02677312084909045), np.float64(0.024000000000000018), np.float64(0.019734234213670418), np.float64(0.016998823488700597), np.float64(0.015574337867145446), np.float64(0.0), np.float64(0.009068627239003717), np.float64(0.021923503369671537), np.float64(0.005600000000000005), np.float64(0.0), np.float64(0.0), np.float64(0.009600000000000008), np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(0.0)]
    start_inf=[np.float64(11.6), np.float64(12.2), np.float64(12.6), np.float64(13.4), np.float64(15.2), np.float64(16.2), np.float64(17.2), np.float64(20.0), np.float64(20.0), np.float64(20.4), np.float64(22.6), np.float64(22.2), np.float64(24.0), np.float64(24.2), np.float64(25.0), np.float64(27.2), np.float64(31.0), np.float64(28.4), np.float64(29.4), np.float64(30.8), np.float64(33.0), np.float64(34.0), np.float64(35.2), np.float64(38.0), np.float64(36.8), np.float64(36.6), np.float64(38.6), np.float64(38.6), np.float64(40.6), np.float64(42.2), np.float64(44.4), np.float64(44.0), np.float64(43.4), np.float64(45.0), np.float64(45.2), np.float64(47.2), np.float64(48.0), np.float64(49.6), np.float64(52.0), np.float64(51.2), np.float64(53.0), np.float64(52.6), np.float64(55.4), np.float64(56.2), np.float64(56.2), np.float64(59.2), np.float64(57.8), np.float64(60.8), np.float64(61.8), np.float64(61.8), np.float64(63.0), np.float64(65.0), np.float64(64.8), np.float64(66.0), np.float64(65.6), np.float64(67.2), np.float64(68.2), np.float64(71.0), np.float64(71.6), np.float64(71.8), np.float64(74.4), np.float64(71.8), np.float64(75.8), np.float64(74.0), np.float64(75.2), np.float64(77.2), np.float64(78.2), np.float64(78.8), np.float64(80.0), np.float64(81.6), np.float64(81.4), np.float64(82.4), np.float64(83.6), np.float64(84.0), np.float64(85.6), np.float64(86.2), np.float64(86.8), np.float64(88.6), np.float64(89.2), np.float64(90.2), np.float64(91.0), np.float64(91.6), np.float64(93.0), np.float64(93.6), np.float64(94.4), np.float64(95.6), np.float64(96.6), np.float64(98.2), np.float64(98.0), np.float64(99.2)]
    
    steps = range(len(score))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9, 6), dpi=150, sharex=True
    )

    ax1.fill_between(steps, np.array(score) - np.array(score_std), np.array(score) + np.array(score_std), alpha=0.2)    
    ax1.plot(steps, score, marker="o", linewidth=2)
    ax1.set_ylabel("Score")
    ax1.set_title(
        f"Interdiction analysis (spread={spread}, type={interdiction_type})"
    )
    ax1.grid(True, alpha=0.3)

    ax2.plot(steps, start_inf, marker="s", linestyle="--", linewidth=2)
    # ax2.set_xlabel("Interdiction step")
    ax2.set_ylabel("Percent infected (%)")
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()







# # ----------------------------------------------------------------------------
#     df=pd.read_csv("data",index_col=0)
#     plt.figure(figsize=(15, 10))
#     sns.heatmap(
#             df,
#             cmap="magma",
#             annot=False,
#             fmt=".0f",
#             vmin=0,vmax=100,
#             linewidths=0.514,
#         )
#     plt.xlabel("Time step")
#     plt.ylabel("Budget")
#     plt.title(f"Infected nodes with spread {0.2} after varying {"edge mzn"} interdiction budgets at {4}")
#     plt.show()  

    # t, edges, sets, infected_over_time =cascade(budget_type="edge mzn", displ=True)
#--- Stats ------------------------------------
    # show(3,edges,sets) #Display graph after simulation

    # print("Sim mode: ", "SI")
    # print("Sim steps: ", t)
    # print("Num suceptible: ", len(sets[0]))
    # print("Num infected: ", len(sets[1]))
    # print("Num safe: ", len(sets[2]))