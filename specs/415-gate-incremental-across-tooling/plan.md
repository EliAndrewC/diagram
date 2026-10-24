# Implementation Plan: the gate stays incremental across tooling changes (feature 415)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-24

## Summary

The gate's planner stops treating a `scripts/` change (or a Makefile or `pyproject.toml` line that does not shape the test
run) as a reason to run everything; the run record says what was run, why, and where the time went; the landing stops
waiting on the cohort's fresh block and on `cover-changed` before the gate; and, once real landings have measured the
gate's fixed and per-test costs, a landing runs exactly what its change reaches, with the baseline refreshed off the
landing's path. `l7r/diagram/ci/` is engine-routed, so each task lands through `make land` (the gated route).

## Technical Context

- `l7r/diagram/ci/incremental.py`: `manifest` (engine, tests, and `state.tooling_hash`), `changed`, `plan` (the tooling
  rule at its `tooling_moved` branch; `FULL_FRACTION` 0.6), `Plan` (written to `<baseline>/plan.json`).
- `l7r/diagram/ci/state.py`: `TOOLING_PATHS`, `tooling_hash` - which decides when the TOOLING tests rerun; it stays.
- `l7r/diagram/ci/selection.py`: keeps affected tests, every test of a changed test module, and new tests.
- `tests/tooling/_test_deps.py`: GATE mode reuses a tooling test on its recorded reads, on a FULL plan only (`gate_full`).
- `Makefile` `done` (the phases), `test` (pytest, merge, carry, floors, save-baseline), `LOGRUN` (the run record),
  `RUNSTATS` (`scripts/measure/runstats.py`: start, fail, end).
- `scripts/land.py`: `cheap_refusals` (runs `cover_changed.py`), the cohort beside the gate (`make cohort-landing`),
  `push`; `scripts/gates/cohort_gate.py` (`landing_shaped` requires the fresh block).

## Performance bookends

N/A: no generator change. The gate's own timing is this feature's measure (T04, T06).

## Constitution Check

- I-XI: N/A (no map, sheet or research change). XII: every task `research: rendering` (tooling). XIII: `make test-file
  FILE=tests/tooling/ci/`, the tooling tests and `make hooks-test` stay green; each landing's gate is the regression check.
  XVI: built as the spec's FRs; the one departure from the request's wording (`gate-stamp.py`) was struck in spec round 2.

## Order

T01 first, so every later landing's run record carries the numbers T04 reads. T02 next (the big saving). T03 the landing
path. T04 measures. T05 sets the cutoff and the refresh on T04's numbers. T06 measures a real engine landing after a
tooling change end to end. T07 closes.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
## T05 - a landing runs what its change reaches (FR-006)

### T05 Approach (checklist part A)

1. **The goal, in the world.** However much a change reaches, the landing runs that and no more; the baseline stays accurate without a landing paying for it.
2. **The constraints.** T04's numbers; one background refresh at a time; never on a landing's path; the gate outside a landing keeps today's fraction (spec US1 scenario 4 names landings).
3. **Where each comes from.** O: the GM's item 6; M: T04's fit and drift.
4. **Do they describe the world here?** Decided on T04's numbers (this block is re-answered then).
5. **The order.** The landing's gate passes `INCR_NO_CUTOFF=1`; the refresh rule from T04's drift; the refresh started after the push.
6. **The exits.** Decided with T04's numbers.
7. **The search smell.** None.
8. **The budget.** 90 min with its landing.
9. **Done, measured.** Unit tests: a landing plan over the fraction stays incremental; the refresh starts when the rule says, never twice at once; SC-004.
10. **Before moving a constant.** `FULL_FRACTION` stays for the gate outside landings; its dropping at landings rests on T04.
11. **Before fitting things into room.** n/a.

### T05 Approach (re-answered 2026-10-24T18:39Z)

1. **The goal, in the world.** However much a change reaches, the landing runs that and no more; the baseline stays accurate without a landing paying for it.
2. **The constraints.** R2's numbers; one background refresh at a time; never on a landing's path; the gate outside a landing keeps today's fraction (spec US1 scenario 4 names landings); the box's shared 10 GB memory cap (the refresh is a gate's worth of workers beside the session's own work).
3. **Where each comes from.** O: the GM's item 6; M: `research.md` R2 (67 s fixed + 12.7 ms per selected test; the selection 1,492 -> 2,657 over three runs since a full one).
4. **Do they describe the world here?** Yes, measured 2026-10-24 (`make gate-costs`, R2): a landing's incremental test phase costs at most about what a full one does (158 s at 60%, 188 s at 80%, 197 s full), so the cutoff saves a landing nothing; the growth is what costs, a landing paying for every change since the last full run.
5. **The order.** The landing's gate without the cutoff; the refresh after the push, in a detached worktree; its baseline copied into the clone, the coverage paths rewritten.
6. **The exits.** (a) refresh in the clone itself - not taken: the session's next edit moves the tree under it and voids the run, and its gate lock would hold the next landing; (b) refresh after every incremental landing - not taken: a full run each time spends ~200 s of the box for a selection of a few hundred tests; (c) the 25% rule in a worktree - taken.
7. **The search smell.** None.
8. **The budget.** 120 min with its landing.
9. **Done, measured.** Unit tests: a landing's plan over the fraction stays incremental; the refresh starts at 25% and not under it, never two at once; its baseline lands in the clone with the paths rewritten and not over a newer one. SC-004.
10. **Before moving a constant.** `FULL_FRACTION` stays for the gate outside landings; the landing passes `INCR_NO_CUTOFF=1`; the refresh's 25% is R2's.
11. **Before fitting things into room.** n/a.

### T05 part B (2026-10-24T19:08Z)

Owed by the round arbiter's ruling on red-gate@2026-10-24T19:05:23Z (continue).

1. **What exactly is refusing?** Two red landing gates, two causes in this feature's own tests: a T03 test started the real `cover_changed.py`, whose nested coverage run overwrote the gate's coverage data (817 failed); and three planner tests inherited `INCR_NO_CUTOFF=1`, which T05's landing exported to its whole gate (3 failed).
2. **A3 again.** O: the GM's item 6 and request amendment 1; nothing in the constraints moved.
3. **A4 again.** The decisions describe the world; the slips were in how the tests were isolated from the gate running them.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: the flag becomes a make variable (`NO_CUTOFF=1`) the test recipe hands to the planner's call alone, never an environment the tests inherit; the T03 test starts a stand-in check; the planner tests clear the variable as a backstop.
6. **The one-sentence test.** "Why did the landing go red?" - its own new tests reached the gate that ran them.
7. **The next step is a measurement.** One `make land` for T05, the three planner tests green and nothing new failing (the ruling's "what").
8. **Every route measured?** n/a - no route is in question.
9. **After a ruling:** the arbiter's continue, recorded in `arbiter.jsonl`.

### T05 part B (2026-10-24T19:22Z)

Owed by the round arbiter's ruling on red-gate@2026-10-24T19:17:09Z (continue).

1. **What exactly is refusing?** The 18:59Z and 19:17Z gates share one cause, read correctly only the second time: T03 made `make land` run `cover_changed.py` beside the gate in the same tree, and its coverage data, with no `COVERAGE_FILE` of its own, landed where the gate's workers wrote theirs ("no such table: context"). T03 landed on the direct route, so the two first met at T05's gated landing. The 19:05Z gate's cause (the inherited `INCR_NO_CUTOFF`) was separate and is fixed.
2. **A3 again.** O: the GM's item 4 (FR-004) still puts `cover-changed` beside the gate; nothing in the constraints moved.
3. **A4 again.** The decision describes the world; the check and the gate needed separate coverage data.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Changing: `cover_changed.py` writes its coverage data in its own temporary directory (`COVERAGE_FILE`); and the arbiter's tooling fix - a delta touching `land.py`, `scripts/gates/`, the Makefile or `l7r/diagram/ci/` lands through a gate, never the direct route (`land.GATE_MACHINERY`).
6. **The one-sentence test.** "Why did the gate lose its coverage tables?" - the check beside it wrote its own coverage data into the same files.
7. **The next step is a measurement.** One `make land` for T05, counted green only on the ruling's three conditions: no INTERNALERROR and no failed test; the three planner tests green by name; `cover_changed.py` run beside the gate with real work, its data in its own directory, no stray `.coverage*` in the clone root after.
8. **Every route measured?** n/a.
9. **After a ruling:** the arbiter's continue and its tooling fix, recorded in `arbiter.jsonl`.

### T05 Decisions

- **D8** On R2's numbers (spec FR-006, amended): `make land`'s gate runs with `INCR_NO_CUTOFF=1`, which `incremental.plan` reads to skip the `FULL_FRACTION` check (the gate outside a landing keeps it). After a successful push whose gate ran incremental and selected at least `REFRESH_FRACTION` (0.25) of its baseline, `land.py` starts `scripts/gates/refresh_baseline.py` detached: under a lock, it adds a detached worktree at the pushed commit, runs `make done INCR_FORCE="refresh: <n> of <N> baseline tests selected"` there (a fresh worktree has no verification to short-circuit on), and when it is green copies the worktree's `gate-baseline/` into the clone's - each coverage file path rewritten from the worktree's root to the clone's - unless the clone's baseline was saved after the refresh started; it removes the worktree, and copies the run record into the clone's `dev/run-log/`, committed path by path. Rendering: none.

## T06 - measured end to end (SC-006)

### T06 Approach (checklist part A)

1. **The goal, in the world.** The GM sees what a landing costs now, against T26's 8.8 minutes.
2. **The constraints.** A real engine landing after a tooling change, its phases from T01's record.
3. **Where each comes from.** O: the GM's item 1 ("the gate measured on the next real landing").
4. **Do they describe the world here?** To be measured.
5. **The order.** After T05.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 20 min.
9. **Done, measured.** `research.md` holds the landing's table beside T26's.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T06 Decisions

- **D9** The landing measured is the first whose own change does not move `gate_config`, whose baseline already carries the `gate_config` key, and which has a `scripts/` change since its baseline - confirmed by `plan_mode: incremental` in its run record (405's next task where it meets this; T01-T05's own landings change `ci/` and run everything). Rendering: none.
