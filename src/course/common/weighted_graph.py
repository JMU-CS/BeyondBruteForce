"""Shared immutable weighted graph representation.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from dataclasses import dataclass, field
from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class WeightedGraph:
    """A simple undirected weighted graph with vertices 0..n-1.

    The graph need not be complete at construction time, although the TSP
    problem specification requires complete instances. Edge weights are
    nonnegative integers.
    """

    num_vertices: int
    edges: tuple[tuple[int, int, int], ...]
    _adjacency: tuple[dict[int, int], ...] = field(repr=False)

    @classmethod
    def from_edges(
        cls,
        num_vertices: int,
        edges: Iterable[tuple[int, int, int]],
    ) -> "WeightedGraph":
        if not isinstance(num_vertices, int):
            raise TypeError("num_vertices must be an int")
        if num_vertices < 0:
            raise ValueError("num_vertices cannot be negative")

        normalized: list[tuple[int, int, int]] = []
        seen: set[tuple[int, int]] = set()
        adjacency: list[dict[int, int]] = [dict() for _ in range(num_vertices)]

        for edge in edges:
            try:
                u, v, weight = edge
            except (TypeError, ValueError) as exc:
                raise ValueError("each weighted edge must contain u, v, weight") from exc
            if not isinstance(u, int) or not isinstance(v, int):
                raise TypeError("edge endpoints must be ints")
            if not isinstance(weight, int):
                raise TypeError("edge weights must be ints")
            if weight < 0:
                raise ValueError("edge weights must be nonnegative")
            if not (0 <= u < num_vertices) or not (0 <= v < num_vertices):
                raise ValueError(f"edge ({u}, {v}) contains an out-of-range vertex ID")
            if u == v:
                raise ValueError("self-loops are not allowed")
            key = (u, v) if u < v else (v, u)
            if key in seen:
                raise ValueError(f"duplicate undirected edge {key}")
            seen.add(key)
            a, b = key
            normalized.append((a, b, weight))
            adjacency[a][b] = weight
            adjacency[b][a] = weight

        normalized.sort()
        return cls(
            num_vertices=num_vertices,
            edges=tuple(normalized),
            _adjacency=tuple(dict(nbrs) for nbrs in adjacency),
        )

    def _check_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int):
            raise TypeError("vertex ID must be an int")
        if not 0 <= vertex < self.num_vertices:
            raise ValueError(f"vertex ID {vertex} is outside 0..{self.num_vertices - 1}")

    def neighbors(self, vertex: int) -> frozenset[int]:
        self._check_vertex(vertex)
        return frozenset(self._adjacency[vertex])

    def degree(self, vertex: int) -> int:
        self._check_vertex(vertex)
        return len(self._adjacency[vertex])

    def has_edge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        return v in self._adjacency[u]

    def weight(self, u: int, v: int) -> int:
        self._check_vertex(u)
        self._check_vertex(v)
        try:
            return self._adjacency[u][v]
        except KeyError as exc:
            raise ValueError(f"edge ({u}, {v}) does not exist") from exc

    @property
    def is_complete(self) -> bool:
        n = self.num_vertices
        return len(self.edges) == n * (n - 1) // 2
