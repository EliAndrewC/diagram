# Research - feature 451, where the time goes and the six cheap fixes

Phase 0 of the plan. Every finding below is a measurement or an observation with its method, taken 2026-11-20 on this clone
(`/diagram/.clones/diagram-backlog`), its event log `.git/l7r-events/449-rust-codebase.jsonl`, the 449 session's transcripts
(`~/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl` and its `subagents/`), and the installed Claude Code
(`~/.local/share/claude/versions/2.1.325`). The window is 2026-11-19T14:00Z onward unless a finding says otherwise. All of it is
`research: rendering` - tooling, nothing about a place.

## R1 - What the event log's writer classes today (FR-001)

- **The writer.** `rust/guard/src/guards/event_log_hooks.rs`, `category()`: an edit tool is `edit`; a Bash call is `quick test`
  (`make quick`), `test file`, `gate` (`make done`), `spec-kit step` (`tick`, `claim`, `plan-verdict`), else `other tool`; an Agent call
  its `agent_category`. The category is FROZEN into each line's `cat` at write time, and the readers (`where_time.rs` through
  `feature_report/tables.rs::tool_cat`) read `cat` back, never the `make` field.
- **What the readers make of it.** `make where-time F=449 SINCE=2026-11-19T14:00:00Z` booked 678 of the window's 845 minutes as
  "waiting on work" and every gate and test column 0 (measured 2026-11-19 by the spec, the same command; spec.md's Why and SC-001).
- **What it misses.** Of the window's PostToolUse minutes, 210.4 were `other tool`, 1.9 `quick test`, the rest under 0.2 (observed
  2026-11-20, method: the `ms` of the log's PostToolUse lines since 14:00Z, summed by `cat` in a Python reader). Of the `other tool`
  Bash minutes with a `make` field: `static` 30.8, `format` 20.9, `hooks-test` 20.2, `rust-test` 16.6, `render-sync` 6.1, `map` 3.6
  (same method, by `make`). 101.2 Bash minutes carried no `make` field (same method).
- **Why 101 minutes had no target** (observed 2026-11-20, method: each such line's `id` joined to its `tool_use` command in the main and
  subagent transcripts, summed by the command's head): a `python3 - <<'EOF'` script 28.9 minutes, `timeout 590 bash -c` wait loops 17.6,
  `timeout 2400 tail` 9.0, `timeout 2400 make static` 3.0, `timeout 1800 make rust-test` 1.7, `l7r-gate.sh rust ...` 4.1.
- **Two make detectors disagree - a defect.** The writer's own `MAKE` pattern takes `(`, `then`, `do`, `else`, `time` and `VAR=` before
  `make` but not `timeout N` or `flock F`; the guards' `shared::make::targets` takes `timeout N`, `env` and `VAR=` but not `(` or `flock`.
  So `timeout 2400 make static` logs no target, and `(make static > log) &` is invisible to every guard reading `shared::make`. A tool
  answering wrongly is a defect (constitution XIV): T02 makes one detector of the two.
- **Old lines can be re-read.** Every Bash line that ran a make target keeps its `make` field, so a reader that classes by `make`
  through the shared table re-books past logs too, without rewriting them.

## R2 - What the hook payloads carry (FR-002, FR-004, FR-006)

Read from the schema compiled into the installed Claude Code (method: `grep -ao` over the binary for the hook-input definitions), and
checked against the log and the transcripts where noted.

- **Every hook's base input** has `session_id`, `transcript_path`, `cwd`, and, "present only when the hook fires from within a
  subagent", `agent_id` and `agent_type` (the schema's own description: "Use this field (not agent_type) to distinguish subagent calls
  from main-thread calls"). Observed: 8,009 lines of the window's log carry `by`, which the writer takes from `agent_id` (observed
  2026-11-20, method: lines with a `by` field counted). `agent_type` is SCHEMA, NOT YET OBSERVED: no guard reads it on PreToolUse
  today. T12's first step captures one real subagent PreToolUse payload and pins it as a fixture.
- **A subagent's `transcript_path` is the session's.** The guard log records `transcript_path` on every firing, and none of its
  89,695 entries names an `agent-*.jsonl` file (observed 2026-11-20, method: `grep` over `~/.claude/guard-log/*.json`). The subagent's
  own transcript is `<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`, beside `agent-<agent_id>.meta.json`
  (observed 2026-11-20, method: the 449 session's directory listing). SubagentStop alone also carries `agent_transcript_path`.
- **A builder's context size** is its last model call's `usage.input_tokens + cache_read_input_tokens + cache_creation_input_tokens`,
  read from the tail of its transcript; one model call writes several assistant rows with the same `message.id`, so a sum dedups by
  it. The largest builder transcript of the session, 50 MB, summed in 0.07 s by a Python line scan (measured 2026-11-20 (`time`, a
  scan of lines holding `"usage"`)), 305 model calls, its largest context 1,167,971 tokens, its output 481,878 tokens (same run).
- **A subagent's Bash environment** holds `CLAUDE_CODE_SESSION_ID`, equal to the `sid` the hooks log for its calls, and
  `CLAUDE_CODE_CHILD_SESSION=1`, but no agent id (observed 2026-11-20, method: this planning agent's own `env` against its lines in
  `.git/l7r-events/451-time-retro-and-efficiency.jsonl`). So a gate tool's own line can name its session, never its agent.
- **The meta file names the brief.** `agent-<id>.meta.json` holds `agentType`, `isBuiltIn`, `description` (for example "T202: rebuild
  the placer from its derivation") and `toolUseId` (observed 2026-11-20, method: the session's meta files read).
- **SubagentStop** carries `agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message` and `background_tasks` (schema).
  It repeats for one agent: an agent that stopped with its own background work running is notified as "may be interim", and a
  SendMessage resume runs it again (observed 2026-11-20, method: the main transcript's `<task-notification>` texts). So a cost read at a
  stop is the cumulative total so far, and the reader keeps the LAST stop per `aid`.
- **Stop and SubagentStop carry `background_tasks`**: the in-flight background work, each with `id`, `type` (`shell`, `subagent`,
  `monitor`, `workflow`), `status`, `description` and, for a shell task, its `command` (schema).
- **No hook event marks a background run's end.** The event list (`PreToolUse` ... `MessageDisplay`) has `TaskCompleted`, but its input
  is `task_id`, `task_subject`, `task_description` - the team task list, not a background shell (schema).
- **The main session's completion notice** arrives as a `UserPromptSubmit` whose prompt is a `<task-notification>` (200 of the
  window's 207 prompts were notifications, observed 2026-11-20, method: `gm` false against true on its UserPromptSubmit lines). A
  shell's notice carries `<task-id>`, `<tool-use-id>` (the launching call's `tool_use_id`), `<output-file>`, `<status>` and a summary
  ending "(exit code N)"; an agent's carries `<task-id>` (its agent id), `<status>`, `<result>` and `<usage><subagent_tokens>,
  <tool_uses>, <duration_ms>` (observed 2026-11-20, method: the main transcript's queue rows). The launching call's PostToolUse
  `tool_response` holds the same `backgroundTaskId` (same method). An agent's notice carries `<tool-use-id>` TOO: 3,801 of 3,986 agent
  notices hold one, beside all 1,992 shell notices (measured 2026-11-20 (T04: the `-diagram` and clone transcripts' enqueued notices,
  tallied by summary and by a `<tool-use-id>` before any `<result>`)). So it is the summary that tells the two apart, a shell's opening
  `Background command "` and an agent's `Agent "`, and not the id (T04's section). A shell's summary ends "completed (exit code N)",
  "completed (exit code N: text)" or "failed with exit code N", and a run stopped at its time limit or by its session's end names no
  code (measured 2026-11-20 (T04: the same transcripts' `<summary>` texts, tallied by form)).
- **A subagent's own background run's notice never reaches a hook**: it lands in the subagent's transcript as an `attachment` row of
  type `queued_command` whose prompt is the `<task-notification>` (observed 2026-11-20, method: 57 of the session's 907 subagent
  transcripts hold one; the first read). So the reader takes those ends from the subagent transcripts, as `task_phases.rs` already reads
  them for whose call is whose.

## R3 - A builder, told apart from a review agent (FR-006)

- At dispatch the Agent call's `subagent_type` is the defined agent's name, or `general-purpose` for a builder (the window's
  SubagentStarts: 55 `general-purpose`, 34 `spec-fidelity`, 29 `impl-drift`, the rest defined checks, observed 2026-11-20, method: the
  log's SubagentStart `agent` field). The defined agents are the files `.claude/agents/<name>.md`.
- **Who passes 300k tokens** (observed 2026-11-20, method: every subagent transcript of the session, its model calls since 14:00Z
  deduped by message id, counted by type and by whether its meta `description` names a `T<n>`): 19 `general-purpose` agents whose
  brief names a task passed it, over 1,207 model calls; 2 calls of 2 `general-purpose` agents naming no task; 1 call of one `impl-drift`
  agent; no other defined agent passed it.
- **Decision input**: "a subagent whose `agent_type` is no file under `.claude/agents/`" catches every builder and nothing defined
  but the one impl-drift call; requiring a task id in the brief as well would let a builder with an unnamed brief through. Recorded in
  plan D8.

## R4 - The background runs the session could not track (FR-008)

Every make or cargo run put in the background inside one Bash call, since 2026-11-12 (observed 2026-11-20, method: the session's
Bash commands, quotes and heredocs blanked, an `&` that is not `&&`, `>&`, `&>` or `2>&1` after a job holding `make` or `cargo`, or
`nohup`/`setsid`/`disown`):

- **With no `wait` in the command, 3**: T225's two `(make static > /tmp/t225-static.log 2>&1; echo END >> ...) & ...`, and one false hit,
  `setsid` as a WORD of a `for c in ... setsid ...` list. So the refusal anchors `nohup`, `setsid` and `disown` at a command position,
  never as a word (constitution XVIII: a mention is not an invocation).
- **With `wait` or a sampled pid in the same command, 6**: `make static > log 2>&1 & wait $!`, and five measurement runs that started a
  make, took its pid and sampled it, then waited. The harness tracks each of those: the Bash call does not return before the run ends.
- **How they waited** (observed 2026-11-20, method: the session's Bash commands since 2026-11-12 with no heredoc, quotes blanked,
  holding `make` or `cargo`, a lone `&` and `wait` at a command position, re-read; five found, the sixth of the count above not found
  again by this search): three by a bare `wait`, one by `wait $!` with nothing between, one (2026-11-12, a memory-peak A/B) by `wait $P`
  after `P=$!`. So plan D12's covering forms (bare, `wait $!`, `wait %N`) pass four of the five as written; the fifth is rewritten
  `wait $!` (nothing between its `&` and its `wait` is backgrounded) or carries `DETACH_OK`. A `wait` merely somewhere later is not enough: `make static &
  echo wait` holds the word and `make static & sleep 5 & wait $!` waits for the sleep, and both return with the run detached.

## R5 - The main session's waits (FR-008)

Every wait the main session started in the window was a backgrounded Bash loop escaped with `POLL_OK`, checking an agent's output file
every 60 s or 45 s and, when it had not grown, sleeping again for 300, 420, 600, 900, 1200 or 1500 s before declaring the agent idle
(observed 2026-11-20, method: the main transcript's Bash inputs holding `sleep`, grouped by their sleeps). So "checks less often than
every 60 s" is the LONGEST `sleep` inside the loop's body, the check sits on the POLL_OK-escaped path (which today returns early), and
the main session is a payload with no `agent_id`. These are waits on an agent that is waiting on its own background work.

## R6 - `make static`, its parts and the crate-scoped checks (FR-003, FR-007)

- `make static` runs ruff, `check file-scale`, `claims coverage --rust`, `rust lint`, `rust format --check`, `rust cover` and more (the
  Makefile's `static:` recipe). The crate-scoped forms exist: `scripts/gates/l7r-gate.sh rust {lint,format,test,cover} --crate <dir>`,
  and `make rust-test CRATE=<dir>`.
- `rust cover` builds per FAMILY of crates (`cover.rs`, `uncovered_each`: one `build` per cover directory), then runs each crate's job
  side by side; `rust test` builds in `Verdict::ask` and runs the owed binaries side by side (`side.rs`). So "build seconds per crate"
  exists only per family, and the summed per-crate run seconds exceed the wall. The phase lines therefore carry a start and an end, and
  the reader books wall-clock segments, never summed seconds.
- The whole log, 2026-11-08 onward, holds 608 `"make":"static"` lines (observed 2026-11-20, method: `grep -c` on the log), and a
  `grep` of the 15 MB log took 0.010 s (measured 2026-11-20 (`time grep -c`)) - a guard can count a task's static runs from the log on
  each `make static` call alone.
- A task's starts are `.git/task-starts.jsonl`'s lines for it, and a task can have several: 48 of the 498 (feature, task) pairs in the
  clone's file have more than one line (observed 2026-11-20, method: the file's lines counted per feature and task in a Python
  reader). So a count reset at a task's LAST start would let a second `make task-start` zero it; plan D11 counts from the last landing,
  else the FIRST start. A landing is a `make land` of it that succeeded: plan D5's `end` line of code 0 naming the tasks it landed
  (`land`'s `T=`, which the writer's task capture does not read today: it reads `T=` for `tick`, `task-start` and `decide` only). A
  refused landing is not a landing, and the `end` line carries its own tasks because a `run_in_background` landing's call returns before
  its `end` is written, so no span ties the two.

## R7 - The landing's `T=` (FR-011)

`land.rs::main` splits `T=` on whitespace (`py_text::split`), so `T="T1,T2"` is one task id `T1,T2` and refused. Feature 448's own plan
wrote `make land F=448 T=T01,T02` (observed 2026-11-20, method: `specs/448-engine-coverage-relax/plan.md` line 103).

## R8 - `make task-add` and `make quick` (FR-011)

`task_add.rs` (the `task` crate, which builds on `core`, `plan`, `reviews`, `trials`, `claims`, not on `checks`) writes the box and the
section; `make quick` is ruff, `check house-style-delta`, `question-size`, `file-scale`, `spec-lint --delta` and `partial-citations`
(the Makefile's `quick:` recipe). The recipe is sequential `@` lines, so make stops at the first that fails (observed 2026-11-20,
method: the `quick:` recipe read, lines 953-962 of the root `Makefile`): a failure already there in ruff hides any later check's. So
task-add runs each check line of the recipe (from `make -n quick`, the `$(STATE)` stamp and the closing `printf` set aside) to its own
end, with the line and, on a red, again without it, and compares the two runs' findings, line numbers masked: a finding the with-line
run has and the other lacks is the line's, whatever else is red. "Red then green" alone would let a line's own failure through
wherever quick was already red.

## R9 - The plan lint and the found-and-left item (FR-009)

`make decide` runs `lint::refusal` on the task's section, then the approach gate; the section's `**Found and left?**` line is written
by `plan/template.rs`'s `TEMPLATE`. No open section of any feature's `plan.md` holds a found-and-left item other than `none` or the
template's placeholder (observed 2026-11-20, method: `grep` of every `specs/*/plan.md` for the line); feature 449's `plan-done.md`
holds 42 such lines, the filed ones in the form "filed as T231, before T158" (same method). So the new rule refuses no section open
today.

## R10 - The hook suites' times (FR-010)

The three slowest suites' last seconds: `entry-gate.sh` 44.1, `l7r-gate.sh` 36.3, `sync-with-main.sh` 33.9; the next is
`idle-tests-hooks.sh` at 18.8 (observed 2026-11-20, method: `.git/hooks-test/<suite>.s`, which `tests/hooks/hookrun.sh` writes each
run, last written 2026-11-19T23:41Z). They run side by side (`xargs -P $(HOOKS_JOBS)`), so a suite's seconds are under the other
suites' load: `test-entry-gate.sh`'s own comments time its two cases at about 5 s and 10 s alone (2026-11-19). The runner maps one
suite to one file `tests/hooks/test-<name>.sh` and keys its stamp by that name, so a shard needs the runner to know the shard form.

## R12 - `make tunables` does not reach the tooling crates

The spec's Assumptions say the four thresholds are retuned "from the new data (`make tunables`)". `make tunables` lists the research
claims of the units `claims::units::walked` reads, and that walk skips `rust/guard`, `rust/gate`, `rust/browser`, `rust/embed` and
`rust/parked` (observed 2026-11-20, method: `rust/gate/crates/claims/src/claims/units.rs` lines 558-562 read). So a knob in a guard
never appears there. Plan D14 records the knobs where the guards' rules are recorded instead (each constant labeled GUESS at its
point of change, and a knob table in `docs/guards.md`), and names this to the plan review as a change to the spec's assumption.

## R11 - The held files

`guard_file_hooks.rs::held`: the root `Makefile`, `scripts/hooks/*.sh`, `.claude/settings.json`, `tests/rolls.py`, `dev/switches.json`,
`dev/work-budget.json`, and every file under `rust/guard/src/` but its test files (`tests.rs`, `tests/`). The gate crates
(`rust/gate/crates/*`) and `tests/hooks/test-*-hooks.sh` are not held. A task editing a held file runs `make guard-edit FILE=<file>
WHY="<reason>"` first.
