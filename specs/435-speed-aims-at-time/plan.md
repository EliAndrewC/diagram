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
### T02 Approach (checklist part A)

1. **The goal, in the world.** The earlier call-cutting changes timed group by group, reverted where they bought no time (D6).
2. **The constraints.** FR-004, FR-006; SC-003.
3. **Where each comes from.** `spec.md`; the A/B of the engine before 417's lane against HEAD, measured 2026-10-27 (make perf
   SCALING=1 alternated in two worktrees).
4. **Do they describe the world here?** Yes: the eight commits FR-004's search returns.
5. **The order.** After T01 (it uses `make perf-ab`).
6. **The exits.** Green: every arm's evidence recorded, the reverted arms landed with no pool manifest moved and the cohort
   passing.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a measurement per arm.
8. **The budget.** One landing per feature's set of reverted arms.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each arm's time | `make perf-ab` against HEAD |
| no map moved | `make maps-moved` |
| no seed regressed | `make cohort-landing` |

### T03 Approach (checklist part A)

1. **The goal, in the world.** The three cheap fixes (D7), each its own task filed with `PERF=1`, its checklist answered.
2. **The constraints.** FR-005, FR-006; SC-004.
3. **Where each comes from.** `specs/417-all-seeds-pass/research/t57-analysis.md` items 2, 3, 1.
4. **Do they describe the world here?** Re-measured first (`make phase-calls`, `make perf-profile`) on the engine T02 leaves.
5. **The order.** After T02.
6. **The exits.** Green: each fix landed with its calls and time evidence, the cohort passing.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Each fix removes a search: a screen before a full test, a result kept.
8. **The budget.** One landing per fix.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** Its research claim read first.
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| each fix | `make phase-calls`, `make perf-ab` against its parent |
| the maps | `make maps-moved`, the cohort |

### T04 Approach (checklist part A)

1. **The goal, in the world.** The new numbers for the GM (D8).
2. **The constraints.** FR-008; SC-006.
3. **Where each comes from.** `request.md` message 3.
4. **Do they describe the world here?** Yes.
5. **The order.** Last.
6. **The exits.** Green: `report-numbers.md` written with both comparisons.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the calls | `make phase-calls` |
| the time | `make perf-ab` |

## Project Structure

- `docs/performance-checklist.md` (new); `scripts/task-add.py`, `Makefile` (`perf-ab`, `task-add PERF=`).
- `l7r/diagram/tools/perf_ab.py` (new); `l7r/diagram/tools/perf_snapshot.py` (the counting pass skippable).
- `.claude/agents/perf-audit.md`; `.specify/memory/constitution.md`; `l7r/diagram/CLAUDE.md`; `dev/performance.md`;
  `docs/guards.md`.
- The reverted engine files (T02), the fixes' modules (T03).

## Complexity Tracking

None.

### T05 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T05 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

