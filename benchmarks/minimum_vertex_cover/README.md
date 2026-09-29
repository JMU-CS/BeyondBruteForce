# Minimum Vertex Cover benchmark suites

These course-owned instances support Checkpoint 2 readiness checks and the
Final Project experiment runner.  Regenerate them deterministically with:

```bash
python tools/generate_minimum_vertex_cover_benchmarks.py
```

The suites are:

- **readiness** — small path, odd-cycle, and complete-bipartite smoke tests;
- **exact_frontier** — three known-optimum families (balanced complete
  bipartite graphs, disjoint star forests, and disjoint triangles).  The local
  frontier allows **900 seconds (15 minutes) per algorithm/instance** and skips
  larger members of a family after that algorithm first times out;
- **quality_known** — bipartite graphs with a planted cover and a matching of
  the same size, which certifies the exact optimum;
- **heuristic_scale** — the same certified construction at 500, 2,000, and
  5,000 vertices; and
- **structure** — nine 300-vertex graphs with **OPT = 120** while edge density
  varies across sparse, medium, and dense settings.

For each planted bipartite instance, one side of the bipartition is a vertex
cover of size `k`, while a matching of size `k` is also present.  The matching
proves that no smaller cover exists, so the optimum is known without solving an
NP-hard instance during benchmark generation.
