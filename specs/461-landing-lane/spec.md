# Feature 461: the landing lane - a thin coordinator, builders that hand in ready work, and a merge queue of its own

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-27

**Status**: Draft - specified, not started ("go ahead and write the spec for the feature now, but don't actually get started on it just yet")

**Affects**: tooling

**Approved**: the GM, 2026-11-27, "Okay, yeah, go ahead and write the spec for the feature now, but don't actually get started on it just yet."

A feature he asked to be filed: "you should treat features that I have asked to be filed as automatic approval, and therefore you
should not ask in the future" (GM 2026-10-18).

**Input**: `request.md` (the GM's words); `specs/449-rust-codebase/port-talk-orchestrator-research.md` (2026-11-26, the sources
and four options) and `port-talk-orchestrator-update.md` (2026-11-27, the night measured and current practice); 451 T510 (the
task time breakdown's two sides) and T512 (a task's size, counts, turns, tokens and own path); the held 451 tasks this feature
takes over (below); trial 458 (the second tier's threshold).

## Why

Over the night of 2026-11-27 (02:00Z to 15:00Z) the builders were not the bottleneck: their pool trees were busy 83 to 98% of the
window. Integration was. The coordinating session carried every builder's commit into its own clone, ran each batch's gate there,
and repaired every red gate and refusal in its own turns, one at a time:

- 50 landing attempts, 18 landed; 19 refused before a gate ran (plan review owed 6, audit entry 5, tripwire 4, ledger row 3,
  unclear 2); 10 gates red (coverage 6, hook suites 4, a failing unit test 3, the regex-scan check 2); the 63-task batch took 14
  attempts over about 5 hours.
- A landing ran in the clone 44% of the window; 74% of those minutes were attempts that did not land.
- 15 of 93 carries (16%) conflicted and were resolved by hand, 8 of them in `plan.md`.
- The landings' side of the task time breakdown: 569 blocking minutes, against the tasks' 137 (451 T510).
- The coordinator's context ran 540k to 966k tokens a call and grew about 100k an hour, every turn re-reading it; 616M cache-read
  tokens over 1,007 calls.

The clone was both the session's workspace and the tree the gate checked, so everything that touched it - a filing, a carry, a
note - queued behind a gate. The GM: "I worry that they are symptomatic of something that is a big deal in other interactions."

## What current practice says (the two notes; the GM: "take existing best practices", not "overhaul our project to use some other framework")

Systems that run parallel coding agents converge on four roles: a THIN COORDINATOR that plans, dispatches and talks to the human;
SHORT-LIVED WORKERS each in a worktree, whose context ends with the task; a MERGE QUEUE that is mostly a script - batch, gate,
bisect a red batch and eject the failing change, land the rest (bors, GitHub's merge queue, Chromium's commit queue, Mergify, Gas
Town's Refinery) - where the failing change goes back to its AUTHOR for repair; and a WATCHER of workers' health. Cursor built an
integrator agent and dropped it ("Workers were already capable of handling conflicts themselves"). A long-lived context is the
token cost to avoid; where judgment is needed at integration, a fresh agent per batch, not a standing one.

What this project keeps: spec-kit, the guards, `make builder-brief` and the report format, `make land`'s checks, the pool, the
queue, the event log. What changes is who runs integration and where.

## User stories

### US1 - the coordinator never integrates (P1)

The coordinating session dispatches builders, reads their short reports, files tasks and talks to the GM. It never carries,
repairs a red gate or answers a landing's refusal in its own turns or its own tree, and nothing it writes waits on a gate.

**Acceptance**: over a window of at least eight hours of builder work, the landings' side's blocking booked to the main session
(451 T510's split) is, per landed task, under 10% of the night of 2026-11-27's (569 minutes over 122 tasks, 4.7 a task); a filing or a note in the session's tree
during a gate is never held.

### US2 - builders hand in work that is ready to land (P1)

Before a builder's hand-in (`make builder-done`), its tree is rebased onto current main with its conflicts resolved by the builder,
and the landing's first pass (`make land`'s cheap checks: audit entries, ledger rows, plan review owed, file size, pointers) and the
coverage of its own crates run green there. A refusal a builder can answer is answered by the builder that has the context.

**Acceptance**: a hand-in that would be refused by the landing's first pass is refused at hand-in, with the command that fixes it;
over the window, the landing's refusals before a gate are under a quarter of the night's rate (19 of 50).

### US3 - a landing lane of its own (P1)

Landing runs in a worktree of its own (the pool's fourth tree, or one made for it), driven by tooling rather than the coordinator's
turns: it takes the handed-in commits in order, carries them, runs the batch gate, and pushes. It wakes the coordinator only for
what needs judgment.

**Acceptance**: a landing's gate never runs in the session's clone; the lane runs a batch with no coordinator turn between the
hand-ins and the push.

### US4 - a red batch is bisected and its failing change ejected (P2)

When a batch's gate is red, the lane finds the change that made it red (by the gate's own report where it names one, else by
bisection), lands the rest, and returns the failing change to the queue as a repair entry for a builder - its original builder's
tree where it still holds the task, otherwise a fresh builder given the gate's output.

**Acceptance**: a batch with one bad change lands its other changes in at most two further gate runs; no batch is repaired whole
by the coordinator.

### US5 - judgment at integration goes to a fresh agent (P3)

A conflict the carry's merge rules cannot resolve, or a red the lane cannot attribute, goes to a fresh agent dispatched for that
batch with the conflict or the gate's output, never to a standing integrator and never into the coordinator's context.

## Requirements

- **FR-001** The coordinator's tree is never the tree a gate checks; the gate-write guard holds only writes to the tree being gated
  (451 T307 (1)).
- **FR-002** `make builder-done` rebases the builder's tree onto current main and runs the landing's first pass and its crates'
  coverage before it commits; a refusal names the fixing command (the project's rule: tips live in error output).
- **FR-003** The landing lane runs in its own worktree, takes hand-ins from the done refs in order, and runs the existing
  `make land` checks there; the push's lock and route are unchanged.
- **FR-004** A red batch: attribute, eject, land the rest, file the repair as a queue entry (US4). How many changes a batch holds
  and when the lane starts one is a knob, seeded from trial 458's finding (451 T415's threshold).
- **FR-005** The lane wakes the coordinator once per landed batch with a short status, and otherwise only for US5's cases.
- **FR-006** Every figure in this spec's acceptance is read from `make task-time` (451 T510, T512) and the landing's own Phase
  lines, before and after, over a like window; token cost per landed task (T512) is reported beside throughput, as the GM's
  fifth process-reviewer message asks.
- **FR-007** Nothing of the existing checks is dropped: a change lands only through the same gate and push checks as today.

## Taken over from feature 451 (moved, not duplicated, when this feature's tasks are written)

- **T302** - every writer has one tree and a landing needs a clean clone.
- **T307** part 3 - what a landing waits on that it need not.
- **T308** - two tiers of checking: the fast one in the builder's tree, the full gate once where work reaches main (US2, US3).
- **T405** - the gate's tree check voids a gate for a write it never read (FR-001).
- **T415** - the second tier's gate proposed at the threshold (FR-004), with trial 458's finding.

## Decisions the plan makes (the record is silent; each a knob or the easier route, said which)

- The lane's tree: b1 (idle since 10:20Z on 2026-11-27 at `L7R_BUILDERS` = 3) or a tree of its own.
- Attribution before bisection: the gate's report names a failing crate or suite and the change that touched it; bisect only where
  that names none.
- Whether a repair goes to the original builder's tree or a fresh builder: the easier route first (a fresh builder with the
  gate's output), the original where its tree still holds the task.

## Out of scope

- Several sessions sharing builders (feature 459).
- The process reviewer (its own feature, after this one; T512's figures are its first data).
- Adopting Gas Town or another framework whole; its Refinery's bisect and eject rules are read as a reference.

## Success measure

Over a like window after the feature lands: landed tasks per hour of builder work at least the night's, the landings' side's
blocking and the coordinator's tokens per landed task each well under the night's, with every check that holds today still
holding.
