# /diagram engine - dev loop

Guidance for *working on the diagram engine* (the `settlement/` package, the `overlap/` taxonomy, the pool
generators), as opposed to *invoking* `/diagram` to draw a map (that is `SKILL.md`). This file
auto-loads whenever a session edits files in this directory - which is exactly when it applies.

The project-wide iteration doctrine lives in the root [`CLAUDE.md`](../../../CLAUDE.md)
"Iteration-loop efficiency" section (batch recon into fewer bigger turns; iterate on the ONE
motivating artifact, then run the full test bed once at the end; background the final gate; never
cut the procedure/guardrail steps). Read that first; this file carries the concrete diagram numbers
and the DIAGRAM-SPECIFIC lessons that section does not cover - each earned by costing real
round-trips.

## Where things live (read this first; load only the index you need)

The skill's Python lives under **`l7r/diagram/`** (feature 119) and is grouped by what a module is
FOR. Each group carries its own `CLAUDE.md` index, so a session can open the one directory its task
is in instead of paging this file.

**Why the extra two levels.** `l7r/` here is a PEP 420 *namespace portion* - it deliberately has no
`__init__.py` - and it shares the `l7r` parent package with the L7R Toolkit webapp's `l7r.app` /
`l7r.names` in `/host-l7r-repo/gm-assistant/webapp/l7r/`. Both directories contribute to one `l7r.__path__`, so
`import l7r.app` and `import l7r.diagram.settlement` work in the same interpreter and the webapp
can render a map without two colliding top-level packages named `l7r`. **Never create
`l7r/__init__.py`**: that makes it a regular package, terminates the import search, and makes the
webapp's portion silently stop existing. `tests/test_namespace_portion.py` guards it in both trees.

This directory - not `l7r/diagram/` - is still the `sys.path` root, and `pool/`, `tests/`, the
`Makefile` and `pyproject.toml` all stay here. That is why every pool generator's bootstrap block
is unchanged by the move: `SKILL = dirname(dirname(HERE))` from `pool/<tier>/x.gen.py` still lands
here. Engine modules that compute the skill root from their OWN location moved two levels deeper and
were adjusted to match (`gencache`, `pool_index`, `render_cache`, `cohort_audit`, `cache_audit`,
`timings`, `hamletgen`) - a test asserts three of them
still resolve here, because a wrong depth is silent and just lands one directory short of `pool/`.

| directory | what is in it | load its index when |
|---|---|---|
| [`l7r/diagram/settlement/`](l7r/diagram/settlement/CLAUDE.md) | the Mode B drawing engine (the `Settlement` class and its mixins) | you are changing what a settlement map DRAWS or where it places something |
| [`l7r/diagram/overlap/`](l7r/diagram/overlap/__init__.py) | the overlap TAXONOMY and matrix: which features may lie on which, and why | you are adding a footprint feature, or a pair overlapped that should not have |
| [`l7r/diagram/waterfields/`](l7r/diagram/waterfields/CLAUDE.md) | the water-first field engine (v2 comb fields) | you are changing paddies, bunds, canals or the field frame |
| [`l7r/diagram/hamletgen/`](l7r/diagram/hamletgen/CLAUDE.md) | the scripted hamlet generator - a whole hamlet from a 9-line spec | you are working on scripted generation |
| [`l7r/diagram/sitegen/`](l7r/diagram/sitegen/CLAUDE.md) | tier-agnostic generation machinery the tiers SHARE (geometry, types, worker counts) | you are adding a tier generator, or moving a stage out of one |
| [`l7r/diagram/pipeline/`](l7r/diagram/pipeline/CLAUDE.md) | how a map gets regenerated, cached, rendered and indexed | the cache is behaving oddly, or you are changing how generation is DRIVEN |
| [`l7r/diagram/interactive/`](l7r/diagram/interactive/CLAUDE.md) | the interactive HTML map (feature 134): the feature-class vocabulary with its explanations, and the page writer | you are adding a KIND of feature (it needs a class and an explanation), changing what a modal says, or the `all_ink_is_ruled_on` check fired |
| [`l7r/diagram/tools/`](l7r/diagram/tools/CLAUDE.md) | read-only diagnostics and audits you run by hand | a map came out wrong and you need to ask WHY, or a number needs measuring |
| [`l7r/diagram/ci/`](l7r/diagram/ci/CLAUDE.md) | the CodeBuild dispatcher: when a PAID remote run may start, and how it is driven (feature 130) | a remote run refused, or you are changing when money may be spent |
| [`tests/`](tests/CLAUDE.md) | every test, mirroring the source layout, plus the frozen fixtures | you need to find or add a test |
| `pool/` | the shipped maps: `<name>.gen.py`, its manifest, its render, its `.notes.md` design journal | - |
| `wip/` | maps staged outside the pool (not gated, not swept) | - |

Two engine modules are still single files rather than packages, and stay that way on purpose:
**`l7r/diagram/compound.py`** (the Mode A compound program and perimeter-first placer) and
**`l7r/diagram/citybudget.py`** (the space-budget city/capital planner). Both are peers of the
engine packages above - pool generators import them directly - and folding them into a package
would rewrite six frozen generator scripts for no navigational gain.

The prose reference (as opposed to the code) splits the same way: [`SKILL.md`](SKILL.md) is the
usage-facing index, and it indexes [`settlements/`](settlements/) and [`buildings/`](buildings/)
(the per-topic design doctrine) and [`research/`](research/) (the historical grounding). Read a
skill index, then load only the topics the subject calls for.

**Run the packaged modules as modules**, from this directory - `python3 -m l7r.diagram.pipeline.regen ...`,
`python3 -m l7r.diagram.tools.why_placed ...`. Running a package module as a loose script path puts its own
directory on `sys.path` instead of the skill root, which is how one file ends up imported twice
under two names.

## Dev-loop doctrine (load on demand)

This file used to carry all of it inline, at 1,449 lines - roughly 28k tokens charged to **every**
session that edits anything in this tree, including sessions that only regenerate a map. The
doctrine itself is unchanged and verbatim; it now lives in [`dev/`](dev/), one file per topic, each
stating when to load it. Same pattern as the root [`CLAUDE.md`](../../../CLAUDE.md) -> `docs/`
split. **Load the one file your task is in.** The short always-on version of each rule is below the
table; the file is where the evidence, the measurements and the failure stories live, and you want
those before you argue with a rule.

| doc | load it when |
|---|---|
| [`dev/loop.md`](dev/loop.md) | You are about to run the gate or a pool sweep, you want the diagram timing numbers, or you are deciding how much to re-run after a change |
| [`dev/placement.md`](dev/placement.md) | You are adding a map feature, or changing where anything is placed or drawn. Carries the DRAW ORDER map (including the scripted `STAGES` table), CENTER vs FOOTPRINT, and the KEEP-CLEAR CONTRACT. Its companion `dev/placement-stages/hamlet-placement.html` SHOWS the order - Inashiro plated after each of its stages, the notice board and the label phase last |
| [`dev/gate.md`](dev/gate.md) | You are adding or changing a check, writing a check test, or waiving a rule for one map |
| [`dev/diagnostics.md`](dev/diagnostics.md) | A map came out wrong and you need to know WHY - `open_seat`, `why_placed`, `site_justice`, `crop_map`, and how a probe lies to you |
| [`dev/performance.md`](dev/performance.md) | A gen or a check got slow (or "hangs"), or a `GEN_TIME_BUDGETS` entry tripped |
| [`dev/cache.md`](dev/cache.md) | The cache is behaving oddly, you changed how generation is DRIVEN, or a coverage floor breached for no reason you can see |
| [`dev/pool.md`](dev/pool.md) | You are about to touch a pool map, convert one to scripted generation, or work on `hamletgen/` |
| [`dev/perf-log/`](dev/perf-log/CLAUDE.md), [`dev/run-log/`](dev/run-log/CLAUDE.md), [`dev/bypass-log/`](dev/bypass-log/CLAUDE.md) | You are about to add an entry to one of the append-only histories, or wonder why they are DIRECTORIES rather than files |
| [`dev/lessons.md`](dev/lessons.md) | A fix is not working and you are about to try another one - dead ends already walked, claims that turned out wrong, and the SHAPES those failures take |
| [`dev/decisions.md`](dev/decisions.md) | You are about to build on a property of the engine nobody decided, or you are leaving a decision open for a later session |
| [`dev/reviews.md`](dev/reviews.md) | You are about to launch `settlement-review`, `building-review` or `backstory-review` |
| [`dev/skill-boundary.md`](dev/skill-boundary.md) | You are wondering whether building plans (Mode A) and settlement maps (Mode B) should be separate skills or packages, you are adding a new Mode A building type, or a Mode A `.gen.py` is about to appear - the 2026-08-27 decision to keep one skill, the prediction of what would change it (a generator, not a building count), and the order to split in when it does |

[`future-work/`](future-work/CLAUDE.md) is the deferred-engineering backlog, split by map type on
2026-08-24 - load `farming-communities.md` for hamlet/village work, `cities.md` for towns and above,
`compounds.md` for Mode A plans, `cross-cutting.md` for anything spanning tiers. Its own CLAUDE.md
carries the rules that keep it from rotting back into one 3,453-line file.

Two more docs that were already separate: [`migration-plan.md`](migration-plan.md) (the standing
plan for converting the pool to scripted generation - **read it before drawing or scripting a
settlement map, and update its status table when a conversion lands**) and
[`timings.md`](timings.md) (the measured timing ledger; never write fresh timings into prose).

## The always-on version

Each line below is the rule; the doc named after it is the evidence. Where the two ever disagree,
the doc is right - it is where the measurement lives.

**The goal all of this serves** (GM 2026-08-25, feature 133, constitution v2.3.0): *"if me asking
for a simple change results in half an hour of work being done when it should have only taken five
minutes, then that limits the number of changes that I can make in a single day."* Every command
below is chosen against that - the cheaper one that answers the question wins; one verification
covers a batch of changes; a simple task that ran long is diagnosed (more complicated than
expected / lengthier tests than needed / more cycles than needed) and the tooling is improved when
it is the tooling. With remote off, a paid run the tooling was about to start is still recorded
(`make ci-status` "Would have dispatched") and audited at the period's end.

**The loop** ([`dev/loop.md`](dev/loop.md))

**THE COMMAND MAP, with measured times** (feature 127; every number is a stopwatch, not an estimate):

| command | what it does | time |
|---|---|---|
| `make quick` | lint, types, and every test that does not roll a map; stops at the first failure, failed-first (`--ff`) so a fix that did not take fails in seconds | **~11 s** (feature 158, 2026-08-29: 41 s before it - one 39 s test was the whole critical path) |
| `make sun-audit M=...` | the sun rules and the belt's page presence off the manifest - the numbers a record may quote | ~1 s |
| `make polder-probe SEED=21` | the polder block ALONE with its geometry metrics - parcels across a channel, the berm, acreage, the organic numbers. The geometry loop's fast path: it builds through the same `fit_polder` the map does, so it cannot pass while the map fails | **0.2 s** (a map roll is ~47 s) |
| `make overlap-audit M=...` | does A overlap B on a finished map, over RECORDS and over drawn INK (five families). Replaces the point-in-polygon script that got hand-written twelve times across feature 150 | ~2 s |
| `make map GEN=... PROFILE=1` | the same roll, plus where its time went: per-stage timings, the total and the slowest stage | the roll + ~0 |
| `make verify` | THE PAIRED RUN: starts the gate and prints the settlement-review to dispatch in the same turn. Neither half runs alone (`pair-hooks.sh`); a one-sided case takes `PAIR_OK="<reason>"` | the gate, with the review beside it |
| `make reference` | one seed of the reference hamlet (Inashiro), alone - through the roll cache since feature 135: **1.7 s** when nothing the roll executes changed (it says HIT), ~37 s when something did; `GATE_NO_CACHE=1` forces the roll | **0.55 s HIT / ~37 s MISS** |
| `make durations` | where the suite's time goes - run this when a target feels slow | ~35 s |
| `make cov-file FILE=... MOD=...` | which lines of MOD does ONE test file reach - the answer `make test-full` costs 10 minutes to give (feature 146). Serial, no workers; grep the module you care about out of the table | ~2-10 s |
| `make maps` | picks its own scope from how the last run went | 1 min - many |
| `make quick` (as it was under the retired scope lock) | lint/format autofix + pyrefly + every test that neither rolls a map nor carries coverage only nor is tagged for other tiers only (`tiers` marker, T17): ~3,000 tests, ~17 s pytest, ~20 s wall (2026-08-26) |
| `make done` | reference + lint/types + the WHOLE suite INCLUDING `tests/full/` + all three coverage floors (feature 174: the test phase is `test-full` on both branches, because `COV_FLOORS=1` is also what turns every deselection off and a deselected test takes its coverage with it; `FULL=1` now adds the perf bookends and the `L7R_TESTS_FULL` signal); **feature 135 (2026-08-28), three audit passes: 21.7 s UNLOCKED warm (3,750 tests), 17 s locked, ~5.7 min after a main merge that re-keys every cached roll; hooks-test re-runs only the suites whose guard changed (coverage traces only the packages the diff touched; the corpus replay and the map rolls are served from the roll cache), ~35 s unlocked warm, ~130 s unlocked after an edit that re-rolls every cached hamlet** - the map-rolling gate tests are served from the roll cache (`pipeline/rollcache.py`) while nothing they execute changed; the audit ledger is `specs/135-done-test-audit/research.md`. Earlier: measured 2026-08-26: ~75 s with scope LOCKED (map-rolling tests deferred to unlock, `hooks-test` skipped while its stamp is fresh), ~4.5 min unlocked (the 31 map-rolling tests are ~4 of them), ~5.5 FULL. **Short-circuits in seconds** (`already verified`; comments and docstrings in engine Python do not re-key it, GM 2026-08-26) when the last record is a green `make done` against exactly this engine content - the dispatcher's own keys: every `.py` under the skill outside `tests/` and `l7r/diagram/ci/`, plus pool gens/manifests (feature 132; [`dev/switches.md`](dev/switches.md)). Docs, tests, Makefile, config and `scripts/` edits never cost the gate | **ask `make audit` - NOT the quick check** (or ~3 s already verified). Feature 162 (GM 2026-08-30) took the standing number out of this cell: it said ~5.5 min while the run log's median over the last 25 green runs was 137 s, and an undated headline in a table is exactly the shape that goes stale unremarked. The dated measurements to its left are history and stay; `scripts/_gatecost.py done` is the live figure |
| `make test-full` | **EVERY test, nothing deselected** - the full tree, the tier trees, the map-rolling tests and the tooling tests all run, `EXHAUSTIVE` is set, and all three coverage floors are judged. This is `done FULL=1`'s TEST phase on its own, with no static checks, no reference roll and no `perf-gate`. **It does not prompt and costs no money** | ask `make audit` |
| `make done FULL=1` | prompt (cancel by default), then the static checks, the reference map, `hooks-test`, **`test-full`** and `perf-gate`. What it adds over `test-full` is NOT more tests - it is lint/format/typecheck, the reference roll and the perf bookends | ask `make audit` |
| `make ci-status` | **free** - the delta, its route (DIRECT/GATED), the verification state, whether the would-be tree is already verified, month-to-date remote spend. The "why won't it dispatch" answer | ~2 s |
| `make ci-check` | **PAID** (~$0.40 est.) - the iteration check on CodeBuild: lint locally, build parked, reference locally, then `make done` against the merge with the latest main; `FULL=1` (prompts), `TARGET=cohort` etc. | measured in `timings.md` |
| `make ci-merge` | **PAID** - the push's gated route; called by `sync-with-main.sh`, never by hand | - |
| `make ci-measure` | **PAID**, prompts - MEASURE what the remote gate costs (feature 177). The only route that may dispatch with NO engine delta, and the only one that writes no `verified/` record and pushes nothing; every other condition still refuses it. `FULL=1` for the full scope. **DETACH it** - a foreground run dies at the 2-minute tool timeout while the BUILD keeps going, leaving no run-log entry | 437 s green warm, 8 billed min, $0.64 (2026-09-03) |
| `make ci-image` | **PAID** (~$1), prompts - rebuild the build image from `Dockerfile.ci`; the GM's to run | - |
| `make switches` | the iteration switch (feature 132): `remote on\|off`, with reason, who and when. The scope axis was retired in feature 185 | ~1 s |
| `make ci-off REASON=...` / `ci-on` | **remote off**: nothing dispatches to CodeBuild, `ci-check`/`ci-image`/`FULL=1` refuse, the gated push lands on a green local `make done` (LOCAL-GATED). Commits the switch | ~1 s |
| `make perf-report AGAINST=<NNN>-start` | the trend, then the **BAND** the newest pair reaches (feature 129): 1 over this environment's line (0.0% local, 2.0% codebuild), 2 >5% total / >10% seed, 3 >10% / >20% - per environment, both measurements | ~1 s |
| `make perf-explain WHY="..."` / `perf-confirm` / `perf-audit` / `perf-signoff` | the review records a band owes; `perf-confirm` and `perf-audit` are the **`perf-audit` subagent's** (they decline without `AS=perf-audit`); `perf-signoff` is the GM's, at a terminal | ~1 s |
| `make perf-review` | does every environment's newest pair carry the records its band owes? The PUSH runs this | ~1 s |
| `make perf-profile SEED=25 STAGE=web` | tier-2 evidence: cProfile of ONE stage of ONE seed (+225% on that stage); the derived table is committed, the raw `.prof` is not | ~3x the stage |

**Nothing runs outside make.** A bare interpreter reaching an engine entry point, a bare pytest, or a
make driven by a foreign makefile is refused before it executes (`scripts/make-only-hooks.sh`), and
the engine refuses in-process calls too (`l7r/diagram/_invocation.py`). If a refusal fires on correct
work that is a BUG in the guard worth fixing, not something to work around - it did so five times
while being built, every one a MENTION mistaken for an INVOCATION.

**`quick` enforces its own 60 s budget and fails over it.** It was 254 s while every guard pointed at
it as the cheap option, because it deselected two FILES and could not see that three polder tests
rolled maps. Marking is `@pytest.mark.rolls_map`, guarded by `tests/test_markers.py`.


- **A performance increase is never silently absorbed** (feature 129, constitution VI): `make perf-report` names the band; an increase over that environment's band-1 line (0.0% local, 2.0% codebuild) on any seed or the total owes `make perf-explain WHY=...` from you and a confirmation from the **`perf-audit` subagent** (launch it; never pass `AS=perf-audit` yourself); above 5%/10% the subagent's audit; above 10%/20% the GM's sign-off. The push refuses without them.
- Iterate on the ONE motivating map; run the full test bed exactly **once**, at the end. That final
  sweep is MANDATORY whenever shared engine code changed (`settlement/`, `overlap/`,
  `waterfields/`, a scripted engine).
- `python3 -m l7r.diagram.pipeline.regen pool/<type>/<map>.gen.py` - the cache skips the work and
  prints `CACHED` / `REGENERATED` / `FROZEN` every time.
- Cheap linters BEFORE the gate: `python3 -m ruff format . && python3 -m ruff check . && pyrefly check`.
- Then the WHOLE affected test file with `-n auto`, never a `-k` subset. Then `make done`, **once**,
  backgrounded, and **never polled** - act on the notification.
- Never re-run what `make done` just ran, and never run pytest serially (~7x slower here).
- Never run a pytest BESIDE a running gate - two writers on the same pool maps is a source of false RED.
- Update the predictably-affected unit tests in the SAME edit as the engine change.
- **CYCLE DISCIPLINE** (GM 2026-08-26, constitution v2.4.0; measured on feature 133 T10, where ~30 of
  57 minutes were round trips): **re-read the WHOLE diff for convention misses before the first
  test run** - an unimported builder, an undeclared segment input, an unsorted fixture, a wrong test
  coordinate are ten-second fixes that cost a full model round trip each when a test finds them one
  at a time; fix everything a failing run lists before re-running; **scaffold a check with
  and **never write a number into a record
  that was not measured on the artifact** (`make sun-audit` for the sun and the belt) - a guessed
  figure is a correction round the reviewer will make you pay.

**Placement** ([`dev/placement.md`](dev/placement.md))

- **Read the DRAW ORDER map before moving anything.** A drawing method sees only what is in `self.M`
  when it runs; a placer avoids only what is in the registries when it runs. Most "wrong geometry"
  is wrong ORDER.
- A new footprint feature MUST go in `_OVERLAP_STRUCTS` (or `_OVERLAP_EXEMPT`, with the reason) and
  get a caption group in `_LABEL_GROUP`. Membership alone gates it off fifteen hazards; nothing else
  has a hand-written key list to remember.
- **Record a footprint the extractor can read** - `x`+`w`/`vw`, a `poly`/`outline` ring, a stroked
  polyline, or `parts` of rotated quads. A record matching none of those is invisible to every
  matrix check in both directions and looks exactly like a feature with nothing wrong.
- **Gap verdicts read footprints, never centers** - `edge_gap` / `within_edge_gap` / `sat_overlap`.
  Classification, association-reach and prefilters may use centers, deliberately; say which family
  your rule is in, in a comment, at the test. Add a `test_gap_verdicts_read_footprints_not_centers`
  entry with every new gap rule.
- **Never let an aggregate (a centroid) stand in for the distributed thing a verdict is about.**
  Measure to the nearest member, or to the wall.
- **Randomness is POSITIONAL or SCOPED, never "wherever the stream happens to be":** `self._hjit(x, y, salt)`
  for a per-feature attribute, `with self.rng_scope(name, *key)` for a phase or region.

**The gate** ([`dev/gate.md`](dev/gate.md))

- **A RULE ABOUT A MAP IS A TEST OF THE PLACER THAT MAKES IT** (feature 166, GM 2026-08-30). There is
  no post-placement check battery: `check_village` and its 1,371 segments are deleted. A clearance or
  seat a placer decides is a unit test of that placer; a property of a FINISHED map that no single
  placement owns is a seed test in `tests/gate/` on a cached roll; a fact about the code is a static
  test; and a rule about a feature no scripted generator produces is a recorded DROP with its
  grounding kept. Mode A is the exception the GM drew himself - a compound plan is placed by a
  person, so it keeps its `building-review` / `size-audit` agents and their frozen bad-SVG fixtures.
- **Non-vacuity is asserted, never assumed.** A seed test whose subject list is empty passes; every
  test in `tests/gate/` states what it FOUND before it states the found thing is well formed.
- Placement and its test must read the SAME source - import the engine's predicate rather than
  restating it, and where a restatement is unavoidable, restate it EXACTLY.


**Diagnostics** ([`dev/diagnostics.md`](dev/diagnostics.md))

- Ask the ENGINE where a feature fits (`s.open_seat(...)`) - do not guess coordinates and regenerate.
- Ask the GEN who placed it (`tools/why_placed.py --at` / `--refused`) - do not grep for the caller.
- Adjudicate a multi-rule siting against the GATE (`tools/site_justice.py`), never against a
  re-statement of the rules.
- Read derived geometry from the MANIFEST (0.2s), not by re-running the generators (minutes).
- Batch every crop you want to look at into ONE `tools/crop_map.py` call, then Read them together.
- **A diagnostic that restates what it observes will lie to you.** Print the value and its
  provenance from ONE expression, or do not print the provenance.

**Performance** ([`dev/performance.md`](dev/performance.md))

- Every slow gen ever profiled here was the same shape: *a per-candidate scan of geometry that does
  not change during the scan*. Hoist, prefilter, or index - and if a gen "hangs", suspect that shape
  and profile before bisecting.
- When a check is slow, **INDEX it - do not coarsen it.** The index prunes; it never decides.
- Trust the A/B against HEAD, not cProfile's seconds.

**The pool** ([`dev/pool.md`](dev/pool.md))

- **The legacy pool is FROZEN.** The 18 hand-authored maps are permanent exhibits: never regenerated,
  never re-gated, renders committed. The fix for a frozen map that breaks a post-freeze rule is
  CONVERSION, not retrofit - do not "fix" one, and do not treat its violations as bugs.
- New rules ship un-gated; engine changes no longer need byte-identity flags.
- A cohort of seeds is a much stronger test bed than a map - and **measure the cohort's baseline
  first**, in a detached worktree (`git worktree add --detach /tmp/base HEAD`), never by stashing.
- A seed that passed before your change and fails after it is a REGRESSION, and nothing merges to
  main carrying one (constitution Principle XIII). "It rotated" is not a defense.

**Reviews** ([`dev/reviews.md`](dev/reviews.md)) - `settlement-review` is mandatory before a Mode B
map ships - which since 2026-08-26 means at ACCEPTANCE and at UNLOCK, not per task: while `scope`
is locked the GM looks at every result and no per-task review runs; when one runs it runs in the
background after the map is handed back (or beside a LONG gate, never `make quick`) and is never
waited on. Say the SCOPE (`DELTA:` vs `FULL`), one map per agent in parallel. **A finding OUTSIDE the delta
is still yours to fix** (constitution Principle XIV) - a reviewer pointed at a delta reliably turns
up unrelated defects, and that is it working.

**Build what was asked** (constitution Principle XVI, NON-NEGOTIABLE) - and in this engine the
temptation is specific: almost every ordering or placement rule has a case where an exception looks
justified, because the geometry really is full of special cases. It is still not yours to approve.
Feature 126 was asked for as "farmhouses before lanes" and specified as farmhouses before lanes
EXCEPT the connector and the field spur; both of those register no-build corridors, so both kept
constraining the placement the feature existed to free. An exception goes to an independent Opus 5
subagent with the GM's request verbatim, and a finished `spec.md` gets the same treatment before
implementation starts. Three rounds, then escalate.

**Fix defects where you find them** (constitution Principle XIV, NON-NEGOTIABLE) - this engine is
where the rule bites hardest, because its reviewers and diagnostics surface defects constantly and
almost none of them belong to the feature in hand. Fix them in the work at hand; defer ONLY an
architectural fix, and then with its measurement, mechanism and sketch. Do not cite Principle XIII's
"pre-existing failures stay ledgered" - that governs what blocks a push, not what you owe a defect
you have seen. And when a fix attempt FAILS, record it at the point of change: `homesteads.py`
carries two dead ends for the front-row lane cap, either of which a later session would otherwise
re-try.

**Recording decisions** ([`dev/decisions.md`](dev/decisions.md)) - before you build on a property of
the engine, check whether anyone DECIDED it; a side effect is not a rule. And an open decision
carries the 2-3 line implementation sketch, not just the question.

- **Research it before you ask the GM, and if two forms are supportable make it a KNOB.** The
  ladder: research -> decisive means implement it -> two attested forms means roll between them per
  settlement -> only a silent record earns a GM ruling. Liberty covers a DEGREE along a continuum,
  never a choice between two distinct FORMS. Constitution Principle XII; evidence and the worked
  example in the doc.
