"""
Step 5 experiment runner: Node and edge weighted network
Compares all 4 interdiction methods on weighted networks where
node influence/infectivity is incorporated via node-aware edge costs.

Methods compared:
  edge        - random edge removal
  semi edge   - eigenvector-guided edge removal
  edge mzn    - MiniZinc with node-aware costs (simulation costs)
  node edge mzn - MiniZinc with original random costs

Runs experiments for multiple graph sizes (100, 500, 1000 nodes)
and multiple early-stop thresholds (10%, 20%, 30% infected).
"""

import ast
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend so it doesn't block
import matplotlib.pyplot as plt

from random_graph import determine_T, analyse_graph, determine_k_dangerous_edges
from Generate_cost_edges import node_edge_costs, test
from run_minizinc import interdiction_minizinc
from Simulation import cascade

# ---- Experiment parameters ----
max_tie = 99 + 1
spread = 0.2
fixed = False
node_importance = 0.8
repr_runs = 50       # simulation replicas per budget level
outer_runs = 50      # independent start-infection draws
solver = "cplex"
seed_selection = 2 ** 32
verbose = 0
early_stop_values = [10, 20, 30]   # % infected at intervention
interdiction_types = ["edge", "semi edge", "edge mzn", "node edge mzn"]

OUTPUT_DIR = "step5_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---- Helpers (same logic as Evaluation_model.py, but self-contained) ----

def determine_start_infection(n, early_stop, infected_nodes, sim_edges, rng):
    pct = 100
    limit = early_stop[1] + 3
    while pct > limit:
        new_edges, states, head_start, end_t = cascade(
            simulation_time=100,
            n=n,
            graph_edges=sim_edges,
            init_infected=infected_nodes,
            verbose_displ=0,
            early_stop=early_stop,
            rng=rng,
            layout=None,
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed,
        )
        pct = len(states[1]) / n * 100
    return new_edges, end_t, states, head_start


def determine_infection_time(n, sim_edges, infected_nodes, rng):
    t_avg = []
    for _ in range(repr_runs):
        _, _, _, t_i = cascade(
            simulation_time=100,
            n=n,
            graph_edges=sim_edges,
            init_infected=infected_nodes,
            verbose_displ=0,
            layout=None,
            early_stop=(True, 100),
            rng=rng,
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed,
        )
        t_avg.append(t_i)
    return int(np.mean(t_avg))


def simulate_infection(n, b, T, infected_nodes, common_start, remaining_time, graph_edges, seed_matrix):
    data = []
    for seed in seed_matrix[b]:
        _, _, infected_over_time, _ = cascade(
            simulation_time=remaining_time,
            n=n,
            graph_edges=graph_edges,
            init_infected=infected_nodes,
            T_set=T,
            verbose_displ=0,
            layout=None,
            rng=np.random.default_rng(seed),
            max_tie=max_tie,
            spread_p=spread,
            fixed=fixed,
        )
        data.append(infected_over_time)
    means = np.mean(data, axis=0)
    return [*common_start.copy(), *means]


def set_up_graph(sim_edges, infected_set, susceptible_set):
    risk_edges = set()
    new_edges = list(sim_edges.copy())
    for edge in sim_edges:
        i, j, _ = edge
        if i in infected_set and j in infected_set:
            new_edges.remove(edge)
        if i in infected_set and j in susceptible_set:
            risk_edges.add(edge)
    return new_edges, risk_edges


def remove_interdicted_edges(rem_edges, new_edges, all_sim_edges):
    if len(rem_edges) > 0:
        for i, j, c in rem_edges:
            # look up the reverse-edge cost from the full weighted graph
            reverse = [(cc) for jj, ii, cc in all_sim_edges if jj == j and ii == i]
            c_2 = reverse[0] if reverse else c
            if (i, j, c) in new_edges:
                new_edges.remove((i, j, c))
            if (j, i, c_2) in new_edges:
                new_edges.remove((j, i, c_2))
        rem_edges.clear()
    return new_edges


def interdict(n, sim_edges, mzn_edges, new_edges, states, infected_nodes, risk_edges,
              interdiction_type, b, rng, all_sim_edges):
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
                layout=None,
                seed=rng.integers(0, seed_selection),
            )
            node_aware_cost = {(i, j): c for i, j, c in sim_edges}
            new_edges = [(i, j, node_aware_cost.get((i, j), c)) for i, j, c in new_edges]
        case "node edge mzn":
            T = determine_T(sim_edges, states)
            T = set(T) - set(infected_nodes)
            new_edges = interdiction_minizinc(
                solver_name=solver,
                num_nodes=n,
                budget=b,
                infected_nodes=infected_nodes,
                critical_nodes=T,
                graph_edges=sim_edges,
                interdiction_type="edge",
                displ=verbose,
                layout=None,
                seed=rng.integers(0, seed_selection),
            )
        case "edge":
            if len(risk_edges) > b:
                risk_list = list(risk_edges)
                rng.shuffle(risk_list)
                rem_edges = set(risk_list[:b])
            else:
                rem_edges = risk_edges.copy()
        case "semi edge":
            if len(risk_edges) > b:
                rem_edges = determine_k_dangerous_edges(sim_edges, risk_edges, states, b)
            else:
                rem_edges = risk_edges.copy()

    remove_interdicted_edges(rem_edges, new_edges, all_sim_edges)
    return T, new_edges


def pad_budget(row, target_len):
    local_row = list(row)
    while len(local_row) < target_len:
        local_row.append(local_row[-1])
    return local_row


# ---- Graph parsing ----

def parse_all_graphs(filepath):
    """Return dict {n_nodes: [(i,j), ...]} for every graph in the edges file."""
    graphs = {}
    with open(filepath, "r") as f:
        lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        data_part = None
        if stripped.startswith("#"):
            rest = stripped[1:].strip()
            if rest.startswith("["):
                data_part = rest
        else:
            if stripped.startswith("["):
                data_part = stripped
        if data_part:
            try:
                edge_list = ast.literal_eval(data_part)
                n = max(max(i, j) for i, j in edge_list) + 1
                graphs[n] = edge_list
                print(f"  Found graph: n={n}, edges={len(edge_list)}")
            except Exception as e:
                pass
    return graphs


# ---- Main experiment loop ----

def run_experiment(raw_edges, n, early_stop_pct, run_seed_base=42):
    early_stop = (True, early_stop_pct)
    print(f"\n{'='*60}")
    print(f"  n={n}, early_stop={early_stop_pct}%")
    print(f"{'='*60}")
    sys.stdout.flush()

    seeds = np.random.SeedSequence(run_seed_base)

    # Build weighted edges
    minizinc_edges = test(raw_edges, np.random.default_rng(seeds.spawn(1)[0]))
    sim_edges = node_edge_costs(minizinc_edges, a=node_importance)

    # Initial infected node (highest eigenvector centrality)
    infected_nodes_init = {analyse_graph(n, raw_edges)}
    print(f"  Initial infected node: {infected_nodes_init}")
    sys.stdout.flush()

    results = {it: [] for it in interdiction_types}
    infected_percentages = []
    average_time = []

    for run_idx, run_seed in enumerate(seeds.spawn(outer_runs), start=1):
        start_seed, time_seed, interdict_seed, sim_seed_master = run_seed.spawn(4)

        # Common pre-interdiction infection
        start_edges, head_start, states, common_start = determine_start_infection(
            n=n,
            early_stop=early_stop,
            infected_nodes=infected_nodes_init,
            sim_edges=sim_edges,
            rng=np.random.default_rng(start_seed),
        )

        infected_set = set(states[1])
        susceptible_set = set(states[0])
        infected_pct = len(states[1]) / n * 100
        infected_percentages.append(infected_pct)

        filtered_sim_edges, risk_edges = set_up_graph(start_edges, infected_set, susceptible_set)
        filtered_mzn_edges, _ = set_up_graph(minizinc_edges, infected_set, susceptible_set)
        budget_max = len(risk_edges)

        # Time to full infection
        t = determine_infection_time(
            n=n,
            sim_edges=filtered_sim_edges,
            infected_nodes=infected_set,
            rng=np.random.default_rng(time_seed),
        )
        average_time.append(t)

        print(f"  Run {run_idx}/{outer_runs} | infected={infected_pct:.1f}% | risk_edges={budget_max} | t={t}")
        sys.stdout.flush()

        seed_matrix = np.random.default_rng(sim_seed_master).integers(
            0, seed_selection, size=(budget_max + 1, repr_runs)
        )
        interdict_rng = np.random.default_rng(interdict_seed)

        for it in interdiction_types:
            data_average = []
            for b in range(budget_max + 1):
                cur_sim_edges = filtered_sim_edges.copy() if it not in ("edge mzn", "node edge mzn") else []
                T, cur_new_edges = interdict(
                    n=n,
                    sim_edges=filtered_sim_edges,
                    mzn_edges=filtered_mzn_edges,
                    new_edges=cur_sim_edges,
                    states=states,
                    infected_nodes=infected_set,
                    risk_edges=risk_edges,
                    interdiction_type=it,
                    b=b,
                    rng=interdict_rng,
                    all_sim_edges=sim_edges,
                )
                data_average.append(
                    simulate_infection(
                        n=n,
                        b=b,
                        T=T,
                        infected_nodes=infected_set,
                        common_start=common_start,
                        remaining_time=t,
                        graph_edges=cur_new_edges,
                        seed_matrix=seed_matrix,
                    )
                )

            person_time = np.array(np.sum(data_average, axis=1), dtype=float)
            score = 1 - person_time / person_time[0]
            results[it].append(score)

    return results, infected_percentages, average_time


def save_plot_and_stats(results, infected_percentages, average_time, n, early_stop_pct):
    flatten = [row for rows in results.values() for row in rows]
    max_budget = max(len(r) for r in flatten)
    mean_infected = np.mean(infected_percentages)
    mean_t = np.mean(average_time)

    plt.figure(figsize=(10, 6))
    stats = {}
    for it in interdiction_types:
        padded = np.array([pad_budget(row, max_budget) for row in results[it]])
        mean = np.mean(padded, axis=0)
        std = np.std(padded, axis=0)
        plt.plot(mean, marker="o", linewidth=2, label=it)
        plt.fill_between(range(len(mean)), mean - std, mean + std, alpha=0.15)

        b_30 = next((b for b, r in enumerate(mean) if r >= 0.3), None)
        b_50 = next((b for b, r in enumerate(mean) if r >= 0.5), None)
        b_70 = next((b for b, r in enumerate(mean) if r >= 0.7), None)
        stats[it] = {"b_30": b_30, "b_50": b_50, "b_70": b_70, "mean": mean.tolist()}

    plt.xlabel("Budget (number of edges removed)")
    plt.ylabel("Exposure Reduction Score")
    plt.title(
        f"Step 5 – Node & Edge Weighted | n={n}, early_stop={early_stop_pct}%\n"
        f"Mean infection at intervention: {mean_infected:.1f}% | Mean remaining time: {mean_t:.0f} steps"
    )
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    fname = f"{OUTPUT_DIR}/{n}n_{early_stop_pct}pct.png"
    plt.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved plot: {fname}")

    # Print stats table
    print(f"\n  Results for n={n}, early_stop={early_stop_pct}%")
    print(f"  Mean infected at intervention: {mean_infected:.2f}%")
    print(f"  Mean t (remaining steps): {mean_t:.1f}")
    print(f"  {'Method':<18} {'b@30%':>7} {'b@50%':>7} {'b@70%':>7}")
    print(f"  {'-'*45}")
    for it, s in stats.items():
        b30 = str(s['b_30']) if s['b_30'] is not None else "N/A"
        b50 = str(s['b_50']) if s['b_50'] is not None else "N/A"
        b70 = str(s['b_70']) if s['b_70'] is not None else "N/A"
        print(f"  {it:<18} {b30:>7} {b50:>7} {b70:>7}")
    sys.stdout.flush()

    # Save raw data
    np.save(f"{OUTPUT_DIR}/{n}n_{early_stop_pct}pct_scores.npy",
            {it: np.array([pad_budget(r, max_budget) for r in results[it]]) for it in interdiction_types},
            allow_pickle=True)

    return stats


if __name__ == "__main__":
    print("Parsing graphs from 'edges' file...")
    all_graphs = parse_all_graphs("edges")
    sizes_to_run = sorted(all_graphs.keys())
    print(f"Found graph sizes: {sizes_to_run}")

    all_stats = {}
    for n in sizes_to_run:
        raw_edges = all_graphs[n]
        all_stats[n] = {}
        for esp in early_stop_values:
            results, inf_pcts, avg_times = run_experiment(raw_edges, n, esp)
            all_stats[n][esp] = save_plot_and_stats(results, inf_pcts, avg_times, n, esp)

    # Final summary table
    print("\n\n" + "=" * 70)
    print("STEP 5 SUMMARY TABLE")
    print("=" * 70)
    for n in sizes_to_run:
        for esp in early_stop_values:
            print(f"\n  n={n}, early_stop={esp}%")
            print(f"  {'Method':<18} {'b@30%':>7} {'b@50%':>7} {'b@70%':>7}")
            for it, s in all_stats[n][esp].items():
                b30 = str(s['b_30']) if s['b_30'] is not None else "N/A"
                b50 = str(s['b_50']) if s['b_50'] is not None else "N/A"
                b70 = str(s['b_70']) if s['b_70'] is not None else "N/A"
                print(f"  {it:<18} {b30:>7} {b50:>7} {b70:>7}")
    print("\nDone. Plots and .npy files saved to:", OUTPUT_DIR)
