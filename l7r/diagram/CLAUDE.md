# The diagram engine - dev loop

Working on the engine (the `l7r/diagram/` packages and the pool generators), as opposed to drawing a map with it (that
is [`docs/usage.md`](../../docs/usage.md)). This file auto-loads under `l7r/diagram/`, and `pool/CLAUDE.md` and
`tests/CLAUDE.md` import it. The project-wide doctrine - iterate once and gate once, the regression baseline in a
detached worktree, fix what you find (XIV), build what was asked (XVI), reviews on their occasion, the research ladder
and knobs, the `Research:` claims gate - is the root [`CLAUDE.md`](../../CLAUDE.md); this file holds only what is
specific to the engine. Every command is a `make` target at the repository root, described in
[`docs/make-targets.html`](../../docs/make-targets.html) (generated from the Makefile's `##` lines).

## Where things live

The engine is grouped by what a module is FOR, and each package carries its own `CLAUDE.md` index: open the one your
task is in.

`l7r/` is a PEP 420 *namespace portion* shared with the L7R Toolkit webapp (`l7r.app`, `l7r.names` in
`/host-l7r-repo/gm-assistant/webapp/l7r/`), so one interpreter imports both. **Never create `l7r/__init__.py`**: it
makes `l7r` a regular package and the webapp's portion silently stops existing (`tests/test_namespace_portion.py`).
**The repository root is the `sys.path` root**: `pool/`, `tests/`, the `Makefile` and `pyproject.toml` sit there, a
pool generator's bootstrap climbs to it, and an engine module that computes the root from its own location
(`gencache`, `pool_index`, `render_cache`) counts its depth - a wrong depth
is silent and lands one directory short of `pool/`.

**The hamlet engine is Rust** (feature 444 amendment 11): the Python hamlet engine - `hamletgen/`, `settlement/`, `waterfields/`,
`sitegen/`, `overlap/` - was deleted on 2026-11-07 and lives in git history; the stages are `rust/phases/` (the ones after the
last efficient stage parked in `rust/parked/`), and the stage-by-stage reference is `dev/placement-stages-frozen/`.

| path | what is in it | load its index when |
|---|---|---|
| [`pipeline/`](pipeline/CLAUDE.md) | how a map is regenerated, cached, rendered and indexed | the cache behaves oddly, or you change how generation is DRIVEN |
| [`interactive/`](interactive/CLAUDE.md) | the interactive HTML page: the feature-class vocabulary, the modals, the page writer, the record's build | you add a KIND of feature, change what a modal says, or the map-vocabulary gate test fired |
| `rust/mode_a/src/caption_place.rs`, `rust/mode_a/src/labels/` | THE ONE CAPTION PLACER (feature 266) and the hand sheet's reader, in Rust (rebuilt from its derivation by feature 449 T202; the Python `labels/` package deleted by T152) | you add a captioned feature (name its SUBJECT and declare its caption; never pick a seat), or a caption sits wrong |
| [`buildings/`](buildings/__init__.py) | the Mode A building TYPES, declared once in `types.json` (feature 254) | you add or change a building type or its program |
| `rust/mode_a/src/compound/` and each generated sheet's `<map>.compound.json` | the Mode A compound generator (feature 449 T152: rebuilt in Rust from `specs/449-rust-codebase/derivations/T208-compound.md`; the Python `compound*.py` and `well_gear.py` deleted): the program read from its spec, the perimeter-first seating, the parts, the open ground, the sheet written; `l7r-mode-a compound <spec>` | you change a compound plan's draft or its program |
| `rust/mode_a/src/dwellings.rs` (the Python `dwellings.py` deleted with the page writer it served, feature 449 T150) | what counts as a DWELLING, in one leaf module with no imports of its own | a count of houses or households disagrees between two readers |
| `switches.py` | the iteration switch (feature 132) in `dev/switches.json`: remote on or off ([`docs/switches.md`](../../docs/switches.md)) | a remote run refused, or you throw the switch |
| `_invocation.py`, `_census.py` | refuse an operation not invoked through this project's make; the roll census's writer (`_memory.py`, the heap trim after a test or a roll, left with pytest, feature 449 T213) | a refusal or the census fired |
| [`tools/`](tools/CLAUDE.md) | read-only diagnostics and audits | a map came out wrong and you need to ask WHY, or a number needs measuring |
| [`tests/`](../../tests/CLAUDE.md) | the guard suites and the fixtures the Rust tests read; no Python test is left (feature 449 T211, T213) | you need to find a fixture or a guard's suite |

`pool/` holds the shipped maps (`<name>.gen.py`, its manifest, render and `.notes.md`); `legacy-hand-authored-pool/` the frozen hand-authored exhibits.

## The dev docs (load the one your task is in)

| doc | load it when |
|---|---|
| [`dev/loop.md`](../../dev/loop.md) | you are about to run the gate or a pool sweep, or deciding how much to re-run after a change |
| [`dev/placement.md`](../../dev/placement.md) | you add a map feature or change where anything is placed or drawn: the DRAW ORDER map (with the scripted `STAGES` table), CENTER vs FOOTPRINT, the KEEP-CLEAR CONTRACT |
| [`dev/gate.md`](../../dev/gate.md) | you add or change a check, write a check test, or waive a rule for one map |
| [`dev/diagnostics.md`](../../dev/diagnostics.md) | a map came out wrong and you need to know WHY, and how a probe lies to you (its `open_seat` and `why_placed` went with the Python engine, feature 444 T39) |
| [`dev/performance.md`](../../dev/performance.md) | a gen or a check got slow (or "hangs"), or you are about to undo a time-for-memory trade |
| [`dev/cache.md`](../../dev/cache.md) | the cache behaves oddly, you changed how generation is DRIVEN, or a coverage floor breached for no reason you can see |
| [`dev/pool.md`](../../dev/pool.md) | you are about to touch a pool map or convert one to scripted generation |
| [`dev/lessons.md`](../../dev/lessons.md) | a fix is not working and you are about to try another - the dead ends already walked |
| [`dev/decisions.md`](../../dev/decisions.md) | you are about to build on a property of the engine nobody decided, or leave a decision open |
| [`docs/reviews.md`](../../docs/reviews.md) | you are about to launch a review check or write a feature's `## Occasions` |
| [`docs/package-boundary.md`](../../docs/package-boundary.md) | you wonder whether Mode A and Mode B should be separate packages, or a Mode A `.gen.py` is about to appear |
| [`docs/migration-plan.md`](../../docs/migration-plan.md) | you draw or script a settlement map (read it first; update its status table when a conversion lands) |
| [`dev/timings.md`](../../dev/timings.md) | you want a measured timing (never write fresh timings into prose; `make audit` and `l7r-gate measure gatecost` give the live ones) |
| [`dev/test-cost.md`](../../dev/test-cost.md) | you are adding a test that rolls a map, or asking why the suite costs what it does |
| [`dev/interactive-page.md`](../../dev/interactive-page.md) | page or raster performance, or the wet-paddy modal's two tint rules |

Deferred engineering is filed as spec-kit features; `make speckit-todo` lists the open ones. The append-only run
records are `dev/run-log/`, `dev/perf-log/` and `dev/bypass-log/`, each with its own `CLAUDE.md`.

## The always-on rules

**The goal they serve** (GM 2026-08-25, constitution v2.3.0): *"if me asking for a simple change results in half an
hour of work being done when it should have only taken five minutes, then that limits the number of changes that I can
make in a single day."* The cheaper command that answers the question wins, and a simple task that ran long is
diagnosed and the tooling improved.

**The loop** ([`dev/loop.md`](../../dev/loop.md))

- **Nothing runs outside make**: an engine entry point, a bare cargo or a foreign makefile is refused
  (`rust/guard/src/guards/make_only_hooks.rs`), and the engine refuses in-process calls too (`_invocation.py`). A refusal on correct
  work is a BUG in the guard to fix (it was always a MENTION mistaken for an INVOCATION).
- `make map GEN=pool/<tier>/<map>/<map>.gen.py` regenerates one map and prints `CACHED` / `REGENERATED` / `FROZEN`;
  `PROFILE=1` adds where its time went. Iterate on that ONE map, `make quick` while iterating, `make rust-test CRATE=<dir>`
  for one crate's tests. The Python tests, their planner and the coverage floor over Python were deleted (feature 449 FR-001b, the GM 2026-11-10), and pytest with them (T213); `make done` runs once, backgrounded, never polled.
- **The cohort, by stage** (feature 386, the GM 2026-10-17): `make cohort` (the Rust driver, N seeds from SEED, each refusal or
  broken rule named) after each fix. The LANDING cohort (`make cohort-landing`, seeds 1-48 and the pinned rows, its record read by
  `scripts/gates/cohort-gate.sh` on a GATED push) is owed only at the port switch's `integrated` (feature 444 FR-023); at rust-only,
  the switch's state now, no landing owes it, and the target refuses - nothing writes its record since the Python driver was deleted
  (feature 449 T223).
- Never run a test BESIDE a running gate - two writers on the same pool maps is a source of false RED. The one exception is
  `make land`'s landing cohort (feature 405 T48): it writes no pool map, its rolls are no gate's, and its new record is unseen by
  the gate's tree check.
- Update the predictably-affected unit tests in the SAME edit as the engine change. **Cycle discipline**
  (constitution v2.4.0): re-read the WHOLE diff for convention misses before the first test run, fix everything a
  failing run lists before re-running, and never write a number into a record that was not measured on the artifact.
- **A check before the fix** (GM 2026-08-10, opening eleven defects on the Shiro Daika capital: *"which all need to be
  fixed after we add new automated checks to catch these issues in the future"*): for each defect the GM names, write
  the check and watch it go RED on the current artifact, then fix, keeping the diagnosis in the failure message. Prove
  the check RUNS at every tier it should: an exact `scale == "city"` test once skipped 74 rules at the capital tier.
- **Derive, don't pin**: a feature defined by other geometry is computed from that geometry at draw time (a bank's
  bearing from the river at the wharf, a well grid from the streets that cross the quarter), and its check measures the
  CURRENT geometry, both bounds. A pinned coordinate fails silently once the river moves (GM 2026-08-10: *"the angle of
  the river changed slightly, but the angle of the granaries did not"*).
- **Did the wave move a map?** `make map` ends by saying whether its manifest differs from HEAD, and `make maps-moved`
  lists every pool manifest that does (feature 429): record that, never a scratch copy, which a test or `make map` may
  already have regenerated (feature 328 wave 68 recorded Sawada unchanged after its board moved 76 degrees).
- **No engine edit while a map review runs** (the `engine_freeze_hooks` guard, feature 429): a review's verdict is keyed to the
  engine it read, so draft a fix outside the clone until every review has returned.
- **Deleting a repair step** is measured on a fresh block rolled BEFORE the change, seed by seed
  (`make cohort N=48 SEED=<that block's first seed> FRESH=0 JOBS=3`), bisecting any new failure: the landing cohort's
  fixed seeds passed feature 417 T41's deletion while a fresh seed regressed.
- **A CPU-time bound in a test** inflates 2-4x under load on this hybrid CPU: scale it by a calibration loop (as
  `tests/test_open_questions.py` does), never a hard-coded figure.
- **Time is the goal of performance work, calls the measure** (feature 435, the GM 2026-10-27: "timings are not a gate, but improving timings is the goal of any performance improvement ticket"): plan a speed change
  with `docs/performance-checklist.md` (`make task-add ... PERF=1`) - where the time goes, whether it removes work or only
  moves it (inlining, merging, writing a builtin out lowers the count, not the time), its growth with size - and read
  a before-and-after timing as evidence, never as a gate.
- **Counted work is the measure, timings only recorded** (feature 427 T03, the GM 2026-10-26: "keep recording the timings, but
  completely stop using timings as a gate on anything ... the call counts themselves are the thing that we are gating on"): the
  Rust stages' counted operations, `make work-budget` (a hamlet stage) and `make budget-sheets` (a Mode A stage), against their
  budgets (feature 443). The Python call-count bookends (`make perf`, `perf-report`, `perf-review`, `perf-profile`, the
  perf-explain family) counted the Python engine and went with it (feature 444 T39); their names left the Makefile with
  feature 449 T223.

**Placement** ([`dev/placement.md`](../../dev/placement.md))

- **Read the DRAW ORDER map before moving anything.** A drawing method sees only what is in `self.M` when it runs; a
  placer avoids only what is in the registries when it runs. Most "wrong geometry" is wrong ORDER.
- A new footprint feature goes in `_OVERLAP_STRUCTS` (or `_OVERLAP_EXEMPT`, with the reason) and gets a caption group
  in `_LABEL_GROUP`. **Record a footprint the extractor can read** - `x`+`w`/`vw`, a `poly`/`outline` ring, a stroked
  polyline, or `parts` of rotated quads; anything else is invisible to every matrix check.
- **Gap verdicts read footprints, never centers** (`edge_gap` / `within_edge_gap` / `sat_overlap`); say at the test
  which family a rule is in, and add a `test_gap_verdicts_read_footprints_not_centers` entry with every new gap rule.
  Never let an aggregate (a centroid) stand in for the distributed thing a verdict is about.
- Randomness is POSITIONAL or SCOPED: `self._hjit(x, y, salt)` per feature, `with self.rng_scope(name, *key)` per phase
  (practice, not a gate-held rule - GM 2026-09-08: *"I am actually okay with an upstream change in the number of random
  draws moving a map"*).

**The gate** ([`dev/gate.md`](../../dev/gate.md)) - **a rule about a map is a test of the placer that makes it**
(feature 166): a seat a placer decides is its unit test; a property of a FINISHED map is a seed test in `tests/gate/` on
a cached roll, which states what it FOUND before it judges it; placement and its test import the same predicate.

**Diagnostics** ([`dev/diagnostics.md`](../../dev/diagnostics.md)) - ask the ENGINE where a feature fits
(the Python engine's `s.open_seat(...)`) and the GEN who placed it (its `why_placed`, deleted with it); read derived geometry from the MANIFEST, not by
re-running a generator; a diagnostic that restates what it observes will lie to you.

**Performance** ([`dev/performance.md`](../../dev/performance.md))

- Every slow gen profiled here was *a per-candidate scan of geometry that does not change during the scan*: build the
  blocked ground ONCE (`PointGrid` / `RingIndex` / `KeepoutGrid`) and ask it per candidate (constitution X clause 15).
- **Maps may ALWAYS change for speed** (GM 2026-09-30: *"They do NOT need to remain identical in output"*; 2026-10-18:
  *"anytime we are trying to make things faster, it's always okay for maps to change, so long as the changes don't violate
  our research findings"*), held to the rules and the research claims, rather than to byte-identity. A slow CHECK is INDEXED, never coarsened. Trust the A/B against HEAD, not cProfile's seconds.
- **So may any port or change** (GM 2026-11-18, constitution XIII: *"remove any references to things needing to be bitwise
  identical or anything like that as an exactness standard"*): an output may differ so long as everything works - tests pass,
  callers get their job done, research claims hold - a drawn output must pass its checks, a ported check must still do its job (red fixtures fail, good sheets pass). The same code and
  seed still give the same map (reproducibility is not this standard).
- **Some slowness is bought memory** (GM 2026-10-05): read `dev/performance.md` "Time traded for memory" before
  undoing one; the RAM each undo costs goes to the GM.

**The pool** ([`dev/pool.md`](../../dev/pool.md)) - **the legacy pool is FROZEN**: its 19 hand-authored maps are
exhibits, never regenerated or re-gated; the fix for one is CONVERSION, not retrofit. A cohort of seeds is a stronger
test bed than one map, and a seed that passed before your change and fails after it is a REGRESSION.

**A fix that FAILED is recorded at the point of change** (as the hamlet generator's modules record their dead ends), so
a later session does not re-try it. **Before you build on a property of the engine, check whether anyone DECIDED it**
([`dev/decisions.md`](../../dev/decisions.md)); an open decision carries its 2-3 line implementation sketch.
