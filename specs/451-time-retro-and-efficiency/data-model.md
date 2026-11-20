# Data model - feature 451

## The event line (FR-001 to FR-004)

One JSON line of `<git common dir>/l7r-events/<feature dir>.jsonl`, written by `rust/guard/src/guards/event_log_hooks.rs` (the hooks)
or by its `append_row` (the gate's tools, in process). Fields today: `t`, `sid`, `ev`, `tool`, `id`, `cat`, `make`, `task`, `by`, `ms`,
`agent`, `aid`, `verdict`, ... (the module's doc comment). This feature adds:

| `ev` | new fields | written by | when |
|---|---|---|---|
| any tool line | `cat` from the category table (D1); `task` on every line where one is known (D2) | the hook | every tool call |
| `PostToolUse` (Bash, backgrounded) | `bg`: the `backgroundTaskId` | the hook | a `run_in_background` call returns |
| `BgEnd` | `id` (the launching `tool_use_id`), `bg` (the task id), `status`, `exit` (number or absent), `make` and `cat` copied from the launch line where the log has it | the hook, on a `UserPromptSubmit` whose prompt holds `<task-notification>` with a `<tool-use-id>` | the main session is told a background shell ended |
| `Stop`, `SubagentStop` | `inflight`: `[{id, type, make?}]` from `background_tasks` | the hook | every stop |
| `SubagentStop` | `tok`: `{in, cached, created, out}` summed over the agent's transcript, deduped by `message.id`; `ctx`: the last call's context; `task`: the `T<n>` its meta `description` names | the hook | every agent stop (cumulative; the reader keeps the last per `aid`) |
| `PreToolUse` (Agent) | `task`: the `T<n>` its `description` (else its prompt's first line) names | the hook | every dispatch |
| `Phase` | `src` (`rust` or `land`), `step` (`build`, `test`, `cover-build`, `cover-run`, `lint`, `format`; `cheap`, `gate`, `cohort`, `claims`, `push`), `crates` (rust: the crate dirs), `t0`, `t1` (UTC, ms), `code` | `append_row`, called by `rustc` and `land` | each step's end |

A line whose `make` target the table does not know is booked `other`, never dropped (spec edge case). A `BgEnd` never seen leaves its
launch OPEN from its start (spec edge case): the reader books it open to the window's end, never zero.

## The category table (FR-001)

One `const` table in `event_log_hooks.rs`, `pub`, read by the writer and by both readers (`where_time.rs`, `feature_report/tables.rs`)
through `l7r_guard::guards::event_log_hooks::bucket_of(make_target)`:

| bucket | make targets (and the gate's own forms) |
|---|---|
| tests | `quick`, `test-file`, `static`, `rust-test`, `hooks-test`, `counters-inert`, `test-times`, `l7r-gate.sh rust test|cover|lint|format` |
| compile | the `build`/`cover-build` phase lines inside a tests run (a phase, not a target) |
| gate | `done`, `verify`, `push-checks`, `cohort`, `cohort-landing` |
| land | `land`, `land-batch`, `land-tooling` |
| review | `plan-delta`, `plan-verdict`, `decide`, `check-bundle`, `claims-bundle`, `arbiter-bundle`, `modal-bundle`, `record-owed`, `claims-owed` |
| docs | `docs`, `record`, `feature-report`, `make-docs` |
| spec-kit step | `tick`, `claim`, `task-start`, `task-add` |
| other | any other target, and a Bash call with none |

The exact membership is the builder's to finish from the Makefile's `## [tests]`, `## [project]` tags (T02), each row commented with
why; a target moved between buckets later is a one-line change.

## Builder, threshold and handoff (FR-006)

- **Builder**: a payload with `agent_id` whose `agent_type` has no `.claude/agents/<agent_type>.md` in the clone (plan D8).
- **Context**: the builder's transcript's last model call, `input + cache_read + cache_creation` tokens, read from its tail.
- **Threshold**: `CONTEXT_CAP_TOKENS = 300_000`, GUESS (spec FR-006), a knob `make tunables` lists.
- **Handoff file**: `<git common dir>/l7r-handoffs/<task or agent id>.md`; the one Write the cap lets through.
- **Landed**: the agent's task (its meta `description`'s `T<n>`) is a ticked box in the feature's `tasks.md` or is in `tasks-done.md`
  (`shared::speckit::tasks`).

## The static count (FR-007)

Per task, from the event log: the `PreToolUse` lines with `make: static` and that task, after the later of the task's last
`task-starts.jsonl` entry and its last `BgEnd`/`PostToolUse` of `make land` naming it. Third and later refused; escape `STATIC_OK`.

## Knobs (each GUESS, labeled at its constant and in `docs/guards.md`'s knob table - `make tunables` does not walk the tooling crates, research R12)

| knob | value | where |
|---|---|---|
| `CONTEXT_CAP_TOKENS` | 300,000 tokens | `context_cap_hooks.rs` |
| `STATIC_RUNS_A_TASK` | 2 | `static_runs_hooks.rs` |
| `POLL_CHECK_S` | 60 s | `no_poll_hooks.rs` |
| `SHARD_BAR_S` | 20 s | the hooks-test recipe's comment and `docs/guards.md` (a measured bar, never a gate) |
