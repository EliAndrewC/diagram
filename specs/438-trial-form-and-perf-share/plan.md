# Implementation Plan: the trial form and perf-share

**Branch**: `438-trial-form-and-perf-share` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md` (FAITHFUL, round 2), `request.md`.

## Summary

`make perf-share` reads a module's share of each stage's time from the kept raw profiles (feature 437's two ad-hoc scripts,
as a command); `make trial` starts a trial brief that pushes its evidence unreviewed while it runs and the engine is
unchanged on net, and is reviewed once when it is done.

## Technical Context

**Language/Version**: Python 3.14, bash. **Testing**: pytest (`tests/tools/test_perf_share.py`, `tests/tools/test_perf_profile.py`,
`tests/test_trial_start.py`); `make hooks-test` (`tests/hooks/test-review-gate.sh`). **Project Type**: tooling.

## Performance bookends

None: no engine code a roll runs changes (`perf_profile` names its raw file; `perf_share` reads profiles).

## Constitution Check

- **I-V, VII-IX, XI**: N/A - no UI, no pool content, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - the tests named above, `make quick`, `make hooks-test`, `make cover-changed`, the
  landing's `make done`; `make perf-share PROFILES=<437's four>` run for real.
- **X. Python Discipline**: PASS - 100% coverage on `perf_share.py` and the changed `perf_profile.py`.
- **XVI. Do the literal thing**: PASS - the review gate's exemption is the one the spec states (not Done, no net engine change).
- **The guard doctrine**: the review gate's refusal text names the trial's two conditions; its test proves the exemption and
  both refusals.

## Decisions

**D1 - perf-share reads kept profiles.** `tools/perf_share.py`: per stage, the files `--profiles` names (matched to the stage
by its `-<stage>.prof` suffix), else the newest `dev/perf-raw/*-seed<S>-hh<H>-<stage>.prof`, else `perf_profile.profile_stage`
then (said so). Per stage: total, the module's self time and share, the 8 largest self times, the module's callers by the
module's cumulative time under them (a call from the module to itself is not a caller). The summary line: the module's share
across the stages read, "an upper bound" (cProfile's inflation).

**D2 - The size in the raw name.** `perf_profile.profile_stage` names its raw profile `<stamp>-seed<S>-hh<H>-<stage>.prof`,
H the roll's household count (the reference's 15 when none is given).

**D3 - `make trial`.** `scripts/trial-start.py <slug>`: runs `scripts/claim-feature.py` (the same lock and numbering as `make
claim`), then writes `spec.md` from `.specify/templates/trial-template.md` (`[DATE]` and `[N]` filled) and a `request.md`
stub; prints the two `export` lines as `make claim` does.

**D4 - The review gate's trial rule.** In `scripts/gates/review-gate.sh`'s spec loop: a spec carrying `**Form**: trial` whose
status does not open `Done` is passed without a verdict when the push's delta changes nothing under `l7r/` on net (`git diff
--quiet $RANGE -- l7r/`); otherwise it owes the verdict as any spec. The refusal names the two conditions.

**D5 - Docs.** `docs/spec-kit-and-reviews.md` "The trial form"; one line in the root `CLAUDE.md`'s development-workflow list;
`docs/guards.md` the review gate's trial rule.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** A module's share of each stage's time, read in one command from the profiles already kept.
2. **The constraints.** FR-001, FR-002, FR-007; D1, D2.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: feature 437's `research/share.md`.
4. **Do they describe the world here?** Yes: `dev/perf-raw/` holds the kept profiles; `profile_stage` writes them.
5. **The order.** First.
6. **The exits.** Green: landed with its tests and a real run on 437's profiles. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make perf-share PROFILES=<437's four>` prints 437's shares (3.5% across the four, measured 2026-10-27 (feature 437, research/share.md)).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the reading | `tests/tools/test_perf_share.py` on a synthetic profile |
| the size in the name | `tests/tools/test_perf_profile.py` |

**Performance work?** No - it reads profiles; it changes no engine code a roll runs.

### T02 Approach (checklist part A)

1. **The goal, in the world.** A trial measured first and reviewed once, its evidence pushed as it is measured.
2. **The constraints.** FR-003, FR-004, FR-006, FR-007; D3-D5.
3. **Where each comes from.** G: the GM 2026-10-27; O: feature 437's three review rounds (`specs/437-array-geometry-trial/report-trial.md`).
4. **Do they describe the world here?** Yes: `review-gate.sh`'s spec loop is the one place a verdict is required at push.
5. **The order.** After T01.
6. **The exits.** Green: landed with the gate's hook tests and `trial-start`'s tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test` passes the gate's new cases; feature 439 is started with `make trial`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the brief written | `tests/test_trial_start.py` |
| the gate's rule | `tests/hooks/test-review-gate.sh` |

**Performance work?** No.

## Project Structure

- `l7r/diagram/tools/perf_share.py` (new), `l7r/diagram/tools/perf_profile.py`; `Makefile` (`perf-share`, `trial`).
- `scripts/trial-start.py` (new), `.specify/templates/trial-template.md` (new), `scripts/gates/review-gate.sh`.
- `docs/spec-kit-and-reviews.md`, `CLAUDE.md`, `docs/guards.md`; the tests named above.

## Complexity Tracking

None.
