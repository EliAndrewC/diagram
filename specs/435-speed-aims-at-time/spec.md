# Feature Specification: Speed work aims at time

**Feature Branch**: `435-speed-aims-at-time` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, engine (the reverts and the three cheap fixes)

**Approved**: the GM, 2026-10-27, "Okay, in that case, yes."

**Input**: `request.md` (the GM's three messages, verbatim).

## Why

Feature 417's speed lane was gated on Python call counts (feature 427's rule) and cut them while time barely moved: an
alternating best-of-3 A/B of the engine before the lane (c9f3db460) against HEAD measured calls -38% to -44% and time 0% to
-6% at 40 households, inside a run-to-run spread of up to 1.2 s, and calls -32% to -35% with time -10% to -16% at 20
households (measured 2026-10-27, `make perf LABEL=ab-<arm>-<n> SCALING=1` alternated in two detached worktrees). Some of
the lane's changes only moved work - helpers inlined, builtins replaced by inline code - which lowers the count without
lowering the time: the trap the GM names. The goal of performance work is less time; the count is its deterministic
measure, never the goal, and time is never a gate.

## The sensibility (the GM's, restated; every requirement below serves it)

- **Time is the goal of every performance change, and never a gate.** No refusal, no pass or fail on a timing, no threshold
  of time up or down - not at a push, not at a task's close. A timing depends on load and on which core runs it, and waiting
  for a quiet host to measure costs the time the work is meant to save.
- **Call counts are the deterministic measure.** They find where work multiplies, and the existing call-count tripwire keeps
  catching work creeping back.
- **Time is evidence read with judgment.** Comparisons taken under similar conditions where convenient (before and after
  alternated, best of a few, the spread shown), read across the totality of what was done: time falling with calls confirms;
  calls falling while time does not, across comparisons, is a finding that changes what is tried next.
- **The checklist is a memory aid, not the goal.** Its items are the questions a good performance change answers; answering
  one honestly is what it asks, never a box ticked, and no item makes fewer calls a goal in itself.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A performance change is planned against time, with a checklist that keeps the steps (Priority: P1)

A session planning a performance change answers the performance checklist in its plan: where the time goes, whether the
change removes work or only moves it, what it expects to save, how the work grows with the settlement's size, and what the
before and after evidence showed and under what conditions.

**Acceptance Scenarios**:

1. **Given** a performance task filed with `make task-add`, **Then** its plan section carries the checklist's questions
   beside the existing approach items, as prompts, with no guard refusing on their answers.
2. **Given** a change that only moves work (a helper inlined, functions merged, a builtin replaced by inline code), **Then**
   the checklist names it so, and the plan says what time evidence would justify it.

### User Story 2 - One command gives the time evidence (Priority: P1)

`make perf-ab` compares two commits of the engine: alternating runs, best of N and the spread for each, calls beside the
times, so the evidence is cheap to take.

**Acceptance Scenarios**:

1. **Given** two commits, **When** `make perf-ab` runs, **Then** it prints per seed and size the best time and spread of each
   arm, alternated, and the calls of each, and refuses nothing.

### User Story 3 - The changes that only moved work are reverted (Priority: P1)

Feature 417's speed changes that only moved work (inlinings and builtin replacements) are reverted where the time evidence
shows they bought nothing measurable, keeping every change that removed work.

**Acceptance Scenarios**:

1. **Given** 417's speed commits, **Then** each change is classed removes-work or moves-work, and the moves-work set is reverted
   where the reverted engine's time sits inside the current engine's spread, with the evidence recorded.

### User Story 4 - The three cheap fixes (Priority: P2)

The three changes T57 ranked first - the notice board's seats screened before the full house-fit test, the homestead bundle's
geometry built once and placed, the wells' seats screened by a feasibility mask before the overlap admission - each planned
with the checklist, each removing work, each with its time evidence.

## Edge Cases

- A revert raises the call count past the call-count tripwire's line: that is the tripwire seeing an intended reversal; it is
  put to the round arbiter with the GM's words, not escaped.
- A timing comparison that cannot separate two arms is reported as inside the spread, not as a gain or a loss.

## Requirements *(mandatory)*

- **FR-001**: A performance checklist (`docs/performance-checklist.md`) holds the questions above and the sensibility, worded
  as prompts; the task-add plan template carries them for a performance task; nothing refuses on them.
- **FR-002**: `make perf-ab A=<commit> B=<commit> [N=] [SEEDS=] [SIZES=]` times two engines in detached worktrees,
  alternating, and prints per seed and size each arm's best time, spread and calls; it gates nothing.
- **FR-003**: The perf-audit agent's contract names an occasion: a performance task's diff read for removes-work or
  moves-work, with its time evidence; its finding informs, it does not gate.
- **FR-004**: Feature 417's moves-work changes are reverted where the time evidence shows no measurable cost of reverting;
  every removes-work change is kept; maps unmoved by the revert stay unmoved.
- **FR-005**: The three cheap fixes are built, each planned with the checklist and its time evidence reported.
- **FR-006**: No timing gates anything anywhere: no requirement, test, guard or exit of this feature refuses on a time.
- **FR-007**: The project's standing guidance (`l7r/diagram/CLAUDE.md`'s performance rules, `dev/performance.md`) says time is
  the goal and calls the measure, pointing at the checklist.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-007): A performance task filed after this feature carries the checklist in its plan section.
- **SC-002** (FR-002, FR-006): `make perf-ab` prints both arms' best, spread and calls per seed and size, and exits 0 whatever
  the times.
- **SC-003** (FR-004): Each 417 speed change is classed; the reverted set's A/B is recorded with its spread; no pool manifest
  moves on the revert.
- **SC-004** (FR-005): The three cheap fixes land, each with its calls and time evidence before and after, the cohort passing.
- **SC-005** (FR-003, FR-006): No guard, test or exit added by this feature refuses on a timing.

## Assumptions

- The call-count tripwire (feature 427) stays as it is; this feature adds nothing to what it gates.
- "The three cheat fixes" are T57's items 2, 3 and 1 (`specs/417-all-seeds-pass/research/t57-analysis.md`).
