"""
Quick demo of step 5 experiments (reduced params to verify pipeline).
Uses runs=10, repr=20, early_stop=[10] only.
For thesis-quality results, run run_step5_experiments.py (runs=50, repr=50, early_stop=[10,20,30]).
"""
import ast, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from random_graph import determine_T, analyse_graph, determine_k_dangerous_edges
from Generate_cost_edges import node_edge_costs, test
from run_minizinc import interdiction_minizinc
from Simulation import cascade

# --- Quick params ---
max_tie = 99 + 1
spread = 0.2
fixed = False
node_importance = 0.5
repr_runs = 20
outer_runs = 10
solver = "cplex"
seed_selection = 2 ** 32
verbose = 0
early_stop_values = [10]   # just one threshold for speed
interdiction_types = ["edge", "semi edge", "edge mzn", "node edge mzn"]

OUTPUT_DIR = "step5_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def determine_start_infection(n, early_stop, infected_nodes, sim_edges, rng):
    pct = 100
    limit = early_stop[1] + 3
    while pct > limit:
        new_edges, states, head_start, end_t = cascade(
            simulation_time=100, n=n, graph_edges=sim_edges,
            init_infected=infected_nodes, verbose_displ=0,
            early_stop=early_stop, rng=rng, layout=None,
            max_tie=max_tie, spread_p=spread, fixed=fixed,
        )
        pct = len(states[1]) / n * 100
    return new_edges, end_t, states, head_start


def determine_infection_time(n, sim_edges, infected_nodes, rng):
    t_avg = []
    for _ in range(repr_runs):
        _, _, _, t_i = cascade(
            simulation_time=100, n=n, graph_edges=sim_edges,
            init_infected=infected_nodes, verbose_displ=0, layout=None,
            early_stop=(True, 100), rng=rng, max_tie=max_tie,
            spread_p=spread, fixed=fixed,
        )
        t_avg.append(t_i)
    return int(np.mean(t_avg))


def simulate_infection(n, b, T, infected_nodes, common_start, remaining_time, graph_edges, seed_matrix):
    data = []
    for seed in seed_matrix[b]:
        _, _, infected_over_time, _ = cascade(
            simulation_time=remaining_time, n=n, graph_edges=graph_edges,
            init_infected=infected_nodes, T_set=T, verbose_displ=0, layout=None,
            rng=np.random.default_rng(seed), max_tie=max_tie, spread_p=spread, fixed=fixed,
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
            reverse = [cc for jj, ii, cc in all_sim_edges if jj == j and ii == i]
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
                solver_name=solver, num_nodes=n, budget=b,
                infected_nodes=infected_nodes, critical_nodes=T,
                graph_edges=mzn_edges, interdiction_type="edge",
                displ=verbose, layout=None, seed=rng.integers(0, seed_selection),
            )
            node_aware_cost = {(i, j): c for i, j, c in sim_edges}
            new_edges = [(i, j, node_aware_cost.get((i, j), c)) for i, j, c in new_edges]
        case "node edge mzn":
            T = determine_T(sim_edges, states)
            T = set(T) - set(infected_nodes)
            new_edges = interdiction_minizinc(
                solver_name=solver, num_nodes=n, budget=b,
                infected_nodes=infected_nodes, critical_nodes=T,
                graph_edges=sim_edges, interdiction_type="edge",
                displ=verbose, layout=None, seed=rng.integers(0, seed_selection),
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
    r = list(row)
    while len(r) < target_len:
        r.append(r[-1])
    return r


def parse_all_graphs(filepath):
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
            except Exception:
                pass
    return graphs


def run_one(raw_edges, n, early_stop_pct):
    early_stop = (True, early_stop_pct)
    print(f"\n{'='*60}\n  n={n}, early_stop={early_stop_pct}%, runs={outer_runs}, repr={repr_runs}\n{'='*60}")
    sys.stdout.flush()

    seeds = np.random.SeedSequence(42)
    minizinc_edges = test(raw_edges, np.random.default_rng(seeds.spawn(1)[0]))
    sim_edges, _ = node_edge_costs(minizinc_edges, a=node_importance)
    init_inf = {analyse_graph(n, raw_edges)}
    print(f"  Initial infected node: {init_inf}")

    results = {it: [] for it in interdiction_types}
    infected_percentages = []
    average_time = []

    for run_idx, run_seed in enumerate(seeds.spawn(outer_runs), start=1):
        start_seed, time_seed, interdict_seed, sim_seed_master = run_seed.spawn(4)

        start_edges, _, states, common_start = determine_start_infection(
            n=n, early_stop=early_stop, infected_nodes=init_inf,
            sim_edges=sim_edges, rng=np.random.default_rng(start_seed),
        )
        infected_set = set(states[1])
        susceptible_set = set(states[0])
        infected_pct = len(states[1]) / n * 100
        infected_percentages.append(infected_pct)

        filtered_sim, risk_edges = set_up_graph(start_edges, infected_set, susceptible_set)
        filtered_mzn, _ = set_up_graph(minizinc_edges, infected_set, susceptible_set)
        budget_max = len(risk_edges)

        t = determine_infection_time(
            n=n, sim_edges=filtered_sim, infected_nodes=infected_set,
            rng=np.random.default_rng(time_seed),
        )
        average_time.append(t)

        print(f"  Run {run_idx}/{outer_runs} | infected={infected_pct:.1f}% | budget_max={budget_max} | t={t}")
        sys.stdout.flush()

        seed_matrix = np.random.default_rng(sim_seed_master).integers(
            0, seed_selection, size=(budget_max + 1, repr_runs)
        )
        interdict_rng = np.random.default_rng(interdict_seed)

        for it in interdiction_types:
            data_average = []
            for b in range(budget_max + 1):
                cur = filtered_sim.copy() if it not in ("edge mzn", "node edge mzn") else []
                T, cur_new = interdict(
                    n=n, sim_edges=filtered_sim, mzn_edges=filtered_mzn,
                    new_edges=cur, states=states, infected_nodes=infected_set,
                    risk_edges=risk_edges, interdiction_type=it, b=b,
                    rng=interdict_rng, all_sim_edges=sim_edges,
                )
                data_average.append(simulate_infection(
                    n=n, b=b, T=T, infected_nodes=infected_set,
                    common_start=common_start, remaining_time=t,
                    graph_edges=cur_new, seed_matrix=seed_matrix,
                ))
            pt = np.array(np.sum(data_average, axis=1), dtype=float)
            score = 1 - pt / pt[0]
            results[it].append(score)

    # --- Stats & plot ---
    flatten = [r for rows in results.values() for r in rows]
    max_budget = max(len(r) for r in flatten)
    mean_infected = np.mean(infected_percentages)
    mean_t = np.mean(average_time)

    plt.figure(figsize=(10, 6))
    print(f"\n  Results for n={n}, early_stop={early_stop_pct}%")
    print(f"  Mean infected at intervention: {mean_infected:.2f}%")
    print(f"  Mean t (remaining steps):      {mean_t:.1f}")
    print(f"  {'Method':<18} {'b@30%':>7} {'b@50%':>7} {'b@70%':>7}")
    print(f"  {'-'*45}")

    all_stats = {}
    for it in interdiction_types:
        padded = np.array([pad_budget(r, max_budget) for r in results[it]])
        mean = np.mean(padded, axis=0)
        std = np.std(padded, axis=0)
        plt.plot(mean, marker="o", linewidth=2, label=it)
        plt.fill_between(range(len(mean)), mean - std, mean + std, alpha=0.15)
        b30 = next((b for b, r in enumerate(mean) if r >= 0.3), None)
        b50 = next((b for b, r in enumerate(mean) if r >= 0.5), None)
        b70 = next((b for b, r in enumerate(mean) if r >= 0.7), None)
        all_stats[it] = {"b_30": b30, "b_50": b50, "b_70": b70}
        print(f"  {it:<18} {str(b30):>7} {str(b50):>7} {str(b70):>7}")

    sys.stdout.flush()

    plt.xlabel("Budget (edges removed)")
    plt.ylabel("Exposure Reduction Score")
    plt.title(
        f"Step 5 – Node & Edge Weighted | n={n}, early_stop={early_stop_pct}%\n"
        f"Mean infection at intervention: {mean_infected:.1f}% | "
        f"runs={outer_runs}, repr={repr_runs} [QUICK DEMO]"
    )
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    fname = f"{OUTPUT_DIR}/{n}n_{early_stop_pct}pct_quick.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved: {fname}")
    sys.stdout.flush()
    return all_stats


if __name__ == "__main__":
    import sys
    # Optionally pass graph sizes as CLI args: python run_step5_quick.py 100 500
    requested = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None

    print("Parsing graphs...")
    all_graphs = parse_all_graphs("edges")
    sizes = sorted(all_graphs.keys())
    if requested:
        sizes = [s for s in sizes if s in requested]
    print(f"Will run for n in {sizes}")

    for n in sizes:
        for esp in early_stop_values:
            run_one(all_graphs[n], n, esp)

    print("\nDone. Plots saved to:", OUTPUT_DIR)
