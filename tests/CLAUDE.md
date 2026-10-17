# `tests/` - the diagram project's test bed

<!-- the engine's dev loop applies to test work too -->
@../l7r/diagram/CLAUDE.md

## THE DIRECTORY DECIDES WHEN A TEST RUNS (feature 135, GM 2026-08-27)

*"if we have one directory for our quick tests, one directory for our done tests, and one directory
for our lengthy AWS tests, then that is probably both a useful efficiency improvement and also
something that helps from an organizational perspective because when we are deciding whether a new
test should be added, then the directory into which we added is the thing that inherently determines
When and under what circumstance that test is run"*. So there is no deselect list and no file roster:
the Makefile collects TREES, and where you put a test is the whole decision.

| tree | runs under | put a test here when |
|---|---|---|
| `tests/` (with its mirrored packages) | `make quick`, `make done`, the full run | it is a UNIT form: milliseconds to ~0.5 s, no map rolled, no tooling run. The quick suite's 60 s budget is the bar |
| `tests/gate/` | `make done` and the full run - never quick | it earns MERGE time: a real roll of one representative spec (served from the roll cache while nothing it executes changed - `l7r/diagram/pipeline/rollcache.py`), the bad-map corpus, a proof of tooling |
| `tests/full/` | a plain `make done` (its test phase IS `test-full`), `make test-full`, `make done FULL=1` and the AWS check | it is a SWEEP or a CARRIER: every pool map, every seed of a cohort, a determinism test that must roll twice for real, a fixture replayed only to carry coverage, a real-map cache round trip. All three coverage floors are enforced here, including the derived 100% floor on every module the scripted hamlet rolls execute (`l7r/diagram/tools/hamlet_floor.py`, run inline by the gate) |
| `tests/tooling/` | the gate and the full run - never quick (GM 2026-09-27; a `tooling`-marked test outside this tree, as in `tests/tools/`, is kept out of quick by its marker); at the gate, run when the tooling hash moved (a full plan), each test reused when its reads are those that made the baseline's coverage of it, that coverage carried (feature 383 amendment 5; never in FULL or `INCREMENTAL=0`); `make test-file FILE=tests/tooling` on demand | it RUNS the make/ci/pipeline tooling (make in a fixture, git repos in tmp, coverage subprocesses) |
| `tests/tier_town/`, `tests/tier_city/` | the gate and the full run | it is relevant to that tier only |
| `tests/soak/` | **no ordinary run** (`norecursedirs`); `make soak` names it (GM 2026-09-08) | it rolls MORE than the gate's floor strictly needs - a behavior asserted on a real map that no coverage line requires (constitution VI, feature 216); [`soak/CLAUDE.md`](soak/CLAUDE.md) |

## WHICH TARGET RUNS WHICH TREE - the table above read the other way round

`make quick` runs `tests/` alone; a plain `make done` is INCREMENTAL over what it collects (not `tier_*/`; `tooling/` only on a
stale stamp, reused per test); `make test-full` deselects nothing. A marker (`rolls_map`, `tooling`, `tiers`) filters within a
tree, the tree is the collection scope; a test with a quick and a full form stays in one tree and reads `EXHAUSTIVE`
(`tests/_scope.py`), a sweep-only test goes to `tests/full/`. **The layout mirrors the source**: a test for `X/y.py` is in
`tests/X/test_y.py`. The per-directory indexes (`settlement/`, `hamletgen/ways/`, `full/interactive/page_browser/`, `soak/`) and
the root-level suites (`test_villages.py`, `gate/test_*.py`, `test_compound.py`, `test_citybudget.py`) are listed in [`test-bed-detail.md`](test-bed-detail.md), with the full target table and what `done FULL=1` adds.

## Running it

    make quick                                         # while iterating: the tests your change reaches
    make test-file FILE=tests/settlement/              # one mirrored package, WHOLE
    make done                                          # the real gate: lint + format + pyrefly + tests + coverage

The hooks refuse a bare `pytest` (`make-only-hooks.sh` rewrites a targeted one to `make test-file`). Before the gate,
run the WHOLE affected file or directory, never a `-k` subset: a filter selects the tests you were thinking about, and a
change breaks the ones you were not (`gate-hooks.sh`).

`testpaths = ["tests"]` in `pyproject.toml` pins collection here. Without it pytest walks the whole
repository, every `.clones/` checkout included - pytest does not read `.gitignore`.

## A HAMLET IS ROLLED ONCE PER GATE, AND ROLLING ANOTHER IS A RECORDED DECISION (feature 213, GM 2026-09-07)

**`tests/rolls.py` is the roster** of every spec the gate may roll, each with its reason; a test rolls only through the roll cache, tests do not render, and a second roll of a spec fails the gate's census - in full: [`test-bed-detail.md`](test-bed-detail.md).

## Conventions

`_builders.py` per package; `test_surface.py` guards a package surface; **a closure you cannot reach is LIFTED OUT, never dropped**; a found defect becomes a unit test of the placer first; before retiring a check, read the placer and grep the
record of what it has caught; never restore the hand-era corpus (a converted tier gets scripted negative fixtures) - in full, with the worked examples: [`test-bed-detail.md`](test-bed-detail.md).

## `tests/` is invisible to the generation cache, on purpose

`gencache.engine_files()` and `render_cache.engine_fingerprint()` both prune this directory. Before
the 2026-08-16 reorganization every test was a root-level `test_*.py` and the name filter covered
them; under `tests/` the helpers match no name filter, and counting them as engine inputs would
invalidate every map in the pool on any edit to a test helper.

The consequence worth knowing: **a `.py` file placed under `tests/` can never affect a map's cache
key.** That is correct for tests and helpers. If you ever need a module here that a generator
imports, it does not belong here - put it in the engine, or in
[`../l7r/diagram/pipeline/`](../l7r/diagram/pipeline/CLAUDE.md).

**`tests/` did not move under `l7r/diagram/` and should not.** The repository root is the `sys.path` root
(feature 119), so `HERE`-style roots computed here resolve to it. Tests import the engine by its full name -
`from l7r.diagram.settlement import Settlement`, `from l7r.diagram import overlap`.
