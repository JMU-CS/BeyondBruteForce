# Minimum Graph Coloring structural benchmark

The required `structure` suite studies **edge density** while holding two major variables fixed:

- number of vertices: `n = 300`;
- chromatic number: `OPT = 8`.

Each graph is generated from eight planted color classes and contains an explicit `K_8`, so its chromatic number is exactly 8. Additional edges are placed only between different planted color classes, preserving an 8-coloring.

The three families use low, medium, and high cross-class edge probabilities. The manifest records the realized edge density for each instance. There are three independently generated instances per density level.

Use these instances to investigate how density affects heuristic solution quality, runtime, variation across seeds, and—when practical—the behavior of your improved exact solver.
