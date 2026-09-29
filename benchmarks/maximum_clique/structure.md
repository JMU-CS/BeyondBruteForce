# Maximum Clique structural benchmark family

The required `structure` suite studies **edge density** while controlling two
important quantities:

- every graph has exactly 300 vertices; and
- every graph has maximum clique size 10.

Each instance is a complete 10-partite graph. Vertices in the same part are not
adjacent; every pair of vertices in different parts is adjacent. Therefore a
clique may contain at most one vertex from each part, and choosing one vertex
from each of the ten parts gives a clique of size 10. Thus `OPT=10` for every
instance in the suite.

The suite changes the part-size distribution:

- **balanced:** ten parts of size 30;
- **moderately imbalanced:** one part of size 120 and nine parts of size 20;
- **highly imbalanced:** one part of size 210 and nine parts of size 10.

Changing the part sizes changes the number of missing within-part edges and
therefore changes graph density without changing `n` or `OPT`. Three independently
relabelled instances are provided for each condition.

Use the suite to investigate whether edge density affects heuristic quality,
runtime, variation across seeds, or the tightness of your polynomial-time upper
bound. Do not assume in advance that denser or sparser instances must be harder;
treat that as an experimental question.
