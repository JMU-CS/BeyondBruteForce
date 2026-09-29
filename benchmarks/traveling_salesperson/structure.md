# TSP structural benchmark: edge-weight structure

## Structural characteristic

**Edge-weight structure** is the characteristic varied by the required TSP `structure` suite.

Every required structural instance has exactly **500 cities**, so the number of cities is held fixed while the way edge weights are generated changes. The suite contains three independently generated instances for each of the following structures.

### Uniform Euclidean

Each city is sampled independently and uniformly from the square
`[0, 10000] x [0, 10000]`. The cost of an edge is the TSPLIB-rounded Euclidean distance between its endpoints.

A typical instance therefore looks like points scattered throughout one rectangular region, with no intentionally created groups. Nearby cities tend to have inexpensive edges, distances satisfy the triangle inequality, and edge costs reflect a coherent spatial layout.

### Clustered Euclidean

Cities are generated around four cluster centers:

```text
(2000, 2000)    (2000, 8000)
(8000, 2000)    (8000, 8000)
```

The generator places an equal number of cities at each center and perturbs each coordinate using a Gaussian distribution with standard deviation `650`. Coordinates are clipped to the same `[0, 10000] x [0, 10000]` square and the city labels are then shuffled. Edge costs are again TSPLIB-rounded Euclidean distances.

This preserves the geometric properties of Euclidean TSP while adding visible large-scale structure: many short edges occur inside clusters, while moving between clusters generally requires longer edges.

### Random weights

There is no underlying map. Each pair of cities receives a deterministic pseudo-random integer weight from **1 through 10,000**. The graph is still complete and symmetric, but edge weights do not arise from a geometric layout and need not satisfy the triangle inequality.

The random weights are generated on demand from the instance seed and the two endpoint IDs; the repository therefore does not need to store all 124,750 edge weights for a 500-city complete graph.

## What is controlled?

Across the three structural families:

- `n = 500` for every instance;
- every graph is complete and symmetric;
- each family contains three independently generated instances;
- Euclidean coordinates use the same 10,000-by-10,000 coordinate scale;
- random-weight values use a comparable numerical range (1 through 10,000); and
- randomized student heuristics are run under the same course-provided seeds.

The principal difference is therefore the **structure of the edge weights**, not the number of cities.

The exact course-generated files can be reproduced with:

```bash
python tools/generate_tsp_benchmarks.py
```

The generator uses fixed instance seeds, so regeneration is deterministic.

## Why this comparison matters

The three families all have the same number of cities and the same complete underlying graph, yet the edge costs contain very different information.

- In a Euclidean instance, nearby edges are related through geometry and the triangle inequality.
- In a clustered Euclidean instance, that local geometry is combined with a larger-scale cluster structure.
- In a random-weight instance, knowing that one edge is inexpensive provides essentially no geometric information about nearby choices.

An algorithm that uses branching, a lower bound, greedy choices, local improvement, or randomized construction may therefore behave differently on the three families even though `n` is identical. **Do not assume in advance which family will be easier.** The purpose of the experiment is to measure whether and how that structure affects the algorithms your team implemented.

## Experimental question

Investigate how edge-weight structure affects algorithm behavior. Depending on the algorithms your team developed, useful evidence may include:

- heuristic solution values and their variation across random seeds;
- heuristic running times and their variation across random seeds;
- the gap between the best feasible tour found and the Checkpoint 2 lower bound; and
- any consistent differences among uniform Euclidean, clustered Euclidean, and random-weight instances.

Explain what your measured data shows and distinguish that evidence from hypotheses about why the behavior occurs.
