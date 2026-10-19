# Implementation Plan: Retire the exhibit-only engine

**Branch**: none (main, in the clone) | **Date**: 2026-10-18 | **Spec**: `spec.md`

## Summary

Delete the 166 engine names that only frozen exhibits reach (the 71 and their closure, `closure-rounds.txt`), the twelve
modules that empty, and their tests; repoint the prose; add the tier placeholders' pointer line. No live map changes.

## Technical Context

Python, the engine under `l7r/diagram/`; pytest under `make`. **Single-artifact target**: none - the deletion changes no live
map; FR-006 is proven across the whole live pool (`make maps`, nothing regenerated) and the landing cohort.

## Performance bookends

`392-start` on unmodified code, `392-end` before the push. Removing code no live map runs should move nothing; a flag over
the band is mentioned with its load.

## Constitution Check

- I, II: N/A - no UI. III, IV, V, VII, VIII, IX: N/A - no pool content, SOURCE block or in-world prose.
- VI: PASS - each task names its verification; `make maps` and the landing cohort stand in for reference-then-pool, since
  nothing is meant to move.
- X: PASS - ruff, pyrefly, the full-coverage floor; no new behavior; no function grows; nothing indexed is added.
- XII: PASS - no rendering decision changes (spec D3); the deleted code's claims leave the index.
- XIII: PASS - the landing cohort refuses a regressed seed. XVI: PASS - the literal reading is the spec's "What it is".

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-18 (feature 375 FR-044) -->
## Project Structure

Touched: `l7r/diagram/settlement/**`, `l7r/diagram/waterfields/hill.py`, `l7r/diagram/citybudget.py`, `tests/**` (deletions),
`docs/`, `dev/`, `specs/380-*/spec.md`, `specs/381-*/spec.md`, `specs/382-*/spec.md`, the claims index.

## Complexity Tracking

None.
