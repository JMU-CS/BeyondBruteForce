# Minimum Vertex Cover benchmark suites

These course-owned instances support Checkpoint 1 readiness checks and the
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

## Open PACE 2019 challenge

After your assigned problem is recorded in `project.json`, run:

```bash
python tools/setup_project.py
```

For Minimum Vertex Cover, setup installs a curated **20-instance open challenge**
from the PACE 2019 Vertex Cover Exact benchmark archive. The selected instances
are precisely cases for which the published PACE solver report did not report a
minimum-cover size in its detailed result tables. Accordingly, the course
manifest records `known_optimum = null`; this means the course is not claiming a
certified optimum for these instances.

The source archive is the official PACE 2019 Track 1 dataset deposited on Zenodo
(DOI `10.5281/zenodo.3368306`). Downloaded/converted files are stored under:

```text
benchmarks/minimum_vertex_cover/external/pace2019/instances/
```

and are ignored by Git. Run the open challenge with:

```bash
python tools/run_experiments.py --suite challenge_open
```

If your heuristic finds a cover of size `U` and your polynomial-time lower bound
returns `L`, the evidence supports only `L <= OPT <= U` unless a separate cited
source establishes the exact optimum.
