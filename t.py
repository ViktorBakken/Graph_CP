from __future__ import annotations
import random
from typing import List, Tuple


Edge = Tuple[int, int, int]


def make_clusters(n: int, c: int) -> List[List[int]]:
    if n <= 0:
        raise ValueError("n must be > 0")
    if c <= 0 or c > n:
        raise ValueError("c must be in [1, n]")

    nodes = list(range(1, n + 1))
    base, rem = divmod(n, c)

    clusters = []
    idx = 0
    for i in range(c):
        size = base + (1 if i < rem else 0)
        clusters.append(nodes[idx: idx + size])
        idx += size

    return clusters


def complete_bidirectional_weighted_edges(
    nodes: List[int],
    rng: random.Random,
    wmin: int = 1,
    wmax: int = 30,
) -> List[Edge]:
    """
    Complete digraph with shared weight for (u,v) and (v,u).
    """
    edges: List[Edge] = []
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            w = rng.randint(wmin, wmax)
            edges.append((u, v, w))
            edges.append((v, u, w))
    return edges


def clustered_bidirectional_weighted_graph(
    n: int,
    c: int,
    bridges_per_adjacent_cluster_pair: int = 1,
    wmin: int = 1,
    wmax: int = 30,
    seed: int | None = 0,
) -> Tuple[List[Edge], List[List[int]]]:
    rng = random.Random(seed)
    clusters = make_clusters(n, c)

    edges: List[Edge] = []

    # Dense intra-cluster edges
    for cl in clusters:
        edges.extend(
            complete_bidirectional_weighted_edges(cl, rng, wmin, wmax)
        )

    # Sparse inter-cluster bridges (chain structure)
    for i in range(c - 1):
        A = clusters[i]
        B = clusters[i + 1]

        for _ in range(max(1, bridges_per_adjacent_cluster_pair)):
            u = rng.choice(A)
            v = rng.choice(B)
            w = rng.randint(wmin, wmax)
            edges.append((u, v, w))
            edges.append((v, u, w))

    # Remove duplicates (safe for repeated bridges)
    seen = set()
    unique_edges = []
    for u, v, w in edges:
        key = (u, v)
        if key not in seen:
            seen.add(key)
            unique_edges.append((u, v, w))

    return unique_edges, clusters


if __name__ == "__main__":
    n = 7
    c = 2

    edges, clusters = clustered_bidirectional_weighted_graph(
        n=n,
        c=c,
        bridges_per_adjacent_cluster_pair=2,
        seed=42,
    )

    print("clusters:", clusters)
    print("edges =", edges)
    # for e in edges:
    #     print(e)
