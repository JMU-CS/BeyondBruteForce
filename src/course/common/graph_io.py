"""Input support for the shared undirected graph format."""

# ----------------------------------------------------------------------
# COURSE INFRASTRUCTURE
# Students should not modify this file.
# ----------------------------------------------------------------------

from pathlib import Path

from course.common.graph import Graph


def read_graph(filename: str | Path) -> Graph:
    """Read an undirected graph from ``filename``.

    File format
    -----------
    The first line contains two integers::

        n m

    where ``n`` is the number of vertices and ``m`` is the number of edges.
    Vertices are numbered from 0 through n - 1.

    The next ``m`` lines each contain two integers ``u v`` describing an
    undirected edge between vertices ``u`` and ``v``.

    Blank lines are ignored.

    Parameters
    ----------
    filename:
        Path to the graph file.

    Returns
    -------
    Graph
        The graph described by the file.

    Raises
    ------
    ValueError
        If the file is malformed.  Additional graph-validity checks are
        performed by ``Graph.from_edges``.
    """
    path = Path(filename)

    if path.suffix.lower() == ".g6":
        from course.common.graph6 import read_graph6
        return read_graph6(str(path))

    with path.open("r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        raise ValueError(f"{path}: graph file is empty")

    header = lines[0].split()
    if len(header) != 2:
        raise ValueError(
            f"{path}: first line must contain exactly two integers: n m"
        )

    try:
        num_vertices, num_edges = map(int, header)
    except ValueError as exc:
        raise ValueError(
            f"{path}: first line must contain exactly two integers: n m"
        ) from exc

    if num_vertices < 0:
        raise ValueError(f"{path}: number of vertices cannot be negative")

    if num_edges < 0:
        raise ValueError(f"{path}: number of edges cannot be negative")

    edge_lines = lines[1:]
    if len(edge_lines) != num_edges:
        raise ValueError(
            f"{path}: header specifies {num_edges} edges, "
            f"but file contains {len(edge_lines)} edge lines"
        )

    edges: list[tuple[int, int]] = []

    for line_number, line in enumerate(edge_lines, start=2):
        parts = line.split()

        if len(parts) != 2:
            raise ValueError(
                f"{path}:{line_number}: edge line must contain "
                "exactly two integers"
            )

        try:
            u, v = map(int, parts)
        except ValueError as exc:
            raise ValueError(
                f"{path}:{line_number}: edge endpoints must be integers"
            ) from exc

        edges.append((u, v))

    return Graph.from_edges(num_vertices, edges)
