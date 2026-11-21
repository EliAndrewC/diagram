# Tasks - feature 451, where the time goes, and the six cheap fixes

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

**Input**: `plan.md` (D1-D17 and each task's section), `research.md` (R1-R12), `data-model.md`, `contracts/refusals.md`, `spec.md`.

Every task is tooling, so every task is `research: rendering`. Each builder task is one guard or one reader, so no builder's context
grows large (the feature's own lesson, User Story 2). A task whose files include a HELD file (research R11: `rust/guard/src/**` but its
tests, `scripts/hooks/*.sh`, the root `Makefile`) says so; its builder runs `make guard-edit FILE=<file> WHY="<reason>"` for each
before the first edit. Every task writes prose or code: American spellings, hyphens only. Each refusal's test is written first and
seen red, then the check deleted and the test seen red again (FR-012).

## Occasions

- none: tooling only - no map feature, sheet, glyph, placement rule or research page changes.

## Dependencies

- T01 before any tick (the plan gate).
- T02 first of the data: every later task reads its detector. T03 next: T07, T08 and T14 read its table and `task` field. T04 before
  T05, T06 (`append_row`) and T09 (`BgEnd`).
- T08 after T02-T07; T09 after T08; T10 after T09; T11 after T10.
- T12 before T13 (one guard). T13 and T14 after T03 (the line's `task`) and T06 (the landing's `end` line naming its tasks, D5), T14
  after T02. T15 before T16 (one file). T17, T18, T19 independent of each other.
- T20 before T21 (the shard form). T22 last.

The order, the GM 2026-11-20 (request.md: "let's prioritize those remaining improvement fixes"): the refusals and the split (T12-T21) before the rest of the data and the readers (T07-T11), since they make the work after them faster; T06, in flight, lands first (T13 and T14 read its `end` line). Lanes: T18 then T14; T15, T16, then T12, T13; then T17, T19, T20, T21; then T07-T11; then T22. Parallel lanes, where two builders are run at once: T05 beside T06
(different crates); T17, T18 and T19 beside each other; T21's two suites beside each other. Two builders never edit one held file at
once.

## Implementation strategy

The refusals and the split first (T12-T21, with T28 after T18), the GM 2026-11-20: performance work before other work, since it
makes the work after it faster. Then the rest of the data and the readers (T07-T11: the retrospective as one command), each refusal
landing on its own, each small; T22 last.

## Tasks

### The plan review

### The event-log data (FR-001 to FR-004)

- [ ] T07 An agent's cost and task: `task` on the Agent dispatch line from its description, and `tok` (in, cached, created, out, each `message.id` once), `ctx` and `task` (from the meta file) on each SubagentStop line, in `rust/guard/src/guards/event_log_hooks.rs` (D6; FR-004)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs (and event_log_hooks/fields.rs)
      verify: red first - a fixture transcript with a repeated `message.id` sums it once, a "T202: ..." meta description gives `task: T202`, a "T08: ..." dispatch gives `task: T08`; one real agent stop carries `tok`; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`

### The readers (FR-005)

- [ ] T08 `make where-time`'s columns - tests, compile, gate, land, review, model - booked by `make` through the shared table, the compile split from the phase lines, and `UNTIL=`, in `rust/gate/crates/measure/src/measure/where_time.rs` and a new `where_time/columns.rs`; the `where-time` recipe's `--until` (D2, D4, D7; FR-005, SC-001); a background run's duration ends at the queue's enqueue row, never the BgEnd's t (when the notice reached the session, minutes late while the session is mid-turn: one enqueued 11:44:08, delivered 11:47:41; T04's plan review, 2026-11-20); and T02's make detector measured on a launch whose command runs `make land` after a multi-line `python3 -c "..."` string: bnikhrir8's launch (2026-11-20 11:44:23) was booked cat 'other tool' with no make, where bl11iumpi's (a heredoc commit, then make land) read make land - fixed red first if T02's invoked() misses it; and a goal-less make, which shared::make::invoked reads as `.DEFAULT_GOAL` since T15, booked to the Makefile's default goal in the event log's `make` field, not as the literal word (T15's plan review, 2026-11-20)
      research: rendering
      held: Makefile
      verify: red first - User Story 1's acceptance scenarios 1 and 3 as fixtures (`make static`, `make rust-test`, `make hooks-test` under tests; a `make static` whose cover-build phase is two thirds of its span split into compile and tests), a past log re-booked by its `make` field; `make where-time F=451 SINCE=<this task's start> UNTIL=<now>` books this task's runs; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T09 `make where-time`'s background-run column: a launch paired with its end - the log's `BgEnd`, else the subagent transcript's `queued_command` row holding its `<tool-use-id>`, else open to the window's end - and a between-turns wait booked to the runs its `Stop` line names `inflight`, in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D3, D7; FR-002, FR-005, SC-001)
      research: rendering
      verify: red first - User Story 1's acceptance scenario 2 as a fixture (a background `make land`, its `BgEnd`, the wait it caused booked to land), a subagent's run ended by its transcript's attachment, a run with no end booked open from its start; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T10 `make where-time`'s critical path apart from the summed agent-minutes, each agent's minutes and tokens under its task, and the rework (refused landings from the landing's `end` lines whose `landed` is false, plan re-rounds from a task's later `spec-fidelity` dispatches), in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D5, D6, D7; FR-005, SC-002)
      research: rendering
      verify: red first - two agents overlapping a main-session wait book the wait once on the critical path and both agents under their tasks with their tokens, a landing `end` of code 1 and a second `spec-fidelity` dispatch count as rework; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T11 `make feature-report` reads the same columns through `where_time/columns.rs`, in `rust/gate/crates/measure/src/measure/feature_report.rs` and `feature_report/tables.rs` (D7; FR-005)
      research: rendering
      verify: red first - T08's fixture through `feature-report` gives `where-time`'s sums; `make feature-report F=451` shows the columns; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`

### The refusals (FR-006 to FR-009, FR-011), each red first (FR-012)

### The hook-suite split (FR-010)

### The close

- [ ] T22 The close: on the first full day of work after T02-T21 land, SC-001 (`make where-time F= SINCE= UNTIL=`, unexplained waiting under a tenth), SC-002 (the day's per-task table from the log against a hand join of the transcripts, each bucket within a tenth), SC-005 (static runs per task, builders' largest contexts, every escape listed), `docs/guards.md`'s knob table complete (D14), then `make feature-report F=451 WRITE=1` (SC-001, SC-002, SC-003, SC-005); and CONTEXT_CAP_TOKENS retuned on the day's per-call speed by context: on 2026-11-20 builders reached their first edit at a median 162k of context (90th percentile 254k, 5 of 99 past 300k) and peaked at a median 498k (99 of 114 past 300k), measured 2026-11-20 (the session's subagent transcripts, the last usage before each builder's first Edit or Write, and its largest) - so at 300k most tasks hand off once; the first real firing stopped T13's builder before any edit
      research: rendering
      verify: `report.md` holds the three measurements against their bars; a missed bar names its number and the knob it retunes; `make quick`
- [ ] T33 guard_file_hooks refuses sed -i on a guard source but lets a Python heredoc write it (found by T14, 2026-11-20): a held file written through python3 -c, a heredoc-fed interpreter or tee is a write like sed -i - refused without a live make guard-edit permit, red first on each form, through T15's shared readers; and the make-only guard refuses a bare `rustfmt` (a format outside make, T34's found-and-left) and its block message names `make format FILE=` / `CRATE=` rather than bare `make format` (T34's plan review, 2026-11-20), red first; and gate_write_hooks lets a shell write change the tree under a running gate - on 2026-11-20 a builder's `git apply` and `cp` of guard files during T34's make land put unfinished code under its gate, which failed static's cover (the landing refused, re-run after the work was set aside) - a write by `git apply`, `cp`, `mv`, `tee` or a redirect into the tree refused while the tree's gate runs, red first; and shared::tree's git_write judges a shell `git diff --output=<file>` (and git's other writing options) in the mirror a read, where it writes a file (T44's builder, 2026-11-20), red first
      research: rendering
- [ ] T36 The archived deferrals T17's replay found (2026-11-20): 449 T156, T200, T201, T208, T218, T219, T221, T224, T239 and 451 T02 (a class fix with no instance count), T03, T16, T26 deferred without a filed task or order in plan-done.md - for each, the deferred defect found carried by an open or ticked task, or filed now (each named), or shown fixed; history is not re-judged, so this is read by hand once
      research: rendering
- [ ] T48 The bundle reads ids inside a clause naming another feature as the reviewed feature's (the round arbiter on ask:451-T46-fourth-round, accept, 2026-11-20): '<ids> in N's' / '<ids> of feature N' fall to the reviewed feature's bare reading; measured first - how often such a clause names a feature other than the reviewed one across specs/*/plan.md and plan-done.md - and fixed (read as N's, carried or named NOT FOUND, red first) only if a real one hands a reviewer the wrong text
      research: rendering
