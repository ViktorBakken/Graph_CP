from random_graph import (
    show,
    show_weighted,
    determine_T,
    analyse_graph,
    determine_k_dangerous_edges,
)
from Generate_cost_edges import node_edge_costs, test, node_weights
from run_minizinc import interdiction_minizinc
from Simulation import cascade
import numpy as np
import matplotlib.pyplot as plt
import ast

# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---Simulation parameters------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
max_tie= 99+1#205
spread = 0.2  # The chance an infection will spread through an edge
fixed=False

lame=0.1
use_lame=False

node_importance=0.5

early_stop = (True, 30)
seed_selection = 2**32

repr = 70
runs = 70

solver = "cplex"
interdiction_types = ["edge", "semi edge", "edge mzn", "node edge mzn"]  #

verbose = 0 # Display settings
# -------------------------------------------------------------------------------------------------------------------------------------------------


def Determine_Start_Infection(
    n, spread, early_stop, infected_nodes, edges, rng, verbose,layout, fixed
):
    procent_infected=100
    limit= early_stop[1]+3
    while(procent_infected>limit):
        new_edges, states, head_start_infected, end_time_step = cascade(
            simulation_time=100,
            n=n,
            graph_edges=edges,
            init_infected=infected_nodes,
            verbose_displ=verbose,
            early_stop=early_stop,
            rng=rng,
            layout=layout,
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed
            
        )
        procent_infected=len(states[1])/n*100
        

    return new_edges, end_time_step, states, head_start_infected


def Determine_Infection_Time(
    n, spread, repr, edges, layout, infected_nodes, verbose, rng, fixed
):
    t_avg = []
    for _ in range(repr):
        _, _, _, t_i = cascade(
            simulation_time=100,
            n=n,
            graph_edges=edges,
            init_infected=infected_nodes,
            verbose_displ=0,
            layout=layout,
            early_stop=(True, 100),
            rng=rng,
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed
        )
        t_avg.append(t_i)
    t = int(np.mean(t_avg))
    # t = t.astype(int)
    return t


def Simulate_Infection(
    n,
    spread,
    b,
    verbose,
    layout,
    T,
    infected_nodes,
    common_start,
    remaining_time,
    graph_edges,
    seed_matrix,
    fixed
):
    data = []

    for seed in seed_matrix[b]:
        _, _, infected_over_time, _ = cascade(
            simulation_time=remaining_time,
            n=n,
            graph_edges=graph_edges,
            init_infected=infected_nodes,
            T_set=T,
            verbose_displ=verbose,
            layout=layout,
            rng=np.random.default_rng(seed),
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed
        )
        data.append(infected_over_time)

    # Determine the average of the runs and store the
    means_over_run = np.mean(data, axis=0)
    return [*common_start.copy(), *means_over_run]


def Set_Up_Graph(edges, infected_set, suceptible_set):
    risk_edges = set()
    new_edges = list(edges.copy())
    for edge in edges:
        i, j,_ = edge
        if i in infected_set and j in infected_set:
            new_edges.remove(edge)
        if i in infected_set and j in suceptible_set:
            risk_edges.add(edge)
        if j == infected_set and j in suceptible_set:
            print("OI")
    return new_edges, risk_edges


def Remove_interdicted_edges(rem_edges, new_edges):
    if len(rem_edges) > 0:
        for i, j, c in rem_edges:
            c_2=[cc for jj,ii,cc in edges if jj==j and ii==i][0]
            if (i, j, c) in new_edges:
                new_edges.remove((i, j, c))
            if (j, i, c_2) in new_edges:
                new_edges.remove((j, i, c_2))
        rem_edges.clear()
    return new_edges


def Interdict(
    n,
    solver,
    verbose,
    edges,
    new_edges,
    mzn_edges,
    states,
    infected_nodes,
    risk_edges,
    interdiction_type,
    b,
    rng,
    layout,
):
    T = set()
    rem_edges = []
    match interdiction_type:
        case "edge mzn":
            T = determine_T(mzn_edges, states)
            T = set(T) - set(infected_nodes)
            new_edges = interdiction_minizinc(
                solver_name=solver,
                num_nodes=n,
                budget=b,
                infected_nodes=infected_nodes,  
                critical_nodes=T,
                graph_edges=mzn_edges,
                interdiction_type="edge",
                displ=verbose,
                layout=layout,
                seed=rng.integers(0, seed_selection),
            )
            node_aware_cost = {(i, j): c for i, j, c in edges}
            new_edges = [(i, j, node_aware_cost.get((i, j), c)) for i, j, c in new_edges]

        case "node edge mzn":
            T = determine_T(edges, states)
            T = set(T) - set(infected_nodes)
            new_edges = interdiction_minizinc(
                solver_name=solver,
                num_nodes=n,
                budget=b,
                infected_nodes=infected_nodes,  
                critical_nodes=T,
                graph_edges=edges,
                interdiction_type="edge",
                displ=verbose,
                layout=layout,
                seed=rng.integers(0, seed_selection),
            )


        case "edge":
            if len(risk_edges) > b:
                risk_edge_list = list(risk_edges)
                rng.shuffle(risk_edge_list)
                rem_edges = set(risk_edge_list[:b])
            else:
                rem_edges = risk_edges.copy()

        case "semi edge":
            if len(risk_edges) > b:
                rem_edges = determine_k_dangerous_edges(edges, risk_edges, states, b)
            else:
                rem_edges = risk_edges.copy()

                # Remove the selected edges
    Remove_interdicted_edges(rem_edges, new_edges)
    return T, new_edges


def pad_budget(row, target_len):
    local_row = list(row)

    while len(local_row) < target_len:
        local_row.append(local_row[-1])
    return local_row


# Select edges
edges = []
with open("edges", "r") as f:
    text = "\n".join(
        line for line in f if line.strip() and not line.lstrip().startswith("#")
    )
edges = ast.literal_eval(text)

n=0
for edge in edges:
    i, _ = edge
    if i > n:
        n=int(i)
n+=1

layout = None
results = {interdiction_type: [] for interdiction_type in interdiction_types}
seeds = np.random.SeedSequence(42)
infected_percentages = []
infected_nodes = {analyse_graph(n, edges)}  
print(f"Infected nodes = {infected_nodes}")
minizinc_edges = test(edges, np.random.default_rng(seeds.spawn(1)[0]))
edges, node_centrality_weights= node_edge_costs(minizinc_edges, a=node_importance)

if use_lame:
    nr_of_lame = int(n * lame)
    lame_rng = np.random.default_rng(seeds.spawn(1)[0])
    lame_users = lame_rng.integers(0, n, nr_of_lame)
    lame_set = set(lame_users)
    edges = [
        (i, j, 0 if i in lame_set else c)
        for i, j, c in edges
    ]


average_time=[]

# --- Run multiple times with new start infection ----------------------------------
for run_idx, run_seed in enumerate(seeds.spawn(runs), start=1):
    start_seed, time_seed, interdict_seed, infection_simulaiton_seed = (
        run_seed.spawn(4)
    )
    
    # --- Common start before interdiction ----------------------------------------
    start_edges, head_start, states, common_start = Determine_Start_Infection(
        n=n,
        spread=spread,
        early_stop=early_stop,
        infected_nodes=infected_nodes,
        edges=edges,
        verbose=verbose,
        rng=np.random.default_rng(start_seed),
        layout=layout,
        fixed=fixed,
    )
    # print("is start_edges == edges:", start_edges == edges)
    if verbose == 1:
        layout = show_weighted(n, start_edges, states)

    infected_set = set(states[1])
    suceptible_set = set(states[0])
    infected_percentage = len(states[1]) / n * 100
    infected_percentages.append(infected_percentage)
    start_edges, risk_edges = Set_Up_Graph(start_edges, infected_set, suceptible_set)
    mzn_start_edges, _ = Set_Up_Graph(minizinc_edges, infected_set, suceptible_set)
    budget_max = len(risk_edges)
    
    # --- Determine time until complete infection ----------------------------------------
    t = Determine_Infection_Time(
        n=n,
        spread=spread,
        repr=repr,
        verbose=verbose,
        edges=start_edges,
        layout=layout,
        infected_nodes=infected_set,
        rng=np.random.default_rng(time_seed),
        fixed=fixed,
    )
    average_time.append(t)

    # --- Print initial graph stats ----------------------------------------
    print(f"Run {run_idx}/{runs}")
    print("Infected percentage: ", (infected_percentage))
    print("Infected edges: ", budget_max)

    # --- Prepare a common random sequence ---------------------------------
    seed_matrix = np.random.default_rng(infection_simulaiton_seed).integers(
        0, seed_selection, size=(budget_max + 1, repr)
    )
    interdict_rng = np.random.default_rng(interdict_seed)

    # --- Evaluate each type of interdiction -------------------------------
    for interdiction_type in interdiction_types:

        data_average = []
        for b in range(budget_max + 1):
            # data=[]
            # for _ in range(repr):
            new_edges = start_edges.copy() if interdiction_type != "edge mzn" and interdiction_type != "node edge mzn" else []

            T , new_edges = Interdict(
                    n=n,
                    solver=solver,
                    verbose=verbose,
                    edges=start_edges,
                    new_edges=new_edges,
                    mzn_edges=mzn_start_edges,
                    states=states,
                    infected_nodes=infected_set,
                    risk_edges=risk_edges,
                    interdiction_type=interdiction_type,
                    b=b,
                    rng=interdict_rng,
                    layout=layout,
            )

            data_average.append(
                    Simulate_Infection(
                        n=n,
                        spread=spread,
                        b=b,
                        verbose=verbose,
                        layout=layout,
                        T=T,
                        infected_nodes=infected_set,
                        common_start=common_start,
                        remaining_time=t,
                        graph_edges=new_edges,
                        seed_matrix=seed_matrix,
                        fixed=fixed,
                    )
            )
            # if interdiction_type=="edge mzn":
            #     if b==19 or b==20:print("\nb=",b,"\n", data_average[-1])
            # data_average.append(np.mean(data,axis=1))
        Person_time = np.array(np.sum(data_average, axis=1), dtype=float)
        score = 1 - Person_time / Person_time[0]

        results[interdiction_type].append(score)

# --- Stats ------------------------------------
flatten_results = [
    rows for rows_per_method in results.values() for rows in rows_per_method
]
max_budget = max(len(rows) for rows in flatten_results)
print("t", np.mean(average_time))
plt.figure(figsize=(10, 6))
result_path = f"res/{n}_{int(early_stop[1])}_{node_importance}.txt"
with open(result_path, "w") as result_file:
    result_file.write(f"t={np.mean(average_time)}\n")
    for interdiction_type in interdiction_types:
        padded_results = np.array(
            [pad_budget(row, max_budget) for row in results[interdiction_type]]
        )

        mean = np.mean(padded_results, axis=0)
        plt.plot(mean, marker="o", linewidth=2, label=interdiction_type)

        b_30 = next((b for b, r in enumerate(mean) if r >= 0.3), None)
        b_50 = next((b for b, r in enumerate(mean) if r >= 0.5), None)
        b_70 = next((b for b, r in enumerate(mean) if r >= 0.7), None)

        print(f"\n{interdiction_type}")
        print("b 30: ", b_30, "\nb 50: ", b_50, "\nb 70: ", b_70)
        print(f"{interdiction_type}=", mean)

        result_file.write(f"\n{interdiction_type}\n")
        result_file.write(f"b 30: {b_30}\nb 50: {b_50}\nb 70: {b_70}\n")
        result_file.write(f"{interdiction_type}= {mean}\n")

# --- Plot the result -------------------------------
mean_infected_at_interdiciton = np.mean(infected_percentages)
plt.xlabel("Budget")
plt.ylabel("ExposureReduction")
plt.title(
    f"ExposureReduction over varying {interdiction_type} interdiction"
    f"budgets at {mean_infected_at_interdiciton}% infection at interdiction"
)
plt.grid(True, alpha=0.3)
plt.legend()

plt.savefig(f"res/{n}_{int(early_stop[1])}_{node_importance}.png",dpi=1200,bbox_inches='tight')

plt.show()
