# External Minimum Graph Coloring benchmark data

Run:

```bash
python tools/setup_project.py
```

The setup tool downloads the configured DIMACS/COLOR graph-coloring challenge
instances from the Carnegie Mellon benchmark archive and converts DIMACS `.col`
edge lists to the common Beyond Brute Force graph format.

Installed files live under `dimacs/instances/` and are intentionally ignored by
Git.  The tracked `../manifest.json` records per-instance provenance, source URLs,
and any published feasible/reference values.
