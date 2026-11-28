# Feature 461: the landing lane - a thin coordinator, builders that hand in ready work, and a merge queue of its own

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-27

**Status**: In progress - started 2026-11-27 ("I think you can go ahead and get started on the orchestrator feature now")

**Affects**: tooling

**Approved**: the GM, 2026-11-27, "Okay, yeah, go ahead and write the spec for the feature now, but don't actually get started on it just yet."

A feature he asked to be filed: "you should treat features that I have asked to be filed as automatic approval, and therefore you
should not ask in the future" (GM 2026-10-18).

**Input**: `request.md` (the GM's words, and the session's sketch he called "very sensible", recorded there as the session's);
`specs/449-rust-codebase/port-talk-orchestrator-research.md` (2026-11-26, the sources and four options) and
`port-talk-orchestrator-update.md` (2026-11-27, the night measured and current practice); 451 T510 (the task time breakdown's two
sides) and T512 (a task's size, counts, turns, tokens and own path); the 451 parts this feature takes over (below); trial 458.

## Why

Over the night of 2026-11-27 the builders were not the bottleneck: their pool trees were busy 93%, 98% and 83% of 02:00Z to 14:29Z (one-shot, measured 2026-11-27)
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
hand-ins and the push but the one wake for a batch silent past the bound; a batch that writes nothing past the bound while its runner
lives wakes the coordinator once, and never silently holds the lane (the red case: batch 461-4's gate, 2026-11-28).

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

### US6 - the GM's priorities decide who gets a builder, enforced by the tools (P1)

The GM states how builders are shared, and the tools hand them out that way, so the coordinator need not remember it (the GM,
2026-11-28, in `request.md`: "our scheduler probably needs some tool-based enforcement of these kinds of prioritizations so that
you don't need to remember to do the correct thing in the future"). His three examples are the forms it must express:

- a feature that gets every builder it can use, others getting only what is left over;
- a feature that always gets one builder so it moves forward, other features getting the rest when they need them, and it filling
  the free builders only where nothing else contends;
- performance fixes and process bugfixes first, whatever feature they are attached to - a rule across every feature's queued
  tasks, not within one feature's.

**Acceptance**: with a policy stating those forms, every place that hands out or names a builder's next work names the work the
policy ranks first: `make builder-next`, `make builder-done`'s next dispatch, `make queue`'s pick, `make builder-brief`, the
pool-idle Stop guard, the set-down Stop hook's "start the next" (`set_down_hooks.rs`, `next_performance_in`) and `make task-start`
(single and bundle) - the list from `grep -rln 'builder_queue::\|queue::offer\|repairs::offer\|next_performance' --include=*.rs
rust`, tests aside (17 files, 2026-11-28), each file that hands out or names work named in the plan. A brief or a Stop that
departs from it is refused with the policy's own pick. The case this story was filed on - 462 disk tasks handed builders while
461's phase 3 tasks stood ready, 2026-11-28 - is the red-first case.

## Requirements

- **FR-001** The coordinator's tree is never the tree a gate checks; the gate-write guard holds only writes to the tree being gated
  (451 T307 part 1, taken over).
- **FR-002** `make builder-done` rebases the builder's tree onto current main and runs the landing's cheap first pass before it
  commits; a refusal names the fixing command. It runs no coverage.
- **FR-003** The landing lane runs in its own worktree, takes hand-ins from the done refs in order, and runs the existing
  `make land` checks there; the push's lock and route are unchanged.
- **FR-004** A red batch: attribute, else bisect; eject; land the rest; file the repair as a queue entry (US4). How many changes a
  batch holds and when the lane starts one is a knob, seeded from trial 458's finding (451 T415).
- **FR-005** The lane wakes the coordinator once per landed batch with a short status, and otherwise only for US5's cases - and
  once for a batch that has written nothing past a bound while its runner lives, so a gate that hangs is never silent (the GM,
  2026-11-28, after a hung test held batch 461-4's gate 4 h 51 min (290.5 minutes, measured 2026-11-28, method: batch 461-4's `run` line in `l7r-lane/lane.jsonl`, 06:42:52Z to 11:33:17Z) with nothing woken: "things look like they've been idle since
  3am", "sounds like our tooling needs a fix for that!"; 461 T107).
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
  compared with: trees held, time-weighted from the pool's log (the night of 2026-11-27: four pool trees, 3.19 held time-weighted over 04:30Z to 14:29Z and 3.34 over 02:00Z to 14:29Z - observed 2026-11-27, method: 461 T02's replay of the pool's log; the Why's 93%, 98% and 83% are three trees' busy shares, a different figure),
  and the machine's load. Every before-and-after figure is stated with the concurrency it was measured under, and where the two
  windows' concurrency differs both are stated beside the figure, so a window of one builder is never compared bare with one of
  four (the GM's seventh process-reviewer message, 2026-11-27, in `specs/449-rust-codebase/port-talk-gm-goal.md`).
- **FR-011** The builders' scheduling policy (US6) is one record the GM's words set, read in one place by every handout path US6
  lists; it expresses at least the three forms of US6 - a feature given every builder it can use, a feature held to a floor of
  builders and filling only uncontended ones, and classes of task ranked first across every feature's queued tasks.
  - **The classes.** PERFORMANCE keeps the membership 451 FR-013 settled (`PERF=1` at filing, a `[perf]` line, a measurement
    counted as performance work). A PROCESS BUGFIX is a fix of a wrong outcome in the process tooling - a defect, as constitution
    XIV defines one - never new process work: a task building a mechanism is not in the class, so a feature of process work (461
    itself) gets no class rank by its subject. Its line carries `[bugfix]` beside `[perf]`, given at filing (`make task-add
    BUGFIX=1`) or added to its line; a task is in the class only by that tag.
  - **The rules it replaces**, each made a form of the one policy and none left as a second rule beside it: performance first
    (451 FR-013, `shared::builder_queue` `next` and `perf_of`, and `set_down_hooks`' `next_performance`); the performance tasks no
    queue line names, named first (451 T313); the caller's own queue preferred (`make builder-next` and `make builder-done`'s
    `dispatch_with`, `queue::offer` with the caller's feature key); the queues read in name order where no caller names one (the
    pool-idle Stop guard's `offer` over the sorted `queues()`); a queue's own order (462 T549's `#! order=queue`, as built), which
    ranks BELOW the classes inside its own feature too - T549's putting 462's queue order ahead of 462's own performance work was a
    session's reading of the GM's 2026-11-27 words ("a higher priority than most of the rest of that new feature"), which name no
    performance work, against his standing performance-first rule (2026-11-20, 451 FR-013), "time continues to be more important
    than disk space" (2026-11-27) and "priority over everything else regardless of what feature" (2026-11-28); and
    repairs first (`LANE_REPAIR_FIRST`, 461 T16), which no words of the GM's set - a repair ranks by its own task's class and
    feature, below the classes.
  - **A departure** is refused with the policy's pick. Its escape names its ground: the pick cannot be worked yet for a reason the
    tool cannot see (it waits on another task's landing, a tree its files hold, the GM's word), stated with the reason. A change
    the GM directs changes the record, never an escape.

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

## Success criteria

The acceptance of each user story, gathered by requirement (the measures themselves unchanged from the stories above):

- **SC-001** (FR-001, FR-003, FR-005): a landing's gate never runs in the session's clone; the lane runs a batch with no coordinator
  turn between the hand-ins and the push but the one wake for a batch silent past the bound, and wakes the coordinator once per
  landed batch; a batch that writes nothing past the bound while its runner lives wakes the coordinator once, and never silently
  holds the lane (the red case: batch 461-4's gate, 2026-11-28); a filing or a note in the session's tree during a gate is never
  held (US1, US3).
- **SC-002** (FR-002): a hand-in the landing's first pass would refuse is refused at hand-in with its fixing command, and runs no
  coverage; landings refused before a gate are well under the night's 19 of 50 (US2).
- **SC-003** (FR-004): a red batch lands its other changes as US4 bounds it, the failing change returned as a repair for a fresh
  builder; no batch is repaired whole by the coordinator (US4).
- **SC-004** (FR-005, FR-008): every integration wake's work goes to a fresh agent, never the coordinator's context, and a change
  lands only through the same gate and push checks as today (US5).
- **SC-005** (FR-006, FR-007, FR-010): over a like window after the feature lands, against the night of 2026-11-27: landed tasks
  per hour of builder work at least the night's, read beside task size; the cross-blocking row no higher; total tokens per landed
  task no higher; every figure stated with its concurrency.
- **SC-006** (FR-009): the plan's reuse decision is recorded for each part of the lane (research.md R1) before that part is built.
- **SC-007** (FR-011): replaying the pool's log of 2026-11-28 under a policy giving 461 every builder it can use, every handout
  path names a ready 461 task wherever one stood ready, and a performance or process-bugfix task of any feature ahead of both;
  over the first like window after US6 lands, no free tree goes to a task the policy ranks below a ready one but by a recorded
  escape, and the escapes are counted with their grounds beside the figure.

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
- 2026-11-27, after round 5: the "Success measure" section restated as SC-001 to SC-006, each naming its requirements, for spec-lint; no requirement or measure changed.
- 2026-11-27, after T02: FR-010's baseline restated - four pool trees, 3.19 held time-weighted (461 T02), where it had said three; the requirement unchanged.
- 2026-11-28, US6 / FR-011 / SC-007 added (the GM's scheduling priorities): spec-fidelity CHANGES REQUIRED, 5 items (every handout
  path, the rules replaced, the process-bugfix class, repairs below the classes, the escape's ground), then FAITHFUL on the revision.
- 2026-11-28, FR-005's stall wake added (the GM on the 4 h 51 min stall): one NOT-REVIEWABLE round (a figure's label, no round used),
  then CHANGES REQUIRED, 2 items (a success criterion in US3 and SC-001; T107's line separating the gate's span from the test
  binary's), both applied; the round arbiter ruled `accept` on round:spec-fidelity|461-landing-lane#1@6 as the review's verdict.
