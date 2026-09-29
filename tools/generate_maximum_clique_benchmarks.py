#!/usr/bin/env python3
"""Generate deterministic course benchmark suites for Maximum Clique.

COURSE INFRASTRUCTURE -- students should not modify this file.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "maximum_clique"
INST = BENCH / "instances"
SEEDS = [11, 29, 47, 71, 101]


def normalize_edges(edges):
    return sorted({(u, v) if u < v else (v, u) for u, v in edges if u != v})


def write_graph(path: Path, n: int, edges) -> int:
    edges = normalize_edges(edges)
    path.write_text(
        f"{n} {len(edges)}\n" + "".join(f"{u} {v}\n" for u, v in edges),
        encoding="utf-8",
    )
    return len(edges)


def relabel(n: int, edges, seed: int):
    rng = random.Random(seed)
    labels = list(range(n))
    rng.shuffle(labels)
    return [(labels[u], labels[v]) for u, v in edges]


def complete_graph(n: int, seed: int | None = None):
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    return relabel(n, edges, seed) if seed is not None else edges


def complete_bipartite(a: int, b: int, seed: int):
    n = a + b
    edges = [(u, a + v) for u in range(a) for v in range(b)]
    return relabel(n, edges, seed), 2 if a and b else 1


def complete_multipartite(parts: list[int], seed: int):
    """Return a complete multipartite graph and its exact clique number."""
    if not parts or any(size <= 0 for size in parts):
        raise ValueError("parts must contain positive sizes")
    starts = []
    cur = 0
    for size in parts:
        starts.append(cur)
        cur += size
    n = cur
    part_of = [0] * n
    for p, (start, size) in enumerate(zip(starts, parts)):
        for v in range(start, start + size):
            part_of[v] = p
    edges = [
        (u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if part_of[u] != part_of[v]
    ]
    return relabel(n, edges, seed), len(parts)


def disjoint_cliques(sizes: list[int], seed: int):
    n = sum(sizes)
    edges = []
    start = 0
    for size in sizes:
        edges.extend(
            (start + u, start + v)
            for u in range(size)
            for v in range(u + 1, size)
        )
        start += size
    return relabel(n, edges, seed), max(sizes, default=0)


def clique_with_independent_distractors(n: int, clique_size: int, seed: int):
    """K_k plus independent distractors attached to one or two core vertices.

    The core K_k is maximum for k >= 3 because distractors have no edges among
    themselves and each sees at most two core vertices.
    """
    if clique_size < 3 or clique_size > n:
        raise ValueError("need 3 <= clique_size <= n")
    rng = random.Random(seed)
    edges = [(u, v) for u in range(clique_size) for v in range(u + 1, clique_size)]
    for v in range(clique_size, n):
        degree_to_core = 1 if rng.random() < 0.65 else 2
        for u in rng.sample(range(clique_size), degree_to_core):
            edges.append((u, v))
    return relabel(n, edges, seed + 900_000), clique_size


def add_item(
    suites,
    suite,
    *,
    item_id,
    filename,
    n,
    m,
    opt,
    algorithms,
    timeout,
    seeds=None,
    structure_name=None,
    structure_value=None,
    frontier_group=None,
    stop_after_timeout=False,
):
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

    # Readiness: tiny smoke tests spanning very different graph structures.
    ready = []
    ready.append(("ready_complete5", "ready_complete5.txt", 5, complete_graph(5, 4005), 5, "complete"))
    e, opt = complete_bipartite(4, 4, 4108)
    ready.append(("ready_bipartite_4_4", "ready_bipartite_4_4.txt", 8, e, opt, "complete_bipartite"))
    e, opt = complete_multipartite([2, 2, 2], 4206)
    ready.append(("ready_multipartite_2_2_2", "ready_multipartite_2_2_2.txt", 6, e, opt, "complete_multipartite"))
    for item_id, fn, n, edges, opt, family in ready:
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "readiness",
            item_id=item_id,
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["improved", "heuristic1"],
            timeout=15,
            seeds=[412],
            structure_name="graph_family",
            structure_value=family,
        )

    # Exact frontier family 1: balanced complete bipartite graphs.  OPT=2, so a
    # descending complete-subset baseline must reject almost the entire subset
    # lattice before reaching a feasible clique.
    for a in (6, 8, 10, 12, 14):
        n = 2 * a
        edges, opt = complete_bipartite(a, a, 1000 + n)
        fn = f"frontier_bipartite_{a}_{a}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "exact_frontier",
            item_id=f"bipartite_{a}_{a}",
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["exhaustive", "improved"],
            timeout=900,
            structure_name="graph_family",
            structure_value="balanced_complete_bipartite",
            frontier_group="balanced_complete_bipartite",
            stop_after_timeout=True,
        )

    # Exact frontier family 2: complete multipartite graphs with parts of size 3.
    # A maximum clique contains exactly one vertex from each part.
    for parts_count in (4, 5, 6, 7, 8):
        parts = [3] * parts_count
        n = sum(parts)
        edges, opt = complete_multipartite(parts, 2000 + n)
        fn = f"frontier_multipartite_{parts_count}x3.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "exact_frontier",
            item_id=f"multipartite_{parts_count}x3",
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["exhaustive", "improved"],
            timeout=900,
            structure_name="graph_family",
            structure_value="complete_multipartite_parts3",
            frontier_group="complete_multipartite_parts3",
            stop_after_timeout=True,
        )

    # Exact frontier family 3: two disconnected equal cliques.  Dense local
    # structure coexists with a hard global separation.
    for size in (6, 8, 10, 12, 14):
        n = 2 * size
        edges, opt = disjoint_cliques([size, size], 3000 + n)
        fn = f"frontier_two_cliques_{size}_{size}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "exact_frontier",
            item_id=f"two_cliques_{size}_{size}",
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["exhaustive", "improved"],
            timeout=900,
            structure_name="graph_family",
            structure_value="two_disconnected_cliques",
            frontier_group="two_disconnected_cliques",
            stop_after_timeout=True,
        )

    # Quality-known: all have exact optima guaranteed by construction.
    quality = []
    e, opt = clique_with_independent_distractors(300, 30, 4300)
    quality.append(("quality_core30_n300", "quality_core30_n300.txt", 300, e, opt, "planted_core_with_distractors"))
    e, opt = complete_multipartite([15] * 12, 4380)
    quality.append(("quality_multipartite_12x15", "quality_multipartite_12x15.txt", 180, e, opt, "complete_multipartite"))
    e, opt = disjoint_cliques([25, 20, 15], 4460)
    quality.append(("quality_disjoint_25_20_15", "quality_disjoint_25_20_15.txt", 60, e, opt, "disjoint_cliques"))
    for item_id, fn, n, edges, opt, family in quality:
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "quality_known",
            item_id=item_id,
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["heuristic1"],
            timeout=60,
            seeds=SEEDS,
            structure_name="graph_family",
            structure_value=family,
        )

    # Scale: sparse planted clique with many independent distractors. Files and
    # algorithms remain manageable even at thousands of vertices.
    for n, k in ((500, 20), (2000, 30), (5000, 40)):
        edges, opt = clique_with_independent_distractors(n, k, 5000 + n)
        fn = f"scale_core{k}_n{n}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(
            suites,
            "heuristic_scale",
            item_id=f"scale_core{k}_n{n}",
            filename=fn,
            n=n,
            m=m,
            opt=opt,
            algorithms=["heuristic1"],
            timeout=60,
            seeds=SEEDS,
            structure_name="graph_family",
            structure_value="planted_core_with_distractors",
        )

    # Structure: n=300 and omega=10 are held fixed. Vary only the imbalance of
    # the ten independent parts of a complete multipartite graph, which changes
    # density while preserving the exact optimum.
    structure_specs = [
        ("balanced", [30] * 10),
        ("moderate", [120] + [20] * 9),
        ("highly_imbalanced", [210] + [10] * 9),
    ]
    for label, parts in structure_specs:
        for rep in range(1, 4):
            seed = 6000 + len(label) * 10 + rep
            edges, opt = complete_multipartite(parts, seed)
            n = sum(parts)
            fn = f"structure_{label}_r{rep}.txt"
            m = write_graph(INST / fn, n, edges)
            density = 0.0 if n < 2 else 2.0 * m / (n * (n - 1))
            add_item(
                suites,
                "structure",
                item_id=f"{label}_r{rep}",
                filename=fn,
                n=n,
                m=m,
                opt=opt,
                algorithms=["heuristic1"],
                timeout=60,
                seeds=SEEDS,
                structure_name="edge_density",
                structure_value=round(density, 6),
            )

    manifest = {
        "schema_version": 1,
        "problem": "maximum_clique",
        "objective": "maximize",
        "bound_kind": "upper",
        "description": "Course-provided Maximum Clique Checkpoint 2 readiness and Final Project experiment suites.",
        "suites": suites,
    }
    (BENCH / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {sum(len(v) for v in suites.values())} manifest entries to {BENCH}")


if __name__ == "__main__":
    main()
