# Minimum Vertex Cover structural experiment

The required structural family varies **edge density** while holding both graph
size and the optimum fixed.

- `n = 300`
- `OPT = 120`
- three density settings: sparse, medium, dense
- three deterministic replicates per setting

Every graph is bipartite.  A designated side containing 120 vertices is a
vertex cover, and the graph also contains a matching of size 120.  Therefore
the minimum vertex-cover size is exactly 120 in every instance even though the
number of additional cross edges changes substantially.

This lets you study whether density changes heuristic running time, solution
quality, variation across seeds, or lower-bound tightness without conflating
those effects with a change in `n` or in the optimum.
