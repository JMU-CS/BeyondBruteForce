# Longest Path structural benchmark

The required Longest Path structural experiment studies **edge density**.

All required structural instances have:

- `n = 300` vertices;
- a randomly labeled planted Hamiltonian path, so the known optimum is always
  `299` edges;
- the same unweighted, undirected graph representation; and
- additional random edges inserted at one of four probabilities.

The manifest identifies the structural variable as:

```text
structure_name = extra_edge_probability
```

with values:

```text
0.01, 0.03, 0.08, 0.20
```

There are three independently generated instances at each value. Random labels
and different generation seeds prevent the planted Hamiltonian path from simply
being the numeric order `0, 1, 2, ...`.

## Why density is interesting

Increasing density gives a path-building algorithm more possible extensions at
many search states. That may help a heuristic avoid getting stuck, but it can
also increase branching for an exact search. Sparse graphs provide fewer
choices, while dense graphs provide many choices and many competing long
partial paths.

You should treat the direction of the effect as an **experimental question**,
not as a result that is known in advance.

## What is controlled

The number of vertices and the optimum path length are fixed. The intended
comparison is therefore not simply "larger graph versus smaller graph." The
main changing characteristic is the number of additional edges.

For your analysis, consider how density affects whichever measurements are most
informative for your implementation, including:

- heuristic path quality across the supplied seeds;
- variation in heuristic quality across seeds;
- heuristic running time or other work measures; and
- if you choose to run the improved exact solver on selected structural cases,
  its search effort or ability to reach the exact frontier.
