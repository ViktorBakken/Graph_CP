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
        # if displ>=1:DATA.append([*analys_Gh(edges,sets),*analys_GF(edges,sets)])


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

    score=[np.float64(0.8786834500389016), np.float64(0.8733293319995553), np.float64(0.8646636656663332), np.float64(0.8526487452976956), np.float64(0.8436635545181728), np.float64(0.8299963321107034), np.float64(0.8097204438516542), np.float64(0.8149981104812715), np.float64(0.8039953302201468), np.float64(0.7956547721822328), np.float64(0.780328553962432), np.float64(0.7673307769256418), np.float64(0.7576533110740123), np.float64(0.7463166573277003), np.float64(0.7413333333333334), np.float64(0.7208101070727279), np.float64(0.7179908858508389), np.float64(0.6994444444444444), np.float64(0.686396887851506), np.float64(0.6604528687237381), np.float64(0.6653897720706398), np.float64(0.660885332147753), np.float64(0.6418722810677092), np.float64(0.637847652765581), np.float64(0.6127325515912713), np.float64(0.5983362167370838), np.float64(0.5855399395137206), np.float64(0.5855999999999999), np.float64(0.5584960468304249), np.float64(0.5683748842206662), np.float64(0.5398669698533245), np.float64(0.5290954429254195), np.float64(0.5245740813013484), np.float64(0.5121015491809354), np.float64(0.5081211805108978), np.float64(0.48425010929569123), np.float64(0.47485043903523394), np.float64(0.45621111111111107), np.float64(0.46303127270874295), np.float64(0.4411365825645585), np.float64(0.44049654321558873), np.float64(0.4354383063587968), np.float64(0.3958539957763699), np.float64(0.3935407667446784), np.float64(0.3968160298361505), np.float64(0.3781652180356414), np.float64(0.3752118405366709), np.float64(0.36205977548071583), np.float64(0.33592725450901806), np.float64(0.34921499759178987), np.float64(0.34132134594733876), np.float64(0.3313024515642314), np.float64(0.3185446768891832), np.float64(0.3169555555555555), np.float64(0.2986318478906714), np.float64(0.2990657109276552), np.float64(0.27447777777777776), np.float64(0.2683816393382596), np.float64(0.2647783318280012), np.float64(0.2522189787671423), np.float64(0.25476666666666664), np.float64(0.24895597421362678), np.float64(0.2356835500722463), np.float64(0.22700299729539475), np.float64(0.2224909562446742), np.float64(0.20987268776555937), np.float64(0.1974677232221847), np.float64(0.18482617235812368), np.float64(0.170163499222241), np.float64(0.15768259902091677), np.float64(0.1563501627145302), np.float64(0.14405760383970365), np.float64(0.12736318381736603), np.float64(0.12966855248045647), np.float64(0.11750177466562928), np.float64(0.1084), np.float64(0.11712551649353926), np.float64(0.09472222222222222), np.float64(0.09872301878403912), np.float64(0.0803046480520972), np.float64(0.07482676684316489), np.float64(0.06047848542106625), np.float64(0.05902387091993626), np.float64(0.05135652254455188), np.float64(0.041742179696174456), np.float64(0.027889255677818543), np.float64(0.0219888888888889), np.float64(0.01765577414693788), np.float64(0.013000000000000012), np.float64(0.008567501369104584)]
    score_std=[np.float64(0.06917987750201209), np.float64(0.016598665263735185), np.float64(0.015649185899217415), np.float64(0.0173233227290906), np.float64(0.01601418207822809), np.float64(0.016329120647594318), np.float64(0.049686987456328865), np.float64(0.01668162915633927), np.float64(0.014971018209673097), np.float64(0.013593885251416877), np.float64(0.017791044738559896), np.float64(0.015902057861670708), np.float64(0.020924429157652906), np.float64(0.014937047480467924), np.float64(0.019618585292749565), np.float64(0.046493937862794), np.float64(0.021036154858921064), np.float64(0.032181008125144524), np.float64(0.05299910582805959), np.float64(0.04327298164991645), np.float64(0.04749422471372506), np.float64(0.04193248807445368), np.float64(0.052040235833128334), np.float64(0.04377859011600311), np.float64(0.04797450207099862), np.float64(0.0819065151908229), np.float64(0.06686396263214675), np.float64(0.04687267228788441), np.float64(0.06475358356339635), np.float64(0.03418171691267113), np.float64(0.07581387999005931), np.float64(0.06550528954187174), np.float64(0.05096185538868971), np.float64(0.059441800874663796), np.float64(0.05046076973859779), np.float64(0.07124423004612264), np.float64(0.07093023080485505), np.float64(0.07699882073812384), np.float64(0.046539218384157255), np.float64(0.05198652381148261), np.float64(0.05033984303369247), np.float64(0.04724780779022645), np.float64(0.07813588014986912), np.float64(0.0586003876790582), np.float64(0.05053557543100393), np.float64(0.05994266955997701), np.float64(0.05199160478825563), np.float64(0.04661538601465651), np.float64(0.06455199578757043), np.float64(0.0524081574443071), np.float64(0.0460736426369284), np.float64(0.05366199461499121), np.float64(0.03954813107718425), np.float64(0.05450740577160701), np.float64(0.05275572040517651), np.float64(0.04324782030360292), np.float64(0.05277742806901685), np.float64(0.04263396592979421), np.float64(0.041894028871266926), np.float64(0.0443931208304431), np.float64(0.033701978181307594), np.float64(0.0276852664667003), np.float64(0.04032056119706454), np.float64(0.03805342871731847), np.float64(0.04445110235951518), np.float64(0.028582177776274236), np.float64(0.03349818736872647), np.float64(0.03264755604179267), np.float64(0.03755755756027987), np.float64(0.04123782342504595), np.float64(0.03512718692963482), np.float64(0.038614959742847), np.float64(0.04035663734506107), np.float64(0.03309116260136191), np.float64(0.030803434981404716), np.float64(0.031056030606583275), np.float64(0.02375970916535762), np.float64(0.02998827960354257), np.float64(0.023046373046914734), np.float64(0.02890044975416862), np.float64(0.018745170371775255), np.float64(0.027694135570506657), np.float64(0.02170049951536306), np.float64(0.017215404886046573), np.float64(0.01798289640174609), np.float64(0.01616118808172895), np.float64(0.013208157785958108), np.float64(0.00919283223818517), np.float64(0.004582575694955844), np.float64(0.0033830785885505484)]

    
    score_2= [np.float64(0.8720000000000001), np.float64(0.860985985985986), np.float64(0.845), np.float64(0.826), np.float64(0.826), np.float64(0.7644), np.float64(0.798), np.float64(0.783), np.float64(0.767), np.float64(0.7186), np.float64(0.741), np.float64(0.74), np.float64(0.673470970970971), np.float64(0.6805), np.float64(0.7010000000000001), np.float64(0.6949999999999998), np.float64(0.6779999999999999), np.float64(0.6425), np.float64(0.652960960960961), np.float64(0.604920920920921), np.float64(0.624), np.float64(0.6120000000000001), np.float64(0.572), np.float64(0.611), np.float64(0.5800000000000001), np.float64(0.5650000000000001), np.float64(0.5313000000000001), np.float64(0.524), np.float64(0.51), np.float64(0.506), np.float64(0.5218617756032586), np.float64(0.462), np.float64(0.45599999999999985), np.float64(0.44699999999999995), np.float64(0.4668997995991983), np.float64(0.42560000000000003), np.float64(0.417), np.float64(0.4162), np.float64(0.39480000000000004), np.float64(0.378), np.float64(0.37820000000000004), np.float64(0.3798), np.float64(0.3588), np.float64(0.33386886886886885), np.float64(0.34500000000000003), np.float64(0.3127299299299299), np.float64(0.319), np.float64(0.316), np.float64(0.28809999999999997), np.float64(0.29410000000000003), np.float64(0.2881), np.float64(0.26242992992993), np.float64(0.2637), np.float64(0.24700000000000003), np.float64(0.20492392392392395), np.float64(0.22399999999999998), np.float64(0.2101), np.float64(0.22400000000000003), np.float64(0.21792492492492493), np.float64(0.17509999999999998), np.float64(0.1961), np.float64(0.16), np.float64(0.16591291291291294), np.float64(0.16499999999999998), np.float64(0.15700000000000003), np.float64(0.13899999999999998), np.float64(0.12999999999999998), np.float64(0.11309999999999998), np.float64(0.10600000000000001), np.float64(0.11699999999999999), np.float64(0.076), np.float64(0.08299999999999999), np.float64(0.074), np.float64(0.08000000000000002), np.float64(0.061), np.float64(0.06100000000000001), np.float64(0.051464160950299376), np.float64(0.04519999999999998), np.float64(0.04500000000000002), np.float64(0.03090490490490492), np.float64(0.033004004004004016), np.float64(0.046000000000000006), np.float64(0.039903903903903915), np.float64(0.03200000000000003), np.float64(0.03080380380380383), np.float64(0.03700000000000003), np.float64(0.025000000000000022), np.float64(0.028000000000000025), np.float64(0.016000000000000014), np.float64(0.009000000000000008)]
    score_std_2= [np.float64(0.014000000000000014), np.float64(0.015133730391457602), np.float64(0.012041594578792305), np.float64(0.03352610922848041), np.float64(0.021540659228537987), np.float64(0.07973857284902959), np.float64(0.02227105745132009), np.float64(0.017916472867168933), np.float64(0.022825424421026672), np.float64(0.09417876618431567), np.float64(0.0320780298646909), np.float64(0.01843908891458579), np.float64(0.09054357219063987), np.float64(0.08168384173139753), np.float64(0.022999999999999993), np.float64(0.029748949561287038), np.float64(0.023579652245103187), np.float64(0.07573803535872842), np.float64(0.034991014186166104), np.float64(0.033242067159294036), np.float64(0.022449944320643626), np.float64(0.03218695387886214), np.float64(0.041182520563948), np.float64(0.01640121946685671), np.float64(0.023237900077244484), np.float64(0.0366742416417845), np.float64(0.07520113031065427), np.float64(0.05748043145279967), np.float64(0.04242640687119287), np.float64(0.042000000000000016), np.float64(0.03677202839373237), np.float64(0.03893584466786357), np.float64(0.0682934843158555), np.float64(0.05060632371551998), np.float64(0.03625571864726972), np.float64(0.06354714785102476), np.float64(0.062136945531623924), np.float64(0.05489954462470521), np.float64(0.06866119719317454), np.float64(0.0511468474101777), np.float64(0.0508031495086673), np.float64(0.05238663951810615), np.float64(0.04904039151556601), np.float64(0.04713464365613204), np.float64(0.053712196007983146), np.float64(0.06205640967802012), np.float64(0.04846648326421053), np.float64(0.02870540018881463), np.float64(0.038503116756958784), np.float64(0.039361021328212516), np.float64(0.0527872143610553), np.float64(0.03962119297897555), np.float64(0.050331004361129125), np.float64(0.05197114584074512), np.float64(0.03794373153498262), np.float64(0.03638681079732051), np.float64(0.037842965000115934), np.float64(0.038262252939418005), np.float64(0.04529068250310734), np.float64(0.04091564492953763), np.float64(0.036012358989657975), np.float64(0.02898275349237888), np.float64(0.030171816778525366), np.float64(0.058180752831155404), np.float64(0.03034798181098703), np.float64(0.05107837115648853), np.float64(0.047116875957558986), np.float64(0.02566105999369475), np.float64(0.04029888335921978), np.float64(0.033778691508109075), np.float64(0.047159304490206375), np.float64(0.0334813380855664), np.float64(0.03666060555964671), np.float64(0.03898717737923584), np.float64(0.04229657196511318), np.float64(0.034770677301427404), np.float64(0.02471254927038984), np.float64(0.025360599362002446), np.float64(0.02617250465660479), np.float64(0.016293181828003583), np.float64(0.02451644754740148), np.float64(0.025377155080899026), np.float64(0.021449548017083337), np.float64(0.01536229149573723), np.float64(0.014610622440742356), np.float64(0.013453624047073722), np.float64(0.009219544457292896), np.float64(0.0040000000000000036), np.float64(0.006633249580710806), np.float64(0.0030000000000000022)]
    
    score_3= [np.float64(0.855), np.float64(0.855), np.float64(0.835), np.float64(0.635), np.float64(0.735), np.float64(0.8049999999999999), np.float64(0.76), np.float64(0.8), np.float64(0.73), np.float64(0.71), np.float64(0.69), np.float64(0.695), np.float64(0.6799999999999999), np.float64(0.61), np.float64(0.665), np.float64(0.71), np.float64(0.655), np.float64(0.595), np.float64(0.565), np.float64(0.48), np.float64(0.515), np.float64(0.585), np.float64(0.47500000000000003), np.float64(0.53), np.float64(0.495), np.float64(0.425), np.float64(0.445), np.float64(0.31), np.float64(0.35), np.float64(0.43), np.float64(0.44), np.float64(0.345), np.float64(0.3725), np.float64(0.315), np.float64(0.36), np.float64(0.315), np.float64(0.24), np.float64(0.42), np.float64(0.36000000000000004), np.float64(0.17500000000000004), np.float64(0.33), np.float64(0.36), np.float64(0.325), np.float64(0.305), np.float64(0.26), np.float64(0.20999999999999996), np.float64(0.28), np.float64(0.27), np.float64(0.235), np.float64(0.22499999999999998), np.float64(0.3), np.float64(0.17500000000000004), np.float64(0.32), np.float64(0.26499999999999996), np.float64(0.33499999999999996), np.float64(0.24), np.float64(0.30000000000000004), np.float64(0.24500000000000005), np.float64(0.255), np.float64(0.20500000000000002), np.float64(0.275), np.float64(0.185), np.float64(0.11499999999999999), np.float64(0.125), np.float64(0.14), np.float64(0.24), np.float64(0.20500000000000002), np.float64(0.19499999999999995), np.float64(0.21499999999999997), np.float64(0.19999999999999996), np.float64(0.14), np.float64(0.16500000000000004), np.float64(0.14), np.float64(0.1528643216080402), np.float64(0.11499999999999999), np.float64(0.14500000000000002), np.float64(0.13), np.float64(0.08500000000000002), np.float64(0.09999999999999998), np.float64(0.08999999999999997), np.float64(0.09499999999999997), np.float64(0.07999999999999996), np.float64(0.06), np.float64(0.03500000000000003), np.float64(0.05500000000000005), np.float64(0.03500000000000003), np.float64(0.030000000000000027), np.float64(0.025000000000000022), np.float64(0.010000000000000009), np.float64(0.010000000000000009)]
    score_std_3= [np.float64(0.015000000000000013), np.float64(0.034999999999999976), np.float64(0.024999999999999967), np.float64(0.195), np.float64(0.025000000000000022), np.float64(0.024999999999999967), np.float64(0.0), np.float64(0.02999999999999997), np.float64(0.06000000000000005), np.float64(0.040000000000000036), np.float64(0.020000000000000018), np.float64(0.015000000000000013), np.float64(0.03999999999999998), np.float64(0.010000000000000009), np.float64(0.034999999999999976), np.float64(0.010000000000000009), np.float64(0.034999999999999976), np.float64(0.004999999999999949), np.float64(0.08500000000000002), np.float64(0.010000000000000009), np.float64(0.025000000000000022), np.float64(0.034999999999999976), np.float64(0.08500000000000002), np.float64(0.08000000000000002), np.float64(0.0050000000000000044), np.float64(0.065), np.float64(0.034999999999999976), np.float64(0.11000000000000004), np.float64(0.10999999999999999), np.float64(0.06), np.float64(0.03999999999999998), np.float64(0.025000000000000022), np.float64(0.04750000000000004), np.float64(0.024999999999999967), np.float64(0.07999999999999996), np.float64(0.034999999999999976), np.float64(0.0), np.float64(0.08000000000000002), np.float64(0.04999999999999999), np.float64(0.0050000000000000044), np.float64(0.04999999999999999), np.float64(0.07999999999999996), np.float64(0.014999999999999958), np.float64(0.044999999999999984), np.float64(0.050000000000000044), np.float64(0.0), np.float64(0.0), np.float64(0.09999999999999998), np.float64(0.125), np.float64(0.0050000000000000044), np.float64(0.06), np.float64(0.0050000000000000044), np.float64(0.009999999999999953), np.float64(0.05499999999999999), np.float64(0.015000000000000013), np.float64(0.09999999999999998), np.float64(0.010000000000000009), np.float64(0.065), np.float64(0.03500000000000003), np.float64(0.05499999999999999), np.float64(0.0050000000000000044), np.float64(0.07500000000000001), np.float64(0.0050000000000000044), np.float64(0.06499999999999995), np.float64(0.030000000000000027), np.float64(0.0), np.float64(0.024999999999999967), np.float64(0.0050000000000000044), np.float64(0.0050000000000000044), np.float64(0.010000000000000009), np.float64(0.040000000000000036), np.float64(0.015000000000000013), np.float64(0.010000000000000009), np.float64(0.007135678391959832), np.float64(0.025000000000000022), np.float64(0.0050000000000000044), np.float64(0.010000000000000009), np.float64(0.034999999999999976), np.float64(0.020000000000000018), np.float64(0.010000000000000009), np.float64(0.0050000000000000044), np.float64(0.010000000000000009), np.float64(0.009999999999999953), np.float64(0.015000000000000013), np.float64(0.0050000000000000044), np.float64(0.015000000000000013), np.float64(0.010000000000000009), np.float64(0.0050000000000000044), np.float64(0.0), np.float64(0.0)]
    
    start_inf=[np.float64(11.6), np.float64(12.2), np.float64(12.6), np.float64(13.4), np.float64(15.2), np.float64(16.2), np.float64(17.2), np.float64(20.0), np.float64(20.0), np.float64(20.4), np.float64(22.6), np.float64(22.2), np.float64(24.0), np.float64(24.2), np.float64(25.0), np.float64(27.2), np.float64(31.0), np.float64(28.4), np.float64(29.4), np.float64(30.8), np.float64(33.0), np.float64(34.0), np.float64(35.2), np.float64(38.0), np.float64(36.8), np.float64(36.6), np.float64(38.6), np.float64(38.6), np.float64(40.6), np.float64(42.2), np.float64(44.4), np.float64(44.0), np.float64(43.4), np.float64(45.0), np.float64(45.2), np.float64(47.2), np.float64(48.0), np.float64(49.6), np.float64(52.0), np.float64(51.2), np.float64(53.0), np.float64(52.6), np.float64(55.4), np.float64(56.2), np.float64(56.2), np.float64(59.2), np.float64(57.8), np.float64(60.8), np.float64(61.8), np.float64(61.8), np.float64(63.0), np.float64(65.0), np.float64(64.8), np.float64(66.0), np.float64(65.6), np.float64(67.2), np.float64(68.2), np.float64(71.0), np.float64(71.6), np.float64(71.8), np.float64(74.4), np.float64(71.8), np.float64(75.8), np.float64(74.0), np.float64(75.2), np.float64(77.2), np.float64(78.2), np.float64(78.8), np.float64(80.0), np.float64(81.6), np.float64(81.4), np.float64(82.4), np.float64(83.6), np.float64(84.0), np.float64(85.6), np.float64(86.2), np.float64(86.8), np.float64(88.6), np.float64(89.2), np.float64(90.2), np.float64(91.0), np.float64(91.6), np.float64(93.0), np.float64(93.6), np.float64(94.4), np.float64(95.6), np.float64(96.6), np.float64(98.2), np.float64(98.0), np.float64(99.2)]
    
    
    steps = range(len(score))

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(9, 6), dpi=150, sharex=True
    )

    ax1.fill_between(steps, np.array(score) - np.array(score_std), np.array(score) + np.array(score_std), alpha=0.2)    
    ax1.plot(steps, score, marker="o", linewidth=2,label="edge")
    ax1.fill_between(steps, np.array(score_2) - np.array(score_std_2), np.array(score_2) + np.array(score_std_2), alpha=0.2)    
    ax1.plot(steps, score_2, marker="o", linewidth=2,label="semi edge")
    ax1.fill_between(steps, np.array(score_3) - np.array(score_std_3), np.array(score_3) + np.array(score_std_3), alpha=0.2)    
    ax1.plot(steps, score_3, marker="o", linewidth=2,label="edge mzn")
    ax1.set_ylabel("Score")
    ax1.set_title(
        f"Interdiction analysis (spread={spread})"
    )
    ax1.grid(True, alpha=0.3)

    ax2.plot(steps, start_inf, marker="s", linestyle="--", linewidth=2)
    # ax2.set_xlabel("Interdiction step")
    ax2.set_ylabel("Percent infected (%)")
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    ax1.legend()
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