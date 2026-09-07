# Research - 213 One roll per hamlet per gate

TOOLING research, nothing physical. Measured in the container on 2026-09-07 with a pytest plugin that
patched every roll entry point (`driver.build`, `driver.roll_scope`, `rollcache._hamlet_in_child`,
`rollcache.obtain`, `gencache.gate_obtain`, `gencache.run_and_record`) and recorded the spec, the
mechanism, the requesting test and the seconds, per worker, over one `make test-full` (3,096 tests,
356 s). The instrument is `specs/213-.../census/rollcensus.py` and its aggregation.

## R1. The count: 37 real rolls of 14 distinct specs

The record (`dev/loop.md`, "THE PACKING QUESTION", 2026-08-31) says 11 distinct rolled, floor 8-9.
Today, leaving out the stub-stage rolls that cost nothing (the stage-profile test, the placement-stages
tests, the roll-scope test):

| mechanism | rolls | detail |
|---|---|---|
| the run-scoped share racing at the start | 9 | Inashiro rolled by 4 workers, Kuwabata by 3, polder seed 19 by 2 - `hamlet()`'s cross-worker share (feature 147) helps only a worker that starts AFTER another finished; under worksteal every gate module starts at t=0, so the first wave rolls in parallel and shares nothing |
| the same seed under two subjects | 4 | cohort seeds 41-44 are rolled through `hamlet()` (`build` only, for the lane-rule tests) and again through `report()` (`generate`, for the cohort gate test): different cache keys for the same seed (feature 192 introduced `report:`) |
| the generator's re-roll loop | 5 | `generate()` re-rolls a map that strands a farmhouse: cohort seed 42 took 3 attempts (205 s in one test), the CLI test's seed 8 took 2; two more are the re-roll TESTS, which need their attempts |
| the reference hamlet rolled for other reasons | 3 | the pool sweep's coverage child, the cache round-trip test (in-process, with a render - the 444 MB PIL child), the perf-snapshot test; Inashiro is rolled 7 times in one gate |
| the actual variety, one each | 16 | Inashiro, Kuwabata, polder 12, polder 19, seeds 41-44, the five emergent-condition rolls (the clamped pond, the woodland ladder, the three homestead seatings), the immune test's Kashikawa, the CLI test, feature 210's child-equality test |

Distinct specs: 14 (the record's 11, plus the CLI test's seed 8, the immune test's Kashikawa, and 210's
child-equality roll). Rolls per distinct spec: about 2.6. The pool sweep itself was 1 REGENERATED (Inashiro,
the engine changed) and 4 HITs.

**What drifted, and why nothing failed.** The 2026-08-31 measurement counted the cache's VARIETY - distinct
subjects - and nothing gated it. Since then: the `report:` subject (feature 192) doubled the cohort seeds;
the share's start-of-run race was never measured, because the share was validated on a later module hitting
an earlier one; and tests kept being added with `HamletSpec` literals of their own, two of them this week.
The GM's diagnosis stands: a measured minimum that nothing enforces is re-derived every time it drifts.

## R2. The 5.5 GiB at the landing gate's peak (feature 210), for the record

| slice | MiB |
|---|---|
| kernel page cache, clean and reclaimable | 2,357 |
| the three Claude sessions | 1,374 |
| the 8 test workers, 138-271 each | ~1,340 |
| one PIL child encoding a real map's raster (the cache round-trip test) | 444 |
| the pytest controller | 190 |

A worker's 165 MB: pytest with xdist and coverage 36, the engine 26, collecting all 3,114 tests ~50, the
run's growth ~50. Eight copies of the same 110 MB collection baseline is 880 MB.

## R3. The designs

**One roll per spec, shared by `build` and `generate` (FR-001).** Today `hamlet()` produces `(plan,
manifest)` by `plan_site` + `build` + `finish`, and `report()` produces a `Report` by `generate` (the
re-roll loop, then `finish` into a scratch directory that is deleted, then the reachability verdict). One
child roll produces all three - the plan, the finished manifest of the roll `generate` KEPT, and the
Report - under one subject; `hamlet()`, `report()` and `report_deps()` read their part. A `Report` gains
the manifest it was judged on. The lane-rule tests then read the SAME map the cohort test judged, which is
more honest than today, where they read a `build`-only roll `generate` might have re-rolled. **The same
change closes feature 207's D14** (relayed by the GM): the hamlet floor's `report_deps` reads the roll's
stored record, so on an incremental run the floor phase no longer re-rolls the subjects the tests just
rolled (207's R8: about 140 s of the polder-only run's 219 s). Two conditions make it hold: the unified
subject must be STORED under the full-run bypass, as `report:` is today (`_stores_under_bypass`, feature
192), not shared only in memory; and the floor's fixed subjects (Inashiro, the two polders, the cohort
seeds) must all be rostered specs - they are.

**The first-wave lock (FR-002).** The run share (`_run_share_path`) gains a lock file per subject: the
first worker takes it (`fcntl.flock`, exclusive) and rolls; a second worker finding it held blocks on it,
then reads the payload the holder wrote. A holder that dies releases the lock with no payload, and the
waiter rolls itself; a wait is bounded (10 minutes, longer than any roll) so a wedged holder cannot hang
the run. Measured cost: the waiters idle for one roll's length instead of rolling - 9 rolls and about
230 s of CPU saved per gate, and the container's coincident peak drops with them.

**The census gate (FR-003, FR-004).** NOT the instrument made permanent as it was: the instrument patched
six entry points and missed one on its first run (the package's re-exported `build`, reached by five
tests) - the spec review named that as the shape that lets the drift return under a green gate. The
record is written instead at the chokepoint every roll crosses in every process: `driver.roll_scope()`,
which feature 210's static AST test proves every stage-running loop enters. It appends one line per roll
(spec, pid, attempts, seconds) to the file named by `L7R_ROLL_CENSUS`, an environment variable the gate
sets and every child inherits - a worker, a roll child, a pool-sweep child, a cohort pool child all
record alike. The pytest plugin (`ci/rollcensus.py`, loaded as a second `-p` beside 207's `gate_plugin`,
which stays a two-hook shim) does attribution and verdicts: it sets `L7R_ROLL_CENSUS_TEST` around each
test so every record names the test that caused it, and records each `obtain` verdict (served or
rolled). After pytest, `python3 -m l7r.diagram.ci rollcensus verdict` aggregates and fails on: a second
ROLL of a spec (a request the share did not serve - many requests served by one roll is the passing
state; attempts inside one `generate` are one roll, reported), a rolled spec absent from the roster, on a
full run a roster entry nothing rolled, a render from a test without the `renders` marker, an in-process
roll in a test worker from a site the roster does not except. The roster (`tests/rolls.py`) names each
spec with its reason and unique coverage, and the stated duplicates with their mechanism.

**First-attempt seeds (FR-005).** The census reports attempts per spec. Cohort seeds 41-44 stay: what
pins them is `GATE_COHORT_EXPECTED` (the expected-failure record over seeds 41-44, measured 2026-08-27,
`tests/gate/hamletgen/test_driver.py`) and the strict seed-43 expected failure in
`tests/gate/test_cohort_lane_rules.py`, both over a contiguous `cohort_specs(4, first_seed=41)`; the perf
ratchet's seeds (4, 25, 39, 47, `perf_snapshot.DEFAULT_SEEDS`) are a different set and not the reason.
The cost accepted: seed 42's two extra attempts, about 140 s of one worker per gate. The CLI test's seed
8 (2 attempts) is free and moves. The two re-roll tests keep their attempts on purpose.

**Tests do not render (FR-006).** `DIAGRAM_SKIP_RENDER=1` as the suite's default in `tests/conftest.py`;
a test OF rendering carries a `renders` marker and clears the switch itself. The census records a render
at the one site that consults the switch for both the PNG and the raster (`finish()`'s `rendering`) and at
a direct `picture()`/`render_png()` call, and the gate fails on a render from a test without the marker.

**The child roll-out (FR-007), the surface derived.** The callers of `hamletgen.generate`,
`hamletgen.build` and `driver.STAGES` (feature 210's own derivation) are the sites; each is in a child or
a stated exception, and the census enforces it by failing on an in-process roll in a worker from any other
site. Moved: `report()`/`report_deps()` (FR-001's one roll); the direct-`build` closures
(`test_homesteads` x3, `test_sink`, `test_woodland_shrink_147`) and the direct-`generate` closures (the
two re-roll tests) - lifted to module-level functions the child runs by name, with their monkeypatches
applied inside the child through `unittest.mock.patch`; the immune test (the child applies the perturbation
when told); the CLI test's roll (`main()` rolls through `generate`, which FR-001 makes a child roll); the
fan-out's serial half (served from the shared roll); the regen site. Not needing a change: the tools
(`cohort_audit`, `mapcheck`, `driver.cohort()` and `driver.main()`) roll through `generate`. The
exceptions: the perf-snapshot and perf-profile tests time the stages where they run; each rolls a seed of
its own, entered in the roster, so neither is a second roll of Inashiro (the perf-snapshot test rolled
seed 4 today - a duplicate the review caught). The fan-out's parallel half is a stated duplicate: the
cohort pool child IS the mechanism under test. `gate_obtain` is the rule, not an exception.

**The pool sweep's child (FR-008).** Profile one `gate_obtain` child with the per-stage instrument: the
550 MB against 121 in-process is unexplained. Coverage under `sys.monitoring` on a 22,000-statement
engine, or the manifest's JSON dump, are the candidates; act if simple, record if not.

**Worker count (FR-009).** 4, 6 and 8 workers on the same content: the gate's time and the container's
peak. The rule for the default: the smallest count within 10% of the fastest time.

**Ordering and the roll cap (FR-010).** A `pytest_collection_modifyitems` hook in the gate plugin moves
the roster's rolling tests to the front of collection so the long rolls start first; a slot semaphore in
the run share dir bounds concurrent child rolls (the count measured against the gate's time).

**Item 5 (FR-011).** Nothing built: feature 207 (another session's, in flight) merges per-test coverage
contexts over the last full run so a change re-rolls only what it reaches. This feature does not build a
second answer, and its census gate must hold under 207's incremental runs too (a subset of the roster
requested is not stale - only a full run judges (c)).

## R4. Measured after

(Filled in by the implementation: rolls per gate, gate time, container peak, worker peaks.)
