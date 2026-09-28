# Course Benchmark Suites

The benchmark framework is **course infrastructure**. Students run it and analyze
its output; they are not expected to write timing, CSV, timeout, validation, or
benchmark-generation code.

Each implemented problem has:

```text
benchmarks/PROBLEM/manifest.json
benchmarks/PROBLEM/instances/
```

The manifest records the suite membership, known optimum when available,
structural metadata, algorithms to run, seeds, and timeout policy.

## Required suites

- `readiness` — tiny CP3 smoke test of improved exact, heuristic1, the bound,
  validation, timing, and result generation.
- `exact_frontier` — compare exhaustive and improved exact on increasingly
  challenging instances with known optima.
- `quality_known` — compare heuristic solution quality and bound quality when
  OPT is known.
- `heuristic_scale` — run heuristic(s) and the bound after exact computation is
  no longer practical; OPT may be unknown.
- `structure` — hold size approximately fixed while varying one course-selected
  structural characteristic.

Run, for example:

```bash
python tools/run_experiments.py --suite readiness
python tools/run_experiments.py --suite exact_frontier
python tools/run_experiments.py --all
```

Results are written to `experiments/latest.csv` and `experiments/latest.json`,
with timestamped copies retained as well.

## Known optimum versus computed bound

`known_optimum` is instructor metadata. It is present only when the course knows
the exact optimum for that benchmark. `bound_value` is computed by the team's
Checkpoint 3 bound function. They are intentionally separate fields.

For a minimization problem with a lower bound, a large-instance result might be:

```text
bound_value = 117
objective   = 126
known_optimum = null
```

which certifies only `117 <= OPT <= 126`.

## Optional established benchmark collections

Core CP4 does not require network access. Optional public packs can be installed
with:

```bash
python tools/install_external_benchmarks.py pace2019-vc
python tools/install_external_benchmarks.py tsplib
```

PACE 2019 Vertex Cover instances are used as established large/hard graph
instances. Selected TSPLIB95 EUC_2D instances are converted to the project's
complete weighted edge-list format and retain their published optimum values.

## Optional `geng` suites

`geng` (from nauty) generates non-isomorphic graphs. It is useful for extensions
that examine *all* non-isomorphic graphs in a small size/edge range rather than
a random sample.

macOS:

```bash
brew install nauty
```

Ubuntu:

```bash
sudo apt install nauty
```

The course wrapper detects both the Homebrew command `geng` and Ubuntu's
`nauty-geng` command.

Example:

```bash
python tools/generate_geng_suite.py --n 9 --edges 12:20 --connected --limit 300
```

The command prints the corresponding `run_experiments.py` invocation. `geng` is
**not required for the core checkpoint**, because required instances are already
materialized in the repository.
