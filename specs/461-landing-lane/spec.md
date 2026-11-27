# Feature 461: the landing lane - a thin coordinator, builders that hand in ready work, and a merge queue of its own

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-27

**Status**: Draft - specified, not started ("go ahead and write the spec for the feature now, but don't actually get started on it just yet")

**Affects**: tooling

**Approved**: the GM, 2026-11-27, "Okay, yeah, go ahead and write the spec for the feature now, but don't actually get started on it just yet."

A feature he asked to be filed: "you should treat features that I have asked to be filed as automatic approval, and therefore you
should not ask in the future" (GM 2026-10-18).

**Input**: `request.md` (the GM's words, and the session's sketch he called "very sensible", recorded there as the session's);
`specs/449-rust-codebase/port-talk-orchestrator-research.md` (2026-11-26, the sources and four options) and
`port-talk-orchestrator-update.md` (2026-11-27, the night measured and current practice); 451 T510 (the task time breakdown's two
sides) and T512 (a task's size, counts, turns, tokens and own path); the 451 parts this feature takes over (below); trial 458.

## Why

Over the night of 2026-11-27 the builders were not the bottleneck: their pool trees were busy 93%, 98% and 83% of 02:00Z to 14:29Z
(t269, t270, t271; the session's run of `tree-idle.py` with its window start edited to 02:00Z, 2026-11-27 about 14:40Z, reported in
`port-talk-orchestrator-update.md`; the script as committed reads only its own 17:00Z window). Integration was. The coordinating session carried every builder's
commit into its own clone, ran each batch's gate there, and repaired every red gate and refusal in its own turns, one at a time.
Each figure below is from `port-talk-orchestrator-update.md` (one read-only agent over the event log, the pool log, the landing
logs and the transcripts, 02:00Z to 15:00Z) unless it names `make task-time`:

- 50 landing attempts, 18 landed; 19 refused before a gate ran (plan review owed 6, audit entry 5, tripwire 4, ledger row 3,
  unclear 2); 10 gates red (coverage 6, hook suites 4, a failing unit test 3, the regex-scan check 2, some red for more than one);
  3 passed the gate and were refused at the tick. The causes are partly inferred: several attempts overwrote one log. The 63-task
  batch took 14 attempts over about 5 hours.
- A landing ran in the clone 44% of the window; 74% of those minutes were attempts that did not land.
- 15 of 93 carries (16%) conflicted and were resolved by hand, 8 of them in `plan.md`.
- `make task-time SINCE=2026-11-27T02:00:00Z UNTIL=2026-11-27T14:29:00Z` (130 tasks landed, its header; 451 T510's split): the
  landings' side 569.1 blocking minutes. The tasks' side read 137.1, of which 26.3 a task's work waited on a landing (the
  cross-blocking row), at 451 T510's builder's run (2026-11-27, about 15:00Z), and 143.2 and 32.3 at spec-fidelity's re-run (the same
  day, about 16:30Z): the row is an upper bound that counts a tree free from its release to its next handout, so handouts after the
  window move it. This spec's baseline is the later run, 32.3 minutes over 130 tasks.
- Tokens: the coordinator 0.58M output and 616M cache-read over 1,007 calls, its context 540k to 966k tokens a call and growing
  about 100k an hour; the builders 4.88M output and 1,026M cache-read over 105 transcripts; review and check agents 1.1M output.

The clone was both the session's workspace and the tree the gate checked, so everything that touched it - a filing, a carry, a
note - queued behind a gate. The GM: "I worry that they are symptomatic of something that is a big deal in other interactions."

## What current practice says (the two notes)

Systems that run parallel coding agents converge on four roles: a THIN COORDINATOR that plans, dispatches and talks to the human;
SHORT-LIVED WORKERS each in a worktree; a MERGE QUEUE that is mostly a script - batch, gate, bisect a red batch to find the failing
change, eject it, land the rest (bors, GitHub's merge queue, Chromium's commit queue, Mergify, Gas Town's Refinery) - where the failing change goes
back to its author for repair; and a WATCHER of workers' health. Cursor built an integrator agent and dropped it ("Workers were
already capable of handling conflicts themselves"). A long-lived context is the token cost to avoid; where judgment is needed at
integration, a fresh agent per batch, not a standing one.

What this project keeps (the GM: not "overhaul our project to use some other framework"): spec-kit, the guards,
`make builder-brief` and the report format, `make land`'s checks, the pool, the queue, the event log. What changes is who runs
integration and where.

## User stories

The thresholds below are GUESS knobs, goals rather than targets to defend (root CLAUDE.md, "Research").

### US1 - the coordinator never integrates (P1)

The coordinating session dispatches builders, reads their short reports, files tasks and talks to the GM. It never carries,
repairs a red gate or answers a landing's refusal in its own turns or its own tree, and nothing it writes waits on a gate.

**Acceptance**: over a like window (eight hours or more of builder work), the cross-blocking row - minutes a task's work waited
on a landing - is no higher than the night's (32.3 minutes over 130 tasks, the baseline run above); a filing or a note in the
session's tree during a gate is never held.

### US2 - builders hand in work that is ready to land (P1)

Before a builder's hand-in (`make builder-done`), its tree is rebased onto current main with its conflicts resolved by the builder,
and the landing's cheap first pass (audit entries, ledger rows, plan review owed, file size, pointers) runs green there. A refusal
a builder can answer is answered by the builder that has the context. Coverage stays in the landing's gate only
(`docs/process-decisions.md`, "REVERSED the same night - coverage stays in the second tier only", the GM 2026-11-26).

**Acceptance**: a hand-in the landing's first pass would refuse is refused at hand-in, with the command that fixes it; over the
window, landings refused before a gate are well under the night's 19 of 50 (a GUESS: under a quarter of that rate).

### US3 - a landing lane of its own (P1)

Landing runs in a worktree of its own, driven by tooling rather than the coordinator's turns: it takes the handed-in commits in
order, carries them, runs the batch gate, and pushes. It wakes the coordinator only for what needs judgment.

**Acceptance**: a landing's gate never runs in the session's clone; the lane runs a batch with no coordinator turn between the
hand-ins and the push.

### US4 - a red batch lands its good changes (P2)

When a batch's gate is red, the lane finds the change that made it red - first by the gate's own report (the failing crate, suite
or check, and the batch change that touched it), by bisection only where that names none - lands the rest, and returns the
failing change to the queue as a repair entry. The repair goes to a FRESH builder given the gate's output; no builder is kept past
its report (451 T308, the GM).

**Acceptance**: where the gate's report attributes the red, the batch's other changes land on the next gate run; where it does not,
in at most ceil(log2 n) + 1 further runs for a batch of n changes with one bad change (more bad changes, one bisection each); no batch is repaired whole by the coordinator.

### US5 - judgment at integration goes to a fresh agent (P3)

A conflict the carry's merge rules cannot resolve, or a red the lane cannot attribute or bisect, goes to a fresh agent dispatched
for that batch with the conflict or the gate's output - never a standing integrator, never the coordinator's context.

## Requirements

- **FR-001** The coordinator's tree is never the tree a gate checks; the gate-write guard holds only writes to the tree being gated
  (451 T307 part 1, taken over).
- **FR-002** `make builder-done` rebases the builder's tree onto current main and runs the landing's cheap first pass before it
  commits; a refusal names the fixing command. It runs no coverage.
- **FR-003** The landing lane runs in its own worktree, takes hand-ins from the done refs in order, and runs the existing
  `make land` checks there; the push's lock and route are unchanged.
- **FR-004** A red batch: attribute, else bisect; eject; land the rest; file the repair as a queue entry (US4). How many changes a
  batch holds and when the lane starts one is a knob, seeded from trial 458's finding (451 T415).
- **FR-005** The lane wakes the coordinator once per landed batch with a short status, and otherwise only for US5's cases.
- **FR-006** TOKENS, weighed with the same standing as throughput (the GM's fifth process-reviewer message): the total tokens per
  landed task - builders, repair builders, fresh integration agents, review agents and the coordinator together, by kind (output,
  fresh input, cache read; 451 T512) - is measured over a like window before and after, and must not rise. A cost moved from the
  coordinator to builders counts where it lands.
- **FR-007** Every per-task figure is read beside the task's size (451 T512's lines, test and non-test), never alone: a figure
  that improves because tasks were cut smaller is not an improvement (the GM's fourth process-reviewer message: no single metric is
  the target).
- **FR-008** Nothing of the existing checks is dropped: a change lands only through the same gate and push checks as today.
- **FR-009** Before building any part of the lane, the plan records whether it can be taken from something that exists - a
  published merge-queue script or bors-style bisect, Gas Town's Refinery, Claude Code's own background agents, worktrees and
  Workflow tool (research C2) - and takes it where it fits (the GM: "I don't want to completely reinvent the wheel ... I would even
  download somebody's skill or whatever if that helped").
- **FR-010** A LIKE WINDOW is one of eight hours or more of builder work (US1) whose concurrency is close to the window it is
  compared with: trees held, time-weighted from the pool's log (the night of 2026-11-27: three pool trees, busy 93%, 98% and 83% - one-shot, the session's tree-idle.py run of 2026-11-27 about 14:40Z, as the Why says),
  and the machine's load. Every before-and-after figure is stated with the concurrency it was measured under, and where the two
  windows' concurrency differs both are stated beside the figure, so a window of one builder is never compared bare with one of
  four (the GM's seventh process-reviewer message, 2026-11-27, in `specs/449-rust-codebase/port-talk-gm-goal.md`).

## Taken over from feature 451

Chosen by reading every open 451 task held for the GM (T302, T307, T308, T321, T354, T401, T405, T415) against FR-001 to FR-005;
moved when this feature's tasks are written, each closed in 451 with a pointer here:

- **T302 parts 1 and 4** (only a session's own clone uses land-alone; a landing refuses an unclean clone and land-alone retires)
  - US3, FR-003. Its parts 2 (pool trees for page sessions) and 3 (a guard confining each builder to its tree) stay in 451.
- **T307 parts 1, 2 and 3** (the gate-write guard's reach; the push refusing after the gate, every push check also in the first
  pass; one gate run for several ready tasks) - FR-001, FR-003, FR-008, US3.
- **T308** (two tiers of checking: the fast one in the builder's tree, the full gate once where work reaches main) - its two-tier
  split and its measurements, US2 and US3. Two of its clauses are replaced, not taken: a gate failure repaired "by whoever is
  cheapest", the coordinating session among them (replaced by US1, US4 and FR-004: a fresh builder, never the coordinator), and the
  changed crate's coverage in the builder's tree (replaced by US2 and FR-002: coverage in the landing's gate only).
- **T405** (the gate's tree check voids a gate for a write it never read) - FR-001.
- **T415** (the second tier's gate proposed at the threshold) - FR-004, with trial 458's finding.

T321 (a reproduction helper), T354 (brief sizing) and T401 (the tree-idle re-measure) are not the lane's and stay in 451.

## Decisions the plan makes (the record is silent; each a knob or the easier route, said which)

- The lane's tree: b1 (idle since 10:20Z on 2026-11-27 at `L7R_BUILDERS` = 3) or a tree of its own.
- The rebase and the first pass at hand-in are the session's additions to current practice's shape, approved with the sketch
  (`request.md`, "very sensible"); the plan measures each against FR-006 and FR-007 and does not reopen them.

## Out of scope

- Several sessions sharing builders (feature 459).
- The process reviewer (its own feature, after this one; T512's figures are its first data).
- Adopting Gas Town or another framework whole (FR-009 takes parts where they fit).

## Success measure

Over a like window after the feature lands, against the night of 2026-11-27: landed tasks per hour of builder work at least the
night's, read beside task size (FR-007); the cross-blocking row no higher; total tokens per landed task no higher (FR-006); every
check that holds today still holding.

## Review history

- 2026-11-27, round 1 (spec-fidelity, MODE 2 against request.md): CHANGES REQUIRED, 8 items - coverage struck from the hand-in
  (it reinstated the closing-step coverage reversed on 2026-11-26); total tokens per landed task weighed with throughput (FR-006)
  and every per-task figure read beside task size (FR-007); US1 measured by the cross-blocking row; the reuse decision (FR-009);
  the figures sourced; one repair order, a fresh builder; the takeover list by part; the approved sketch recorded in request.md.
- 2026-11-27, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 6 items - the cross-blocking baseline dated to its run
  (32.3 minutes over 130 tasks, round 2's own run of `make task-time`, 2026-11-27 about 16:30Z), the tree-busy figures' real source, T302 parts 1 and 4 and T307 part 2 taken, T308's two
  contradicting clauses replaced, bisection restored to current practice, US4's bound for one bad change.
- 2026-11-27, round 3 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - T307 part 2's parenthetical said only its own
  text. The same commit added FR-010 from the GM's seventh process-reviewer message.
- 2026-11-27, round 4 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - FR-010's like window reworded so the night's
  baseline can meet it (concurrency close, time-weighted, never compared bare).
- 2026-11-27, round 5 (spec-fidelity-verify, MODE 3): FAITHFUL.
