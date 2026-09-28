"""Input support for shared weighted undirected graph format."""

from pathlib import Path
from course.common.weighted_graph import WeightedGraph


def read_weighted_graph(filename: str | Path) -> WeightedGraph:
    """Read `n m` followed by `u v weight` lines."""
    path = Path(filename)
    with path.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        raise ValueError(f"{path}: weighted graph file is empty")
    header = lines[0].split()
    if len(header) != 2:
        raise ValueError(f"{path}: first line must contain exactly two integers: n m")
    try:
        n, m = map(int, header)
    except ValueError as exc:
        raise ValueError(f"{path}: first line must contain exactly two integers: n m") from exc
    edge_lines = lines[1:]
    if len(edge_lines) != m:
        raise ValueError(f"{path}: header specifies {m} edges, but file contains {len(edge_lines)} edge lines")
    edges: list[tuple[int, int, int]] = []
    for line_number, line in enumerate(edge_lines, start=2):
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"{path}:{line_number}: weighted edge line must contain u v weight")
        try:
            u, v, w = map(int, parts)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: u, v, and weight must be integers") from exc
        edges.append((u, v, w))
    return WeightedGraph.from_edges(n, edges)
