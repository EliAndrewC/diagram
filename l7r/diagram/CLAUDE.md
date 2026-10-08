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
(`gencache`, `pool_index`, `render_cache`, `cohort_audit`, `cache_audit`, `hamletgen`) counts its depth - a wrong depth
is silent and lands one directory short of `pool/`.

| path | what is in it | load its index when |
|---|---|---|
| [`settlement/`](settlement/CLAUDE.md) | the Mode B drawing engine (the `Settlement` class and its mixins) | you change what a settlement map DRAWS or where it places something |
| [`overlap/`](overlap/__init__.py) | the overlap TAXONOMY and matrix: which features may lie on which, and why | you add a footprint feature, or a pair overlapped that should not have |
| [`waterfields/`](waterfields/CLAUDE.md) | the water-first field engine (comb fields, terraces, polders) | you change paddies, bunds, canals or the field frame |
| [`hamletgen/`](hamletgen/CLAUDE.md) | the scripted hamlet generator - a whole hamlet from a short spec | you work on scripted generation |
| [`sitegen/`](sitegen/CLAUDE.md) | tier-agnostic generation machinery the tiers SHARE | you add a tier generator, or move a stage out of one |
| [`pipeline/`](pipeline/CLAUDE.md) | how a map is regenerated, cached, rendered and indexed | the cache behaves oddly, or you change how generation is DRIVEN |
| [`interactive/`](interactive/CLAUDE.md) | the interactive HTML page: the feature-class vocabulary, the modals, the page writer, the record's build | you add a KIND of feature, change what a modal says, or the map-vocabulary gate test fired |
| [`labels/`](labels/__init__.py) | THE ONE CAPTION PLACER (feature 266), used by the settlement engine, `compound.py` and the hand-drawn sheets (`labels/hand_sheet.py`) | you add a captioned feature (name its SUBJECT and call the placer; never pick a seat), or a caption sits wrong |
| [`buildings/`](buildings/__init__.py) | the Mode A building TYPES, declared once in `types.json` (feature 254) | you add or change a building type or its program |
| `compound.py`, `compound_model.py`, `compound_parts.py` | the Mode A compound program and perimeter-first placer; its vocabulary (units, palettes, program types); what it seats around the masses | you change a compound plan's draft |
| `citybudget.py` | budget-first city wall sizing (feature 009) | you size a city |
| `dwellings.py` | what counts as a DWELLING, in one leaf module with no imports of its own | a count of houses or households disagrees between two readers |
| `switches.py` | the iteration switch (feature 132) in `dev/switches.json`: remote on or off ([`docs/switches.md`](../../docs/switches.md)) | a remote run refused, or you throw the switch |
| `_invocation.py`, `_census.py`, `_memory.py` | refuse an operation not invoked through this project's make; the roll census's writer; give freed C memory back after a roll | a refusal or the census fired |
| [`tools/`](tools/CLAUDE.md) | read-only diagnostics and audits | a map came out wrong and you need to ask WHY, or a number needs measuring |
| [`ci/`](ci/CLAUDE.md) | the CodeBuild dispatcher and the incremental gate | a remote run refused, money may be spent, or the gate selected oddly |
| [`tests/`](../../tests/CLAUDE.md) | every test, mirroring the source layout, plus the frozen fixtures | you need to find or add a test |

`pool/` holds the shipped maps (`<name>.gen.py`, its manifest, render and `.notes.md`); `wip/` maps staged outside it.

## The dev docs (load the one your task is in)

| doc | load it when |
|---|---|
| [`dev/loop.md`](../../dev/loop.md) | you are about to run the gate or a pool sweep, or deciding how much to re-run after a change |
| [`dev/placement.md`](../../dev/placement.md) | you add a map feature or change where anything is placed or drawn: the DRAW ORDER map (with the scripted `STAGES` table), CENTER vs FOOTPRINT, the KEEP-CLEAR CONTRACT |
| [`dev/gate.md`](../../dev/gate.md) | you add or change a check, write a check test, or waive a rule for one map |
| [`dev/diagnostics.md`](../../dev/diagnostics.md) | a map came out wrong and you need to know WHY: `open_seat`, `make why-placed`, and how a probe lies to you |
| [`dev/performance.md`](../../dev/performance.md) | a gen or a check got slow (or "hangs"), or you are about to undo a time-for-memory trade |
| [`dev/cache.md`](../../dev/cache.md) | the cache behaves oddly, you changed how generation is DRIVEN, or a coverage floor breached for no reason you can see |
| [`dev/pool.md`](../../dev/pool.md) | you are about to touch a pool map or convert one to scripted generation |
| [`dev/lessons.md`](../../dev/lessons.md) | a fix is not working and you are about to try another - the dead ends already walked |
| [`dev/decisions.md`](../../dev/decisions.md) | you are about to build on a property of the engine nobody decided, or leave a decision open |
| [`docs/reviews.md`](../../docs/reviews.md) | you are about to launch a review check or write a feature's `## Occasions` |
| [`docs/package-boundary.md`](../../docs/package-boundary.md) | you wonder whether Mode A and Mode B should be separate packages, or a Mode A `.gen.py` is about to appear |
| [`docs/migration-plan.md`](../../docs/migration-plan.md) | you draw or script a settlement map (read it first; update its status table when a conversion lands) |
| [`dev/timings.md`](../../dev/timings.md) | you want a measured timing (never write fresh timings into prose; `make audit` and `scripts/measure/gatecost.py` give the live ones) |
| [`dev/test-cost.md`](../../dev/test-cost.md) | you are adding a test that rolls a map, or asking why the suite costs what it does |
| [`dev/ci.md`](../../dev/ci.md) | you are changing when money may be spent on a remote run, or its threat model |
| [`dev/interactive-page.md`](../../dev/interactive-page.md) | page or raster performance, or the wet-paddy modal's two tint rules |

The deferred-engineering backlog is [`future-work/`](../../future-work/CLAUDE.md), by map type. The append-only run
records are `dev/run-log/`, `dev/perf-log/` and `dev/bypass-log/`, each with its own `CLAUDE.md`.

## The always-on rules

**The goal they serve** (GM 2026-08-25, constitution v2.3.0): *"if me asking for a simple change results in half an
hour of work being done when it should have only taken five minutes, then that limits the number of changes that I can
make in a single day."* The cheaper command that answers the question wins, and a simple task that ran long is
diagnosed and the tooling improved.

**The loop** ([`dev/loop.md`](../../dev/loop.md))

- **Nothing runs outside make**: a bare interpreter, a bare pytest or a foreign makefile is refused
  (`scripts/hooks/make-only-hooks.sh`), and the engine refuses in-process calls too (`_invocation.py`). A refusal on correct
  work is a BUG in the guard to fix (it was always a MENTION mistaken for an INVOCATION).
- `make map GEN=pool/<tier>/<map>/<map>.gen.py` regenerates one map and prints `CACHED` / `REGENERATED` / `FROZEN`;
  `PROFILE=1` adds where its time went. Iterate on that ONE map, `make quick` while iterating, `make test-file FILE=...`
  for a whole affected file (never a `-k` subset alone), then `make done` once, backgrounded, never polled.
- `make quick` fails over its own 60 s budget; a test that rolls a map carries `@pytest.mark.rolls_map`
  (`tests/test_markers.py`).
- Never run a test BESIDE a running gate - two writers on the same pool maps is a source of false RED.
- Update the predictably-affected unit tests in the SAME edit as the engine change. **Cycle discipline**
  (constitution v2.4.0): re-read the WHOLE diff for convention misses before the first test run, fix everything a
  failing run lists before re-running, and never write a number into a record that was not measured on the artifact.
- **A performance increase is never silently absorbed** (feature 129, constitution VI): `make perf-report` names the
  band, and the push refuses until its records exist - your `make perf-explain`, the **`perf-audit` subagent's**
  confirmation or audit (never pass `AS=perf-audit` yourself), and above band 2 the GM's sign-off.

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
(`s.open_seat(...)`) and the GEN who placed it (`make why-placed`); read derived geometry from the MANIFEST, not by
re-running a generator; a diagnostic that restates what it observes will lie to you.

**Performance** ([`dev/performance.md`](../../dev/performance.md))

- Every slow gen profiled here was *a per-candidate scan of geometry that does not change during the scan*: build the
  blocked ground ONCE (`PointGrid` / `RingIndex` / `KeepoutGrid`) and ask it per candidate (constitution X clause 15).
- **Maps may change for speed** (GM 2026-09-30: *"They do NOT need to remain identical in output"*), held to the rules,
  never to byte-identity. A slow CHECK is INDEXED, never coarsened. Trust the A/B against HEAD, not cProfile's seconds.
- **Some slowness is bought memory** (GM 2026-10-05): read `dev/performance.md` "Time traded for memory" before
  undoing one; the RAM each undo costs goes to the GM.

**The pool** ([`dev/pool.md`](../../dev/pool.md)) - **the legacy pool is FROZEN**: its 18 hand-authored maps are
exhibits, never regenerated or re-gated; the fix for one is CONVERSION, not retrofit. A cohort of seeds is a stronger
test bed than one map, and a seed that passed before your change and fails after it is a REGRESSION.

**A fix that FAILED is recorded at the point of change** (as the hamlet generator's modules record their dead ends), so
a later session does not re-try it. **Before you build on a property of the engine, check whether anyone DECIDED it**
([`dev/decisions.md`](../../dev/decisions.md)); an open decision carries its 2-3 line implementation sketch.
