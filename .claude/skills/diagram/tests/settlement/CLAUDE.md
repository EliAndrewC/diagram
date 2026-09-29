# tests/settlement/ - the engine's unit tests as a package

Split from the 7,123-line `test_settlement.py` by feature 025 (constitution Principle X clause
13, tests included per v1.6.1). **Load only the module the task calls for.** Collection is
unchanged: same test names, same count, `python3 -m pytest tests/settlement/` from the skill dir.

The mapping rule mirrors the `settlement/` package: a test lives in the module named after the
`settlement/` subfile that defines the method or helper it primarily exercises (assignment was
derived from each test's attribute references, not guessed from names). When editing
`settlement/<module>.py`, the tests to load alongside are `tests/settlement/test_<module>.py`.

| module | tests for |
|---|---|
| `_builders.py` | shared fixture factories (`_town`, `_village`, `_city`, `_nuc_village`, `_walled_city`, ...) |
| `test_geom.py` / `test_knobs.py` | the `settlement/_geom/` package (all eleven submodules - its own index is `settlement/_geom/CLAUDE.md`) and the `settlement/_knobs.py` helper module. `test_geom.py` also holds the package's two surface guards, which are what a star-import re-export needs and an MRO does not |
| `test_core.py` | `core.py` (init/record streams/meta/rng/crop) plus tests with no single dominant subsystem |
| `test_<subsystem>.py` (fields, water_ways, shrines_wells, trades, homestead_parts, land, civic_grounds, city, castle_civic, houses, rolling, finish) | the same-named `settlement/` mixin module |
| `test_bearing.py` | `rolling/bearing.py` - which way a farmhouse faces, the turned boxes the placer clears, the quarter-turned yard - and the dooryard clause of `water_ways/lanes.py` `trim_lane_stubs` (269 E3, B17/B18) |
| `test_homestead_woods.py` | the homesteads' woods and the woods' own figures (269 E6): `CrownIndex` / `CanopyArea` (`_geom/indexes.py`), the commons' coppice stocking (`land/cover.py`), the bamboo under the belt and the yashikirin's range (`homestead_parts/groves.py`), the copse's area goal (`homestead_parts/stands.py`) |
| `structures/` | `settlement/structures/`, which is itself a package - one file per submodule, its own index in `tests/settlement/structures/CLAUDE.md` (feature 174) |

Adding a test: put it in the module matching the `settlement/` subfile (index in
`settlement/CLAUDE.md`); shared factories go in `_builders.py`, one-test helpers next to their
test. No test here monkeypatches a settlement module-level name (census:
`specs/025-human-scale-splits/consumer-census.json`); if one ever must, patch the DEFINING
submodule, per `settlement/CLAUDE.md`.
