# Pipeline Context: Graph Interdiction Experiment

This document describes the full pipeline starting from `Evaluation_model.py`, intended as context for a Claude agent working on this codebase.

---

## Overview

The project evaluates four **network interdiction strategies** for containing a spreading infection on a directed weighted graph. For each strategy and each budget level, it measures how much infection exposure is reduced compared to doing nothing. The output is a plot and text file in `res/`.

---

## File Map

| File | Role |
|---|---|
| `Evaluation_model.py` | Main orchestration script (entry point) |
| `run_minizinc.py` | Calls MiniZinc CP solver for optimal interdiction |
| `Solver_2.mzn` | MiniZinc model (M passed externally) |
| `Solver.mzn` | Older MiniZinc model (M computed internally as sum of all costs) |
| `Simulation.py` | `cascade()` — SI infection spread simulation |
| `Generate_cost_edges.py` | Edge cost generation and node-centrality weighting |
| `random_graph.py` | Graph utilities: `determine_T`, `determine_k_dangerous_edges`, `analyse_graph`, display functions |
| `edges` | Input graph: a Python list literal of `(i, j)` or `(i, j, c)` tuples |
| `res/` | Output directory for result `.txt` and `.png` files |

---

## Stage 1 — Graph Loading and Preprocessing (`Evaluation_model.py`, lines 244–275)

### Input

The `edges` file is read as a Python literal (via `ast.literal_eval`). It is a list of directed edge tuples. Lines starting with `#` are stripped. The edges may be unweighted `(i, j)` or weighted `(i, j, c)`.

```
edges = [(i, j), ...] or [(i, j, c), ...]
```

Node count `n` is inferred as `max(i for i, _ in edges) + 1`.

### Initial infected node

`analyse_graph(n, edges)` (`random_graph.py`) builds a `nx.DiGraph` and returns the node with the highest eigenvector centrality. This becomes the single initial infection seed.

### Edge cost assignment — `Generate_cost_edges.test(edges, rng)`

Called once on the raw `edges`. For each undirected pair `{i, j}`, assigns a single random cost in `[1, 99]` (shared by both directions). Produces `minizinc_edges` — a list of `(i, j, c)` triples with symmetric costs.

### Node-aware cost blending — `Generate_cost_edges.node_edge_costs(minizinc_edges, a=node_importance)`

Blends edge costs with eigenvector centrality of target nodes.

```
r[j] = (rank[j] - 1) / (n - 1)   # 0 = lowest centrality, ~1 = highest
p_edge = 1 - c/100                 # edge cost as probability-to-spread proxy
p_new  = r[j] * a + p_edge * (1-a)
c_new  = max(1, int((1 - p_new) * 100))
```

`node_importance` (default `0.5`) controls how much node centrality blends in. Output is `edges` (used by `"node edge mzn"`) and `node_centrality_weights`.

**Key distinction:**
- `minizinc_edges` — costs are purely random (symmetric per undirected pair). Used by `"edge mzn"`.
- `edges` — costs are centrality-blended (asymmetric after blending). Used by `"node edge mzn"` and the heuristic strategies.

---

## Stage 2 — Outer Run Loop (`Evaluation_model.py`, lines 281–385)

The experiment repeats `runs` times (default 30). Each run uses a fresh random seed sequence.

### Per-run sub-stages:

#### 2a. Determine Common Start — `Determine_Start_Infection()`

Calls `cascade()` repeatedly until the infected fraction is **below** `early_stop[1]` percent (default 30%). This ensures a consistent low-infection starting point.

Returns:
- `start_edges` — the edge list at the moment interdiction begins
- `states` — `[susceptible_set, infected_set, target_set]`
- `head_start` — infected-over-time list up to the stop point (the "common start" trajectory)
- `end_time_step` — how many steps the cascade ran

The `common_start` prefix is **shared across all interdiction strategies**, ensuring fair comparison.

#### 2b. Determine Infection Time — `Determine_Infection_Time()`

Runs `cascade()` with `repr` repetitions (default 30) from the current infected state, with `early_stop=(True, 100)` (run to completion). Returns the **mean** time to full infection, used as the horizon `t` for the comparative simulations.

#### 2c. Build Candidate Edge Sets

```python
start_edges, risk_edges = Set_Up_Graph(start_edges, infected_set, susceptible_set)
mzn_start_edges, _ = Set_Up_Graph(minizinc_edges, infected_set, susceptible_set)
budget_max = len(risk_edges)
```

`risk_edges` = edges from an infected node to a susceptible node (the only edges that can spread infection).

---

## Stage 3 — Interdiction Loop (per strategy, per budget)

For each `interdiction_type` and each `b` in `range(0, budget_max + 1)`:

1. **`Interdict()`** → selects edges to remove, returns updated `new_edges` and target set `T`
2. **`Simulate_Infection()`** → runs `cascade()` `repr` times on `new_edges`, returns mean infected-count over time

### Interdiction Types

#### `"edge"` — Random Baseline
Randomly shuffles `risk_edges` and removes the first `b`.

#### `"semi edge"` — Eigenvector Heuristic
Calls `determine_k_dangerous_edges(edges, risk_edges, states, b)` (`random_graph.py`).  
Builds a `nx.DiGraph` from the healthy subgraph, computes eigenvector centrality per strongly-connected component, and picks the `b` risk edges whose **target node** has highest centrality.

#### `"edge mzn"` — MiniZinc CP (Uniform Costs)
1. Computes `T = determine_T(mzn_edges, states) - infected_nodes`
2. Calls `interdiction_minizinc(..., graph_edges=mzn_start_edges, node_b_weights=True, M=diameter)`
   - `node_b_weights=True` overrides all edge costs to `1` before passing to MiniZinc (treats budget as edge count)
   - `M = nx.diameter(G) * max(cost)` (per line 147 of `run_minizinc.py`)
3. After MiniZinc returns, re-applies node-aware costs: `node_aware_cost = {(i,j): c for i,j,c in edges}` — so the simulation uses real costs even though the solver used uniform ones.

#### `"node edge mzn"` — MiniZinc CP (Node-Weighted Costs)
1. Computes `T = determine_T(edges, states) - infected_nodes` (uses centrality-blended costs)
2. Calls `interdiction_minizinc(..., graph_edges=start_edges)` — edge costs are already node-centrality blended; `node_b_weights=False`

---

## Stage 4 — MiniZinc Solver (`run_minizinc.py` → `interdiction_minizinc()`)

### Problem Formulation

Network interdiction modeled as a max-flow dual LP. The goal is to select up to `K` edges from the infected frontier to maximize the disruption of flow from infected sources `S` to target nodes `T`.

### Node classification via `b` vector

```
b[v] = +1  if v in S (infected source)
b[v] = -1  if v in T (critical target node)
b[v] =  0  otherwise
```

`S` = current infected set.  
`T` = `determine_T()` output — top ~20% of nodes by voterank on the susceptible subgraph, minus infected nodes.

### Candidate edges

`E_can` = subset of edges where `tail ∈ S` and `head ∉ S` (i.e., only risk edges can be interdicted).

### Variables (`Solver_2.mzn`)

| Variable | Domain | Meaning |
|---|---|---|
| `x[e]` | {0, 1} | 1 = interdict edge e |
| `pi[v]` | [-2M, M] | dual price of node v |
| `beta[e]` | [0, M] | complementary slack |
| `w[e]` | [0, M] | linearization auxiliary |

### Constraints

```
∀ s ∈ S:  pi[s] = 0                          (source potentials fixed)
          sum(x[e] for e in E_can) = K        (exact budget)
∀ e ∉ E_can: x[e] = 0                        (only frontier edges can be cut)
∀ e:  pi[i[e]] - pi[j[e]] - beta[e] ≤ c[e]  (dual flow constraint)
∀ e:  beta[e] - M*x[e] ≤ w[e]               (big-M linearization)
```

### Objective

```
maximize  sum(b[v] * pi[v]) - sum(w)
```

This maximizes the flow value between S and T after interdiction.

### M parameter

`Solver_2.mzn` receives `M` from Python (line 147 of `run_minizinc.py`):
```python
instance["M"] = max(cost) * M   # M here is the graph diameter
```
`Solver.mzn` (older version) sets `M = sum(c[e] for e in E)` internally — larger and potentially looser.

### Output

`result["x"]` is a binary array over all edges. Interdicted edge indices → `interdicted_idxs`. Returns `edge_remaining` (the list of non-removed edges).

---

## Stage 5 — Scoring and Output

### Metric: ExposureReduction

```python
Person_time = np.sum(data_average, axis=1)   # sum of infected-counts per budget b
score = 1 - Person_time / Person_time[0]     # relative to no-interdiction (b=0)
```

`score[b]` = fraction of exposure eliminated by budget `b`. Higher is better. `score[0] = 0` by construction.

### Output files

- `res/{n}_{early_stop_threshold}_{node_importance}.txt` — mean score, budget thresholds for 30%/50%/70% reduction
- `res/{n}_{early_stop_threshold}_{node_importance}.png` — line plot of score vs budget per strategy

---

## Key Parameters (top of `Evaluation_model.py`)

| Parameter | Default | Meaning |
|---|---|---|
| `spread` | 0.2 | Base infection probability (when `fixed=True`) |
| `fixed` | False | If False, spread probability = `1 - c/max_tie` (edge cost controls transmission) |
| `max_tie` | 100 | Denominator for cost-based spread: `rand >= c/max_tie` → infect |
| `node_importance` | 0.5 | Weight of node centrality vs edge cost in blended costs (`a` parameter) |
| `early_stop` | (True, 30) | Stop common-start cascade when infection exceeds 30% |
| `runs` | 30 | Number of independent outer repetitions |
| `repr` | 30 | Cascade repetitions per budget evaluation |
| `solver` | `"cplex"` | MiniZinc solver backend |
| `interdiction_types` | `["edge", "semi edge", "edge mzn", "node edge mzn"]` | Strategies compared |
| `use_lame` | False | If True, sets cost=0 for a fraction of nodes (lame/non-spreader nodes) |

---

## Spread Model (`Simulation.py` — `cascade()`)

SI model on a directed weighted graph:

```python
for each risk edge (i, j, c):
    rand = rng.uniform(0, 1)
    if fixed:
        infect j if rand <= spread_p
    else:
        infect j if rand >= c / max_tie   # low cost → high spread probability
```

High edge cost = harder to infect through (costly edges are safer).  
The simulation returns `(edges, sets, infected_over_time, end_time_step)`.

---

## `determine_T()` — Target Node Selection (`random_graph.py`)

Filters the graph to **susceptible nodes only**, builds an unweighted `nx.Graph`, and selects the top `n//5` nodes by **voterank** (an iterative voting-based influence measure). These are the nodes the interdiction solver tries to protect.

---

## Data Flow Diagram

```
edges (file)
    │
    ├─ test() ──────────────────────────────► minizinc_edges  (symmetric random costs)
    │                                                │
    └─ node_edge_costs() ──────────────────► edges  (centrality-blended costs, asymmetric)
                                                     │
                              ┌──────────────────────┤
                              │                      │
                    "edge mzn"             "node edge mzn"
                    uses mzn_edges         uses edges
                    costs overridden to 1  real blended costs
                              │                      │
                              └──────────┬───────────┘
                                         │
                              interdiction_minizinc()
                                   │
                              Solver_2.mzn (MiniZinc CP)
                                   │
                              edge_remaining
                                   │
                              cascade() × repr times
                                   │
                              ExposureReduction score
                                   │
                          res/{n}_{thresh}_{alpha}.{png,txt}
```

---

## Common Gotchas for a Claude Agent

- **Two edge lists in flight**: `edges` (node-weighted, used for simulation and `"node edge mzn"`) vs `minizinc_edges` (symmetric costs, used for `"edge mzn"`). They differ after `node_edge_costs()`.
- **`"edge mzn"` post-processing**: After MiniZinc returns `new_edges`, the caller in `Evaluate_model.py` re-applies node-aware costs (line 195–196). The solver optimized with uniform costs but the simulation uses real costs.
- **`b` vector**: In MiniZinc, `b[v] = +1` for infected sources, `-1` for targets. The objective maximizes `sum(b[v]*pi[v])` — infected sources contribute positively, targets negatively. This is a max-flow dual.
- **`M` in `Solver_2.mzn`**: Passed as `max(cost) * diameter`. In `Solver.mzn` it's `sum(all costs)`. Using the externalized M gives tighter bounds and faster solve.
- **Budget b=0**: No edges removed. `score[0] = 0` always. Used as baseline for normalization.
- **`node_b_weights=True`**: When set, `run_minizinc.py` replaces all costs with 1 before passing to MiniZinc. The solver then treats budget as a pure edge-count constraint rather than cost-weighted.
- **`fixed` mode**: When `fixed=False` (default), edge cost controls spread. When `fixed=True`, all edges spread with probability `spread` regardless of cost — the cost weighting becomes irrelevant to simulation outcomes.
