# TSP leaderboard and reach benchmarks

The optional TSP leaderboard uses established public benchmark instances so that
heuristic results can be compared with a meaningful external target.

## Known-optimum leaderboard

The `leaderboard_known` suite uses University of Waterloo National TSP instances
whose optimal tour length has been proven.  Each randomized heuristic is run on
the same fixed course seeds.

For one run, the reported percentage gap is

\[
100\,\frac{\text{tour length} - \mathrm{OPT}}{\mathrm{OPT}}.
\]

A gap of `0%` means the heuristic found an optimal tour.

For a multi-instance scoreboard, the recommended score is:

1. compute the **median percentage gap** across the fixed seeds for each instance;
2. take the **unweighted mean** of those per-instance medians; and
3. rank lower scores as better.

This prevents one unusually lucky random seed, or one benchmark with more recorded
runs, from dominating the board.  The best tour found and runtime summaries can be
displayed alongside the score, but are not part of the primary quality ranking.

Use:

```bash
python tools/summarize_tsp_leaderboard.py experiments/results/leaderboard_known.json --suite leaderboard_known
```

## Known-optimum reach problems

The `reach_known` suite uses much larger National TSP instances for which OPT is
also proven.  These are intended as stretch targets rather than required Final Project work.
A team that reaches `0%` has matched a known optimal tour.

## Open reach problems

The `reach_open` suite contains instances for which the manifest records both a
published **best-known tour** and a published **lower bound**.  The experiment
runner reports gap to the best-known tour, but does **not** call that tour optimal.
Students should use the published lower bound to understand how close the public
record itself is to the unknown optimum.

## Open VLSI challenge

The `challenge_open` suite is the common 20-instance open challenge used for the
large-scale TSP heuristic study.  It uses University of Waterloo's VLSI collection
and ranges from 14,233 to 38,478 cities.  Waterloo's public solution-status table
still lists these instances as open.

Every instance has a published best-known tour. The first six selected instances
also have a published Concorde lower bound; the remaining fourteen have no lower
bound recorded in Waterloo's summary. In those cases the team's required
polynomial-time lower-bound routine supplies the certified lower side of the
experimental interval.

Run it with:

```bash
python tools/run_experiments.py --suite challenge_open
```

## Installation

External data is downloaded during post-assignment setup and is ignored by Git:

```bash
python tools/setup_project.py
```

The command reads the assigned TSP project from `project.json` and installs all TSP external collections configured by the course.

Student algorithm code still receives the normal `WeightedGraph` API.  The course
input layer reads the coordinate-based benchmark and computes edge weights on demand.
