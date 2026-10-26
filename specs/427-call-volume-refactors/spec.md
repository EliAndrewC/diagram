# Feature Specification: Call-volume refactors - remove the loops that multiply calls

**Feature Branch**: `427-call-volume-refactors` (no branch; work on `main` in the clone)

**Created**: 2026-10-26

**Status**: Draft - filed, not started. Held until the GM says to start (`request.md` 3: "once I'm in a place to actually work
on that, then we can do that"); the reason is the engine refactors in flight (`request.md` 2).

**Affects**: hamlet, performance, tooling

**Approved**: the GM, 2026-10-26, "I think I would like you to write all of this up as its own feature."

**Input**: `request.md` (the GM's three messages, verbatim).

## Why

A hamlet takes 6.8 s to generate at 20 households and 14.7 s at 40 (`research/measurements.md`). Six independent estimates
of a competent implementation of the same rules, on the same stack, came to 1-2 s and 2-4 s (`research/estimate-exercise.md`). (Observed 2026-10-26, method: `make perf LABEL=adhoc SCALING=1`
on commit fd707b608, snapshot `dev/perf-log/20261026T114000Z-adhoc-diagram-performance.json`; the estimates are agents'
estimates, not measurements.)

The gap is not any slow function. It is about 62.8 million Python calls at 40 households (24.1M at 20), at 0.2-0.45 µs each,
produced by loops that multiply (observed 2026-10-26, method: `make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=<20|40>`
over all 23 stages, the summaries `dev/perf-log/20261026T1159*Z-profile-adhoc-seed39-*.txt` and `20261026T1200*Z-...`, the
survey `research/fanout-2026-10-26.txt`; seconds per call = the snapshot's stage seconds over these counts):

- recomputing what did not change;
- checking each candidate against its neighbors one pure-Python call per pair;
- caches whose keys cost a scan;
- point-at-a-time reads beside existing batch versions.

Past tuning sessions found small gains because a time-sorted profile shows no hotspot.

## Where each piece is (load only what the task needs)

| file | holds |
|---|---|
| `request.md` | the GM's words |
| `working-notes.md` | what to do before the first change, the rules the work is held to, lessons from the exercise |
| `tooling-perf-fanout.md` | the `make perf-fanout` target: design, the reference chain-walk code, its coverage and landing rules, a refinement for the GM |
| `research/measurements.md` | baseline wall times per stage and size, call totals per stage, caveats, how to re-measure |
| `research/estimate-exercise.md` | the six-agent first-principles exercise: method, estimates, diagnoses, the corrected wells prediction |
| `research/hotspots-recompute.md` | R1-R7: wells re-ranking (the cubic term), crop boxes, `free_seats`, `household_reach`, `free_components`, field `_falls`, field settle |
| `research/hotspots-pairwise.md` | the per-pair scalar checks by stage: lane web and law, homestead seating, well treads and admission, water, ground cover |
| `research/hotspots-cheap-wins.md` | C1-C6: `ring_index` and `pts_key` cache keys, `Region.taken`, `seg_dists`, `CanopyArea`, record reads |
| `research/fanout-2026-10-26.txt` | the raw survey output: every chain with its counts at 20 and 40 households |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The call-volume survey is a command (Priority: P1)

A session asks "which functions are called millions of times, and from which loop?" and gets the answer from one make
target. That target is also how every later story proves its multiplier is gone.

**Independent Test**: `make perf-fanout` on the current engine reproduces the chains in `research/fanout-2026-10-26.txt`
(counts may differ if the engine moved). Its tests reach 100% of the new tool.

### User Story 2 - Batches before rewrites: the contained wins (Priority: P2)

The cheap wins in `research/hotspots-cheap-wins.md` (C1-C3, C5) and the single-site recomputations in
`research/hotspots-recompute.md` (R2, R3, R5, R6) are removed, each with its chain's count shown falling.

**Independent Test**: each named chain's leaf count falls by at least 10x in `make perf-fanout` at 40 households. The cohort
and the research claims hold.

### User Story 3 - The wells without the cubic term (Priority: P2)

The shared wells are seated with kept state (R1): a candidate's score is one array operation, and only the winner is
admitted.

**Independent Test**: at 40 households the lane_wells chain falls from about 2.19M inner calls to under 100k. The slowest
seed's lane_wells time falls below 0.5 s. (The 2.19M was observed 2026-10-26, method: `make perf-profile SEED=39
STAGE=lane_wells HOUSEHOLDS=40`; both thresholds are a GUESS at what a kept-state solve reaches.)

### User Story 4 - Pairwise checks in bulk (Priority: P3)

The families in `research/hotspots-pairwise.md` are converted one at a time (lanes, homestead parts, cover). Each asks its
pair questions per candidate set through an STRtree or numpy broadcast, not one Python call per pair. The homestead reach
test (R4) and the field settle (R7) go with their families.

**Independent Test**: per family, its chains' counts fall at least 10x. Total calls at 20 households fall below 2.5M (SC-002).

### Edge Cases

- A refactor changes a map: allowed for speed (GM 2026-10-18), judged by `make cohort-landing` and the research claims.
- A chain is seed-dependent (lane_wells is zero on some seeds below about 20 households): size and verify it on more than one
  seed.
- 40 households refuses on seed 4 (`WebRefused`, `research/measurements.md`). This feature does not own that failure, but any
  web change is checked against that seed.

## Requirements *(mandatory)*

- **FR-001**: `make perf-fanout` exists as `tooling-perf-fanout.md` describes, lands as tooling on its own, and owes 100%
  coverage.
- **FR-002**: Before any engine change, the survey is re-run on the then-current engine and the task list is scoped
  against its output, not against `research/` (`working-notes.md`).
- **FR-003**: Each engine task names the chain(s) it removes, with before and after counts from `make perf-fanout`.
- **FR-004**: No research claim is broken. A claim on rewritten code is re-checked through the claims round.
- **FR-005**: Timing is reported as bookends (`make perf LABEL=427-start|end SCALING=1`) and a seed-by-seed A/B against
  HEAD, never from medians or cProfile seconds alone.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): the survey re-runs in one command, and its output lists every chain of 50k+ calls with its
  anchor.
- **SC-002** (FR-003, US2-US4): total Python calls fall by an order of magnitude (the GM: "literal order of magnitude
  improvements", `request.md` 1): from 24.1M to under 2.5M at 20 households, and from 62.8M to under 6.5M at 40. (The
  baselines were observed 2026-10-26, method: `make perf-profile SEED=39` over all 23 stages at each size; the targets are
  the baselines divided by ten, rounded up.)
- **SC-003** (FR-005): at 40 households, every stage takes under a second on every seed (the GM: "I would expect every
  single stage of our Hamlet generation to take a fraction of a second. even when we artificially inflate the number of
  homesteads ... such as 40", `request.md` 1). The whole roll lands near the first-principles estimate of 1-2 s at 20
  households and 2-4 s at 40 (`research/estimate-exercise.md`; agents' estimates, not research figures), against 6.8 s and
  14.7 s today (observed 2026-10-26, method: `make perf LABEL=adhoc SCALING=1` on commit fd707b608). An intermediate
  checkpoint (for example a 20-household median under 3 s) may be reported along the way, but it does not close the
  feature.
- **SC-004** (FR-004): `make cohort-landing` shows no seed regressed, and the claims round is clean.

## Out of scope

- Moving the engine off Python (the GM: "without changing our fundamental technology stack away from Python"). The
  session's reading, for the GM to confirm at planning: shapely and numpy stay too, as the tools the refactors move toward.
- The 40-household `WebRefused` correctness failure (a lane-law matter), beyond checking against it.
- A clean-room prototype placer (the GM deferred it, `request.md` 1).

## Review history

- 2026-10-26, spec-fidelity MODE 2, round 1: NOT-REVIEWABLE. Measured figures carried no observed-date-and-method label.
  Labels added; spec-lint clean.
- 2026-10-26, spec-fidelity MODE 2, round 2: CHANGES REQUIRED, 3 items:
  - SC-002 and SC-003 set success below the GM's stated expectation. SC-003 now requires every stage under a second at
    40 households, and SC-002 a tenfold cut in calls; an intermediate checkpoint does not close the feature.
  - The Status line used the refactors landing as the start trigger. It now waits for the GM's word, with the refactors
    as the reason.
  - Out of scope attributed shapely and numpy to the GM. That is now marked as the session's reading, for the GM to confirm.
  - Aside applied: folding in feature 373 needs the GM's approval (`working-notes.md`).
- 2026-10-26, spec-fidelity-verify MODE 3, round 2: CHANGES REQUIRED, 2 items. US4's test still said 8M against SC-002's
  2.5M; it now reads 2.5M (SC-002). SC-002's note now says "rounded up". Items 2 and 3 of round 2 were confirmed
  resolved.
- 2026-10-26, spec-fidelity-verify MODE 3, round 3: FAITHFUL. (The tooling counts the rounds 1-3 after the NOT-REVIEWABLE
  dispatch, which did not count; the two "round 2" labels above are the same review's rounds 1 and 2.)
