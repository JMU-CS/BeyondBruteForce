# External Maximum Clique benchmark data

After project assignment, run:

```bash
python tools/setup_project.py
```

For a team assigned `maximum_clique`, the setup tool downloads and normalizes
the 20-instance SNAP social-network challenge pack configured in the tracked
`benchmarks/maximum_clique/manifest.json`.

Downloaded/converted graph files are stored below this directory and are
intentionally ignored by Git. The converter removes self-loops and collapses repeated/reversed
undirected edges so every installed instance matches the project simple-graph
format. The tracked manifest preserves the published source edge count when it
differs from the normalized count. This README and the manifest remain tracked so the
benchmark provenance and installation recipe are preserved in every team repo.

Run the installed challenge with:

```bash
python tools/run_experiments.py --suite challenge_open
```
