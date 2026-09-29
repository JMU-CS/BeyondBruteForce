# Longest Path benchmark suites

These are the course-provided experiment suites for Longest Path.

Run them with, for example:

```bash
python tools/run_experiments.py --suite readiness
python tools/run_experiments.py --suite exact_frontier
python tools/run_experiments.py --suite quality_known
python tools/run_experiments.py --suite heuristic_scale
python tools/run_experiments.py --suite structure
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
