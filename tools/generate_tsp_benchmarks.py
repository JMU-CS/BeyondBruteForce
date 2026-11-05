#!/usr/bin/env python3
"""Regenerate the course-created TSP benchmark instances.

This generator intentionally creates only the course-owned synthetic TSP data.
Public TSPLIB/Waterloo instances are installed separately by
``tools/install_external_benchmarks.py``.
"""
from __future__ import annotations

import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "benchmarks" / "traveling_salesperson" / "instances"
SQUARE_SIZE = 10_000.0
CLUSTER_CENTERS = ((2000.0, 2000.0), (2000.0, 8000.0), (8000.0, 2000.0), (8000.0, 8000.0))
CLUSTER_SIGMA = 650.0
RANDOM_WEIGHT_MIN = 1
RANDOM_WEIGHT_MAX = 10_000


def clipped(x: float) -> float:
    return min(SQUARE_SIZE, max(0.0, x))


def uniform_points(n: int, seed: int) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    return [(rng.uniform(0.0, SQUARE_SIZE), rng.uniform(0.0, SQUARE_SIZE)) for _ in range(n)]


def clustered_points(n: int, seed: int) -> list[tuple[float, float]]:
    """Four equally used Gaussian clusters in the corners of an inner square."""
    rng = random.Random(seed)
    points=[]
    for i in range(n):
        cx, cy = CLUSTER_CENTERS[i % len(CLUSTER_CENTERS)]
        x = clipped(rng.gauss(cx, CLUSTER_SIGMA))
        y = clipped(rng.gauss(cy, CLUSTER_SIGMA))
        points.append((x, y))
    # Vertex IDs should not reveal the cluster directly.
    rng.shuffle(points)
    return points


def write_euc_2d(path: Path, name: str, points: list[tuple[float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines=[
        f"NAME : {name}",
        "TYPE : TSP",
        f"DIMENSION : {len(points)}",
        "EDGE_WEIGHT_TYPE : EUC_2D",
        "NODE_COORD_SECTION",
    ]
    lines += [f"{i} {x:.6f} {y:.6f}" for i,(x,y) in enumerate(points, start=1)]
    lines.append("EOF")
    path.write_text("\n".join(lines)+"\n", encoding="utf-8")


def write_random(path: Path, name: str, n: int, seed: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"NAME : {name}\n"
        "TYPE : TSP\n"
        f"DIMENSION : {n}\n"
        "EDGE_WEIGHT_TYPE : BBF_RANDOM_UNIFORM\n"
        f"BBF_RANDOM_SEED : {seed}\n"
        f"BBF_WEIGHT_MIN : {RANDOM_WEIGHT_MIN}\n"
        f"BBF_WEIGHT_MAX : {RANDOM_WEIGHT_MAX}\n"
        "EOF\n",
        encoding="utf-8",
    )


def main() -> int:
    frontier = BASE / "frontier"
    for n in (10, 12, 14, 16, 18, 20):
        name=f"frontier_uniform_euclidean_n{n}"
        write_euc_2d(frontier/f"{name}.tsp", name, uniform_points(n, 1000+n))
        name=f"frontier_clustered_euclidean_n{n}"
        write_euc_2d(frontier/f"{name}.tsp", name, clustered_points(n, 2000+n))
        name=f"frontier_random_weights_n{n}"
        write_random(frontier/f"{name}.tsp", name, n, 3000+n)

    scale = BASE / "scale"
    for n in (250, 1000, 3000):
        name=f"scale_uniform_euclidean_n{n}"
        write_euc_2d(scale/f"{name}.tsp", name, uniform_points(n, 4000+n))

    structure = BASE / "structure"
    for r in (1,2,3):
        name=f"uniform_euclidean_n500_r{r}"
        write_euc_2d(structure/f"{name}.tsp", name, uniform_points(500, 5100+r))
        name=f"clustered_euclidean_n500_r{r}"
        write_euc_2d(structure/f"{name}.tsp", name, clustered_points(500, 5200+r))
        name=f"random_weights_n500_r{r}"
        write_random(structure/f"{name}.tsp", name, 500, 5300+r)

    print("Regenerated synthetic TSP benchmark instances.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
