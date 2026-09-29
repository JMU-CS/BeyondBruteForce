# Maximum Clique benchmarks

These course-provided suites support the Checkpoint 2 readiness check and the Final Project
experimental study for Maximum Clique.

All required instances are simple, unweighted, undirected graphs.  The exact
optimum is known for every required instance because the graphs are generated
from families whose clique number is known by construction.

## Required suites

- `readiness` — tiny smoke tests for the improved exact solver, heuristic, bound,
  validation, and experiment runner.
- `exact_frontier` — compares `exhaustive` and `improved` with a 900-second
  (15-minute) experimental ceiling per run. A timeout retires that algorithm
  from larger members of the same frontier family.
- `quality_known` — evaluates heuristic quality on moderate instances with known
  optimum values using five fixed seeds.
- `heuristic_scale` — checks heuristic scalability on sparse graphs up to 5,000
  vertices.
- `structure` — holds `n=300` and `OPT=10` fixed while changing edge density in
  complete multipartite graphs.

## Exact-frontier families

1. **Balanced complete bipartite graphs.** The maximum clique has size 2.
   A complete-candidate exhaustive search must reject almost every larger
   subset before reaching size 2.
2. **Complete multipartite graphs with parts of size 3.** A maximum clique
   contains exactly one vertex from each part. These graphs are dense but have
   a substantially smaller clique than the number of vertices.
3. **Two disconnected equal cliques.** Dense local structure is separated by a
   complete absence of edges between components. The maximum clique is one
   component.

Run, for example:

```bash
python tools/run_experiments.py --problem maximum_clique --suite readiness
python tools/run_experiments.py --problem maximum_clique --suite exact_frontier
python tools/run_experiments.py --problem maximum_clique --all
```

The exact-frontier timeout is an experimental ceiling, not a Gradescope limit.
Students may increase or decrease it locally with `--timeout` or
`--timeout-scale`.
