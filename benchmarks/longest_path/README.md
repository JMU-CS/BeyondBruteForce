# Longest Path benchmark suites

These are the course-provided experiment suites for Longest Path.

Run them with, for example:

```bash
python tools/run_experiments.py --suite readiness
python tools/run_experiments.py --suite exact_frontier
python tools/run_experiments.py --suite quality_known
python tools/run_experiments.py --suite heuristic_scale
python tools/run_experiments.py --suite structure
python tools/run_experiments.py --suite challenge_open
```

The project-wide experiment runner applies the timeout externally and records
both wall-clock time and the student's `statistics["time"]` value.

## Exact-search frontier

The Longest Path frontier uses three graph families whose optimum is known from
the construction:

1. **Three-arm trees.** Sparse graphs in which every pair of vertices has a
   unique connecting path. These emphasize how much work can be avoided by
   extending only valid partial paths instead of enumerating arbitrary ordered
   vertex sequences.
2. **Imbalanced complete bipartite graphs.** Connected graphs with many possible
   extensions but no Hamiltonian path when the two parts differ by more than
   one. These emphasize the difficulty of proving that a nearly Hamiltonian
   path is optimal.
3. **Two disconnected cliques.** Dense local structure combined with a global
   connectivity limitation. These reward algorithms that recognize that one
   path must remain inside a single connected component.

Each family is ordered from smaller to larger instances. The default local
exact-frontier ceiling is **900 seconds (15 minutes) per algorithm/instance**.
After an algorithm times out within one family, the runner skips larger
instances for that algorithm in the same family.

This 15-minute experimental ceiling is intentionally much larger than the
shorter timeout used by Gradescope. Gradescope is an automated correctness and
performance check; it is not intended to determine the true practical frontier
of an exact solver.

## Heuristic quality and scale

`quality_known` contains several graph families with known optimum values. Run
the randomized heuristic under the supplied fixed seeds and compare returned
path length with OPT.

`heuristic_scale` contains sparse graphs with a hidden, randomly labeled
Hamiltonian path plus additional edges. Therefore OPT is known to be `n - 1`,
while the graphs are large enough that the heuristic—not exhaustive exact
search—is the intended method.

## Structural experiment

See [`structure.md`](structure.md). The required structural variable is extra
edge density while graph size is held fixed. Every structural instance has a
hidden Hamiltonian path, so OPT is the same (`n - 1`) at every density.


## Open challenge benchmarks

After your team has been assigned Longest Path, run:

```bash
python tools/setup_project.py
```

This installs the 20-instance `challenge_open` suite under
`benchmarks/longest_path/external/snap/instances/`. The source files come from
the Stanford Large Network Dataset Collection (SNAP) and span collaboration,
social, communication, Twitch, and Internet autonomous-system networks. The
tracked `manifest.json` records the source dataset page, original file/member,
citation, size, and download location for every instance.

These are **open course challenges**: `known_optimum` is intentionally `null`
because the cited source does not establish the Longest Path optimum. A team may
report the longest valid path it found together with its valid upper bound, but
must not label a best-so-far path as optimal unless optimality is independently
proved.

SNAP files are converted only as needed to the course graph format (`n m` followed
by 0-based undirected edges). Vertex labels may be renumbered; self-loops are
removed and duplicate undirected edges are collapsed. The selected source datasets
are already documented by SNAP as undirected, so edge direction is not discarded.
