#!/usr/bin/env python3
"""Generate deterministic course benchmark suites for Minimum Vertex Cover.

COURSE INFRASTRUCTURE -- students should not modify this file.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "minimum_vertex_cover"
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


def path_graph(n: int):
    return [(v, v + 1) for v in range(n - 1)]


def cycle_graph(n: int):
    return path_graph(n) + ([(n - 1, 0)] if n > 2 else [])


def complete_bipartite(a: int, b: int, seed: int):
    n = a + b
    edges = [(u, a + v) for u in range(a) for v in range(b)]
    return relabel(n, edges, seed), min(a, b)


def star_forest(stars: int, leaves_per_star: int, seed: int):
    n = stars * (leaves_per_star + 1)
    edges = []
    for s in range(stars):
        center = s * (leaves_per_star + 1)
        edges.extend((center, center + i) for i in range(1, leaves_per_star + 1))
    return relabel(n, edges, seed), stars


def disjoint_triangles(count: int, seed: int):
    n = 3 * count
    edges = []
    for t in range(count):
        a = 3 * t
        edges.extend([(a, a + 1), (a + 1, a + 2), (a, a + 2)])
    return relabel(n, edges, seed), 2 * count


def planted_bipartite_cover(n: int, cover_size: int, seed: int, *, degree: int | None = None, p: float | None = None):
    """Bipartite graph with a certified optimum of exactly cover_size.

    The left side has ``cover_size`` vertices and is itself a vertex cover.
    A matching saturating the left side is always included, so every vertex
    cover has size at least ``cover_size``.  Therefore OPT is known exactly.
    """
    if not (0 <= cover_size <= n - cover_size):
        raise ValueError("need 0 <= cover_size <= n-cover_size")
    if (degree is None) == (p is None):
        raise ValueError("specify exactly one of degree or p")
    left = cover_size
    right = n - left
    rng = random.Random(seed)
    edges = {(u, left + u) for u in range(left)}
    if degree is not None:
        d = max(1, min(int(degree), right))
        for u in range(left):
            matched = u
            choices = [v for v in range(right) if v != matched]
            for v in rng.sample(choices, min(d - 1, len(choices))):
                edges.add((u, left + v))
    else:
        for u in range(left):
            for v in range(right):
                if v == u:
                    continue
                if rng.random() < float(p):
                    edges.add((u, left + v))
    return relabel(n, edges, seed + 900_000), cover_size


def add_item(suites, suite, *, item_id, filename, n, m, opt, algorithms, timeout,
             seeds=None, structure_name=None, structure_value=None,
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

    # Readiness.
    ready = [
        ("ready_path8", "ready_path8.txt", 8, path_graph(8), 4, "path"),
        ("ready_cycle9", "ready_cycle9.txt", 9, cycle_graph(9), 5, "odd_cycle"),
    ]
    e, opt = complete_bipartite(4, 6, 4010)
    ready.append(("ready_bipartite_4_6", "ready_bipartite_4_6.txt", 10, e, opt, "complete_bipartite"))
    for item_id, fn, n, edges, opt, family in ready:
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "readiness", item_id=item_id, filename=fn, n=n, m=m, opt=opt,
                 algorithms=["exhaustive"], timeout=15,
                 structure_name="graph_family", structure_value=family)

    # Exact frontier family 1: balanced complete bipartite graphs, OPT=a.
    for a in (5, 7, 9, 11, 13):
        n = 2 * a
        edges, opt = complete_bipartite(a, a, 1000 + n)
        fn = f"frontier_bipartite_{a}_{a}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"bipartite_{a}_{a}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"], timeout=900,
                 structure_name="graph_family", structure_value="balanced_complete_bipartite",
                 frontier_group="balanced_complete_bipartite", stop_after_timeout=True)

    # Exact frontier family 2: disjoint star components, one center per component.
    for stars in (3, 4, 5, 6, 7):
        edges, opt = star_forest(stars, 4, 2000 + stars)
        n = stars * 5
        fn = f"frontier_stars_{stars}x4.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"stars_{stars}x4", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"], timeout=900,
                 structure_name="graph_family", structure_value="disjoint_stars",
                 frontier_group="disjoint_stars", stop_after_timeout=True)

    # Exact frontier family 3: disjoint triangles, two cover vertices per triangle.
    for count in (4, 5, 6, 7, 8):
        edges, opt = disjoint_triangles(count, 3000 + count)
        n = 3 * count
        fn = f"frontier_triangles_{count}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "exact_frontier", item_id=f"triangles_{count}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["exhaustive", "improved"], timeout=900,
                 structure_name="graph_family", structure_value="disjoint_triangles",
                 frontier_group="disjoint_triangles", stop_after_timeout=True)

    # Quality with known optimum from a saturating matching certificate.
    for n, k, degree, seed in [(120, 40, 10, 5101), (200, 70, 12, 5201), (300, 100, 15, 5301)]:
        edges, opt = planted_bipartite_cover(n, k, seed, degree=degree)
        fn = f"quality_bipartite_n{n}_k{k}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "quality_known", item_id=f"quality_n{n}_k{k}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["heuristic1"], timeout=60, seeds=SEEDS,
                 structure_name="construction", structure_value="planted_bipartite_cover")

    # Heuristic scaling through 5,000 vertices.
    for n, k, degree, seed in [(500, 150, 10, 6101), (2000, 600, 12, 6201), (5000, 1500, 15, 6301)]:
        edges, opt = planted_bipartite_cover(n, k, seed, degree=degree)
        fn = f"scale_bipartite_n{n}_k{k}.txt"
        m = write_graph(INST / fn, n, edges)
        add_item(suites, "heuristic_scale", item_id=f"scale_n{n}_k{k}", filename=fn,
                 n=n, m=m, opt=opt, algorithms=["heuristic1"], timeout=60, seeds=SEEDS,
                 structure_name="construction", structure_value="planted_bipartite_cover")

    # Structural study: n and OPT fixed, edge density varied.  The matching
    # certificate keeps OPT exactly 120 for every graph.
    n, k = 300, 120
    for label, prob in [("sparse", 0.03), ("medium", 0.12), ("dense", 0.35)]:
        for rep in (1, 2, 3):
            edges, opt = planted_bipartite_cover(n, k, 7000 + rep + int(prob * 1000), p=prob)
            fn = f"structure_{label}_r{rep}.txt"
            m = write_graph(INST / fn, n, edges)
            density = round((2.0 * m) / (n * (n - 1)), 6)
            add_item(suites, "structure", item_id=f"{label}_r{rep}", filename=fn,
                     n=n, m=m, opt=opt, algorithms=["heuristic1"], timeout=60, seeds=SEEDS,
                     structure_name="edge_density", structure_value=density)

    manifest = {
        "schema_version": 1,
        "problem": "minimum_vertex_cover",
        "objective": "minimize",
        "bound_kind": "lower",
        "description": "Course-provided Minimum Vertex Cover Checkpoint 1 readiness and Final Project experiment suites.",
        "suites": suites,
    }
    (BENCH / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
