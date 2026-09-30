"""Reference randomized high-degree MVC heuristic."""
from argparse import Namespace
from random import Random
from time import perf_counter
from course.common.graph import Graph


def _one_attempt(edges: tuple[tuple[int, int], ...], rng: Random) -> set[int]:
    remaining = set(edges)
    cover: set[int] = set()
    while remaining:
        degrees: dict[int, int] = {}
        for u, v in remaining:
            degrees[u] = degrees.get(u, 0) + 1
            degrees[v] = degrees.get(v, 0) + 1
        best_degree = max(degrees.values())
        # Randomize among vertices whose residual degree is close to the current
        # maximum.  This keeps the method recognizably high-degree greedy while
        # making repeated attempts capable of following different trajectories.
        threshold = max(1, best_degree - 1)
        choices = [v for v, d in degrees.items() if d >= threshold]
        vertex = choices[rng.randrange(len(choices))]
        cover.add(vertex)
        remaining = {e for e in remaining if vertex not in e}
    return cover


def solve(instance: Graph, args: Namespace) -> tuple[dict, dict]:
    start = perf_counter()
    rng = Random(args.seed)
    attempts = 8
    best: set[int] | None = None
    for _ in range(attempts):
        candidate = _one_attempt(instance.edges, rng)
        if best is None or len(candidate) < len(best):
            best = candidate
    if best is None:
        best = set()
    answer = sorted(best)
    return ({"size": len(answer), "vertices": answer},
            {"time": perf_counter() - start, "attempts": attempts})
