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

### T05 Decisions

- **D8** To be decided on T04's numbers (amended into the spec as FR-006's rule, and reviewed); the refresh run's record carries its reason (`refresh: <the rule's trigger>`, D2). Rendering: none.

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
