# External Longest Path benchmark data

After project assignment, run:

```bash
python tools/setup_project.py
```

For Longest Path, setup installs the tracked 20-instance SNAP open-challenge pack
under `external/snap/instances/`. Downloaded instance files are intentionally
ignored by Git; source/provenance metadata stays tracked in the parent
`benchmarks/longest_path/manifest.json`.

Normal student use should not download or rename these files by hand. Rerunning
setup skips instances that are already installed; `--force` is available through
the lower-level installer for instructor/debug use.
