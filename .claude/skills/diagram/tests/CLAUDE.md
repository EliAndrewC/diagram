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
| `tests/full/` | `make done FULL=1` and the AWS check only | it is a SWEEP or a CARRIER: every pool map, every seed of a cohort, a determinism test that must roll twice for real, a fixture replayed only to carry coverage, a real-map cache round trip. The full run is where the coverage floors are enforced and where no cache serves a roll |
| `tests/tooling/` | the gate and the full run; quick ONLY when the tooling changed since the last green gate; skipped at the gate too while it is unchanged (never in FULL) | it RUNS the make/ci/pipeline tooling (make in a fixture, git repos in tmp, coverage subprocesses) |
| `tests/tier_town/`, `tests/tier_city/` | the gate and the full run; quick once the scope lock moves to that tier | it is relevant to that tier only |

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
| `check_village/` | the gate (the ~1,371-segment check battery) | [CLAUDE.md](check_village/CLAUDE.md) |
| `hamletgen/` | the scripted hamlet generator | - |
| `sitegen/` | the machinery the tiers SHARE (geometry, types, worker counts) | - |
| `waterfields/` | the water-first field engine | - |
| `pipeline/` | the cache, regen driver, render cache and pool index | - |
| `interactive/` | the interactive HTML map (feature 134): the class registry and the page's string layer; the Playwright browser test is `full/interactive/test_page_browser.py` (the GM's ruling, 2026-08-28: a 15 s browser test is full-tree material) | - |
| `tools/` | the audits and diagnostics that are under the 100% rule | - |
| `fixtures/` | DATA, not tests: frozen red SVGs (Mode A negative fixtures), `gate_check_names.json`, `registry_legacy_rows.json` | - |

At the root of `tests/` sit the suites that are not about one module:

- **`test_villages.py`** - the pool's cheap ratchets (every gen classified, the CPU-budget guard) and the
  helpers; the sweep itself - every LIVE map through `gencache.gate_obtain` and the full check battery,
  plus the `GEN_TIME_BUDGETS` - is `full/test_villages.py`.
- **`gate/test_regressions.py`** - replays the frozen negative-fixture corpus in `pool/regressions/`,
  demanding each manifest still fires the checks it was frozen to fire; its coverage carriers are
  `full/test_coverage_carriers.py`.
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
  builders. Import it by package path: `from tests.check_village._builders import bldg, house`.
  These files do not start with `test_`, which is why the engine-tree walks prune `tests/` by name
  (below).
- **`test_surface.py`** in `check_village/`, `hamletgen/` and `waterfields/` is the package-surface
  guard: it censuses what the rest of the skill actually reaches through the package and proves the
  `__init__.py` re-export still resolves it. Feature 027 replaced hand-maintained rosters with star
  imports plus these guards, so the surface is derived and the guard is what makes that safe.
- **Every found defect becomes a check, and the check gets a negative fixture.** Mode B fixtures
  are frozen manifests in `pool/regressions/`; Mode A fixtures are frozen bad SVGs in
  `fixtures/`. Coverage alone does not prove a check has teeth - a red fixture does.

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
`from l7r.diagram.settlement import Settlement`, `from l7r.diagram import check_village`.
