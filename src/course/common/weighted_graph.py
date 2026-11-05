"""Shared immutable weighted graph representation.

COURSE INFRASTRUCTURE
Students should not modify this file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Iterable, Iterator
from math import hypot


@dataclass(frozen=True, slots=True)
class WeightedGraph:
    """A simple undirected weighted graph with vertices 0..n-1.

    The graph can be backed by one of three storage modes:

    * explicit edges;
    * TSPLIB-style EUC_2D coordinates, with weights computed on demand; or
    * a deterministic course-generated random complete graph.

    Student TSP code should prefer ``num_vertices`` and ``weight(u, v)``.  For
    large implicit complete graphs, materializing every edge would require
    O(n^2) memory, so ``edges`` is intentionally unavailable; use
    ``edge_count`` or ``iter_edges()`` instead.
    """

    num_vertices: int
    _edges: tuple[tuple[int, int, int], ...] | None = field(repr=False, default=None)
    _adjacency: tuple[dict[int, int], ...] | None = field(repr=False, default=None)
    _coordinates: tuple[tuple[float, float], ...] | None = field(repr=False, default=None)
    _storage_kind: str = field(default="explicit")
    _name: str | None = field(default=None, repr=False)
    _random_seed: int | None = field(default=None, repr=False)
    _random_min: int | None = field(default=None, repr=False)
    _random_max: int | None = field(default=None, repr=False)

    @classmethod
    def from_edges(
        cls,
        num_vertices: int,
        edges: Iterable[tuple[int, int, int]],
        *,
        name: str | None = None,
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
            _edges=tuple(normalized),
            _adjacency=tuple(dict(nbrs) for nbrs in adjacency),
            _storage_kind="explicit",
            _name=name,
        )

    @classmethod
    def from_euc_2d(
        cls,
        coordinates: Iterable[tuple[float, float]],
        *,
        name: str | None = None,
    ) -> "WeightedGraph":
        coords = tuple((float(x), float(y)) for x, y in coordinates)
        if len(coords) < 2:
            raise ValueError("a coordinate-backed graph must contain at least two vertices")
        return cls(
            num_vertices=len(coords),
            _coordinates=coords,
            _storage_kind="euc_2d",
            _name=name,
        )

    @classmethod
    def from_random_complete(
        cls,
        num_vertices: int,
        *,
        seed: int,
        min_weight: int = 1,
        max_weight: int = 1000,
        name: str | None = None,
    ) -> "WeightedGraph":
        if not isinstance(num_vertices, int) or num_vertices < 0:
            raise ValueError("num_vertices must be a nonnegative int")
        if not isinstance(seed, int):
            raise TypeError("seed must be an int")
        if not isinstance(min_weight, int) or not isinstance(max_weight, int):
            raise TypeError("random-weight bounds must be ints")
        if min_weight < 0 or max_weight < min_weight:
            raise ValueError("invalid random-weight range")
        return cls(
            num_vertices=num_vertices,
            _storage_kind="bbf_random_uniform",
            _name=name,
            _random_seed=seed,
            _random_min=min_weight,
            _random_max=max_weight,
        )

    def _check_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int):
            raise TypeError("vertex ID must be an int")
        if not 0 <= vertex < self.num_vertices:
            raise ValueError(f"vertex ID {vertex} is outside 0..{self.num_vertices - 1}")

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def storage_kind(self) -> str:
        """Return ``explicit``, ``euc_2d``, or ``bbf_random_uniform``."""
        return self._storage_kind

    @property
    def edge_count(self) -> int:
        if self._storage_kind == "explicit":
            assert self._edges is not None
            return len(self._edges)
        n = self.num_vertices
        return n * (n - 1) // 2

    @property
    def edges(self) -> tuple[tuple[int, int, int], ...]:
        """Return materialized edges for explicitly stored graphs.

        Large coordinate-backed and generated complete graphs deliberately do
        not materialize O(n^2) edge tuples.  Use ``iter_edges()`` when a full
        scan is truly needed.
        """
        if self._edges is None:
            raise RuntimeError(
                "graph.edges is not materialized for this implicit complete graph; "
                "use graph.edge_count, graph.iter_edges(), or graph.weight(u, v)"
            )
        return self._edges

    def iter_edges(self) -> Iterator[tuple[int, int, int]]:
        """Iterate over all undirected edges without requiring materialization."""
        if self._edges is not None:
            yield from self._edges
            return
        for u in range(self.num_vertices):
            for v in range(u + 1, self.num_vertices):
                yield (u, v, self.weight(u, v))

    def neighbors(self, vertex: int) -> frozenset[int]:
        self._check_vertex(vertex)
        if self._adjacency is not None:
            return frozenset(self._adjacency[vertex])
        return frozenset(v for v in range(self.num_vertices) if v != vertex)

    def degree(self, vertex: int) -> int:
        self._check_vertex(vertex)
        if self._adjacency is not None:
            return len(self._adjacency[vertex])
        return max(0, self.num_vertices - 1)

    def has_edge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            return False
        if self._adjacency is not None:
            return v in self._adjacency[u]
        return True

    @staticmethod
    def _mix64(x: int) -> int:
        # SplitMix64 finalizer.  This is deterministic across Python versions
        # and avoids storing an O(n^2) random-weight table.
        mask = (1 << 64) - 1
        x &= mask
        x ^= x >> 30
        x = (x * 0xBF58476D1CE4E5B9) & mask
        x ^= x >> 27
        x = (x * 0x94D049BB133111EB) & mask
        x ^= x >> 31
        return x & mask

    def weight(self, u: int, v: int) -> int:
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise ValueError("self-loop weights are not defined")

        if self._adjacency is not None:
            try:
                return self._adjacency[u][v]
            except KeyError as exc:
                raise ValueError(f"edge ({u}, {v}) does not exist") from exc

        if self._storage_kind == "euc_2d":
            assert self._coordinates is not None
            x1, y1 = self._coordinates[u]
            x2, y2 = self._coordinates[v]
            # TSPLIB EUC_2D uses nint(sqrt(dx^2+dy^2)) = int(d + 0.5).
            return int(hypot(x1 - x2, y1 - y2) + 0.5)

        if self._storage_kind == "bbf_random_uniform":
            assert self._random_seed is not None
            assert self._random_min is not None and self._random_max is not None
            a, b = (u, v) if u < v else (v, u)
            x = (
                (self._random_seed & ((1 << 64) - 1))
                ^ ((a + 1) * 0x9E3779B97F4A7C15)
                ^ ((b + 1) * 0xD1B54A32D192ED03)
            )
            value = self._mix64(x)
            span = self._random_max - self._random_min + 1
            return self._random_min + (value % span)

        raise RuntimeError(f"unsupported storage kind {self._storage_kind!r}")

    @property
    def is_complete(self) -> bool:
        if self._storage_kind != "explicit":
            return True
        n = self.num_vertices
        assert self._edges is not None
        return len(self._edges) == n * (n - 1) // 2
