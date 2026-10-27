# Implementation Plan: Speed work aims at time

**Branch**: `435-speed-aims-at-time` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md` (FAITHFUL, round 4), `request.md` (the GM's three messages, verbatim).

## Summary

In the GM's order: the performance checklist and its tools (a doc, a one-line question in every task's approach items,
`make task-add PERF=1`, `make perf-ab`, the perf-audit agent's occasion, the guidance in the constitution and the dev docs);
then the earlier call-cutting changes timed group by group and reverted where their time shows no gain and their growth with
size does not argue for them; then the three cheap fixes; then the closing report with the new numbers.

## Technical Context

**Language/Version**: Python 3.14. **Testing**: pytest under `make quick` / `make test-file`; the hook suites under
`make hooks-test` where a script changes. **Project Type**: tooling (`scripts/`, `l7r/diagram/tools/`, docs) and engine (the
reverts, the cheap fixes). **Single-artifact target**: the reference hamlet's spec at 40 households, seed 39 (`make
phase-calls`, `make perf-ab`).

## Performance bookends

`make perf LABEL=435-start SCALING=1` was taken on the unmodified engine before the first edit (2026-10-27); `-end` before the
last push. The bookends' call counts are gated as feature 427 gates them; their times are recorded and gate nothing (FR-006).
A revert raises calls on purpose: the call-count refusal it meets goes to the round arbiter with the GM's words (the spec's
Edge Cases), never escaped.

## Constitution Check

- **I, II**: N/A - no UI. **III, IV, V, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - each task's tests, `make quick`, `make cover-changed`, the landing's `make done`
  and cohort; the reverts and fixes each with `make maps-moved` and their `make perf-ab` evidence.
- **X. Python Discipline**: PASS - ruff, pyrefly, 100% coverage on every changed module; functions under 100 statements.
- **XIII. No Known Regressions**: PASS - each landing's cohort; a revert moves no map (T63-T65 and the 427 changes landed as
  value-preserving rewrites, so their reverts compute the same values).
- **The constitution itself (FR-007)**: its performance principle gains "time is the goal; calls the measure" beside the
  standing gate wording, which is unchanged.

## Decisions

**D1 - The checklist is prompts.** `docs/performance-checklist.md` states the sensibility and six questions (where the time
goes; removes or moves work; expected saving; growth with size; the before and after evidence and its conditions; maps and
research). No hook, test or exit refuses on an answer (FR-006).

**D2 - How it reaches a task.** `scripts/task-add.py` gains `--performance` (`make task-add ... PERF=1`), appending the six
questions to the task's plan section; every task's approach template gains one line: "Is this performance work? Then answer
docs/performance-checklist.md here (PERF=1)." - the memory aid present on every task.

**D3 - `make perf-ab`.** `tools/perf_ab.py`: two detached worktrees, `make perf SCALING=1` alternated N times (default 3), the
first run of each arm counted and the rest skipping the counting pass (`L7R_PERF_NO_COUNTS`, which `perf_snapshot` honors; an
older commit ignores it and counts, after its timed runs, so its times are taken as an arm's that skips); per size and seed
each arm's best time, spread and calls. It exits 0 always.

**D4 - The perf-audit agent's occasion.** Its contract gains "a performance task's diff, read for removes-work or moves-work
with its `make perf-ab` evidence"; the finding informs the task's report, it gates nothing.

**D5 - The guidance.** The constitution's performance principle, `l7r/diagram/CLAUDE.md`'s "Call counts are watched, timings
only recorded", `dev/performance.md`, `docs/guards.md`'s call-count row and the perf-audit agent's contract (beside its D4
occasion) each gain one sentence: time is the goal, calls the measure, the checklist the process; the gate's wording stays
(FR-007).

**D6 - The reverts.** The candidates are FR-004's eight commits, every hunk classed (the 417 ones read 2026-10-27: T63's
`conflicts(first=True)` removes work, its four inlinings move it; T64 and T65 move work in every hunk; 427 T07, T08, T09, T12
and 417 T54 classed hunk by hunk). Each commit is a group, its hunks split by class into a moves-work arm and a removes-work arm,
moves-work first; each arm's revert is a patch against HEAD, timed against HEAD by `make perf-ab` (best of N, the spread shown).
An arm is reverted where its revert costs no time beyond the spread and its growth with size does not argue for it, kept
otherwise; the evidence of every arm is recorded in `research.md`. An arm whose revert needs later code adapted is written with that code
adapted, and timed; a claim that an arm's revert cannot be written at all goes through `make arbiter-ask`.

**D7 - The three cheap fixes**, each a task answering the checklist (D1) in its plan: the notice board's route seats screened
by an index of the houses and yards before the full house-fit test; the homestead bundle's geometry built once per (form,
size, fixtures) and moved into place; the wells' seats screened by a feasibility mask before the overlap admission.

**D8 - The closing report** (`report-numbers.md`): `make phase-calls` after this feature beside T57's per-stage table, and
`make perf-ab` of the engine before this feature against after it.

## Task approaches

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-27 (feature 375 FR-044) -->
## Project Structure

- `docs/performance-checklist.md` (new); `scripts/task-add.py`, `Makefile` (`perf-ab`, `task-add PERF=`).
- `l7r/diagram/tools/perf_ab.py` (new); `l7r/diagram/tools/perf_snapshot.py` (the counting pass skippable).
- `.claude/agents/perf-audit.md`; `.specify/memory/constitution.md`; `l7r/diagram/CLAUDE.md`; `dev/performance.md`;
  `docs/guards.md`.
- The reverted engine files (T02), the fixes' modules (T03).

## Complexity Tracking

None.

### T05 (impl-drift's two notes outside T02's change, 2026-10-27: 0047's drawing page states the 48 ft reach (research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html) only for the sunny side, and records no choice for a privy with no seat in reach)

- **Approach**: 0047's drawing page gains what the code does, read 2026-10-27 in `fixture_seats.lay_fixtures`: every privy
  seat offered, the sunny side's and the four places' outward steps alike, is held to the privy's reach (`within_reach_of`,
  `PRIVY_SUN_MAX_FT`, far corner to the house's walls; research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html); a privy with no seat in reach raises `FixtureUnlaid`, so the bundle
  is not the household's and another seat or garden side is sought - never a privy past the reach, never a farm kept short
  of one. Each labeled (the reach a decision of this project's, the refusal a map drawing convention). Worked as a page
  session (`make page-session`); no engine code changes.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the page's two blocks | n/a (record only) | n/a | none (no code) | n/a |

### T05 Approach (checklist part A)

1. **The goal, in the world.** The record says how far from its house every privy stands, and what a farm whose privy
   cannot stand within that reach does.
2. **The constraints.** Constitution XII (every rendering decision labeled); `research/CLAUDE.md`.
3. **Where each comes from.** O: impl-drift's reply on T02's claims, 2026-10-27; the code read the same day.
4. **Do they describe the world here?** Yes: the code is the hamlet's, which every pool hamlet rolls.
5. **The order.** After T02 lands; independent of T03 and T04.
6. **The exits.** Green: the page's two blocks written and checked (`make record-owed`'s checks). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make claims-owed` names no privy claim of `lay_fixtures` against the changed page, or its round is IN-STEP.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** No.

### T06 (T57 item 1, re-measured on the engine T02 left: the wells' per-seat tests are the largest share of `seat_wells`)

- **Approach**: `seat_wells` asks three tests of each lattice seat one Python call at a time: the caller's verge test
  (`on_a_verge`'s `ok`, a `seg_dist` per lane leg near the seat), the wood floor (`ReservedSeats.disc_covers`) and, for the
  sort, the belt (`point_in_poly`). Each gains an array form asked of many seats at once - the verge through
  `primitives.seg_dists` against the legs, in blocks of rows; the wood floor against the reserved seats' points; the belt by
  the crossing test `SeatSweep.walls` already uses - and `SeatSweep` keeps each seat's verdict in an array beside its distance
  table (`ok`, keyed by the test, NaN until asked), so the stage's later `seat_wells` calls read it: the sweep is the index
  (`stage_kept`, keyed as now), the overlap admission `well_at` still asked of each seat ranked, in the same order. Profiled
  shares, measured 2026-10-27 (make perf-profile SEED=25 STAGE=lane_wells HOUSEHOLDS=40, dev/perf-log/20261027T174428Z-profile-adhoc-seed25-lane_wells.txt): `_seat_ok` 0.230 s, the belt 0.126 s, of the stage's 1.316 s under cProfile.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| verge, wood floor and belt as arrays on the sweep | the scalar tests kept as the arrays' reference in their tests | `make cohort-landing` | `make maps-moved` (a seat at a float boundary may flip; allowed under the GM's 2026-10-18 speed rule, held to 0196's claims) | n/a |

### T06 Approach (checklist part A)

1. **The goal, in the world.** The same wells, seated by the same rules, in less time.
2. **The constraints.** FR-005, FR-006; D7; research/questions/0196-communal-wells-ido.drawing.html (the verge, the cluster
   well off every lane); the wood floor (feature 287 W25).
3. **Where each comes from.** O: the lane_wells profile above; R: 0196; G: the GM 2026-10-27, "please proceed with the three cheat fixes" (dictated; "cheat" is "cheap").
4. **Do they describe the world here?** Re-measured on the engine T02 left (the profile above, and `make phase-calls`: lane
   wells 2,009,602 calls at seed 39, measured 2026-10-27 (make phase-calls)).
5. **The order.** After T02; before T07 (the notice board).
6. **The exits.** Green: landed with its `make perf-ab` evidence, the cohort passing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** A lattice of seats each tested alone - this screens it in bulk.
8. **The budget.** One landing.
9. **Done, measured.** `make phase-calls` and `make perf-ab A=<parent> B=HEAD` recorded in research/t06-evidence.md.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** Yes - its answers below.

### T06 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In `lane_wells`, 1.316 s under cProfile, measured 2026-10-27 (make perf-profile SEED=25 STAGE=lane_wells HOUSEHOLDS=40). Of it, `seat_wells`' per-seat tests (`_seat_ok`, the verge's `seg_dist` legs, `disc_covers`, `_in_belt`'s `point_in_poly`) take about 0.36 s, measured 2026-10-27 (make perf-profile SEED=25 STAGE=lane_wells HOUSEHOLDS=40). The overlap admission `well_at` takes 0.282 s and the sweep's distance table 0.148 s, measured 2026-10-27 (make perf-profile SEED=25 STAGE=lane_wells HOUSEHOLDS=40).
2. **Removes work, or only moves it?** Removes: a loop of Python calls moved into numpy (a loop into C), and each verdict kept
   on the sweep for the stage's later calls instead of asked again.
3. **What do you expect it to save, and why?** Most of the per-seat tests' 0.36 s profiled, measured 2026-10-27 (make perf-profile SEED=25 STAGE=lane_wells HOUSEHOLDS=40). Unprofiled that is about 0.1 s, a GUESS from cProfile's inflation (largest on call-dense Python like this) - about 1 to 2 percent of the 40-household roll, a GUESS from the profile's share; the stage itself perhaps a quarter faster, a GUESS.
4. **How does the work grow with the settlement?** The lattice grows with the cluster's area and the lane legs with the
   households, so the verge test grows faster than the wells placed; the arrays keep that product but take it out of the
   interpreter. It does not bend the curve; it lowers its constant.
5. **What did the before and after show, and under what conditions?** Recorded at landing: `make phase-calls` before and after,
   `make perf-ab A=<parent> B=HEAD` (best of 3, each arm's spread, the host's load).
6. **Did any map move, and does it still keep the research?** Recorded at landing: `make maps-moved` and the cohort; a moved
   well held to 0196's claims by the claims round.

### T07 (impl-drift's two notes outside T06's change, 2026-10-27: the belt claim's wording, and 0072's page silent on the rule)

- **Approach**: `seat_wells`' claim "not in the windbreak" says what the code does: a belt seat is ranked behind coverage (the
  worst walk's bucket) and the first well's look ahead, never refused; and 0072's drawing page
  (research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html) gains the maps' rule beside its
  block on a wellhead in a belt - among seats that serve the households alike, one outside the belt is taken first - labeled
  this project's choice. The page worked as a page session (`make page-session`); the claim a docstring edit.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the claim and the page's block | n/a (record and docstring only) | n/a | none (no code) | n/a |

### T07 Approach (checklist part A)

1. **The goal, in the world.** The record says how the maps keep a well out of the shelter belt, as the code does it.
2. **The constraints.** Constitution XII (every rendering decision labeled); `research/CLAUDE.md`.
3. **Where each comes from.** O: impl-drift's reply on T06's claims, 2026-10-27; the code read the same day.
4. **Do they describe the world here?** Yes: every hamlet with a belt seats its wells this way.
5. **The order.** After T06; independent of T08 and T04.
6. **The exits.** Green: the claim reworded and the page's block written and checked (`make record-owed`'s checks). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The claims round on `seat_wells` IN-STEP against the changed page.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** No.

### T08 (T57 item 2, re-measured on the engine T02 left: the notice board's route seats each run the full house-fit test)

- **Approach**: `_route_seats` asks `_fits` of every seat that clears the view, the placard, the beds and the water; `_fits`
  runs the field-bund, blocked and hard-ground tests before the indexed clearance from what stands (the houses, their yards
  and parts, `self.placed`, and the groves). That tail of `_fits` becomes its own method (`_clear_of_placed`), which `_fits`
  still calls last; `_route_seats` asks it first, as the screen, so a seat a house or a yard already refuses is never put
  through the rest. The screen is the same index (`_reach_index`, versioned by the registry) asked once more of each seat that
  passes it - a pure conjunction, so no seat's verdict changes. Profiled shares, measured 2026-10-27 (make perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40, dev/perf-log/20261027T174447Z-profile-adhoc-seed25-notice.txt): `_route_seats` 0.282 s and `_fits`
  0.117 s of the stage's 0.430 s under cProfile.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the placed clearance asked first | `_fits`' verdict unchanged on random seats (its test) | `make cohort-landing` | `make maps-moved` (none expected: the same conjunction) | n/a |

### T08 Approach (checklist part A)

1. **The goal, in the world.** The same notice board, sited by the same rules, in less time.
2. **The constraints.** FR-005, FR-006; D7; research/questions/0190-notice-boards-kosatsuba.drawing.html (the board's seat).
3. **Where each comes from.** O: the notice profile above; G: the GM 2026-10-27, "please proceed with the three cheat fixes" (dictated; "cheat" is "cheap").
4. **Do they describe the world here?** Re-measured on the engine T02 left (the profile above, and `make phase-calls`: notice 953,393 calls at seed 39, measured 2026-10-27 (make phase-calls)).
5. **The order.** After T06; before T04.
6. **The exits.** Green: landed with its `make perf-ab` evidence, the cohort passing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** A band of seats each put through the whole house-fit test - this screens it.
8. **The budget.** One landing.
9. **Done, measured.** `make phase-calls` and `make perf-ab A=<parent> B=HEAD` recorded in research/t08-evidence.md.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** Yes - its answers below.

### T08 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In `notice`, 0.430 s under cProfile, measured 2026-10-27 (make perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40, dev/perf-log/20261027T174447Z-profile-adhoc-seed25-notice.txt). Of it, `_route_seats` takes 0.282 s and its `_fits` 0.117 s, measured 2026-10-27 (make perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40, dev/perf-log/20261027T174447Z-profile-adhoc-seed25-notice.txt); `_fits`' field-bund test takes 0.052 s and its blocked test 0.032 s, measured 2026-10-27 (make perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40, dev/perf-log/20261027T174447Z-profile-adhoc-seed25-notice.txt).
2. **Removes work, or only moves it?** Removes: a cheap indexed screen before an expensive test, so a refused seat skips the bund, blocked and hard-ground tests.
3. **What do you expect it to save, and why?** At most the bund and blocked tests' 0.084 s profiled, measured 2026-10-27 (make perf-profile SEED=25 STAGE=notice HOUSEHOLDS=40, dev/perf-log/20261027T174447Z-profile-adhoc-seed25-notice.txt), for the seats a house refuses - about 0.03 s unprofiled, a GUESS from cProfile's inflation, under half a percent of the 40-household roll. The GM named the fix; the honest answer is that it is small.
4. **How does the work grow with the settlement?** The band's seats grow with the main ways' length and the houses beside them; the screen keeps that product and drops the dearer tests from most of it. It lowers the constant, not the curve.
5. **What did the before and after show, and under what conditions?** Recorded at landing: `make phase-calls` before and after, `make perf-ab A=<parent> B=HEAD` (best of 3, each arm's spread, the host's load; legs timed from their stages since T06).
6. **Did any map move, and does it still keep the research?** Recorded at landing: `make maps-moved` and the cohort; none expected, the conjunction being the same.

### T09 (impl-drift's note outside T08's change, 2026-10-27: 0190's page says a board clears no ground, while the fit keeps it out of a farmstead's grove)

- **Approach**: read what the code does and record it: `_fits`' clearance (`_clear_of_placed`) refuses a board seat within
  reach of a farmstead's own grove bands (`grove_rects`, recorded by `rolling/farmsteads.py` - the household's windbreak, not
  a lone tree or the commons' wood), which stands beside 0190's blocks "The board clears no ground" and "A board may stand
  under a tree's canopy" (research/questions/0190-notice-boards-kosatsuba.drawing.html). The page gains a block saying so -
  the board stands off a household's own grove as off its yard, labeled a map drawing convention - or, if a research pass
  finds a board posted in a farm's grove, the claim and the fit change instead (then a task of its own). Worked as a page
  session (`make page-session`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the page's block | n/a (record only) | n/a | none (no code) | n/a |

### T09 Approach (checklist part A)

1. **The goal, in the world.** The record says where a notice board may and may not stand among the farmsteads' groves.
2. **The constraints.** Constitution XII (every rendering decision labeled); `research/CLAUDE.md`.
3. **Where each comes from.** O: impl-drift's reply on T08's claims, 2026-10-27; the code read the same day.
4. **Do they describe the world here?** Yes: every dispersed and grove farm records its grove bands in `grove_rects`.
5. **The order.** After T08; independent of T05, T07 and T04.
6. **The exits.** Green: the page's block written and checked (`make record-owed`'s checks). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The claims round on `_route_seats` IN-STEP against the changed page.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** No.
