# Minimum Vertex Cover Benchmarks

The core manifest is `manifest.json`.

- `readiness`: three tiny, known-optimum instances for CP3 readiness.
- `exact_frontier`: fixed deterministic graphs of increasing size; OPT is known.
- `quality_known`: small graphs with known OPT, run under fixed heuristic seeds.
- `heuristic_scale`: 200-, 500-, and 1000-vertex graphs; OPT is intentionally
  not supplied, so students interpret the heuristic result with their lower bound.
- `structure`: 80-vertex graphs across an edge-density sweep, with three graph
  replicates at each density.

The optional PACE 2019 pack is installed under `external/pace2019/`. The course
uses it for additional hard-instance investigation; it is not needed to pass
core CP4.
