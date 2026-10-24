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

## T01 - the run record says what ran, why, and where the time went (FR-002, FR-005)

### T01 Approach (checklist part A)

1. **The goal, in the world.** Anyone reading a gate's run record can tell whether it ran everything, why, how many tests it selected, and how long each phase took - without reconstructing it from a log.
2. **The constraints.** The record is written once per gate run by `LOGRUN`; it must not slow the gate or fail it when a figure is missing.
3. **Where each comes from.** O: the GM's items 2 and 5 (request.md).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the run record held seconds and mode but no reason, no selection count and no phases, and the phase table had to be rebuilt by hand.
5. **The order.** Phase marks first (runstats), then the plan fields, then the record.
6. **The exits.** (a) read the log after each run - not taken, the record is what tools read; (b) the fields - taken.
7. **The search smell.** None.
8. **The budget.** 60 min with its landing.
9. **Done, measured.** Unit tests of `runstats.py phase`/`end` and of the record's new fields (red without); a real gate run's record carries `plan_mode`, `plan_reason`, `selected` and `phases`.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** `runstats.py phase <dir> <name> <seconds>` appends a phase mark; `end` returns them as `phases: {name: seconds}`. The `done` recipe marks the preflight, each of static, format and typecheck, the reference step, the hooks suite and the test phase; the `test` recipe marks `pytest` and `floors` (merge, carry, the reports, save-baseline) inside it. Rendering: none.
- **D2** `LOGRUN` adds `plan_mode`, `plan_reason` and `selected` from `<baseline>/plan.json` and the selection plugin's count of tests kept (written beside it by `selection.py` on the controller), each left out where its source is absent. Rendering: none.

## T02 - a tooling change no longer runs everything (FR-001)

### T02 Approach (checklist part A)

1. **The goal, in the world.** A landing after a tooling change runs the tests its change reaches, plus the tests that read the changed tooling - not the whole suite.
2. **The constraints.** Never miss a test a change can break: the gate's machinery, the test run's configuration and the pinned lockfiles still plan `full`; the planner's other fallbacks are unchanged (spec FR-001).
3. **Where each comes from.** O: the GM's item 1; spec rounds 1-2 (the lockfiles ADDED; the word `scripts` read loosely; `gate-stamp.py` incremental).
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: the gate's planner asked offline on T26's baseline): T26's two engine files reached 143 of 11,890 baseline tests; the gate ran 10,376 because `scripts/` had moved the tooling hash.
5. **The order.** A planner hash of the gate's configuration beside the tooling hash; the `scripts/` readers; the plan; the tooling-test reuse on an incremental plan; tests.
6. **The exits.** (a) take `scripts/` out of `tooling_hash` - not taken: that hash decides when the tooling tests rerun, which stays; (b) a second hash for the planner - taken.
7. **The search smell.** None: one static scan of the test sources per plan.
8. **The budget.** 120 min with its landing.
9. **Done, measured.** SC-001's fixture cases (red without); `make test-file FILE=tests/tooling/ci/` green; T26's case re-asked of the planner plans incremental.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3** `state.gate_config_hash(root)`: a content hash over `l7r/diagram/ci/`, `l7r/diagram/pipeline/`, `l7r/diagram/switches.py`, `l7r/diagram/_invocation.py`, `tests/conftest.py`, `tests/_scope.py`, the pinned lockfiles (`requirements.txt`, `requirements-dev.txt`, `requirements-ci.txt`), `pyproject.toml`'s `[tool.pytest*]` and `[tool.coverage*]` tables, and the Makefile's TEST CONFIGURATION - the recipes of `test` and `test-full` and every variable definition they reference, closed over the variables those reference, with each `##` help comment stripped. `incremental.manifest` records it as `gate_config` and the `scripts/` tree's blob ids as `scripts`; `plan` plans `full` when `gate_config` moved (a baseline without the key counts as moved, once) and no longer on `tooling` alone. Rendering: none.
- **D4** Where `scripts` moved and `gate_config` did not, the plan adds to its changed test modules every test module under `tests/tooling/` and `tests/hooks/`, and every other test module whose source - or the source of a module under `tests/` it imports, transitively - contains the substring `scripts` (spec FR-001 read loosely; a substring, so `tests._scripts` and `"scripts"` both match - spec round 3's aside), and carries `reuse_tooling: true`; `_test_deps.gate_full` becomes `gate_reuses`, true on a full plan or one carrying `reuse_tooling`, so the tooling tests whose recorded reads are unchanged are deselected as on a full plan (their baseline coverage is kept by the merge). Rendering: none.

## T03 - the landing waits only on what can refuse it (FR-003, FR-004)

### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing returns once its work is on main, having waited only on the checks that can refuse it.
2. **The constraints.** The fixed seeds and pinned rows still refuse a regressed seed beside the gate; the fresh block's record still reaches `make cohort-seeds`; an uncovered added line still refuses the landing.
3. **Where each comes from.** O: the GM's items 3 and 4.
4. **Do they describe the world here?** Yes, observed 2026-10-24 (method: T26's landing log): the cohort finished 1.4 min after the gate; `cover-changed` took 48 s before the gate started.
5. **The order.** The cohort split (fixed beside the gate, fresh after the push); `cover-changed` beside the gate with a stop; the cohort gate's record shape.
6. **The exits.** (a) drop the fresh block - not taken, its trend is read; (b) after the push - taken.
7. **The search smell.** None.
8. **The budget.** 90 min with its landing.
9. **Done, measured.** Unit tests: the fresh block started after a push and not before; a failing `cover-changed` stops the gate and refuses; `cohort_gate.check` takes a landing record with no fresh block. A landing's log shows both.
10. **Before moving a constant.** None moves.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** `make cohort-landing` rolls `N=48 FRESH=0` beside the gate; after a successful push, `land.py` starts `make cohort N=0 FRESH=48` detached (its own process group, its log under the git directory), one at a time (a lock file), and the landing returns; its record is committed by the cohort as today and goes out with the next push. `cohort_gate.check` asks the landing record for the fixed seeds and pinned rows only (`landing_shaped(..., need_fresh=False)`). Rendering: none.
- **D6** `land.py` starts `cover_changed.py` beside `make done` (both in their own process groups); when it exits non-zero the gate's group is stopped (as `make land-stop` does) and the landing refused with its lines; `cheap_refusals` no longer runs it. Rendering: none.

## T04 - the gate's costs, measured (FR-007)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The cutoff and the refresh rule rest on what a gate run costs here, not on a guess.
2. **The constraints.** Real landings' records (T01's fields), at least three incremental and two full; the host's load at each end is recorded beside each (runstats), and a reading under heavy load is said so.
3. **Where each comes from.** O: the GM's item 6 ("first measure the fixed cost and the per-test cost on a few real landings").
4. **Do they describe the world here?** To be measured - this task is the measurement.
5. **The order.** Collect T01-T03's own landings' records and any other session's; fit seconds = fixed + per-test x selected for the test phase, the other phases read directly; and the merged baseline's drift: after the incremental runs, one full run's baseline compared with the merged one (contexts gained or lost).
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 45 min, mostly waiting on landings.
9. **Done, measured.** `research.md` holds the table of runs, the fit, and the drift count, each figure labeled with its date and method.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D7** The measurement is `scripts/measure/gate_costs.py`, reading `dev/run-log/` (T01's fields) and printing the table and the least-squares fit, and `incremental drift` (a subcommand comparing a full run's fresh baseline with the merged one it replaced). Rendering: none.

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

- **D8** To be decided on T04's numbers (amended into the spec as FR-006's rule, and reviewed). Rendering: none.

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

- **D9** The landing measured is the next engine landing after T05 (T05's own, or 405's next task). Rendering: none.
