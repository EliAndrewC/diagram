# tests/settlement/ - the engine's unit tests as a package

**Load only the module the task calls for.** Run the package whole with `make test-file FILE=tests/settlement/`.

The mapping rule mirrors the `settlement/` package: a test lives in the module named after the
`settlement/` subfile that defines the method or helper it primarily exercises (assignment was
derived from each test's attribute references, not guessed from names). When editing
`settlement/<module>.py`, the tests to load alongside are `tests/settlement/test_<module>.py`.

| module | tests for |
|---|---|
| `_builders.py` | shared fixture factories (`_town`, `_village`, `_city`, `_nuc_village`, `_walled_city`, ...) |
| `test_geom.py` / `test_knobs.py` | the `settlement/_geom/` package (all its submodules - its own index is `l7r/diagram/settlement/_geom/CLAUDE.md`) and the `settlement/_knobs.py` helper module. `test_geom.py` also holds the package's two surface guards, which are what a star-import re-export needs and an MRO does not |
| `test_core.py` | `core.py` (init/record streams/meta/rng/crop) plus tests with no single dominant subsystem |
| `test_<subsystem>.py` (fields, water_ways, shrines_wells, trades, homestead_parts, land, civic_grounds, city, castle_civic, houses, rolling, finish) | the same-named `settlement/` mixin module |
| `test_bearing.py` | `rolling/bearing.py` - which way a farmhouse faces, the turned boxes the placer clears, the quarter-turned yard - and the dooryard clause of `water_ways/lanes.py` `trim_lane_stubs` |
| `test_homestead_woods.py` | the homesteads' woods and the woods' own figures: `CrownIndex` / `CanopyArea` (`_geom/indexes.py`), the commons' coppice stocking (`land/cover.py`), the bamboo under the belt and the yashikirin's range (`homestead_parts/groves.py`), the copse's area goal (`homestead_parts/stands.py`) |
| `test_grove_sides.py` | the farmstead grove's sides: `homestead_parts/grove_sides.py`, `grove_rules.py`, `rolling/dispersed.py` and the plan's roll of them |
| `test_*_NNN.py` (`test_fit_287.py`, `test_tiles_298.py`, ...) | one feature's tests of its own subject, named for that feature; the docstring names the module it holds. A new test still goes in the module matching its `settlement/` subfile |
| `structures/` | `settlement/structures/`, which is itself a package - one file per submodule, its own index in [`structures/CLAUDE.md`](structures/CLAUDE.md) |

Adding a test: put it in the module matching the `settlement/` subfile (index in
[`l7r/diagram/settlement/CLAUDE.md`](../../l7r/diagram/settlement/CLAUDE.md)); shared factories go in `_builders.py`,
one-test helpers next to their test. No test here monkeypatches a settlement module-level name (census:
`specs/025-human-scale-splits/consumer-census.json`); if one ever must, patch the DEFINING submodule, per
`l7r/diagram/settlement/CLAUDE.md`.
