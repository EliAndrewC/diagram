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

Feature 451 (time retro and efficiency) ran past 530 tasks, the project's largest, and its records grew past what a session can read
safely: `plan-review.json` 4.96 MB, `plan-done.md` 3.3 MB, its event log 52 MB (measured 2026-11-27, `ls`; 461 T01 and the GM's
seventeenth and eighteenth process-reviewer messages in `specs/449-rust-codebase/port-talk-gm-goal.md`). The GM asked to finish its
short-run tasks, close it, and carry the rest in a new feature, so later work starts from small records and a session that comes back
to 451 is warned off whole reads.

## Requirements

- **FR-001** Every open 451 task not in its closing set moves here, its line keeping its 451 number (`451 T<n>`) and its plan section
  moving with it; a task that belongs to feature 461 (the landing lane) moves there instead. The closing set (the GM's go,
  2026-11-27): the tasks in flight and the short-run bug fixes - 451 T513, T514, T523, T528, T529, T531, T532, T533, T534, T535.
- **FR-002** Each moved task is worked as any open task is: no task is dropped, and none changes its meaning in the move.
- **FR-003** A task that belongs to the process-reviewer feature moves there once that feature is filed (it is not yet).

## Success criteria

- **SC-001** (FR-001, FR-002): every open 451 task is either ticked in 451, closed in 451 with a pointer here or to 461, or open here
  with its 451 number; `make speckit-todo` lists 451 as closed.
- **SC-002** (FR-003): when the process-reviewer feature is filed, its tasks named there are moved with a pointer.
