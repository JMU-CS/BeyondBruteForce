#!/usr/bin/env python3
"""Regenerate the deterministic course-created Longest Path benchmark suite.

COURSE INFRASTRUCTURE
Students may run this file to reproduce the supplied synthetic instances, but
should not edit it.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "longest_path"
INST = BENCH / "instances"

SEEDS = [11, 29, 47, 71, 101]


def write_graph(path: Path, n: int, edges) -> int:
    normalized = sorted({(min(u, v), max(u, v)) for u, v in edges if u != v})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"{n} {len(normalized)}\n")
        for u, v in normalized:
            f.write(f"{u} {v}\n")
    return len(normalized)


def relabel(n: int, edges, seed: int):
    rng = random.Random(seed)
    labels = list(range(n))
    rng.shuffle(labels)
    return [(labels[u], labels[v]) for u, v in edges]


def path_graph(n: int, seed: int | None = None):
    edges = [(i, i + 1) for i in range(n - 1)]
    return relabel(n, edges, seed) if seed is not None else edges


def star_graph(n: int, seed: int | None = None):
    edges = [(0, i) for i in range(1, n)]
    return relabel(n, edges, seed) if seed is not None else edges


def spider_graph(n: int, seed: int):
    """Three-arm tree. Return edges and its exact longest-path length."""
    if n < 4:
        raise ValueError("spider needs at least 4 vertices")
    remaining = n - 1
    q, r = divmod(remaining, 3)
    lengths = [q + (1 if i < r else 0) for i in range(3)]
    edges = []
    nxt = 1
    for length in lengths:
        prev = 0
        for _ in range(length):
            edges.append((prev, nxt))
            prev = nxt
            nxt += 1
    opt = sum(sorted(lengths, reverse=True)[:2])
    return relabel(n, edges, seed), opt


def complete_bipartite(a: int, b: int, seed: int):
    n = a + b
    edges = [(u, a + v) for u in range(a) for v in range(b)]
    smaller = min(a, b)
    larger = max(a, b)
    opt = n - 1 if smaller == larger else min(n - 1, 2 * smaller)
    return relabel(n, edges, seed), opt


def two_cliques(a: int, b: int, seed: int):
    n = a + b
    edges = []
    for start, size in ((0, a), (a, b)):
        edges.extend(
            (start + i, start + j)
            for i in range(size)
            for j in range(i + 1, size)
        )
    return relabel(n, edges, seed), max(a, b) - 1


def disjoint_paths(component_sizes: list[int], seed: int):
    n = sum(component_sizes)
    edges = []
    start = 0
    for size in component_sizes:
        edges.extend((start + i, start + i + 1) for i in range(size - 1))
        start += size
    opt = max((s - 1 for s in component_sizes), default=0)
    return relabel(n, edges, seed), opt


def planted_path_random(n: int, extra_edges: int, seed: int):
    """Connected graph with a hidden Hamiltonian path, plus random extra edges."""
    rng = random.Random(seed)
    order = list(range(n))
    rng.shuffle(order)
    edge_set = {(min(order[i], order[i + 1]), max(order[i], order[i + 1])) for i in range(n - 1)}
    target = len(edge_set) + extra_edges
    while len(edge_set) < target:
        u = rng.randrange(n)
        v = rng.randrange(n - 1)
        if v >= u:
            v += 1
        edge_set.add((min(u, v), max(u, v)))
    return list(edge_set), n - 1


def planted_path_density(n: int, p: float, seed: int):
    rng = random.Random(seed)
    order = list(range(n))
    rng.shuffle(order)
    edge_set = {(min(order[i], order[i + 1]), max(order[i], order[i + 1])) for i in range(n - 1)}
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edge_set and rng.random() < p:
                edge_set.add((u, v))
    return list(edge_set), n - 1


def add_item(suites, suite, *, item_id, filename, n, m, opt, algorithms,
             timeout, seeds=None, structure_name=None, structure_value=None,
             frontier_group=None, stop_after_timeout=False):
    item = {
        "id": item_id,
        "file": f"instances/{filename}",
        "n": n,
        "m": m,
        "known_optimum": opt,
        "algorithms": algorithms,
        "timeout": timeout,
    }
    if seeds is not None:
        item["seeds"] = seeds
    if structure_name is not None:
        item["structure_name"] = structure_name
        item["structure_value"] = structure_value
    if frontier_group is not None:
        item["frontier_group"] = frontier_group
    if stop_after_timeout:
        item["stop_after_timeout"] = True
    suites.setdefault(suite, []).append(item)


def main():
    INST.mkdir(parents=True, exist_ok=True)
    for old in INST.glob("*.txt"):
        old.unlink()

    suites = {}

    # Readiness: small, quick smoke tests spanning three graph structures.
    specs = [
        ("ready_path8", "ready_path8.txt", 8, path_graph(8, 4108), 7),
        ("ready_star9", "ready_star9.txt", 9, star_graph(9, 4209), 2),
    ]
    e, opt = complete_bipartite(3, 5, 4308)
    specs.append(("ready_bipartite_3_5", "ready_bipartite_3_5.txt", 8, e, opt))
    for item_id, fn, n, edges, opt in specs:
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "readiness", item_id=item_id, filename=fn, n=n, m=m,
                 opt=opt, algorithms=["improved", "heuristic1"], timeout=15,
                 seeds=[412])

    # Exact frontier family 1: sparse three-arm trees.  Improved path-extension
    # search should exploit sparse adjacency; complete-candidate enumeration does not.
    for n in (8, 9, 10, 11, 12, 13):
        edges, opt = spider_graph(n, 1000 + n)
        fn = f"frontier_spider_n{n}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"spider_n{n}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"],
                 timeout=900, structure_name="graph_family",
                 structure_value="three_arm_tree", frontier_group="three_arm_tree",
                 stop_after_timeout=True)

    # Exact frontier family 2: one connected graph with a part-size imbalance.
    # No Hamiltonian path exists once the bipartition differs by more than one.
    for a in (3, 4, 5, 6, 7):
        b = a + 2
        n = a + b
        edges, opt = complete_bipartite(a, b, 2000 + n)
        fn = f"frontier_bipartite_{a}_{b}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"bipartite_{a}_{b}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"],
                 timeout=900, structure_name="graph_family",
                 structure_value="imbalanced_complete_bipartite",
                 frontier_group="imbalanced_complete_bipartite", stop_after_timeout=True)

    # Exact frontier family 3: two disconnected dense components.
    for size in (4, 5, 6, 7, 8):
        n = 2 * size
        edges, opt = two_cliques(size, size, 3000 + n)
        fn = f"frontier_two_cliques_{size}_{size}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"two_cliques_{size}_{size}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"],
                 timeout=900, structure_name="graph_family",
                 structure_value="two_disconnected_cliques",
                 frontier_group="two_disconnected_cliques", stop_after_timeout=True)

    # Heuristic quality where OPT is known analytically/by construction.
    quality_specs = []
    e, opt = spider_graph(101, 4101); quality_specs.append(("quality_spider101", "quality_spider101.txt", 101, e, opt, "three_arm_tree"))
    e, opt = complete_bipartite(20, 30, 4150); quality_specs.append(("quality_bipartite_20_30", "quality_bipartite_20_30.txt", 50, e, opt, "imbalanced_complete_bipartite"))
    e, opt = two_cliques(40, 30, 4170); quality_specs.append(("quality_two_cliques_40_30", "quality_two_cliques_40_30.txt", 70, e, opt, "two_disconnected_cliques"))
    e, opt = planted_path_random(120, 240, 4220); quality_specs.append(("quality_planted120", "quality_planted120.txt", 120, e, opt, "planted_hamiltonian_sparse"))
    for item_id, fn, n, edges, opt, family in quality_specs:
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "quality_known", item_id=item_id, filename=fn, n=n, m=m,
                 opt=opt, algorithms=["heuristic1"], timeout=60, seeds=SEEDS,
                 structure_name="graph_family", structure_value=family)

    # Scale: hidden Hamiltonian path plus O(n) extra edges.  The randomized
    # Hamiltonian path labels prevent algorithms from relying on numeric order.
    for n in (500, 2000, 5000):
        edges, opt = planted_path_random(n, 2 * n, 5000 + n)
        fn = f"scale_planted_n{n}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "heuristic_scale", item_id=f"scale_planted_n{n}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["heuristic1"], timeout=60,
                 seeds=SEEDS, structure_name="graph_family",
                 structure_value="sparse_planted_hamiltonian")

    # Structure: hold n fixed and vary extra-edge density. Every graph contains
    # a hidden Hamiltonian path, so OPT=n-1 for every row; only density changes.
    n = 300
    for density_index, p in enumerate((0.01, 0.03, 0.08, 0.20), start=1):
        for rep in range(1, 4):
            seed = 6000 + density_index * 100 + rep
            edges, opt = planted_path_density(n, p, seed)
            label = str(p).replace(".", "_")
            fn = f"structure_density_{label}_r{rep}.txt"
            m = write_graph(INST / fn, n, edges)
            add_item(suites, "structure", item_id=f"density_{label}_r{rep}", filename=fn,
                     n=n, m=m, opt=opt, algorithms=["heuristic1"], timeout=60,
                     seeds=SEEDS, structure_name="extra_edge_probability",
                     structure_value=p)

    manifest = {
        "schema_version": 1,
        "problem": "longest_path",
        "objective": "maximize",
        "bound_kind": "upper",
        "description": "Course-provided Longest Path CP3 readiness and CP4 experiment suites.",
        "suites": suites,
    }
    (BENCH / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {sum(len(v) for v in suites.values())} manifest entries to {BENCH}")


if __name__ == "__main__":
    main()
