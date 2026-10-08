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
| `tests/tooling/` | the gate and the full run - never quick (GM 2026-09-27; a `tooling`-marked test outside this tree, as in `tests/tools/`, is kept out of quick by its marker); skipped at the gate while the tooling is unchanged (never in FULL); `make test-file FILE=tests/tooling` on demand | it RUNS the make/ci/pipeline tooling (make in a fixture, git repos in tmp, coverage subprocesses) |
| `tests/tier_town/`, `tests/tier_city/` | the gate and the full run | it is relevant to that tier only |
| `tests/soak/` | **no ordinary run** (`norecursedirs`); `make soak` names it (GM 2026-09-08) | it rolls MORE than the gate's floor strictly needs - a behavior asserted on a real map that no coverage line requires (constitution VI, feature 216); [`soak/CLAUDE.md`](soak/CLAUDE.md) |

## WHICH TARGET RUNS WHICH TREE - the table above read the other way round

The table says where to PUT a test. This one says what each command actually collects, because the
names do not say it (a session once told the GM `make test-full` ran less than the whole suite).

| command | `tests/` | `gate/` | `full/` | `tooling/` | `tier_*/` | floors |
|---|---|---|---|---|---|---|
| `make quick` | yes | no | no | no | no | no |
| `make done` | yes | yes | **yes** | only if its stamp is stale | under the lock, no | **all three** |
| **`make test-full`** | **yes** | **yes** | **yes** | **yes** | **yes** | **all three** |
| `make done FULL=1` | as `test-full` - it RUNS `test-full` | | | | | all three |

**A plain `make done` is INCREMENTAL (feature 207)** - the rows above say what a target COLLECTS; the incremental gate then deselects, within the collected suite, every test the change cannot reach (its own coverage contexts and its fixtures' never executed a changed file), and the floors are judged over the merge with the last full run. `make done INCREMENTAL=0` and `make test-full` run everything.

**`make test-full` DESELECTS NOTHING.** Everything is keyed on `COV_FLOORS`, which it sets, and each
deselection is written `$(if $(COV_FLOORS),,<the deselection>)` - present only when it is EMPTY:
`FULL_TREE_IGNORE` switches off, `L7R_TESTS_FULL=1` and `EXHAUSTIVE` switch on. The tooling ignore is not even in
that family - it lives only in `QUICK_TREE`, so `make quick` is the ONLY target that ever skips a tooling test.

**So what does `done FULL=1` add over `test-full`? NOT MORE TESTS.** It adds the non-test phases:
`lint`, `format`, `typecheck`, the reference map roll, `hooks-test`, `perf-gate` - and the paid-run
prompt. The pool sweep is NOT one of them; it is `full/test_villages.py::test_village_passes_gate`, a
pytest test, and `test-full` runs it. **`test-full` = the full TESTS; `done FULL=1` = the full GATE.**

The marker on a test (`rolls_map`, `tooling`, `tiers`) is the exact filter within a tree; the tree
is the collection scope. `make quick` announces how many `rolls_map` tests it did not run; the gate
short-circuits when nothing it exercises changed. A test with a quick FORM and a full FORM
(`tests/_scope.py`: `subset`, `full_or`) stays in one tree and reads `EXHAUSTIVE`; a test whose
whole value is the sweep goes to `tests/full/`. The audit that drew these lines: `specs/135-done-test-audit/research.md`.

**The layout mirrors the source.** A test for `settlement/houses.py` is in
`tests/settlement/test_houses.py`; a test for `pipeline/gencache.py` is in
`tests/pipeline/test_gencache.py`. That is the whole navigation rule - if you know which module you
changed, you know which directory to open. The trees above (`gate/`, `full/`, `tier_*/`) mirror the same packages inside.

| directory | tests | its own index |
|---|---|---|
| `settlement/` | the Mode B drawing engine | [CLAUDE.md](settlement/CLAUDE.md) |
| `hamletgen/` | the scripted hamlet generator | `hamletgen/ways/` has [CLAUDE.md](hamletgen/ways/CLAUDE.md) |
| `sitegen/` | the machinery the tiers SHARE (geometry, types, worker counts) | - |
| `waterfields/` | the water-first field engine | - |
| `pipeline/` | the cache, regen driver, render cache and pool index | - |
| `labels/` | caption paths and the hand-sheet labels | - |
| `interactive/` | the interactive HTML map: the class registry and the page's string layer; the research RECORD's form (`test_footnotes.py`, `test_sources.py`, `test_record*.py`, `test_citations.py`, ...), each reading the record through `tests/_record_pages.py` and `sources.record_text` because nothing built is committed; `tests/_flat_record.py` is the small record the tests build and break. The Playwright browser test is `full/interactive/page_browser/` ([CLAUDE.md](full/interactive/page_browser/CLAUDE.md)), skipped by the gate while nothing it reads changed (`gate-stamp.py`'s `browser` key; earned by `make page-check` or a `make done` that ran it) | - |
| `tools/` | the audits and diagnostics that are under the 100% rule | - |
| `tooling/` | the make/ci/pipeline tooling, run for real (the tree above) | - |
| `gate/`, `full/`, `tier_town/`, `tier_city/` | the trees above | - |
| `soak/` | the soak tier | [CLAUDE.md](soak/CLAUDE.md) |
| `fixtures/` | DATA, not tests: frozen red SVGs (Mode A negative fixtures), `gate_check_names.json`, `registry_legacy_rows.json` | - |

At the root of `tests/` sit the suites that are not about one module:

- **`test_villages.py`** - the pool's cheap ratchets (every gen classified, the CPU-budget guard) and the
  helpers; the sweep itself - every LIVE map through `gencache.gate_obtain`, proving each shipped
  generator RUNS inside its `GEN_TIME_BUDGETS` entry and emits a manifest - is `full/test_villages.py`.
- **`gate/test_*.py`** - the rules that used to be the check battery, each now asserted once per code
  change on a cached roll rather than once per map generated (feature 166; the per-rule ledger is
  `specs/166-retire-the-check-battery/migration-record.md`).
- **`test_compound.py` / `test_citybudget.py`** - the two engine modules that are still single
  top-level files.

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

The GM, on finding the gate rolling 37 hamlets where the packing record had measured 11: *"we definitely had
this solved at one point, and then the problem just came back on its own ... program our unit tests to never
allow the same hamlet to be rolled twice within the tests and also to have some required process around
adding another hamlet that gets rolled."* So:

- **`tests/rolls.py` is the roster.** Every spec the gate may roll, with the unique coverage or emergent
  condition it carries - ZERO rows since feature 219: the gate rolls no map of its own (the GM retired the immune
  requirement on 2026-09-08 and Polder 12's lines became unit tests; `rolls.COVERAGE` is the two shipped maps the gate reads): the
  gate rolls only what 100% coverage strictly needs, and since feature 217 the census verdict MEASURES it - a rostered
  roll whose coverage context reaches no engine line no other context reaches FAILS the gate, every roll's count and
  lines are printed on every gate, `make roll-audit` asks the same off the last baseline, the roster is a GUARD file
  (an edit needs `GUARD_EDIT_OK` with a reason; a change to it makes the next gate FULL) and every `Roll`/`Duplicate`
  row points at the research section recording its audit (`audit=`, checked by `tests/test_rolls.py`); a test that
  rolls more belongs in `tests/soak/` (constitution VI v2.23.0). The reference and Kuwabata are the POOL's maps: every gate reader takes them
  through `tests/gate/_pool.py` (`rolled_map`, `rolled_report` - the sweep's entry, served warm, rolled cold once
  under a per-gen lock); nothing rolls the reference under a spec. A rolling test's spec must be there; the roll census fails the gate otherwise and
  says to add the row WITH ITS REASON - and if the reason is a row that already exists, reuse that row's
  roll instead. Three stated exceptions live beside it: a `Duplicate` (a site that must roll a rostered spec
  again by its nature; none today),
  a `PoolGen` (a shipped generator the pool sweep runs only when its cache key moved) and an `InProcess`
  module (the perf tests, which time the stages where they run, each on its own seed; the stub-stage
  tests, `stub=True`, whose stand-in rolls are reported and bounded rather than counted).
- **The census is written at the chokepoint, not by patching.** `driver.roll_scope()` - which every
  stage-running loop enters, proven by the AST test in `tests/hamletgen/test_driver.py` - appends a record
  to the file `L7R_ROLL_CENSUS` names, in every process of the run; the `-p l7r.diagram.ci.rollcensus`
  plugin attributes each record to the test that caused it; the gate's `l7r.diagram.ci rollcensus verdict` step
  judges the run after the hamlet-floor phase (`ci/rollverdict.py`), which runs under the same census: a
  second roll of a spec, an unrostered roll, a stale row on a full run, a render from an unmarked test, an
  in-process roll from an unexcepted module, a roll the floor made itself. And because the incremental gate
  (feature 207) selects tests from coverage CONTEXTS, every coverage child is labeled with its requester's
  context (`_census.CONTEXT_ENV`, exported by `ci/selection.switch`) - a roll in a child would otherwise be
  invisible to the selection, which is exactly what the polder-only run of 2026-09-08 showed. And a fixture's
  context is keyed by WHERE it is defined (`tests/gate/test_water.py::rolled`, `ci/selection.fixture_id`): ten
  gate modules each define a `rolled` fixture, and one shared name made that same edit re-roll 18 specs.
- **Rolling tests get their roll from the roll cache, in a child.** `rollcache.hamlet(spec)` /
  `report(spec)` are two views of ONE roll per spec (`generate`, kept manifest and all), shared across the
  workers behind a lock so the first wave waits instead of each rolling, and stored so the hamlet floor
  reads the same roll. A test that must patch the engine lifts its produce closure to a module-level
  function and passes `child="module:function"` to `rollcache.keyed_to` (the feature-146 doctrine, now
  with a reason beyond testability: the roll must leave the worker).
- **Tests do not render.** `DIAGRAM_SKIP_RENDER=1` is the suite's default (`conftest.py`); a test OF
  rendering carries the `renders` marker and clears it itself. The census records every PNG and page-raster
  render and the verdict fails on one from an unmarked test.

## Conventions

- **`_builders.py`** in a mirrored package holds that package's shared manifest/settlement
  builders. Import it by package path: `from tests.settlement._builders import bldg, house`.
  These files do not start with `test_`, which is why the engine-tree walks prune `tests/` by name
  (below).
- **`test_surface.py`** in `hamletgen/` and `waterfields/` is the package-surface
  guard: it censuses what the rest of the project actually reaches through the package and proves the
  `__init__.py` re-export still resolves it. Feature 027 replaced hand-maintained rosters with star
  imports plus these guards, so the surface is derived and the guard is what makes that safe.
- **A CLOSURE YOU CANNOT REACH IS LIFTED OUT, NEVER DROPPED** (feature 146, GM 2026-08-28: *"if something
  is only available as an inner function in a closure, then you can move it out into its own function to make
  it more unit testable ... you can generally have your unit tests be much simpler if you're just calling
  functions that take simple inputs and outputs without needing to create a lot of very complicated setup"*).
  This repository's own commits carried the failure it replaces - *"dropped (nested closure)"* - so the rule is
  written down: move the inner function to module level with its captured values as parameters, have the inner
  one delegate so there is ONE body, and test the lifted function with plain dicts and tuples. Worked examples:
  `web_pieces` / `web_rejoinable` / `commit_lane` / `bowtie_cut` / `push_clear_of_fabric` (hamletgen/ways.py),
  `fan_rival` (settlement/water_ways.py),
  `hem_on_water` (settlement/fields/comb.py), `s_on_side`
  (waterfields/polder.py), `bamboo_blocked` (hamletgen/hinterland.py). **Lifting only helps when the closure
  is CALLED and one branch inside it is not** - a closure a live roll never calls at all leaves the delegate
  uncovered too, and that one wants a direct test of the function that owns it (`_pull_back_to_service`,
  `_touch_junctions`, `caption_lane_clearance`), or the code deleted if nothing can reach it.
- **A found defect becomes a UNIT TEST OF THE PLACER first, and a check only where a later stage can
  undo the placer** (feature 141, GM 2026-08-28: *"If the thing which fixes the wrongness of the map is
  an update to our placement algorithm, then I don't think that saving off that past map actually has
  value ... we can have one hundred percent unit test coverage and have a unit test which asserts that
  things are now correct without saving off the old map."*). The test per check is SAME MEASURE vs SAME
  FACT: a check that re-measures what a correct placer guaranteed is retired, its guarantee carried by
  the placer's test (the ledger in `specs/141-checks-and-corpus-audit/`); a check that measures a LATER
  fact - a caption after the scatter, the lane web after clipping, the board after the yards - stays,
  because its placer only does its best. A kept check proves it fires on a SCRIPTED negative fixture (a
  cached roll plus one deliberate break, targeted), not on a frozen manifest from the hand-placement era.
  Mode A fixtures are frozen bad SVGs in `fixtures/`.
- **Before retiring a check, read the placer and grep the record of what it has caught** (feature 158): a
  dataflow verdict that no later stage changes the check's inputs makes it a CANDIDATE only, because it
  cannot see a placer that fails softly. `bridges_span_their_water` was kept on that ground - `hamletgen/ways.py`
  records it catching the scripted placer four times on oblique crossings.
- **Don't restore the hand-era corpus** (feature 158, GM 2026-08-29: *"there is no reason to see what would
  happen if we encountered a type of map, which is literally impossible to produce any longer"*). When a tier
  converts to scripted generation it gets scripted negative fixtures, not a restored corpus.

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
