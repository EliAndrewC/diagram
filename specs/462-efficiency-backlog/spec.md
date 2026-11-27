# Feature 462: the efficiency backlog - feature 451's deferred tasks, carried on after it closes

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-11-27

**Status**: Open - a placeholder: the tasks feature 451 filed for later, moved here when 451 closes

**Affects**: tooling

**Approved**: the GM, 2026-11-27, "In the meantime, it seems like you have a good amount of work to do with both the tasks that you are closing out and moving everything new feature, afterwards, and then doing the split that we discussed which is all on top of the orchestrator feature that you are working in parallel to that"

A feature he asked to be filed: "you should treat features that I have asked to be filed as automatic approval, and therefore you
should not ask in the future" (GM 2026-10-18).

**Input**: `request.md` (the GM's words); feature 451's `tasks.md`, `plan.md` and `request.md` (the tasks moved here, each keeping
its 451 number in its line, its plan section moved with it).

## Why

Feature 451 (time retro and efficiency) ran to 531 tasks, the project's largest (observed 2026-11-27, method: counting `- [x]` in
its tasks-done.md, 416, and `- [ ]` in its tasks.md, 115), and its records grew past what a session can read safely: `plan-review.json`
about 4.99 MB and growing, `plan-done.md` 3.3 MB, its event log 52 MB (observed 2026-11-27, method: `ls -l`; 461 T01 and the GM's
seventeenth and eighteenth process-reviewer messages in `specs/449-rust-codebase/port-talk-gm-goal.md`). The GM asked to finish its
short-run tasks, close it, and carry the rest in a new feature, so later work starts from small records and a session that comes back
to 451 is warned off whole reads.

## Requirements

- **FR-001 The closing set stays in 451.** It is the session's list, approved by the GM's go (request.md, the session's proposal of
  2026-11-27 and his answer): the tasks in flight and the short-run fixes - 451 T513, T514, T519, T523, T527, T528, T529, T531, T532 -
  and T535 (filed after the go: a gate red on good work blocks the closing set's own landings), with the two closing tasks of
  FR-004 (T536, T537). The set is fixed: a task filed from now on is filed in 462, unless it is a defect that blocks a closing-set
  task from landing.
- **FR-002 The rest moves here.** Every other open 451 task moves here, its line keeping its 451 number (`451 T<n>`) and its plan
  section moving with it - T533 and T534 among them (filed after the go, neither short-run) - except those feature 461 takes over
  (FR-003). No task is dropped, and none changes its meaning in the move.
- **FR-003 What 461 takes over is closed in 451 at the move,** each box pointing to the 461 task that carries it - the list is 461's
  `tasks.md` takeover paragraph: T302 parts 1 and 4 (461 T03, T30; parts 2 and 3 move here as `451 T302`), T307 parts 1 and 3 and its
  box (461 T27, T14; part 2 already closed by 461 T06), T308 (461 T16), T405 (461 T28), T415 (461 T26), and T525 (closed by 461 T30,
  not moved). The session's proposal told the GM T307 would move here; 461's accepted spec takes it over, so it goes there.
- **FR-004 The split and its measurement are 451's closing tasks:** 451 T536 measures which tools, hooks and agents read 451's large
  records whole, while they are whole (the proposal's item 4, which put it "first in the new feature": it runs in 451 instead because the before reading needs the records whole, before T537 splits them); 451 T537 splits them mechanically with a note warning future sessions
  off whole reads (the GM's "doing the split that we discussed"), after T536.
- **FR-005** A task that belongs to the process-reviewer feature moves there once that feature is filed (it is not yet).

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003): every open 451 task is either ticked in 451, closed in 451 with a pointer here or to 461, or
  open here with its 451 number; `make speckit-todo` lists 451 as closed.
- **SC-002** (FR-004): T536's before figure is recorded before T537 lands, and after it no reader named there reads a record whole.
- **SC-003** (FR-005): when the process-reviewer feature is filed, its tasks named there are moved with a pointer.
