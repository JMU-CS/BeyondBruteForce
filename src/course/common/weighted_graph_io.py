"""Input support for weighted graphs and coordinate-backed TSP instances."""

from __future__ import annotations

import gzip
from pathlib import Path

from course.common.weighted_graph import WeightedGraph


def _open_text(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open("r", encoding="utf-8")


def _noncomment_lines(path: Path) -> list[str]:
    with _open_text(path) as file:
        return [
            line.strip()
            for line in file
            if line.strip() and not line.lstrip().startswith("#")
        ]


def _looks_like_tsplib(lines: list[str], path: Path) -> bool:
    suffixes = [s.lower() for s in path.suffixes]
    if ".tsp" in suffixes:
        return True
    if not lines:
        return False
    first = lines[0].upper()
    return first.startswith("NAME") or first.startswith("TYPE") or first.startswith("DIMENSION")


def _parse_header_line(line: str) -> tuple[str, str] | None:
    if ":" in line:
        key, value = line.split(":", 1)
        return key.strip().upper(), value.strip()
    parts = line.split(maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip().upper(), parts[1].strip()
    return None


def read_tsplib_tsp(filename: str | Path) -> WeightedGraph:
    """Read the supported subset of TSPLIB-style symmetric TSP files.

    Supported edge-weight types:
      * ``EUC_2D`` (standard TSPLIB coordinates)
      * ``BBF_RANDOM_UNIFORM`` (course-generated implicit random weights)

    Vertices are converted from TSPLIB's conventional 1-based labels to the
    course API's 0-based IDs.
    """
    path = Path(filename)
    lines = _noncomment_lines(path)
    if not lines:
        raise ValueError(f"{path}: TSP file is empty")

    metadata: dict[str, str] = {}
    section_index: int | None = None
    for i, line in enumerate(lines):
        upper = line.upper()
        if upper == "NODE_COORD_SECTION":
            section_index = i + 1
            break
        if upper == "EOF":
            break
        parsed = _parse_header_line(line)
        if parsed:
            key, value = parsed
            metadata[key] = value

    tsp_type = metadata.get("TYPE", "TSP").upper()
    if tsp_type != "TSP":
        raise ValueError(f"{path}: only symmetric TYPE TSP is supported")
    try:
        dimension = int(metadata["DIMENSION"])
    except KeyError as exc:
        raise ValueError(f"{path}: TSPLIB file is missing DIMENSION") from exc
    except ValueError as exc:
        raise ValueError(f"{path}: DIMENSION must be an integer") from exc
    if dimension < 2:
        raise ValueError(f"{path}: TSP DIMENSION must be at least 2")

    weight_type = metadata.get("EDGE_WEIGHT_TYPE", "").upper()
    name = metadata.get("NAME", path.stem)

    if weight_type == "EUC_2D":
        if section_index is None:
            raise ValueError(f"{path}: EUC_2D instance is missing NODE_COORD_SECTION")
        coords_by_id: dict[int, tuple[float, float]] = {}
        for line in lines[section_index:]:
            if line.upper() == "EOF":
                break
            parts = line.split()
            if len(parts) < 3:
                raise ValueError(f"{path}: coordinate line must contain id x y")
            try:
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
            except ValueError as exc:
                raise ValueError(f"{path}: invalid NODE_COORD_SECTION line: {line}") from exc
            if node_id in coords_by_id:
                raise ValueError(f"{path}: duplicate TSPLIB node id {node_id}")
            coords_by_id[node_id] = (x, y)
        expected = set(range(1, dimension + 1))
        if set(coords_by_id) != expected:
            raise ValueError(
                f"{path}: NODE_COORD_SECTION must contain IDs 1..{dimension} exactly once"
            )
        coords = [coords_by_id[i] for i in range(1, dimension + 1)]
        return WeightedGraph.from_euc_2d(coords, name=name)

    if weight_type == "BBF_RANDOM_UNIFORM":
        def get_int(key: str) -> int:
            try:
                return int(metadata[key])
            except KeyError as exc:
                raise ValueError(f"{path}: {weight_type} instance is missing {key}") from exc
            except ValueError as exc:
                raise ValueError(f"{path}: {key} must be an integer") from exc

        seed = get_int("BBF_RANDOM_SEED")
        min_weight = get_int("BBF_WEIGHT_MIN")
        max_weight = get_int("BBF_WEIGHT_MAX")
        return WeightedGraph.from_random_complete(
            dimension,
            seed=seed,
            min_weight=min_weight,
            max_weight=max_weight,
            name=name,
        )

    raise ValueError(
        f"{path}: unsupported EDGE_WEIGHT_TYPE {weight_type!r}; "
        "supported types are EUC_2D and BBF_RANDOM_UNIFORM"
    )


def read_weighted_graph(filename: str | Path) -> WeightedGraph:
    """Read either the course edge-list format or a supported TSP format.

    Traditional course format::

        n m
        u v weight
        ...

    TSP coordinate/generated formats are detected automatically from ``.tsp``
    (including ``.tsp.gz``) or from TSPLIB-style header keywords.
    """
    path = Path(filename)
    lines = _noncomment_lines(path)
    if not lines:
        raise ValueError(f"{path}: weighted graph file is empty")

    if _looks_like_tsplib(lines, path):
        return read_tsplib_tsp(path)

    header = lines[0].split()
    if len(header) != 2:
        raise ValueError(
            f"{path}: first line must contain exactly two integers: n m, "
            "or the file must use a supported TSPLIB-style TSP format"
        )
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
    return WeightedGraph.from_edges(n, edges, name=path.stem)
