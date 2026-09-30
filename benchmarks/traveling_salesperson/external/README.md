# External TSP benchmarks

This directory is populated automatically after project assignment by:

```bash
python tools/setup_project.py
```

Downloaded benchmark files are intentionally ignored by Git. The tracked parent
`manifest.json` records the provenance and published reference values for the
Waterloo National and VLSI challenge suites. The tracked 20-instance open VLSI
pack is extracted from Waterloo's published `vlsi_tsp.tgz` archive into
`external/vlsi/instances/`. Additional installed packs may keep their generated
metadata under this external directory.

Students normally should not call collection-specific installers or copy files
into this directory by hand.
