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

**Target Platform**: the dev container (Linux), its containers sharing a 10 GB memory cap (observed 2026-10-26, method: the laptop memory watch's notices)

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
- for every stage holding a non-builtin function called `HOT` times or more at the larger size - no floor on the stage's
  own total, so a 100,000-call chain in a small stage is listed (SC-001: every chain of 50,000 calls or more; the design note's
  300,000-call stage floor is dropped) - it prints the multiplier chains by the reference walk, kept as
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

**D2 - call counts in the snapshot (FR-006, US5; `call-count-flag.md` "How to count cheaply").** `make perf` gains, after its
timed rolls, a COUNTING PASS: the same seeds (and, under `SCALING=1`, the same sizes) rolled again with a `sys.monitoring`
`PY_START` counter, each stage's Python-level calls recorded per seed as the row's `calls`, and the snapshot's `versions` (the
interpreter, numpy, shapely). A separate pass, because a per-call Python callback costs about what the calls it counts do: on the
timed roll it would distort the very timings the snapshot keeps. The counter takes a tool id of its own (`sys.monitoring` tool 3:
`gencache` holds `PROFILER_ID`, coverage `COVERAGE_ID`). The task measures the pass's overhead on the reference seeds and records
it beside the code; counts are taken only of Python functions, so shapely's and numpy's C work is not counted, as the design note
wants. A test rolls one stand-in stage twice and asserts equal counts (deterministic per seed).

**D3 - the call counts are what is watched (FR-006, US5, SC-005).** `perf_review.check`, which the push runs:
- compares the newest `-start`/`-end` pair's counts seed by seed and stage by stage; a pair on DIFFERENT versions (an interpreter
  or library upgrade between them) is not compared and REFUSES the push until a comparable pair exists - the `-start` re-taken on
  the current versions - or the round arbiter rules on the same `<NNN>-calls` subject; it never passes silently;
- the line: an increase over `CALLS_STAGE_LINE` (5% in any stage on any seed) or `CALLS_TOTAL_LINE` (2% in the total), both
  GUESS knobs of the design note, the reason beside them;
- an increase over the line with no round-arbiter accept REFUSES the push, naming `make arbiter-ask SUBJECT=<NNN>-calls
  WHY="..." ` with the stages, seeds and counts filled in; an accept recorded on that subject in the feature's `arbiter.jsonl`
  clears it; a decrease is printed and needs nothing;
- timings are printed for information beside the counts, and no rule acts on them: the band FLAG is retired (`perf_bands`
  keeps only what the printing needs).
`scripts/sync-with-main.sh` refuses on the check's exit as it now refuses on its failing to run. The round arbiter's agent file
gains the call-count case: `accept` when the increase is the cost of a rule the feature adds and is commensurate, `continue` to
optimize first, and to the GM when it judges the increase too large; `perf-audit.md` is repointed at a call-count
investigation. Constitution Principle VI is amended (MINOR) to say so, with `l7r/diagram/CLAUDE.md`, `dev/performance.md` and
`docs/guards.md`; the project memory "perf is a flag, never a gate" is updated when it lands.

**D4 - T04, the contained wins (FR-002, FR-003, US2).** Eight changes, each named by the chain it removes in the T01 survey
(`research/survey-t01.md`; counts at seed 39, 40 households, observed 2026-10-26, method: `make perf-fanout`) and each
proven by that chain's count falling at least tenfold (US2's test). Where a change computes the same values, a pool reroll
diffed against HEAD's manifests shows the maps unchanged (the GM's approach, `request.md` 5: identical manifests where that comes
free); where it may move a value by a rounding, the landing cohort judges it, as speed work may move maps (FR-007).
- **C5, `CanopyArea.add`** (1.05M `set.add` calls in the windbreak stage): the cells under a crown found by one numpy mask over
  its bounding box, written into the set by one `set.update` of integer cell keys - the same cells, so the same area.
- **R6, `_falls`** (514k `_Frame.to_uf` calls under `grid_lines`): the fall of every vertex as one comprehension over the frame's
  fall unit, the same expression `to_uf` computes, without a call per vertex.
- **R2, `crop_boxes`' house shelter** (122k generator steps over 21 calls): every clump against every house in one numpy distance
  comparison per grove, the same squared-distance test.
- **R3, `free_seats`' `_near_a_house`** (82k): the grid's points tested against every house in one numpy pass after the static
  ground's test, `np.hypot` for `math.hypot` (a last-place rounding may move a point on the half-pitch line: the cohort judges).
- **C3, `Region.taken`** (36k PIL `getpixel` calls in `close_belt_gaps`): the raster held as a numpy array, built on the first
  read after a paint and dropped when the region is painted again (where `_sat` is already dropped), and indexed.
- **C1, `clearance.ring_index`** (70.6k calls, 361k key steps) and **C2, `keeper.pts_key`** (41k keys, 229k steps): the key built
  by `tuple(map(tuple, pts))`, a walk in C with no Python frame per point, in place of a generator of `float()` pairs - a key equal
  to the old one wherever the old one was made, since an int coordinate and its float hash and compare alike. The content key
  stays: an identity key is the guess `dev/performance.md` forbids (the comment at `clearance.py`).
- **R5, `free_components`** (40 whole-grid labelings at 40 households, about 19 ms each, measured 2026-10-26 in
  `research/hotspots-recompute.md`): the run-length union-find replaced by `scipy.ndimage.label` with 4-connectivity, one C call -
  the same components (only their numbers differ, and `np.isin(labels, hit)` reads components, not numbers). scipy is installed
  in the container but not declared: it joins `requirements.in` and is locked by `pip-compile` with the numpy pin unchanged
  (FR-008: a library may change where an analysis shows it better).
Each change keeps its research claims; a claim on rewritten code is re-owed and checked through the claims round (FR-004).

## Task approaches

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T04 Approach (checklist part A)

1. **The goal, in the world.** The same hamlets, rolled with tenfold fewer Python calls in each chain T04 names.
2. **The constraints.** D4; FR-002, FR-003, FR-004, FR-007, FR-008, US2.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 1 and 5; `research/hotspots-cheap-wins.md`,
   `research/hotspots-recompute.md`, `research/survey-t01.md`.
4. **Do they describe the world here?** Yes: each chain is in the T01 survey of this engine.
5. **The order.** After T03 and the start bookend; before T05 (the wells).
6. **The exits.** Green: each named chain's count down tenfold in `make perf-fanout`, the cohort with no seed regressed. Red: what
   failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** Two landings: C1-C3, C5 and R6 first, then R2, R3 and R5 (the dependency).
9. **Done, measured.** Each chain's before and after count from `make perf-fanout`, and the pool reroll's manifest diff.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T05 Approach (checklist part A)

1. **The goal, in the world.** The same shared wells, seated without re-ranking every seat against every household per well.
2. **The constraints.** FR-003, FR-004, FR-007, US3; its decisions are written, and reviewed, when T05 starts, after T04.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 1 and 5; `research/hotspots-recompute.md` R1,
   `research/survey-t01.md`.
4. **Do they describe the world here?** Yes: lane_wells is the largest stage of the T01 survey of this engine (`research/survey-t01.md`).
5. **The order.** After T04, the order the GM approved (`request.md` 5).
6. **The exits.** Green: the lane_wells chain under US3's bound, the cohort with no seed regressed. Red: what failed recorded and
   the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None yet; to be answered with its decisions.
8. **The budget.** One landing.
9. **Done, measured.** US3's test: the lane_wells chain's count and the slowest seed's lane_wells time.
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

