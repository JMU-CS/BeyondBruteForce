# Traveling Salesperson Benchmarks

All course instances are complete undirected weighted graphs using the shared
`n m` / `u v weight` format.

- `readiness`: 6-8 city instances with known OPT.
- `exact_frontier`: 8-11 city instances with known OPT.
- `quality_known`: small Euclidean instances with known OPT.
- `heuristic_scale`: 100-, 250-, and 500-city Euclidean instances.
- `structure`: fixed-size instances in three weight-structure families:
  uniform Euclidean points, clustered Euclidean points, and independent random
  edge weights. These mirror the broad instance types used in the DIMACS TSP
  Challenge testbed.

Selected official TSPLIB95 instances can be installed under `external/tsplib/`
with `tools/install_external_benchmarks.py tsplib`. The installer converts
EUC_2D coordinates using TSPLIB's integer rounding rule and stores the published
optimal tour cost in the external manifest.
