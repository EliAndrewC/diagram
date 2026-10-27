# Feature Specification: Speed work aims at time

**Feature Branch**: `435-speed-aims-at-time` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, performance, hamlet

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

### User Story 3 - The changes that cut calls without improving time are reverted (Priority: P1)

The earlier call-cutting changes - every one the search below finds, in features 427 and 417 - are classed removes-work or
moves-work, the class deciding where to look first; a change is reverted where its time evidence shows no gain and its growth
with the settlement's size does not argue for it, and kept where either does.

**Acceptance Scenarios**:

1. **Given** the candidates, **Then** each is classed (the class ordering the work, moves-work first), its hunks grouped by
   the commit that made them, and each group's revert timed against the current engine (`make perf-ab`, best of N, the spread
   shown); a group is kept where its revert costs time or where how its work grows with the settlement's size argues for it,
   and reverted otherwise, the evidence recorded either way.

### User Story 4 - The three cheap fixes (Priority: P2)

The three changes T57 ranked first - the notice board's seats screened before the full house-fit test, the homestead bundle's
geometry built once and placed, the wells' seats screened by a feasibility mask before the overlap admission - each planned
with the checklist, each removing work, each with its time evidence.

### User Story 5 - New numbers to decide what is next (Priority: P1)

When the reverts and the three cheap fixes have landed, one report sets the per-stage calls at 40 households (`make
phase-calls`) beside feature 417 T57's, and the time of the engine before this feature against the engine after it (`make
perf-ab`, best of N with its spread), for the GM to decide what performance work comes next.

## Order

The GM's order (`request.md`, message 3): the checklist and its tools first, then the reverts, then the three cheap fixes, then
the closing report.

## Edge Cases

- A revert raises the call count past the call-count tripwire's line: that is the tripwire seeing an intended reversal; it is
  put to the round arbiter with the GM's words, not escaped.
- A timing comparison that cannot separate two arms is reported as inside the spread, not as a gain or a loss.

## Requirements *(mandatory)*

- **FR-001**: A performance checklist (`docs/performance-checklist.md`) holds the questions above and the sensibility, worded
  as prompts; nothing refuses on them. It reaches every task: the task-add plan template's approach items carry one line
  asking whether the task is performance work, and `make task-add ... PERF=1` writes the checklist's questions into its plan
  section.
- **FR-002**: `make perf-ab A=<commit> B=<commit> [N=] [SEEDS=] [SIZES=]` times two engines in detached worktrees,
  alternating, and prints per seed and size each arm's best time, spread and calls; it gates nothing.
- **FR-003**: The perf-audit agent's contract names an occasion: a performance task's diff read for removes-work or
  moves-work, with its time evidence; its finding informs, it does not gate.
- **FR-004**: The candidates are the call-cutting changes of features 427 and 417 that `git log --oneline -i -E
  --since=2026-10-25 --grep='inline|without (builtin |inner )?calls|fewer builtin|no abs|plain loops|by comparison|as
  conditionals|written in|written out' -- 'l7r/**'` finds (427 T07, T08, T09, T12; 417 T54, T63, T64, T65), read hunk by hunk
  and each classed removes-work or moves-work. The class orders the work, moves-work first, and excludes no hunk from timing. The hunks are
  grouped by the commit that made them; each group's revert is timed against the current engine (`make perf-ab`, best of N,
  the spread shown); a group is kept where its time shows a gain or where how its work grows with the settlement's size argues
  for it, and reverted otherwise, the evidence recorded either way. Maps unmoved by a revert stay unmoved.
- **FR-005**: The three cheap fixes are built, each planned with the checklist and its time evidence reported.
- **FR-006**: No timing gates anything anywhere: no requirement, test, guard or exit of this feature refuses on a time.
- **FR-007**: The project's standing guidance says time is the goal and calls the measure, pointing at the checklist, wherever
  `grep -rln "call counts" .specify/memory/constitution.md docs/ dev/performance.md l7r/diagram/CLAUDE.md .claude/agents/`
  finds the rule stated: the constitution's performance principle, `l7r/diagram/CLAUDE.md`, `dev/performance.md`,
  `docs/guards.md` and the perf-audit agent; the gate's own wording (calls gated, timings recorded) stays as it is, so
  `docs/make-targets.html` (generated from the Makefile's `perf-gate` and `perf-review` help lines, the gate's own wording) is
  left as it is.
- **FR-008**: A closing report (`specs/435-speed-aims-at-time/report-numbers.md`) gives the per-stage calls at 40 households
  after this feature beside feature 417 T57's, and the time A/B of the engine before this feature against after it.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-007): A performance task filed after this feature carries the checklist in its plan section.
- **SC-002** (FR-002, FR-006): `make perf-ab` prints both arms' best, spread and calls per seed and size, and exits 0 whatever
  the times.
- **SC-003** (FR-004): Every candidate hunk is classed; each commit group's A/B is recorded with its spread and its decision;
  no pool manifest moves on a revert.
- **SC-004** (FR-005): The three cheap fixes land, each with its calls and time evidence before and after, the cohort passing.
- **SC-005** (FR-003, FR-006): No guard, test or exit added by this feature refuses on a timing.
- **SC-006** (FR-007, FR-008): The constitution and the guidance files name time as the goal; the closing report exists with
  both comparisons.

## Assumptions

- The call-count tripwire (feature 427) stays as it is; this feature adds nothing to what it gates.
- "The three cheat fixes" are T57's items 2, 3 and 1 (`specs/417-all-seeds-pass/research/t57-analysis.md`).

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - the revert's search space stopped at 417; the deciding test
  was the change's type, not its time; the constitution missing from FR-007; no mechanism bringing the checklist to a task; no
  closing report, the GM's order unstated.
- 2026-10-27, round 2 (spec-fidelity-verify): CHANGES REQUIRED - FR-004 grouped by feature and filtered by class against User
  Story 3; FR-007's grep found a sixth file.
- 2026-10-27, round 3 (spec-fidelity-verify): CHANGES REQUIRED - the argument that the revert covers moves-work only did not
  hold: the GM defines the trap by its result, so every hunk is timed, the class only ordering the work.
- 2026-10-27, round 4 (spec-fidelity-verify): FAITHFUL.
