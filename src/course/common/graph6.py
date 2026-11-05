"""Minimal graph6 decoding used by course benchmark infrastructure.

Supports ordinary graph6 graphs up through the extended vertex-count header.
Student algorithms never need to use this module directly.
"""

from course.common.graph import Graph


def _decode_n(data: bytes) -> tuple[int, int]:
    if not data:
        raise ValueError("empty graph6 string")
    vals = [b - 63 for b in data]
    if any(v < 0 or v > 63 for v in vals):
        raise ValueError("invalid graph6 character")
    if vals[0] <= 62:
        return vals[0], 1
    if len(vals) < 4:
        raise ValueError("truncated graph6 vertex-count header")
    if vals[1] <= 62:
        n = (vals[1] << 12) | (vals[2] << 6) | vals[3]
        return n, 4
    if len(vals) < 8:
        raise ValueError("truncated graph6 large vertex-count header")
    n = 0
    for v in vals[2:8]:
        n = (n << 6) | v
    return n, 8


def decode_graph6(text: str) -> Graph:
    line = text.strip()
    if line.startswith(">>graph6<<"):
        line = line[len(">>graph6<<"):]
    data = line.encode("ascii")
    n, pos = _decode_n(data)
    bits: list[int] = []
    for byte in data[pos:]:
        value = byte - 63
        if not 0 <= value <= 63:
            raise ValueError("invalid graph6 character")
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = n * (n - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 edge data")
    edges: list[tuple[int, int]] = []
    k = 0
    # graph6 order: (0,1), (0,2),(1,2), (0,3),(1,3),(2,3), ...
    for v in range(1, n):
        for u in range(v):
            if bits[k]:
                edges.append((u, v))
            k += 1
    return Graph.from_edges(n, edges)


def read_graph6(filename: str) -> Graph:
    with open(filename, "r", encoding="ascii") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith(">>graph6<<")]
    if len(lines) != 1:
        raise ValueError("a .g6 instance file must contain exactly one graph")
    return decode_graph6(lines[0])
