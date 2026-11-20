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

The caller's order is kept: data, readers, refusals, split, close. Parallel lanes, where two builders are run at once: T05 beside T06
(different crates); T17, T18 and T19 beside each other; T21's two suites beside each other. Two builders never edit one held file at
once.

## Implementation strategy

MVP is T02-T11 (User Story 1: the retrospective is one command). Each refusal (T12-T19) then lands on its own, each small. The split
(T20-T21) last, since it touches only the test runner.

## Tasks

### The plan review

### The event-log data (FR-001 to FR-004)

- [ ] T04 A background run's end: `bg` on a backgrounded Bash call's PostToolUse, a `BgEnd` line from a `<task-notification>` prompt with a `<tool-use-id>`, `inflight` on Stop and SubagentStop from `background_tasks`, and `append_row` public for the gate's tools, in `rust/guard/src/guards/event_log_hooks.rs` (its tool fields moved to `event_log_hooks/fields.rs` if the file would pass the file cap); and the one reader, `rust/gate/crates/measure/src/measure/events.rs::load_events`, setting the new kinds (`BgEnd`, `Phase`) aside from the time-gap stream until T08 and T09 read them (D3, D4; FR-002)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs (and event_log_hooks/fields.rs if made)
      verify: red first - research R2's observed shell notification writes its `BgEnd` (id, status, exit code), an agent notification writes none, a Stop with two `background_tasks` lists both; a log with a `BgEnd` and a `Phase` line gives `make where-time` and `make feature-report` the same tables as the log without them; one real background run in the clone writes its `BgEnd`; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`
- [ ] T05 The Rust checks' phase lines: `build`, `test`, `cover-build` (per family), `cover-run`, `lint` and `format` per crate, each with its wall-clock span, through `append_row`, in `rust/gate/crates/rustc/src/rustc.rs`, `rustc/cover.rs`, `rustc/side.rs`, `rustc/kept.rs` (D4; FR-003); and every reader outside measure's load_events filters the event log by kind before it reads a line's time - reviews/glyph.rs takes the log's first event as the feature's start, which a Phase line would become (T04, 2026-11-20), red first
      research: rendering
      verify: red first - a fixture crate's `rust test` and `rust cover` in a scratch tree write nested phase lines, a kept green result writes none; `make rust-test CRATE=rust/gate/crates/rustc`; `make quick`
- [ ] T06 The landing's phase lines: `cheap`, `gate`, `cohort`, `claims`, `push` and an `end` with the exit code and `tasks` (the ids it was asked to land), in `rust/gate/crates/land/src/land.rs` and `land/long_runs.rs` (D5; FR-003)
      research: rendering
      verify: red first - the land tests' fake world writes the lines in order and a refused landing's `end` carries its code, a `T="T1 T2"` landing's `end` names both tasks; `make rust-test CRATE=rust/gate/crates/land`; this task's own landing's lines read off the log; `make quick`
- [ ] T07 An agent's cost and task: `task` on the Agent dispatch line from its description, and `tok` (in, cached, created, out, each `message.id` once), `ctx` and `task` (from the meta file) on each SubagentStop line, in `rust/guard/src/guards/event_log_hooks.rs` (D6; FR-004)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs (and event_log_hooks/fields.rs)
      verify: red first - a fixture transcript with a repeated `message.id` sums it once, a "T202: ..." meta description gives `task: T202`, a "T08: ..." dispatch gives `task: T08`; one real agent stop carries `tok`; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`

### The readers (FR-005)

- [ ] T08 `make where-time`'s columns - tests, compile, gate, land, review, model - booked by `make` through the shared table, the compile split from the phase lines, and `UNTIL=`, in `rust/gate/crates/measure/src/measure/where_time.rs` and a new `where_time/columns.rs`; the `where-time` recipe's `--until` (D2, D4, D7; FR-005, SC-001); a background run's duration ends at the queue's enqueue row, never the BgEnd's t (when the notice reached the session, minutes late while the session is mid-turn: one enqueued 11:44:08, delivered 11:47:41; T04's plan review, 2026-11-20)
      research: rendering
      held: Makefile
      verify: red first - User Story 1's acceptance scenarios 1 and 3 as fixtures (`make static`, `make rust-test`, `make hooks-test` under tests; a `make static` whose cover-build phase is two thirds of its span split into compile and tests), a past log re-booked by its `make` field; `make where-time F=451 SINCE=<this task's start> UNTIL=<now>` books this task's runs; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T09 `make where-time`'s background-run column: a launch paired with its end - the log's `BgEnd`, else the subagent transcript's `queued_command` row holding its `<tool-use-id>`, else open to the window's end - and a between-turns wait booked to the runs its `Stop` line names `inflight`, in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D3, D7; FR-002, FR-005, SC-001)
      research: rendering
      verify: red first - User Story 1's acceptance scenario 2 as a fixture (a background `make land`, its `BgEnd`, the wait it caused booked to land), a subagent's run ended by its transcript's attachment, a run with no end booked open from its start; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T10 `make where-time`'s critical path apart from the summed agent-minutes, each agent's minutes and tokens under its task, and the rework (refused landings from the landing's `end` lines, plan re-rounds from a task's later `spec-fidelity` dispatches), in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D5, D6, D7; FR-005, SC-002)
      research: rendering
      verify: red first - two agents overlapping a main-session wait book the wait once on the critical path and both agents under their tasks with their tokens, a landing `end` of code 1 and a second `spec-fidelity` dispatch count as rework; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T11 `make feature-report` reads the same columns through `where_time/columns.rs`, in `rust/gate/crates/measure/src/measure/feature_report.rs` and `feature_report/tables.rs` (D7; FR-005)
      research: rendering
      verify: red first - T08's fixture through `feature-report` gives `where-time`'s sums; `make feature-report F=451` shows the columns; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`

### The refusals (FR-006 to FR-009, FR-011), each red first (FR-012)

- [ ] T12 The context cap: a new guard `context_cap_hooks` refusing a builder's tool call past `CONTEXT_CAP_TOKENS` (GUESS, 300k) but the Write of its handoff file, naming the file and the next step; its first step one real subagent PreToolUse payload captured and pinned as the fixture (D8, D9; FR-006, FR-012, SC-003, SC-005)
      research: rendering
      held: rust/guard/src/guards/context_cap_hooks.rs (new), rust/guard/src/guards.rs, rust/guard/src/lib.rs, Makefile (`make context-ok`)
      verify: red first - a builder past the cap refused naming the handoff path, under it passes, its handoff Write passes alone and through the whole guard chain (no `--only`), a defined agent past it passes, the main session passes, `CONTEXT_OK` in a Bash call and a `make context-ok AID= WHY=` permit each pass and are recorded; the check deleted, the firing case red; `tests/hooks/context-cap-hooks.sh` linked to `guard-shim.sh` and `tests/hooks/test-context-cap-hooks.sh` green under `make hooks-test`; the `docs/guards.md` row and knob; `make rust-test CRATE=rust/guard`; `make quick`
- [ ] T13 A builder resumed: `context_cap_hooks` refuses a SendMessage to a builder past the cap, or to one whose task (D2's chain: its meta `description`'s `T<n>`, else its first line's `task`, else the `task-starts.jsonl` entry in force at its dispatch) has landed since its dispatch (D5's `end` line of code 0 naming it) or is ticked or archived, naming a fresh dispatch with the handoff file; with no task found the landing check passes with a `no task` guard-log record, and the cap check still applies (D10; FR-006, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/context_cap_hooks.rs
      verify: red first - past the cap refused, a ticked task refused, a builder whose description names NO `T<n>` and whose task (from the start in force at its dispatch, a later start for another task in the log, its own later lines carrying that open task) landed after its dispatch refused, a task landed by a background `make land` (its `end` after the call returned) refused, a task whose only landing since dispatch was refused (`end` code 1) passes, no task found under the cap passes and writes its record, no task found past the cap refused, a defined agent passes, an open builder under the cap passes, `CONTEXT_OK` in the summary passes and is recorded; the check deleted, the firing cases red; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`
- [ ] T14 The third `make static`: a new guard `static_runs_hooks` refusing a task's third run since its last landing that succeeded, or since its first start if it has never landed (a later `task-start` resets nothing), naming the crate-scoped checks for the crates its delta changes; `STATIC_RUNS_A_TASK` (GUESS, 2) (D11; FR-007, FR-012, SC-003, SC-005)
      research: rendering
      held: rust/guard/src/guards/static_runs_hooks.rs (new), rust/guard/src/guards.rs, rust/guard/src/lib.rs
      verify: red first - two runs of a task pass and a third is refused naming `l7r-gate.sh rust test --crate <dir>`, a run after a landing of the task that succeeded (an `end` line of code 0 naming it, from a background land) passes, a refused landing (`end` code 1) resets nothing, a task with no landing counts from its first start, two runs then a second `task-start` of the same task then a third run refused, `STATIC_OK` passes and is recorded; the check deleted, the firing case red; its link and suite green under `make hooks-test`; the `docs/guards.md` row and knob; `make rust-test CRATE=rust/guard`; `make quick`
- [ ] T15 A run the harness cannot track: `no_poll_hooks` refuses a make or cargo job detached by a lone `&` unless a `wait` at a command position covers it (in the job's own list and shell, unconditional, not backgrounded; bare, `wait $!` with no `&` between, or `wait %N` naming it), or started under `nohup` or `setsid` at a command position, or followed by a `disown` in any form (bare, `%N`, `-h`, `-a`) whatever `wait` follows, naming `run_in_background`; `DETACH_OK` (D12; FR-008, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/no_poll_hooks.rs
      verify: red first - research R4's observed `(make static > ...; echo END >> ...) & sleep 1` refused, `nohup make rust-test` refused, `for c in git setsid make; do ...` passes, `make static > log 2>&1 & wait $!` passes, `make static & echo wait` refused, `make static & sleep 5 & wait $!` refused, `make static & P=$!; wait $P` refused, `make static & (wait)`, `make static & false && wait` and `make static & wait &` refused, R4's `(make static > log) & make decide ... | tail -40; wait` passes, `sleep 30 & make static & wait %2` passes, `setsid make static` and `make static & disown` refused, `make static & disown; wait` and `make static & disown; wait $!` refused (each red with the disown check deleted), `make static & disown -h; wait` and `make static & disown %1; wait` refused, `{ make static; } &`, `VAR=x make static &` and `env X=1 make static &` refused, a `run_in_background` make passes, `DETACH_OK` passes and is recorded; the check deleted, the firing cases red; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`
- [ ] T16 A main-session wait slower than its check: `no_poll_hooks` refuses, on the POLL_OK and the file-watching paths, a loop whose longest `sleep` is over `POLL_CHECK_S` (GUESS, 60 s) from a payload with no `agent_id`, naming the 60 s form; `SLOW_POLL_OK` (D13; FR-008, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/no_poll_hooks.rs
      verify: red first - research R5's observed POLL_OK loop (`sleep 60`, then `sleep 420`) refused, the same at `sleep 60` passes, the slow loop from a subagent passes, a main-session file wait sleeping past the knob refused, `SLOW_POLL_OK` passes and is recorded; the check deleted, the firing cases red; `make rust-test CRATE=rust/guard`; `make hooks-test`; `make quick`
- [ ] T17 The deferral's form: `make decide` refuses a found-and-left deferral without its reason, task id and order, or whose task id or "lands before" id names no OPEN task (an unticked box of the feature's `tasks.md`) when `make decide` judges it, or whose order names its own id, and a class fix without its labeled line on how every instance was found, in `rust/gate/crates/plan/src/plan/lint.rs` (the timeless parts, which `make plan-delta` runs too) and `plan.rs::decide` (the open test alone); the template's placeholder states the form (`plan/template.rs`); `DEFER_FORM_OK` on `make decide`, honored by `make plan-delta` for a section decided under it and taken by `make plan-delta` too (D15; FR-009, FR-012, SC-003)
      research: rendering
      held: Makefile
      verify: red first - User Story 5's five cases, the passing case's `T123` and `T124` unticked boxes of the fixture's `tasks.md`; a deferral naming an unfiled task id `T999` refused; one whose "lands before" id is unfiled refused; a done deferral id (ticked, or in `tasks-done.md`) refused; a done "lands before" id refused; "T123 lands before T123" refused; a reason and a filed open task id with no "lands before" refused; a section decided, then T124 ticked, not refused by `make plan-delta` (the open test runs in `decide` alone); a section decided under `DEFER_FORM_OK`, its block then changed, not refused by `make plan-delta`; `DEFER_FORM_OK` on `make plan-delta` passes and is recorded; the check deleted, the firing cases red; no open plan section refused (research R9 re-read); `make rust-test CRATE=rust/gate/crates/plan`; `make quick`
- [ ] T18 `make land T="T1,T2"` read as `T="T1 T2"`, in `rust/gate/crates/land/src/land.rs` and `make land`'s help (D16; FR-011); lands before T08, so a land line naming two tasks is booked to both (T03's plan review, 2026-11-20)
      research: rendering
      held: Makefile (the help line only)
      verify: red first - `T="T1,T2"` and `T="T1, T2"` land both in the land tests' fake world; `make rust-test CRATE=rust/gate/crates/land`; `make quick`
- [ ] T19 `make task-add` runs each of `make quick`'s checks to its own end over what it wrote and, on a red, again with the line withdrawn; where the with-line run has any failure (a check's finding, line numbers masked) the other lacks, the line stays withdrawn and it refuses naming those failures; the line is restored only when the failures are the same; `QUICK_OK` on `make task-add`, in `rust/gate/crates/task/src/task_add.rs` (D16; FR-011, FR-012, SC-003)
      research: rendering
      held: Makefile
      verify: red first - a line citing a bare requirement id another feature defines withdrawn and refused, a clean line kept, an existing failure in an earlier check (ruff) plus the line's own spec-lint failure withdrawn and refused naming the spec-lint failure alone, an existing failure the line adds nothing to (its finding's line number shifted by the line) keeps the line and reports it; the check deleted, the firing case red; `make rust-test CRATE=rust/gate/crates/task`; `make quick`

### The hook-suite split (FR-010)

- [ ] T20 The shard form - `tests/hooks/test-<name>.<k>.sh`, each shard a job under the suite's stamp key, the suite stamped green only when every shard is, the companion check accepting shards - in the `hooks-test` recipe and `tests/hooks/hookrun.sh`; `tests/hooks/test-entry-gate.sh` split by its two cases (D17; FR-010, SC-004)
      research: rendering
      held: Makefile
      verify: red first - a scratch roster's sharded fixture suite runs both shards and stamps only when both are green; `make hooks-test HOOKS_ALL=1`, each `.git/hooks-test/test-entry-gate.*.s` about 20 s or less (`SHARD_BAR_S`, GUESS); the case count before and after equal; `make quick`
- [ ] T21 `tests/hooks/test-l7r-gate.sh` and `tests/hooks/test-sync-with-main.sh` split into shards by their case groups (D17; FR-010, SC-004)
      research: rendering
      verify: each suite's case count before and after equal; `make hooks-test HOOKS_ALL=1`, each shard's kept seconds about 20 or less; `make quick`

### The close

- [ ] T22 The close: on the first full day of work after T02-T21 land, SC-001 (`make where-time F= SINCE= UNTIL=`, unexplained waiting under a tenth), SC-002 (the day's per-task table from the log against a hand join of the transcripts, each bucket within a tenth), SC-005 (static runs per task, builders' largest contexts, every escape listed), `docs/guards.md`'s knob table complete (D14), then `make feature-report F=451 WRITE=1` (SC-001, SC-002, SC-003, SC-005)
      research: rendering
      verify: `report.md` holds the three measurements against their bars; a missed bar names its number and the knob it retunes; `make quick`
- [ ] T24 A gate test reads the real environment (found by T02, 2026-11-20): rust/gate/crates/bundle/src/record/helpers/tests.rs (about line 377) means to reach helpers.rs:537's error path by writing [1] into feature.json, but l7r_guard compiled without cfg(test) reads SPECIFY_FEATURE from the real environment, so with it exported the path is skipped, the test still passes (it accepts 0 or 1) and make static's coverage goes red - the test given its own environment, asserting the one outcome it means, red first with SPECIFY_FEATURE exported; lands before T08 (T03's plan review, 2026-11-20)
      research: rendering
