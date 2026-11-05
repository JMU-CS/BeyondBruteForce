#!/usr/bin/env python3
"""Install external benchmark data for the assigned Beyond Brute Force problem.

Normal student use requires no collection name::

    python tools/install_external_benchmarks.py

The assigned problem is read from project.json.  Instructors may override it with
--problem or install every currently configured problem with --all.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_PROJECTS_PATH = ROOT / "tools" / "valid_projects.json"
PROJECT_PATH = ROOT / "project.json"


def download(url: str) -> bytes:
    print(f"Downloading {url}")
    req = urllib.request.Request(
        url, headers={"User-Agent": "Beyond-Brute-Force-Benchmark-Installer/1.0"}
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def valid_projects() -> dict[str, str]:
    return json.loads(VALID_PROJECTS_PATH.read_text(encoding="utf-8"))


def assigned_problem() -> str | None:
    try:
        value = json.loads(PROJECT_PATH.read_text(encoding="utf-8")).get(
            "assigned_problem"
        )
    except (OSError, json.JSONDecodeError):
        return None
    return value.strip() if isinstance(value, str) and value.strip() else None


def _parse_pace_vc(raw: bytes, *, item_id: str) -> tuple[int, int | None, list[tuple[int, int]]]:
    """Parse one PACE 2019 Vertex Cover graph into zero-based edges."""
    text = raw.decode("utf-8-sig", errors="replace")
    n: int | None = None
    source_m: int | None = None
    edges: list[tuple[int, int]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        parts = line.split()
        if parts[0] == "p":
            if len(parts) < 4:
                raise ValueError(f"{item_id}: malformed PACE problem line {lineno}")
            n = int(parts[-2])
            source_m = int(parts[-1])
            continue
        if len(parts) < 2:
            raise ValueError(f"{item_id}: malformed PACE edge line {lineno}")
        u, v = int(parts[0]) - 1, int(parts[1]) - 1
        edges.append((u, v))
    if n is None:
        raise ValueError(f"{item_id}: PACE file has no problem line")
    return n, source_m, edges


def _pace_archive_member(archive: zipfile.ZipFile, idx: str) -> str:
    """Locate a PACE graph by its three-digit instance number."""
    token = idx.zfill(3)
    candidates: list[str] = []
    for name in archive.namelist():
        if name.endswith("/"):
            continue
        base = Path(name).name.lower()
        suffix = Path(base).suffix.lower()
        if suffix not in {".hgr", ".gr", ".txt"}:
            continue
        # Archives have appeared with names such as vc-exact_085.hgr and 085.hgr.
        # Require the instance number to be a complete numeric token so 085 cannot
        # accidentally match a larger number.
        positions = [i for i in range(len(base) - len(token) + 1) if base[i:i+3] == token]
        if any(
            (i == 0 or not base[i - 1].isdigit())
            and (i + 3 == len(base) or not base[i + 3].isdigit())
            for i in positions
        ):
            candidates.append(name)
    if len(candidates) != 1:
        raise ValueError(
            f"PACE instance {token}: expected exactly one archive member; "
            f"found {len(candidates)} ({candidates[:5]})"
        )
    return candidates[0]


def install_pace(*, force: bool = False) -> int:
    """Install the tracked 20-instance PACE 2019 MVC open challenge pack."""
    label = "PACE 2019 Minimum Vertex Cover"
    manifest_path = ROOT / "benchmarks/minimum_vertex_cover/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("suites", {}).get("challenge_open", [])
    if not rows:
        print(f"{label}: no challenge_open entries are configured")
        return 0

    targets = [manifest_path.parent / item["file"] for item in rows]
    if not force and all(
        _installed_course_graph_matches(path, n=int(item["n"]), m=int(item["m"]))
        for item, path in zip(rows, targets)
    ):
        print(f"{label}: {len(rows)}/{len(rows)} already installed")
        return len(rows)

    first_download = rows[0].get("download") or {}
    archive_url = first_download.get("url")
    expected_md5 = first_download.get("archive_md5")
    if not archive_url:
        raise ValueError("PACE challenge manifest has no download URL")

    payload = download(archive_url)
    if expected_md5:
        got = hashlib.md5(payload).hexdigest()
        if got.lower() != str(expected_md5).lower():
            raise RuntimeError(
                f"PACE archive MD5 mismatch: expected {expected_md5}, got {got}"
            )

    installed = 0
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for item, dest in zip(rows, targets):
            if (
                not force
                and _installed_course_graph_matches(
                    dest, n=int(item["n"]), m=int(item["m"])
                )
            ):
                installed += 1
                continue

            spec = item.get("download") or {}
            idx = str(spec.get("member_id") or item["id"].rsplit("_", 1)[-1]).zfill(3)
            member = _pace_archive_member(archive, idx)
            source_n, source_m, source_edges = _parse_pace_vc(
                archive.read(member), item_id=item["id"]
            )
            expected_n = int(item["n"])
            expected_m = int(item["m"])
            if source_n != expected_n:
                raise RuntimeError(
                    f"{item['id']}: PACE vertex count {source_n} does not match "
                    f"manifest n={expected_n}"
                )
            if source_m is not None and source_m != expected_m:
                raise RuntimeError(
                    f"{item['id']}: PACE header edge count {source_m} does not match "
                    f"manifest source m={expected_m}"
                )
            n, edges = _normalize_undirected_edges(source_edges, expected_n=expected_n)
            if len(edges) != expected_m:
                raise RuntimeError(
                    f"{item['id']}: normalized edge count {len(edges)} does not match "
                    f"manifest m={expected_m}. The source may contain loops or duplicate "
                    "edges; update the tracked normalization metadata before distributing it."
                )
            _write_course_graph(dest, n, edges)
            installed += 1

    print(f"{label}: {installed}/{len(rows)} installed (1 source archive this run)")
    return installed


def install_tsplib_classic(*, force: bool = False) -> int:
    """Install a small classic TSPLIB pack without expanding O(n^2) edges."""
    names = {
        "eil51": 426,
        "berlin52": 7542,
        "kroA100": 21282,
        "a280": 2579,
        "pr1002": 259045,
        "pcb3038": 137694,
    }
    out = ROOT / "benchmarks/traveling_salesperson/external/tsplib"
    inst = out / "instances"
    inst.mkdir(parents=True, exist_ok=True)
    rows = []
    base = "https://softlib.rice.edu/pub/tsplib/tsp/"
    downloaded = 0

    for name, optimum in names.items():
        dest = inst / f"{name}.tsp"
        source_url = base + name + ".tsp.gz"
        if force or not dest.is_file():
            raw = gzip.decompress(download(source_url))
            dest.write_bytes(raw)
            downloaded += 1
        rows.append(
            {
                "id": name,
                "file": f"instances/{dest.name}",
                "n": None,
                "m": None,
                "known_optimum": optimum,
                "algorithms": ["heuristic1"],
                "timeout": 30,
                "seeds": [11, 29, 47, 71, 101],
                "origin": "external",
                "source": {
                    "collection": "TSPLIB95",
                    "instance": f"{name}.tsp",
                    "url": source_url,
                    "citation": "TSPLIB95 benchmark collection",
                },
                "reference": {
                    "known_optimum": {
                        "url": "https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/TSP-BEST.html",
                        "citation": "TSPLIB95 best/optimal tour values",
                    }
                },
            }
        )

    manifest = {
        "schema_version": 2,
        "problem": "traveling_salesperson",
        "objective": "minimize",
        "bound_kind": "lower",
        "suites": {"tsplib_classic": rows},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    total = len(rows)
    if downloaded:
        print(f"TSPLIB95: downloaded {downloaded}; {total}/{total} installed")
    else:
        print(f"TSPLIB95: {total}/{total} already installed")
    return total


def install_waterloo_tsp(*, force: bool = False) -> int:
    """Install every Waterloo TSP suite currently configured in the tracked manifest."""
    manifest_path = ROOT / "benchmarks/traveling_salesperson/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    suites = ["leaderboard_known", "reach_known", "reach_open"]
    count = 0
    downloaded = 0
    for suite in suites:
        if suite not in manifest.get("suites", {}):
            continue
        for item in manifest["suites"][suite]:
            target = manifest_path.parent / item["file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            source = item.get("source")
            source_url = source.get("url") if isinstance(source, dict) else item.get("source_url")
            if not source_url:
                raise ValueError(f"{item['id']} has no external source URL")
            if force or not target.is_file():
                raw = download(source_url)
                target.write_bytes(raw)
                downloaded += 1
            count += 1
    if downloaded:
        print(f"Waterloo National TSP: downloaded {downloaded}; {count}/{count} installed")
    else:
        print(f"Waterloo National TSP: {count}/{count} already installed")
    return count



def _tsplib_dimension(raw: bytes, *, item_id: str) -> int:
    """Read the DIMENSION field from a TSPLIB text payload."""
    text = raw.decode("utf-8-sig", errors="replace")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if upper.startswith("DIMENSION"):
            if ":" in stripped:
                value = stripped.split(":", 1)[1].strip()
            else:
                parts = stripped.split()
                if len(parts) < 2:
                    break
                value = parts[-1]
            try:
                return int(value)
            except ValueError as exc:
                raise ValueError(f"{item_id}: invalid TSPLIB DIMENSION {value!r}") from exc
    raise ValueError(f"{item_id}: TSPLIB file has no DIMENSION field")


def _installed_tsplib_matches(path: Path, *, n: int) -> bool:
    if not path.is_file():
        return False
    try:
        return _tsplib_dimension(path.read_bytes(), item_id=path.name) == n
    except (OSError, ValueError):
        return False


def install_waterloo_vlsi_tsp(*, force: bool = False) -> int:
    """Install the tracked 20-instance open Waterloo VLSI TSP challenge."""
    label = "Waterloo VLSI TSP open challenge"
    manifest_path = ROOT / "benchmarks" / "traveling_salesperson" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("suites", {}).get("challenge_open", [])
    if not rows:
        print(f"{label}: no challenge_open entries are configured")
        return 0

    targets = [manifest_path.parent / item["file"] for item in rows]
    if not force and all(
        _installed_tsplib_matches(path, n=int(item["n"]))
        for item, path in zip(rows, targets)
    ):
        print(f"{label}: {len(rows)}/{len(rows)} already installed")
        return len(rows)

    archive_cache: dict[str, bytes] = {}
    downloaded_urls: set[str] = set()
    installed = 0
    for item, target in zip(rows, targets):
        if not force and _installed_tsplib_matches(target, n=int(item["n"])):
            installed += 1
            continue
        spec = item.get("download") or {}
        url = spec.get("url")
        if not url:
            raise ValueError(f"{item['id']} has no download.url")
        if url not in archive_cache:
            archive_cache[url] = download(url)
            downloaded_urls.add(url)
        raw = _extract_source_bytes(archive_cache[url], spec, item_id=item["id"])
        source_n = _tsplib_dimension(raw, item_id=item["id"])
        if source_n != int(item["n"]):
            raise RuntimeError(
                f"{item['id']}: TSPLIB DIMENSION {source_n} does not match "
                f"manifest n={item['n']}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        installed += 1

    print(
        f"{label}: {installed}/{len(rows)} installed "
        f"({len(downloaded_urls)} source archive download(s) this run)"
    )
    return installed


def _parse_edge_text(raw: bytes, *, csv_format: bool = False) -> list[tuple[int, int]]:
    """Parse the first two integer columns of a SNAP edge-list payload."""
    text = raw.decode("utf-8-sig")
    edges: list[tuple[int, int]] = []
    if csv_format:
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            if len(row) < 2:
                continue
            try:
                u, v = int(row[0].strip()), int(row[1].strip())
            except ValueError:
                # SNAP CSV edge files use one header row such as ``from,to``.
                continue
            edges.append((u, v))
        return edges

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "%")):
            continue
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            u, v = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        edges.append((u, v))
    return edges


def _normalize_undirected_edges(
    raw_edges: list[tuple[int, int]], *, expected_n: int
) -> tuple[int, list[tuple[int, int]]]:
    """Normalize source labels to the course's 0..n-1 simple-graph format."""
    labels = {x for edge in raw_edges for x in edge}
    if len(labels) > expected_n:
        raise ValueError(
            f"source contains {len(labels)} distinct vertices but manifest expects {expected_n}"
        )

    # Preserve SNAP's labels when they already lie in the course range.  Otherwise
    # relabel observed vertices contiguously.  Any source-declared isolated vertices
    # remain as unused course vertex IDs at the end of the range.
    if all(0 <= x < expected_n for x in labels):
        remap = None
    else:
        remap = {label: i for i, label in enumerate(sorted(labels))}

    simple: set[tuple[int, int]] = set()
    for u, v in raw_edges:
        if remap is not None:
            u, v = remap[u], remap[v]
        if u == v:
            continue
        simple.add((u, v) if u < v else (v, u))
    return expected_n, sorted(simple)


def _write_course_graph(dest: Path, n: int, edges: list[tuple[int, int]]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        f"{n} {len(edges)}\n" + "".join(f"{u} {v}\n" for u, v in edges),
        encoding="utf-8",
    )


def _installed_course_graph_matches(path: Path, *, n: int, m: int) -> bool:
    """Cheap integrity check for an already installed normalized graph."""
    if not path.is_file():
        return False
    try:
        with path.open("r", encoding="utf-8") as infile:
            header = infile.readline().split()
            if header != [str(n), str(m)]:
                return False
            edge_lines = sum(1 for line in infile if line.strip())
        return edge_lines == m
    except OSError:
        return False


def _extract_source_bytes(payload: bytes, spec: dict, *, item_id: str) -> bytes:
    """Extract one source edge-list file from a configured payload."""
    archive_kind = spec.get("archive")
    member_name = spec.get("member")

    if archive_kind == "zip":
        if not member_name:
            raise ValueError(f"{item_id} zip download has no member")
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            candidates = [
                name for name in archive.namelist()
                if Path(name).name.lower() == member_name.lower()
            ]
            if len(candidates) != 1:
                raise ValueError(
                    f"{item_id}: expected one ZIP member named {member_name!r}; "
                    f"found {len(candidates)}"
                )
            return archive.read(candidates[0])

    if archive_kind in {"tar.gz", "tgz"}:
        if not member_name:
            raise ValueError(f"{item_id} tar download has no member")
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            candidates = [
                member for member in archive.getmembers()
                if member.isfile() and Path(member.name).name.lower() == member_name.lower()
            ]
            if len(candidates) != 1:
                raise ValueError(
                    f"{item_id}: expected one TAR member named {member_name!r}; "
                    f"found {len(candidates)}"
                )
            extracted = archive.extractfile(candidates[0])
            if extracted is None:
                raise ValueError(f"{item_id}: could not extract {member_name!r}")
            return extracted.read()

    if spec.get("compression") == "gzip":
        return gzip.decompress(payload)
    return payload


def _install_snap_graph_pack(
    *, problem: str, suite: str = "challenge_open", label: str, force: bool = False
) -> int:
    """Install a manifest-defined SNAP simple-undirected-graph pack."""
    manifest_path = ROOT / "benchmarks" / problem / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("suites", {}).get(suite, [])
    if not rows:
        print(f"{label}: no {suite} entries are configured")
        return 0

    targets = [manifest_path.parent / item["file"] for item in rows]
    if not force and all(
        _installed_course_graph_matches(path, n=int(item["n"]), m=int(item["m"]))
        for item, path in zip(rows, targets)
    ):
        print(f"{label}: {len(rows)}/{len(rows)} already installed")
        return len(rows)

    payload_cache: dict[str, bytes] = {}
    installed = 0
    downloaded_urls: set[str] = set()

    for item, dest in zip(rows, targets):
        if (
            not force
            and _installed_course_graph_matches(
                dest, n=int(item["n"]), m=int(item["m"])
            )
        ):
            installed += 1
            continue

        spec = item.get("download") or {}
        url = spec.get("url")
        if not url:
            raise ValueError(f"{item['id']} has no download.url")
        if url not in payload_cache:
            payload_cache[url] = download(url)
            downloaded_urls.add(url)
        source_bytes = _extract_source_bytes(
            payload_cache[url], spec, item_id=item["id"]
        )
        source_edges = _parse_edge_text(
            source_bytes, csv_format=spec.get("format") == "snap_edge_list_csv"
        )
        n, edges = _normalize_undirected_edges(
            source_edges, expected_n=int(item["n"])
        )
        expected_m = item.get("m")
        if expected_m is not None and len(edges) != int(expected_m):
            raise RuntimeError(
                f"{item['id']}: normalized edge count {len(edges)} does not match "
                f"manifest m={expected_m}"
            )
        _write_course_graph(dest, n, edges)
        installed += 1

    print(
        f"{label}: {installed}/{len(rows)} installed "
        f"({len(downloaded_urls)} source download(s) this run)"
    )
    return installed


def install_longest_path_snap(*, force: bool = False) -> int:
    """Install the tracked 20-instance SNAP Longest Path open challenge pack."""
    return _install_snap_graph_pack(
        problem="longest_path", label="SNAP Longest Path", force=force
    )


def install_maximum_clique_snap(*, force: bool = False) -> int:
    """Install the tracked 20-instance SNAP Maximum Clique open challenge pack."""
    return _install_snap_graph_pack(
        problem="maximum_clique", label="SNAP Maximum Clique", force=force
    )


# Legacy implementation retained below only until the common SNAP installer was
# introduced; replace its body with the common installer above.

def _parse_dimacs_col(raw: bytes, *, item_id: str) -> tuple[int, int | None, list[tuple[int, int]]]:
    """Parse a DIMACS/COLOR `.col` graph into zero-based undirected edges."""
    text = raw.decode("utf-8-sig", errors="replace")
    n: int | None = None
    source_m: int | None = None
    edges: list[tuple[int, int]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        parts = line.split()
        tag = parts[0].lower()
        if tag == "p":
            if len(parts) < 4:
                raise ValueError(f"{item_id}: malformed DIMACS problem line {lineno}")
            n = int(parts[-2])
            source_m = int(parts[-1])
            continue
        if tag == "e":
            if len(parts) < 3:
                raise ValueError(f"{item_id}: malformed DIMACS edge line {lineno}")
            u, v = int(parts[1]) - 1, int(parts[2]) - 1
            edges.append((u, v))
            continue
        # Ignore other COLOR extensions (for example fixed-color or node-weight
        # records); the curated challenge entries are ordinary graph-coloring
        # instances and use only their simple undirected edge relation.
    if n is None:
        raise ValueError(f"{item_id}: DIMACS file has no problem line")
    return n, source_m, edges


def install_graph_coloring_dimacs(*, force: bool = False) -> int:
    """Install the tracked 20-instance DIMACS/COLOR coloring open challenge."""
    problem = "minimum_graph_coloring"
    label = "DIMACS/COLOR Minimum Graph Coloring"
    manifest_path = ROOT / "benchmarks" / problem / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("suites", {}).get("challenge_open", [])
    if not rows:
        print(f"{label}: no challenge_open entries are configured")
        return 0

    targets = [manifest_path.parent / item["file"] for item in rows]
    if not force and all(
        _installed_course_graph_matches(path, n=int(item["n"]), m=int(item["m"]))
        for item, path in zip(rows, targets)
    ):
        print(f"{label}: {len(rows)}/{len(rows)} already installed")
        return len(rows)

    installed = 0
    downloaded = 0
    for item, dest in zip(rows, targets):
        if (
            not force
            and _installed_course_graph_matches(
                dest, n=int(item["n"]), m=int(item["m"])
            )
        ):
            installed += 1
            continue

        spec = item.get("download") or {}
        url = spec.get("url")
        if not url:
            raise ValueError(f"{item['id']} has no download.url")
        payload = download(url)
        downloaded += 1
        source_n, source_m, source_edges = _parse_dimacs_col(
            payload, item_id=item["id"]
        )
        if source_n != int(item["n"]):
            raise RuntimeError(
                f"{item['id']}: DIMACS vertex count {source_n} does not match "
                f"manifest n={item['n']}"
            )
        n, edges = _normalize_undirected_edges(
            source_edges, expected_n=int(item["n"])
        )
        if len(edges) != int(item["m"]):
            detail = f"; source header m={source_m}" if source_m is not None else ""
            raise RuntimeError(
                f"{item['id']}: normalized edge count {len(edges)} does not match "
                f"manifest m={item['m']}{detail}"
            )
        _write_course_graph(dest, n, edges)
        installed += 1

    print(
        f"{label}: {installed}/{len(rows)} installed "
        f"({downloaded} source download(s) this run)"
    )
    return installed

def install_for_problem(problem: str, *, force: bool = False) -> int:
    """Install all external packs currently configured for one project problem."""
    projects = valid_projects()
    if problem not in projects:
        raise ValueError(f"unknown problem identifier: {problem}")

    print(f"External benchmark setup: {problem}")
    if problem == "minimum_vertex_cover":
        return install_pace(force=force)
    if problem == "traveling_salesperson":
        return (
            install_tsplib_classic(force=force)
            + install_waterloo_tsp(force=force)
            + install_waterloo_vlsi_tsp(force=force)
        )
    if problem == "longest_path":
        return install_longest_path_snap(force=force)
    if problem == "maximum_clique":
        return install_maximum_clique_snap(force=force)
    if problem == "minimum_graph_coloring":
        return install_graph_coloring_dimacs(force=force)

    # The common interface is in place before the remaining curated collections
    # are selected.  Adding those packs does not change the student command.
    print("No external benchmark pack is configured for this problem yet.")
    return 0


def main() -> int:
    projects = valid_projects()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--problem",
        choices=sorted(projects),
        help="override project.json assigned_problem (instructor/debug use)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="install external packs for every currently configured problem",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload files even when they are already present",
    )
    args = parser.parse_args()

    if args.all and args.problem:
        parser.error("--all and --problem cannot be used together")

    if args.all:
        for problem in projects:
            print()
            install_for_problem(problem, force=args.force)
        return 0

    problem = args.problem or assigned_problem()
    if not problem:
        parser.error(
            "no assigned problem; set assigned_problem in project.json after project "
            "assignments are posted, or pass --problem"
        )
    install_for_problem(problem, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
