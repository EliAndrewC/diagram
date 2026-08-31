# `tests/` - the diagram skill's test bed

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
| `tests/full/` | `make test-full`, `make done FULL=1` and the AWS check | it is a SWEEP or a CARRIER: every pool map, every seed of a cohort, a determinism test that must roll twice for real, a fixture replayed only to carry coverage, a real-map cache round trip. The full run is where the coverage floors are enforced - including the derived 100% floor on every module the scripted hamlet rolls execute (feature 145, `make hamlet-floor`) - and where no cache serves a roll |
| `tests/tooling/` | the gate and the full run; quick ONLY when the tooling changed since the last green gate; skipped at the gate too while it is unchanged (never in FULL) | it RUNS the make/ci/pipeline tooling (make in a fixture, git repos in tmp, coverage subprocesses) |
| `tests/tier_town/`, `tests/tier_city/` | the gate and the full run; quick once the scope lock moves to that tier | it is relevant to that tier only |

## WHICH TARGET RUNS WHICH TREE - the table above read the other way round

The table says where to PUT a test. This one says what each command actually collects, because the
names do not say it and a session got it wrong on 2026-08-31, in the direction that matters: it told
the GM `make test-full` ran less than the whole suite.

| command | `tests/` | `gate/` | `full/` | `tooling/` | `tier_*/` | floors |
|---|---|---|---|---|---|---|
| `make quick` | yes | no | no | only if the tooling changed | no | no |
| `make done` | yes | yes | no | only if its stamp is stale | under the lock, no | no - deferred |
| **`make test-full`** | **yes** | **yes** | **yes** | **yes** | **yes** | **all three** |
| `make done FULL=1` | as `test-full` - it RUNS `test-full` | | | | | all three |

**`make test-full` DESELECTS NOTHING.** Everything is keyed on `COV_FLOORS`, which it sets, and each
deselection is written `$(if $(COV_FLOORS),,<the deselection>)` - present only when it is EMPTY:
`FULL_TREE_IGNORE`, `ROLL_DESELECT` and `TIER_SELECT` all switch off, `L7R_TESTS_FULL=1` and
`EXHAUSTIVE` switch on. The tooling ignore is not even in that family - it lives only in `QUICK_TREE`,
so `make quick` is the ONLY target that ever skips a tooling test.

**So what does `done FULL=1` add over `test-full`? NOT MORE TESTS.** It adds the non-test phases:
`lint`, `format`, `typecheck`, the reference map roll, `hooks-test`, `perf-gate` - and the paid-run
prompt. The pool sweep is NOT one of them; it is `full/test_villages.py::test_village_passes_gate`, a
pytest test, and `test-full` runs it. **`test-full` = the full TESTS; `done FULL=1` = the full GATE.**

The marker on a test (`rolls_map`, `tooling`, `tiers`) is the exact filter within a tree; the tree
is the collection scope. `make quick` announces how many `rolls_map` tests it did not run; the gate
short-circuits when nothing it exercises changed. A test with a quick FORM and a full FORM
(`tests/_scope.py`: `subset`, `full_or`) stays in one tree and reads `EXHAUSTIVE`; a test whose
whole value is the sweep goes to `tests/full/`. The audit that drew these lines, with the cost of every
test the gate ran on 2026-08-27, is `specs/135-done-test-audit/research.md`.

**The layout mirrors the source.** A test for `settlement/houses.py` is in
`tests/settlement/test_houses.py`; a test for `pipeline/gencache.py` is in
`tests/pipeline/test_gencache.py`. That is the whole navigation rule - if you know which module you
changed, you know which directory to open.

| directory | tests | its own index |
|---|---|---|
| `settlement/` | the Mode B drawing engine | [CLAUDE.md](settlement/CLAUDE.md) |
| `hamletgen/` | the scripted hamlet generator | - |
| `sitegen/` | the machinery the tiers SHARE (geometry, types, worker counts) | - |
| `waterfields/` | the water-first field engine | - |
| `pipeline/` | the cache, regen driver, render cache and pool index | - |
| `interactive/` | the interactive HTML map (feature 134): the class registry and the page's string layer; the Playwright browser test is `full/interactive/test_page_browser.py` (the GM's ruling, 2026-08-28: a 15 s browser test is full-tree material) | - |
| `tools/` | the audits and diagnostics that are under the 100% rule | - |
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

    python3 -m pytest -q -n auto                      # everything (from the skill root)
    python3 -m pytest tests/settlement/ -q -n auto    # one mirrored package, WHOLE
    make done                                          # the real gate: lint + format + pyrefly + tests + coverage

**Always `-n auto`.** Serial pytest is about 7x slower here; the 695-manifest regression replay is
~2 minutes under the gate and 13.4 minutes serial. And before the gate, run the WHOLE affected file
or directory, never a `-k` subset: a filter selects the tests you were thinking about, and a change
breaks the ones you were not. Both rules, with the round trips they each cost once, are in the
skill's [`../CLAUDE.md`](../CLAUDE.md).

`testpaths = ["tests"]` in `pyproject.toml` pins collection here. Without it pytest walks the whole
skill directory, and from the repo root it walks every `.clones/` checkout as well - pytest does
not read `.gitignore`.

## Conventions

- **`_builders.py`** in a mirrored package holds that package's shared manifest/settlement
  builders. Import it by package path: `from tests.settlement._builders import bldg, house`.
  These files do not start with `test_`, which is why the engine-tree walks prune `tests/` by name
  (below).
- **`test_surface.py`** in `hamletgen/` and `waterfields/` is the package-surface
  guard: it censuses what the rest of the skill actually reaches through the package and proves the
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
  `fan_rival` (settlement/water_ways.py), `pick_caption_seat` (settlement/structures/fixtures.py),
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
  the placer's test (`make check-census`; the ledger in `specs/141-checks-and-corpus-audit/`); a check
  that measures a LATER fact - a caption after the scatter, the lane web after clipping, the board after
  the yards - stays, because its placer only does its best. A kept check proves it fires on a SCRIPTED
  negative fixture (`gate/test_scripted_fixtures.py`: a cached roll plus one deliberate break, targeted),
  not on a frozen manifest from the hand-placement era; `pool/regressions/` holds what remains of that
  corpus until the GM's ruling on the legacy tiers. Mode A fixtures are frozen bad SVGs in `fixtures/`.
- **THE RECORD OF WHAT HAS FIRED BEATS THE DATAFLOW VERDICT (feature 158, 2026-08-29).** `make
  check-census` answers one question - does any stage after this check's placer change an input it
  reads - and a NO makes the check a retirement CANDIDATE. It is not a ruling, because the census
  cannot see a placer that fails softly: it reads the manifest, not the code. Before retiring a
  candidate, read the placer and grep the record. Worked example, both directions, in one feature:
  `bridges_align_with_their_way` was retired (it re-derived the crossings from the same source the
  placer uses, and its only evidence in the whole repository was two decks a person placed by hand on
  maps no generator can produce), while `bridges_span_their_water` - the same family, the same
  mechanical verdict - was KEPT, because `hamletgen/ways.py` records it catching the SCRIPTED placer
  four separate times on oblique crossings. The candidate list is where the audit starts, not where
  it ends.
- **The hand-era corpus at the LEGACY tiers is gone (feature 158, GM 2026-08-29:** *"there is no
  reason to see what would happen if we encountered a type of map, which is literally impossible to
  produce any longer"***).** Every fixture in `pool/regressions/` declaring `town`, `city`, `capital`
  or `village` scale was deleted (26 of them), along with `tests/tier_city/test_frozen_pool_gate.py`
  and the five frozen-pool coverage carriers in `tests/full/`. The fixtures that declare NO tier stay:
  those are synthetic manifests captured from unit tests - hand-BUILT, not hand-PLACED - and they are
  the cheapest negative fixtures there are. When a tier converts to scripted generation it gets
  scripted negative fixtures, not a restored corpus.

## `tests/` is invisible to the generation cache, on purpose

`gencache.engine_files()` and `render_cache.engine_fingerprint()` both prune this directory. Before
the 2026-08-16 reorganization every test was a root-level `test_*.py` and the name filter covered
them; under `tests/` the helpers match no name filter, and counting them as engine inputs would
invalidate every map in the pool on any edit to a test helper.

The consequence worth knowing: **a `.py` file placed under `tests/` can never affect a map's cache
key.** That is correct for tests and helpers. If you ever need a module here that a generator
imports, it does not belong here - put it in the engine, or in
[`../l7r/diagram/pipeline/`](../l7r/diagram/pipeline/CLAUDE.md).

**`tests/` did not move under `l7r/diagram/` and should not.** The skill directory stays the
`sys.path` root (feature 119), so `HERE`-style roots computed here are unchanged, while the engine's
own roots moved two levels deeper. Tests import the engine by its full name -
`from l7r.diagram.settlement import Settlement`, `from l7r.diagram import overlap`.
