# Implementation Plan: Call-volume refactors - remove the loops that multiply calls

**Branch**: `427-call-volume-refactors` (no branch; `main` in the clone) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/427-call-volume-refactors/spec.md` (reviewed FAITHFUL, the amendment's round 2)

## Summary

The work goes in the order the GM approved (`request.md` 5): the survey tool (T01), the call-count watch (US5), the cheap wins
and single-site recomputations (US2), the wells (US3), the pairwise families outside the lanes, and the lane web and law last,
after feature 417's lane conversions. FR-002 scopes every engine task against the survey's output on the engine as it then
stands, so this plan holds T01 now; each later task is filed with its own section once the survey has run.

## Technical Context

**Language/Version**: Python 3.14 (the container's)

**Primary Dependencies**: the standard library (`cProfile`, `pstats`, `concurrent.futures`); `tools/perf_profile.py`'s
`profile_stage`, the hamlet driver's `STAGES`

**Storage**: the report in `dev/perf-log/` (committed, as the snapshots are); the `.prof` files in gitignored `dev/perf-raw/`

**Testing**: pytest through `make test-file`; 100% coverage of the new module

**Target Platform**: the dev container (Linux), its containers sharing a 10 GB memory cap

**Project Type**: a by-hand diagnostic, never a gate

**Performance Goals**: SC-001 - one command lists every chain of 50,000 calls or more with its anchor

**Constraints**: the shared memory cap bounds how many stage profiles run at once

**Scale/Scope**: one module, one make target, one row of `tools/CLAUDE.md`

## Performance bookends

T01 changes no stage. The start bookend, `make perf LABEL=427-start SCALING=1`, is taken before the first engine task (T02 on).

## Constitution Check

- **I, II, III, IV, V, VII, VIII, IX**: N/A - no UI, pool content, SOURCE blocks or in-world writing.
- **VI. Verify Before Reporting Done**: PASS - T01's tests are red without it; its survey of the current engine is the measurement.
- **X. Python Discipline**: PASS - ruff, pyrefly, 100% coverage of `tools/perf_fanout.py` the day it lands; functions under the
  100-statement cap.
- **XII, XIX**: N/A - asserts nothing about the world and places nothing.
- **XIII. No Known Regressions**: PASS - no stage changes; the landing cohort it rides with is the gate's own.

## Decisions

**D1 - `make perf-fanout`, the call-volume survey (FR-001, SC-001).** A new `l7r/diagram/tools/perf_fanout.py`, as
`tooling-perf-fanout.md` designs it:
- `make perf-fanout [SEED=39] [HOUSEHOLDS="20 40"] [STAGES=all] [HOT=50000] [JOBS=3] [LABEL=adhoc]` profiles each (size, stage)
  pair once through `perf_profile.profile_stage`, the pairs side by side in `JOBS` worker processes;
- per stage it prints the total Python-level calls at each size and the growth exponent, `log2` of the larger size's calls
  over the smaller's;
- for each stage of 300,000 calls or more at the larger size it prints the multiplier chains by the reference walk, kept as
  written there (from each non-builtin function called `HOT` times or more, up the caller edge giving the most calls, a lambda
  or comprehension reached only through a builtin stepping to the `def` that encloses it, stopping at an ancestor called 300
  times or fewer), grouped by anchor;
- the fastest growers between the two sizes, functions of 20,000 calls or more at the larger;
- the report written to `dev/perf-log/<stamp>-fanout-<label>.txt`.
`JOBS` defaults to 3, a CONVENTION: the design note's five held on 2026-10-26 with the other containers near 4 GB, and the memory
watch has since read the shared cap at 9.1-9.3 of 10 GB. The analysis reads `pstats` data alone, so it is tested on synthetic
data; the profiling seam is stubbed, as `perf_profile`'s own tests stub it. A row in `tools/CLAUDE.md` names the question it
answers.
It lands through `make land`: a module under `l7r/` is engine by the push's own rule (`ci/delta.is_engine`), so the
`make land-tooling` route the design note names is not open to it.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** A session asks which functions run millions of times and from which loop, and one command
   answers.
2. **The constraints.** D1; FR-001, FR-002, SC-001.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 2 and 5; `tooling-perf-fanout.md`.
4. **Do they describe the world here?** Yes: the reference walk produced `research/fanout-2026-10-26.txt`.
5. **The order.** First: every engine task is scoped against its output (FR-002).
6. **The exits.** FR-008 green: landed with its fresh rate. Red: the failing seeds recorded and the task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35).
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D1; `make perf-fanout` on the current engine lists the chains, compared with
   `research/fanout-2026-10-26.txt`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

## Project Structure

### Documentation (this feature)

```text
specs/427-call-volume-refactors/
├── request.md, spec.md, working-notes.md, tooling-perf-fanout.md, call-count-flag.md, research/
├── plan.md            # this file
└── tasks.md
```

### Source Code (repository root)

```text
l7r/diagram/tools/perf_fanout.py      # new: the survey (D1)
tests/tools/test_perf_fanout.py       # new
Makefile                              # perf-fanout
l7r/diagram/tools/CLAUDE.md           # its row
```

## Complexity Tracking

None.
