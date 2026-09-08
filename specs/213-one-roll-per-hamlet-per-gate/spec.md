# Feature 213 - one roll per hamlet per gate

**Status**: DRAFT - `spec-fidelity` round 1 required five changes, all applied: FR-007's surface DERIVED
from the callers of `generate`/`build`/`STAGES` with every site in a child or a stated exception and a
gate check on it; FR-003's rule on a second ROLL, not a second request; the three exceptions adjudicated
(perf tests roll their own rostered seed; the fan-out's pool half a stated duplicate; `gate_obtain` not
an exception); the census recording at the chokepoint `roll_scope()` rather than patched entry points
(D5); FR-005's pin named exactly with its cost. Round 2 pending (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim, including the six changes they approved.
**Research**: [`research.md`](research.md) - the census (37 rolls of 14 specs), the 5.5 GiB breakdown, the
designs.
**Predecessors**: 210 (the roll leaves the worker; its FR-004 roll-out list); 208 (the raster is a render);
147/192 (the run-scoped share and the `report:` subject); the packing record of 2026-08-31 (`dev/loop.md`);
207 (another session's incremental gate - the answer to item 5, not rebuilt here).

## Summary

The GM: *"nail down the number of hamlets which are being rolled"* - 37 real rolls of 14 distinct specs
per gate against a recorded floor of 8-9 - and *"program our unit tests to never allow the same hamlet
to be rolled twice within the tests and also to have some required process around adding another hamlet
that gets rolled"*, plus the six changes they approved verbatim. This feature makes the gate roll each
hamlet ONCE, gates that it stays so, and takes the six changes start to finish: no test renders a map
unless it tests rendering; every gate roll runs in a child; the pool sweep's child is profiled; the worker
count is measured; the long rolls start first and their concurrency is capped; item 5 is left to 207.

## Functional requirements

- **FR-001 One roll per spec.** One child roll produces everything any test needs of a spec - the plan,
  the finished manifest of the roll `generate` kept, and the `Report` - under one cache subject;
  `rollcache.hamlet()`, `rollcache.report()` and `rollcache.report_deps()` read their part of it. `Report`
  gains the manifest it was judged on. The cohort seeds are no longer rolled twice. **And the hamlet
  floor's second roll goes with them (feature 207's D14, relayed by the GM through the "Diagram html"
  session on 2026-09-07):** on an incremental gate the selected tests re-roll a changed subject under
  `hamlet()`'s cache subject and the floor phase (`hamlet_floor.module_set` -> `report_deps`) rolls the
  same spec again under `report:`'s, serially - about 140 s of the polder-only run's 219 s (207's R8). The
  floor's fixed subjects are all rostered specs, so with one subject per spec the roll the tests made IS
  the record the floor reads - which requires the unified roll to be STORED under the full-run bypass
  (as `report:` rolls are today, feature 192) rather than shared only in memory. Confirmed by
  measurement on the polder-only incremental run, in its own task, ticked even if nothing beyond FR-001
  turns out to be needed.
- **FR-002 The first wave waits.** The run-scoped share takes a per-subject lock: the first worker rolls,
  a worker that finds the lock held waits (bounded) for the payload rather than rolling its own; a holder
  that dies without a payload lets the next waiter roll. Inashiro, Kuwabata and the polder are rolled once
  per run whatever the workers' start order.
- **FR-003 The census is the gate, and it records at the chokepoint every roll crosses.** The record is
  written by `driver.roll_scope()` itself - the one boundary every stage-running loop enters, in every
  process (feature 210's static test proves every such loop sits inside it) - to a file named by an
  environment variable the gate sets and every child inherits, so a roll in a worker, in a roll child, in
  a pool-sweep child or in a cohort pool child is recorded the same way, with the spec, the process, the
  attempts and the seconds. The pytest plugin's part is attribution: it sets the requesting test's id in
  the environment around each test, so every record names the test that caused it, and it records the
  roll-cache verdicts (served or rolled). After pytest the Makefile aggregates and FAILS the gate on:
  **a second ROLL of a spec in one run** - a request the run-scoped share did not serve (many tests
  requesting one shared roll is the passing state, and the re-roll attempts inside one `generate` are one
  roll, reported with their count); a rolled spec absent from the roster; on a full run, a roster entry
  nothing rolled; a render from a test not marked as a test of rendering (FR-006); and an in-process roll
  in a worker from a site the roster does not name as a stated exception (FR-007). The verdict names the
  tests involved.
- **FR-004 The roster is the required process.** `tests/rolls.py` lists each spec allowed to roll at the
  gate with its reason and the unique coverage or emergent condition it carries, seeded from the packing
  record and the census. A site that must roll a rostered spec a second time by its nature carries its own
  entry naming the mechanism and the reason, and the verdict lists it as a stated duplicate: the fan-out
  test's pool-child path (the mechanism under test; its serial half is served from the shared roll) -
  the only one the drafting census showed; the first gated census (2026-09-08) found three more sites that
  roll a rostered spec by their nature and two roster kinds the draft had no word for, all recorded in D6
  and D7 rather than waived. A test that rolls a spec not in the roster fails the gate with the instruction to
  add the entry with its reason. The roster's size is the recorded roll count; `make audit` prints it.
- **FR-005 First-attempt seeds.** Where a test does not exist to exercise the re-roll loop and its seed
  needs more than one attempt, the seed moves to one that finishes first (the CLI test's seed 8). The
  cohort seeds 41-44 stay, and the pin is named exactly: `GATE_COHORT_EXPECTED` in
  `tests/gate/hamletgen/test_driver.py`, the expected-failure record measured on 2026-08-27, and the
  strict seed-43 expected failure in `tests/gate/test_cohort_lane_rules.py`, both over a contiguous
  `cohort_specs(4, first_seed=41)` that cannot move one seed at a time (the perf ratchet's seeds are
  another set, 4/25/39/47, and are not the reason). The cost accepted, recorded per the
  accept-a-limitation rule: seed 42's two extra attempts, about 140 s of one worker per gate, reported by
  the census on every run. The two re-roll tests keep their attempts by design.
- **FR-006 Tests do not render.** `DIAGRAM_SKIP_RENDER=1` is the suite's default; a test OF rendering
  carries an explicit `renders` marker. The census records a render at the one place the switch is
  consulted for both the PNG and the page's raster (`finish()`'s render decision) and a `picture()` or
  `render_png()` call made directly, and the gate fails on either from a test without the marker.
- **FR-007 The child roll-out, finished - the surface derived, never listed.** The set of sites that can
  roll is derived the way feature 210's FR-004 derived it: the callers of `hamletgen.generate`,
  `hamletgen.build` and `driver.STAGES`. Every site the walk finds is EITHER in a child OR a stated
  exception with its reason in the roster, and the census enforces it: an in-process roll in a test
  worker from any other site fails the gate, so a new in-process roll site cannot appear unnoticed.
  What moves to a child here: `report()`/`report_deps()` (FR-001), the direct-`build` and
  direct-`generate` produce closures in the gate tests - lifted to module-level functions the child runs
  by name, their patches applied inside the child - the immune test (the child applies the one-extra-draw
  perturbation when told), the CLI test's roll, the fan-out test's serial half (served from the shared
  roll), and the regen site (`run_and_record` in a child - `gate_obtain`'s driver without coverage) so
  `make map`, `make maps` and render-sync roll in children too. The tools (`cohort_audit`, `mapcheck`,
  `driver.cohort()` and `driver.main()` outside the tests) roll through `generate`, which FR-001 makes a
  child roll, so they need no change of their own. The stated exceptions, each adjudicated: the
  perf-snapshot and perf-profile tests time the stages where they run and must roll in-process - and so
  that they are not a second roll of a rostered spec, each rolls a seed of its own, entered in the
  roster with that reason; the fan-out test's parallel half rolls in a cohort pool child, which is the
  mechanism under test (a stated duplicate, FR-004). `gate_obtain` is not an exception: it is the rule.
- **FR-008 The pool sweep's child, profiled.** One `gate_obtain` child under the per-stage instrument;
  the cause of 550 MB against 121 named; acted on if the fix is simple, recorded with a sketch if not.
- **FR-009 The worker count, measured.** 4, 6 and 8 workers on identical content: gate time and container
  peak recorded; the default becomes the smallest count within 10% of the fastest, stated with the numbers.
- **FR-010 Ordering and the cap.** The roster's rolling tests are collected first so the long rolls start
  at t=0; a slot semaphore in the run share bounds concurrent child rolls, its count measured against the
  gate's time.
- **FR-011 Item 5 is 207's.** Nothing built for it here; FR-003's stale-roster check applies only to a
  full run so 207's incremental runs pass it.
- **FR-012 Measured before and after.** Rolls per gate (37 / 14 distinct before), gate time, container
  peak, worker peaks; research R4.
- **FR-013 Tests and the record.** Each mechanism proved to fire: the lock (two producers, one roll), the
  second-roll refusal, the unrostered refusal, the stale-roster refusal, the render refusal, the
  in-process-site refusal, the child equality for each lifted closure; a static test that the callers of
  `generate`/`build`/`STAGES` are each in a child or in the roster's exceptions (the derivation of
  FR-007, kept honest); 100% coverage over the plugin and the roll cache. The why at each point
  of change; `tests/CLAUDE.md`, `pipeline/CLAUDE.md`, `dev/loop.md`'s packing section and
  `dev/performance.md` extended; the root `CLAUDE.md` gains the roster rule.

## Success criteria

- **SC-001** A full gate rolls each roster spec exactly once, the stated duplicates aside and listed; the
  census verdict says so, and the roll count equals the roster's size.
- **SC-002** Each refusal shown once (a second roll, an unrostered spec, a stale entry, a stray render, an
  in-process roll from an unlisted site).
- **SC-003** `make done` green; the after numbers in R4.
- **SC-004** On the polder-only incremental run of 207's R8 (a harmless statement in
  `waterfields/polder.py` `s_on_side`), the floor phase rolls nothing: the census shows each polder spec
  rolled once, by the tests, and the gate's time falls by about the 140 s the floor used to spend.

## Decisions Recorded

- **D1 - the roster lives in `tests/`**, beside the tests it governs, as Python (typed entries, no parser).
- **D2 - a lock, not a queue.** The first wave waits on the roll in flight; nothing schedules rolls
  centrally. The cap (FR-010) is a semaphore in the same share directory.
- **D3 - cohort seeds stay** despite seed 42's three attempts: the expected-failure record and the seed-43
  expected failure pin the contiguous range 41-44 (FR-005 names them); the cost is recorded there.
- **D4 - the census counts ROLLS, attributes REQUESTS.** A `generate` that re-rolls is one roll with N
  attempts - the generator's behavior is reported, not forbidden - and N tests served by one shared roll
  is the passing state.
- **D5 - the record is written at the chokepoint, not by patching entry points.** The 2026-09-07
  instrument patched six functions and missed the package's re-exported `build` on its first run; the
  gate must not be able to be short the same way, so `roll_scope()` writes the record and the AST test of
  feature 210 is what proves the chokepoint is total.
- **D6 - a roll is (spec, request, PROCESS), and two more duplicates and a seed.** The first gated census
  (2026-09-08) grouped by request alone and reported the fan-out's serial and pool children as one roll with
  two attempts - hiding the very duplicate FR-004 states. A `generate` that re-rolls does so in one process,
  so grouping by pid keeps its attempts together and separates two children of one test. The same census
  found: the immune test's perturbed second roll (Kashikawa 3) and the real-map cache round trip (Inashiro
  4, which ran the gen TWICE - a subprocess for the files and `run_and_record` in the worker for the record;
  now one child roll) are stated `Duplicate`s with their reasons; the two perf-profile tests both rolled
  Inashiro 5 in the worker, so the first-stage test rolls seed 7, rostered (it stops after `water_frame`,
  milliseconds); and the stub-stage modules (`tests/hamletgen/test_driver.py`, `test_placement_stages.py`)
  record rolls of stand-in stages - `InProcess(stub=True)`: reported and bounded by `STUB_MAX_S` (5 s
  against an 11 s shortest real roll), never counted as hamlets.
- **D7 - the pool sweep's generators are a roster kind of their own, `PoolGen`, not unified with the spec
  roll.** `gate_obtain` rolls a shipped `.gen.py` only when its cache key moved (an engine change) and
  serves it from the gen cache otherwise, so it can be neither a `Roll` (stale on every warm full run) nor
  a `Duplicate` (two of the five - Sawada, Mizuguchi - ship no rostered spec). Three of the five share a
  (name, seed) with a gate roll, so a COLD run rolls the reference twice: once as the spec the gate tests
  read, once as the generator that ships it. Unifying them - the sweep reading the spec roll's manifest
  instead of running the gen - was priced and declined: the gen script is the unit the sweep exists to run
  (its budget, its manifest, its coverage child), and the two briefs are not the same today - the pool's
  Inashiro carries `fixtures_min={'shrine': 1}` and the gate's SPEC literals do not (recorded in the roster
  row and R4; the GM's to rule on). The verdict allows a pool gen once per run, from the sweep only, and
  prints whether it rolled or was served.
- **D8 - a coverage child is labeled with its requester's context, and the floor phase is inside the
  census.** The polder-only incremental run of T10 (2026-09-08) ran 54 tests in 38 s and took 228 s - no
  faster than 207's 219 s - and its census showed one roll, by the cache round trip. The polder gate tests
  had not been selected at all: feature 207 selects from the baseline's per-test and per-fixture coverage
  contexts, and a roll made in a child (210, 213) records the engine's lines under NO context, so a change
  only a roll reaches selected 46 unit tests and not one roller; the hamlet floor then re-rolled both polder
  subjects itself, unseen, because the floor phase ran outside the census. Two fixes, both gated:
  `ci/selection.switch` exports the context it sets (`_census.CONTEXT_ENV`) and every coverage child - the
  roll child, the pool sweep's `gate_obtain` child - runs `coverage run --context=<it>`, so the baseline sees
  the roll under its requesting fixture or test exactly as it did when the roll was in the worker; and the
  floor phase runs under `L7R_ROLL_CENSUS` with the verdict AFTER it, where a roll no test requested fails
  the gate and says what it means. SC-004 is read off that verdict after a full baseline taken with the
  labels in place.
- **D9 - a fixture's context is keyed by WHERE it is defined, not by its argument name.** With D8 in place
  the polder-only run selected the rollers - and 106 tests with them, re-rolling 18 specs in 297 s, because
  ten gate modules each define a `rolled` fixture and feature 207 named every one of them `fixture:rolled`:
  one context, so a file one of their rolls touched selected every test behind any of them. The id is now
  `<definition site>::<name>` (`tests/gate/test_water.py::rolled`; a root-conftest fixture keeps its bare
  name), in the context, the closure file and the dependency graph alike (`ci/selection.fixture_id`).
  A defect in 207's own granularity, found because the census made the roll count visible, fixed here
  under Principle XIV.
