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

<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
