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
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->

## T08 - a hook suite keeps the gate incremental

### T08 Approach (checklist part A)

1. **The goal, in the world.** A change to a `tests/hooks/*.sh` suite, which no pytest module runs, no longer makes a landing's
   gate run all ~10,000 tests, so T06 can be measured on a landing that carries one.
2. **The constraints.** The planner selects every test that can read a changed file; nothing it would catch today is missed.
3. **Where each comes from.** O: 405 T106/T138's two full-planned landing gates on 2026-10-25 (`tests/hooks/test-no-poll-hooks.sh`).
4. **Do they describe the world here?** Yes: feature 430 T02 (landed 7d1ced680, 2026-10-26) made a non-module file below
   `tests/<dir>/` select its readers (`incremental.tree_file_readers`) instead of planning full; a hook suite is one.
5. **The order.** After 430 T02; before T07.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 15 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `test_a_hook_suite_keeps_the_gate_incremental` plans incremental on today's planner and fails on the
   planner before 7d1ced680.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T08 Decisions

- **D10** No planner change of this feature's own: 430 T02's reader rule already covers the hooks tree, so T08 adds the test that
  pins the case it was filed for. Rendering: none.

## T07 - the close

### T07 Approach (checklist part A)

1. **The goal, in the world.** The feature's report states what was asked, what was built and measured, and what is left.
2. **The constraints.** Every task ticked first; the report from `make feature-report F=415 WRITE=1`.
3. **Where each comes from.** O: the project's close rule (root `CLAUDE.md`, "A feature ends with `make feature-report`").
4. **Do they describe the world here?** Yes.
5. **The order.** Last, after T06 and T08.
6. **The exits.** Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** 10 min (a GUESS, the session's, 2026-10-26).
9. **Done, measured.** `report.md` written and the feature landed on main.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T07 Decisions

- **D12** The report carries R3's open item: whether the gate now stays incremental under 430's planner is read from the next
  landings' run records (`make gate-costs`), no task of this feature's. Rendering: none.
