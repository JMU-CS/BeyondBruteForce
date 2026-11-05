# Maximum Clique benchmarks

These course-provided suites support the Checkpoint 1 readiness check and the Final Project
experimental study for Maximum Clique.

All required instances are simple, unweighted, undirected graphs.  The exact
optimum is known for every required instance because the graphs are generated
from families whose clique number is known by construction.

## Required suites

- `readiness` — tiny smoke tests for the Checkpoint 1 exhaustive baseline,
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

## Open SNAP challenge

After your assigned problem appears in `project.json`, run:

```bash
python tools/setup_project.py
```

For Maximum Clique, setup installs a 20-instance open challenge collection from
Stanford's SNAP repository. The selected graphs are undirected social networks
from Facebook, Deezer, Twitch, GitHub, and the Facebook ego-network collection.
The downloaded graph files are stored under:

```text
benchmarks/maximum_clique/external/snap/instances/
```

and are intentionally ignored by Git. The tracked `manifest.json` keeps the
source page, original source filename/archive member, citation, and download
information for each instance.

Run the open challenge with:

```bash
python tools/run_experiments.py --suite challenge_open
```

For source files that contain self-loops or repeated undirected edges, the installer normalizes them to the project's simple-graph representation. The manifest keeps SNAP's published source edge count separately when it differs from the installed simple-graph edge count.

The course does **not** claim an exact maximum clique size for these instances;
each entry therefore records `known_optimum = null`. If your heuristic finds a
valid clique of size `L` and your polynomial-time upper-bound routine returns
`U`, the evidence supports only:

```text
L <= OPT <= U
```

A clique found by your team or another team is a feasible lower bound on the
optimum. Do not describe a best-so-far clique as optimal unless optimality has
actually been established.
