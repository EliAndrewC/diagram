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
Report - under one subject; `hamlet()` and `report()` read their part. A `Report` gains the manifest it
was judged on. The lane-rule tests then read the SAME map the cohort test judged, which is more honest
than today, where they read a `build`-only roll `generate` might have re-rolled.

**The first-wave lock (FR-002).** The run share (`_run_share_path`) gains a lock file per subject: the
first worker takes it (`fcntl.flock`, exclusive) and rolls; a second worker finding it held blocks on it,
then reads the payload the holder wrote. A holder that dies releases the lock with no payload, and the
waiter rolls itself; a wait is bounded (10 minutes, longer than any roll) so a wedged holder cannot hang
the run. Measured cost: the waiters idle for one roll's length instead of rolling - 9 rolls and about
230 s of CPU saved per gate, and the container's coincident peak drops with them.

**The census gate (FR-003, FR-004).** The instrument, made permanent: a pytest plugin in `l7r/diagram/ci/`
loaded by the gate's test phase records every roll request per worker; after pytest the Makefile
aggregates and fails on (a) a spec requested twice in one run, (b) a spec absent from the roster, (c) a
roster entry no test requested (a stale roster). Re-roll attempts inside one `generate` are ONE request,
reported with their count. The roster is a Python module in `tests/` naming each spec allowed to roll at
the gate with its reason and the unique coverage or emergent condition it carries (from the packing
record); adding a rolling test means adding its entry with its reason, and the gate says so.

**First-attempt seeds (FR-005).** The census reports attempts per spec. Cohort seeds 41-44 are the
ratchet's pinned canonical range and stay; the CLI test's seed 8 (2 attempts) is free and moves to a
first-attempt seed. The two re-roll tests keep their attempts on purpose.

**Tests do not render (FR-006).** `DIAGRAM_SKIP_RENDER=1` as the suite's default in `tests/conftest.py`;
the tests OF rendering opt out with `monkeypatch.delenv`. Derived, not enumerated: the census also records
every `render_png` and `raster.picture` call with its test, and the gate fails on one from a test that
did not opt out.

**The child roll-out (FR-007).** Feature 210's FR-004 list, done: `report()`/`report_deps()` (folded into
FR-001's one roll), the five direct-`build` closures (their produce functions lifted to module level and
run in the child by name - the feature-146 doctrine), the immune test (the child applies the one-extra-draw
perturbation when told), the CLI test and the fan-out test (the fan-out compares the pool-child path with
the serial path and rolls twice by design - the serial half moves to the child, the comparison stands),
the three tools' tests (stub stages; nothing to move), and the regen site (`run_and_record` in a child,
`gate_obtain`'s driver minus coverage). What stays in-process, stated: `gate_obtain` (already a child),
the perf-snapshot and perf-profile tests (they time stages and must roll where they measure).

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
