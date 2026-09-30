# Traveling Salesperson benchmark suites

These benchmark suites support Checkpoints 3 and 4 for the Traveling Salesperson Problem (TSP).

Student algorithms do **not** parse benchmark files themselves. Course-owned input code converts every supported file into the same `WeightedGraph` interface. In particular, student code should rely on:

```python
graph.num_vertices
graph.weight(u, v)
```

Large complete TSP instances are not stored as millions of explicit edges. Coordinate-backed instances compute edge weights on demand, and course-generated random-weight instances compute deterministic weights on demand.

## Required suites

### `readiness`

Small known-optimum instances used during Checkpoint 2 to verify the improved exact solver and first heuristic.

### `exact_frontier`

Known-optimum instances designed to identify the practical boundary of exact computation.

The suite contains three matched instance families:

- `uniform_euclidean`
- `clustered_euclidean`
- `random_weights`

For each family, the number of cities increases through 10, 12, 14, 16, 18, and 20. The runner stops trying a particular exact algorithm on later instances in a family after that algorithm times out. This prevents the experiment from spending repeated timeout periods after its practical frontier has already been crossed.

The straightforward exhaustive solver is expected to reach its limit much earlier than a successful improved exact solver. Because the three families use the same values of `n`, the experiment can also reveal whether the improved method is sensitive to edge-weight structure.

### `quality_known`

Small known-optimum instances for early heuristic-quality and bound checks.

### `heuristic_scale`

Coordinate-backed Euclidean instances with 250, 1,000, and 3,000 cities. These are intended to test whether a heuristic continues to run on instances far beyond the exact-search range.

Each randomized heuristic is run with the same five course-provided seeds so that students can examine variation in both returned solution value and wall-clock time.

### `structure`

Nine matched 500-city instances: three independent instances for each of three edge-weight structures. See [`structure.md`](structure.md) for the experimental variable and generation details. The synthetic benchmark files are reproducible with `python tools/generate_tsp_benchmarks.py`.

## Optional leaderboard and reach suites

The repository manifest also defines public University of Waterloo challenge suites:

- `leaderboard_known` — National TSP instances from 194 to 4,663 cities, all with proven optimal tour lengths;
- `reach_known` — larger National TSP instances from 7,146 to 24,978 cities, also with proven optimal tour lengths;
- `reach_open` — two very large National TSP instances with a published best-known tour and published lower bound rather than a known optimum; and
- `challenge_open` — 20 VLSI TSP instances from 14,233 to 38,478 cities that Waterloo still lists as open. Every entry has a published best-known tour; the first six also have a published Concorde lower bound.

After your problem assignment is recorded in `project.json`, install the external benchmark files with:

```bash
python tools/setup_project.py
```

The setup command installs the TSP external collections configured by the course, including the optional leaderboard and reach files. It is safe to rerun.

Then run them through the normal experiment framework, for example:

```bash
python tools/run_experiments.py --suite leaderboard_known
```

For a known-optimum instance, the generated result records the percentage gap from OPT. For an open instance, it records the percentage gap from the published best-known tour. When Waterloo also publishes a certified lower bound, that value is preserved separately. **A best-known tour is not labeled as an optimum unless optimality has been proven.**

Run the common 20-instance open challenge with:

```bash
python tools/run_experiments.py --suite challenge_open
```

For an instance with a published lower bound `L` and best-known tour `B`, the public record establishes `L <= OPT <= B`. When no public lower bound is recorded, your team's own polynomial-time lower-bound routine becomes the available certified lower side of the interval.

See [`leaderboard.md`](leaderboard.md) for the recommended multi-seed scoreboard metric and the distinction between the proven-optimum and open challenge boards.

## File formats

The TSP course input layer supports:

1. the original course weighted edge-list format (`n m`, followed by `u v weight`);
2. symmetric TSPLIB-style `EUC_2D` coordinate files; and
3. the compact course `BBF_RANDOM_UNIFORM` format used for large random-weight complete graphs.

For TSPLIB `EUC_2D`, `graph.weight(u, v)` uses the TSPLIB integer-distance rule rather than unrounded floating-point Euclidean distance.
