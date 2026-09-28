"""Shared immutable graph representation used by graph-based project problems.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from dataclasses import dataclass, field
from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Graph:
    """A simple undirected graph with vertices numbered 0 through n - 1.

    Student code should treat Graph objects as read-only.  Graphs are normally
    created by ``read_graph`` or ``Graph.from_edges``.
    """

    num_vertices: int
    edges: tuple[tuple[int, int], ...]
    _adjacency: tuple[frozenset[int], ...] = field(repr=False)

    @classmethod
    def from_edges(
        cls,
        num_vertices: int,
        edges: Iterable[tuple[int, int]],
    ) -> "Graph":
        """Construct a simple undirected graph from an iterable of edges."""
        if not isinstance(num_vertices, int):
            raise TypeError("num_vertices must be an int")
        if num_vertices < 0:
            raise ValueError("num_vertices cannot be negative")

        normalized: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        adjacency: list[set[int]] = [set() for _ in range(num_vertices)]

        for edge in edges:
            try:
                u, v = edge
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "each edge must contain exactly two vertex IDs"
                ) from exc

            if not isinstance(u, int) or not isinstance(v, int):
                raise TypeError("edge endpoints must be ints")
            if not (0 <= u < num_vertices) or not (0 <= v < num_vertices):
                raise ValueError(
                    f"edge ({u}, {v}) contains an out-of-range vertex ID"
                )
            if u == v:
                raise ValueError("self-loops are not allowed")

            edge_key = (u, v) if u < v else (v, u)
            if edge_key in seen:
                raise ValueError(f"duplicate undirected edge {edge_key}")

            seen.add(edge_key)
            normalized.append(edge_key)
            adjacency[u].add(v)
            adjacency[v].add(u)

        normalized.sort()

        return cls(
            num_vertices=num_vertices,
            edges=tuple(normalized),
            _adjacency=tuple(frozenset(nbrs) for nbrs in adjacency),
        )

    def _check_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int):
            raise TypeError("vertex ID must be an int")
        if not 0 <= vertex < self.num_vertices:
            raise ValueError(
                f"vertex ID {vertex} is outside 0..{self.num_vertices - 1}"
            )

    def neighbors(self, vertex: int) -> frozenset[int]:
        """Return the immutable set of neighbors of ``vertex``."""
        self._check_vertex(vertex)
        return self._adjacency[vertex]

    def degree(self, vertex: int) -> int:
        """Return the degree of ``vertex``."""
        self._check_vertex(vertex)
        return len(self._adjacency[vertex])

    def has_edge(self, u: int, v: int) -> bool:
        """Return True exactly when the undirected edge {u, v} exists."""
        self._check_vertex(u)
        self._check_vertex(v)
        return v in self._adjacency[u]
