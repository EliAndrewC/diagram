# Implementation Plan: where the time goes, and the six cheap fixes

**Branch**: none - `main` in the clone (`SPECIFY_FEATURE=451-time-retro-and-efficiency`) | **Date**: 2026-11-20 | **Spec**: `spec.md`

**Input**: `spec.md` (APPROVED, `spec-fidelity` round 3 FAITHFUL), `request.md`.

## Summary

Four kinds of new event line - one category table the writer and readers share, a background run's end, a make run's phases, an
agent's token cost - and `make where-time` and `make feature-report` reading them into the GM's columns with `UNTIL=`. Then six
refusals, each red first with an escape and a message naming the compliant command: a builder past its context cap (and its resume),
a third `make static` in a task, a make or cargo run detached inside a Bash call, a main-session wait slower than its check interval, a
deferral with no reason, task or order, and a task-add line that fails `make quick`; plus `make land T="T1,T2"`. Last, the three
slowest hook suites split into shards. The measurements behind every decision are `research.md` (R1-R12), each with its method.

## Technical Context

**Language/Version**: Rust (the workspace `rust/Cargo.toml`). **Primary Dependencies**: the guard crate `rust/guard` (`l7r-guard`)
and the gate crates `rust/gate/crates/{measure,rustc,land,plan,task}`; no new outside crate. **Storage**: the clone's event log
`<git common dir>/l7r-events/<feature>.jsonl`, `task-starts.jsonl`, the guard log. **Testing**: each crate's own tests (`make rust-test
CRATE=<dir>`, 100% line coverage of new code by its own tests), the guard suites (`make hooks-test`), `make quick`, the landing's
`make done`. **Target Platform**: this container's Claude Code 2.1.325 hooks. **Project Type**: tooling. **Performance Goals**: a guard
on every tool call adds no process and reads at most one transcript tail (R2); a count reads the event log only on the call it judges
(R6). **Constraints**: the held files (R11) - each task that edits one says so and runs `make guard-edit FILE=<file> WHY="<reason>"`
first. **Scale/Scope**: no map, no engine code, no research claim.

**Single-artifact target**: N/A - no generator change.

## Performance bookends

N/A: no generator change, no stage's counted work moves.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX, XI**: N/A - no pool content, no SOURCE block, no setting prose, no kanji.
- **VI**: PASS - each task names its verification: its crate's tests with the red case first, `make hooks-test` for a guard, `make
  quick`, and the landing's `make done`; the closing task measures SC-001, SC-002 and SC-005 on real work.
- **X**: PASS - the only Python touched is none; the Rust owes 100% of its new lines from its own tests, functions and files at human
  scale (`check file-scale`): `event_log_hooks.rs` is 605 lines (observed 2026-11-20, method: `wc -l`) and gains three tasks' fields, so T04 moves the writer's tool fields
  into `event_log_hooks/fields.rs` if the file would pass the file cap.
- **XII**: N/A - nothing a generator asserts about the world; every task is `research: rendering`.
- **XIII**: PASS - baseline before the first edit: `make hooks-test HOOKS_ALL=1` and `make rust-test` on unmodified code in a detached
  worktree (`git worktree add --detach`), recorded in T02's section; zero new failures at each landing. What each change is held to:
  its tests, its callers' reads (the two readers, the arbiter's bundle), its guard suites; a differing report is not a regression.
- **XIV**: PASS - two defects found while measuring are fixed in the task that touches them: the two disagreeing make detectors (R1,
  T02), and the readers booking by the frozen `cat` (R1, T08).
- **XVI**: PASS - built as the spec's FRs; the places this plan reads the spec narrowly or broadly are each named for the plan review
  (T01): D4 (phases per family where FR-003 says per crate), D8 (the builder), D11 (the main session's runs counted), D12 (`cmd &`
  followed by a `wait` covering the job passes) and D14 (`make tunables`).
- **XVIII**: PASS - each refusal ships with its suite case firing and its quiet case, proven by deleting the check (FR-012).
- **XIX**: N/A - nothing placed on a map.

## What the measurements changed (research.md)

- **No hook marks a background run's end** (R2). The main session's end comes from its `<task-notification>` prompt; a subagent's own
  background run's end reaches no hook at all, so the reader takes it from the subagent's transcript (D3).
- **A subagent's `transcript_path` is the session's** (R2); its own transcript is derived from `agent_id` (D9).
- **Coverage builds per family and runs side by side** (R6), so phase lines carry wall-clock spans, never per-crate sums (D4).
- **The observed slow waits are POLL_OK-escaped loops** checking every 60 s and then sleeping
  300-1500 s (observed 2026-11-20, method: the main transcript's Bash inputs holding `sleep`, grouped by their sleeps; R5), so the
  slow-poll refusal sits on the escaped path and judges the longest sleep (D13).
- **`make tunables` does not walk the tooling crates** (R12), so the knobs are recorded where the guards' rules are (D14).

## Decisions

**D1 - One make detector** (FR-001; R1). `shared::make` gains `invoked(cmd) -> Vec<String>`, the targets in command order, at a command
position that also takes `(`, `{`, `flock <file>`, `nice`, `time` and `timeout N`, beside the `env` and `VAR=` it takes today (R1);
`targets()` becomes its set. The event-log writer's own
`MAKE` pattern is deleted and `make_target` is `invoked(cmd).first()`. The gate's own crate-scoped form `scripts/gates/l7r-gate.sh rust
<cmd>` is read as the target `rust-<cmd>`. Every guard reading `shared::make` then sees `(make static) &` and `timeout 2400 make static`.

**D2 - The category table and the line's task** (FR-001; R1). One `pub` table in `event_log_hooks.rs`, `bucket_of(target)`, its rows
in `data-model.md`; `category()` books a Bash call by it, and both readers book a line by its `make` field through the same function,
falling back to `cat` only for a line with no `make` - so a past log is re-booked too. A target the table does not know is `other`.
Every line carries `task` where one is known: the `T=` of a `tick`, `task-start`, `decide` or `land` command; else, for a subagent's
call, the `T<n>` its meta file's `description` names (`<session dir>/subagents/agent-<agent_id>.meta.json`, read once a call); else the
clone's last `task-starts.jsonl` entry for the feature.

**D3 - A background run's end** (FR-002; R2). The PostToolUse of a `run_in_background` call records `bg`, the `backgroundTaskId`. A
`UserPromptSubmit` whose prompt holds `<task-notification>` with a `<tool-use-id>` writes a `BgEnd` line: that id, the task id, its
status and exit code. Every `Stop` and `SubagentStop` line records `inflight` from `background_tasks`. The readers (T08) pair a launch
with its `BgEnd`; for a subagent's launch with none, they read the subagent transcript's `queued_command` attachment holding the same
`<tool-use-id>`, its row's timestamp the end; a launch with no end anywhere is open to the window's end. A wait between turns is booked
to the runs `inflight` names on the `Stop` that opened it, else to the launch whose span holds it.

**D4 - A make run's phases** (FR-003; R6). `event_log_hooks::append_row(root, row)`, the line writer the hooks use, made callable by the
gate's tools in process (the gate crates already build on `l7r_guard`). `rustc` writes a `Phase` line at each step's end: `build` and
`test` per crate where `Verdict::ask` builds and `side.rs` runs, `cover-build` per family in `cover.rs::build`, `cover-run` per crate,
`lint` and `format` per crate - each with its wall-clock `t0` and `t1`. The readers book, inside the Bash call or background span that
holds them, the union of the `build`/`cover-build` spans as compile and the rest as tests. A `Phase` line has no hook payload, so it
carries `sid` from the process's `CLAUDE_CODE_SESSION_ID` (a subagent's Bash holds its session's id, the same the hooks log, and
`CLAUDE_CODE_CHILD_SESSION`, but no agent id: observed 2026-11-20, method: this planning agent's own Bash environment against its
lines in the 451 event log), its `make` target and its clone; the reader ties it to the Bash call or background run of that session,
clone and target whose span holds it, and where two such spans overlap, to the one that started last before the phase began. Per
crate is what the runner can time: a coverage build serves a family of crates at once, so its line names the family's crates (a
narrow reading of FR-003's "per crate", named for the plan review).

**D5 - The landing's phases** (FR-003). `land` writes a `Phase` line for each of its steps - `cheap` (the first pass), `gate` (`make
done`), `cohort` (`make cohort-landing`), `claims` (the wait), `push` - and a last `end` line with its exit code and `tasks`, the task
ids it was asked to land (`T=`, split as D16), so a refused landing is counted from the landing's own line (FR-005's rework), not
guessed from a tool response, and D10 and D11 read a landing of a task from that one line, whether the landing ran in the foreground
or in the background.

**D6 - An agent's cost and task** (FR-004; R2). The Agent call's PreToolUse line records `task` from its `description` (else its
prompt's first line). Each `SubagentStop` line records `tok` (`in`, `cached`, `created`, `out`), summed over `agent_transcript_path` with
each `message.id` counted once, `ctx` (its last call's context), and `task` from the agent's meta file. A stop is cumulative; the reader
keeps the last per `aid`.

**D7 - The readers** (FR-005). `where-time` gains the columns tests, compile, gate, land, review, background run and model, from D2 to
D6, and `UNTIL=` (the Makefile passes `--until`); the CRITICAL PATH is the window's wall clock partitioned by what the main session was
doing or waiting on (a wait booked by D3 to its run), and beside it the summed agent-minutes, each agent's span and tokens under its
task; the REWORK counts refused landings (D5's `end` lines with a non-zero code) and plan re-rounds (a task's `spec-fidelity` and
`spec-fidelity-verify` dispatches after its first). `feature-report` reads the same columns through the same functions (one place:
`where_time.rs`'s new `columns` module), keeping its existing `UNTIL=`.

**D8 - Who is a builder** (FR-006; R3). A payload with `agent_id` whose `agent_type` names no `.claude/agents/<agent_type>.md` in the
clone. Measured, this catches every builder that passed the cap and, among defined agents, one call; it also catches a general-purpose
agent dispatched without a task, which is judged by the same cap (the spec defines a builder as "an agent dispatched with a task's
brief, not a defined review agent"; every general-purpose dispatch here is one with a brief, and requiring a `T<n>` in it would let a
builder with an unnamed brief pass). Named for the plan review.

**D9 - The context cap** (FR-006; R2). A new guard, `context_cap_hooks`, PreToolUse `*`. For a builder it reads its transcript's tail
(`<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`, backwards to the last `usage`) and, past `CONTEXT_CAP_TOKENS`
(GUESS, 300,000 tokens, the spec's knob), refuses every tool call but a Write of `<git common dir>/l7r-handoffs/<task or agent id>.md`,
naming that path and the next step: write what is done and what is left, then stop; the session dispatches a fresh builder with it.
The main session and a defined agent are never read. The escape (FR-012): `CONTEXT_OK="<reason>"` in a Bash command, or, for any
tool, a permit the session grants for that agent, `make context-ok AID=<agent id> WHY="<reason>"` (the guard-edit permit's mechanism,
`l7r-guard.sh permit grant context-cap:<agent id> "<reason>"`, recorded in the guard log; a new Makefile target, so held). The handoff
Write is the cap's one exit, so its case runs through the whole guard chain (no `--only`), proving no other guard refuses a write under
the git dir.

**D10 - A builder resumed** (FR-006). The same guard, on SendMessage: `to` is the agent id (R2); refused where that agent is a builder
past the cap, or its task has landed since it was dispatched, naming a fresh dispatch with the handoff file or the next task's brief.
Escape: `CONTEXT_OK` in the message's `summary`.

- **Its dispatch** is the event-log line of the Agent call whose `id` is the agent's meta `toolUseId` (R2), else the agent's first
  logged line (its `aid`), else its transcript's first row.
- **Its task** is found by D2's chain, never by the description alone (a builder with an unnamed brief is still a builder, D8): the
  `T<n>` its meta `description` names; else the `task` its FIRST event-log line carries (by `aid`; never its latest, since D2 stamps a
  line with no `T<n>` by the clone's active task at write time, and with two lanes running, T05 beside T06, a later line can carry the
  other, open task); else the clone's
  `task-starts.jsonl` entry for the feature IN FORCE AT ITS DISPATCH (the last entry before the dispatch time - read at resume time,
  the last entry is today's open task, and a builder of a landed one would pass).
- **A landing** (one definition, D11's too) is a `make land` of the task that SUCCEEDED: D5's `end` line of code 0 whose `tasks` names
  it. The `end` line names its own tasks, so no span is matched: a `run_in_background` landing's call returns at once and its `end`
  falls outside the call. A refused landing is not one. Any such landing after the dispatch
  refuses the resume; so does the task ticked in the feature's `tasks.md` or archived in `tasks-done.md`, whatever the log holds (a
  landing the log missed still refuses).
- **No task found at all** (no `T<n>`, no line carrying one, no `task-starts.jsonl` entry before the dispatch): the LANDING check
  passes, and the pass is written to the guard log as `context-cap: resume, no task` with the agent id, so it leaves a record. The cap
  check does not need a task: a builder past the cap with no task found is still refused.

**D11 - The third `make static`** (FR-007; R6). A new guard, `static_runs_hooks`, PreToolUse Bash, where `invoked` (D1) holds `static`:
it counts the event log's `make: static` PreToolUse lines of this call's task (D2) since its last landing (D10's definition: a `make
land` naming it that succeeded, so a refused landing resets nothing), or, where it has never landed, since its FIRST
`task-starts.jsonl` entry (a task with neither counts every line of it). A later `task-start` resets nothing: 48 of the clone's 498 started tasks have more than one entry (observed
2026-11-20, method: `.git/task-starts.jsonl`'s entries counted per feature and task; R6), so a reset at the last start would let a
second `make task-start` zero the count with no record. The third and later is refused, naming the crate-scoped checks for the crates the
task's delta changes (`l7r_gate_tree`'s delta is the gate's; the guard lists the changed files' crates from `git diff --name-only` of
the merge base), `make static` once before the landing, and `STATIC_OK`. Every session and agent's run counts, the main session's too:
the spec counts runs in a task, not in an agent. Knob `STATIC_RUNS_A_TASK`, GUESS, 2.

**D12 - A run the harness cannot track** (FR-008; R4). In `no_poll_hooks`: a job holding `make` or `cargo` (D1's detector, and
`cargo` at a command position) followed by a lone `&`, or started under `nohup` or `setsid` AT A COMMAND POSITION, or disowned, is
refused naming the Bash tool's `run_in_background`; `DETACH_OK` escapes. DISOWNED: a `disown` at a command position after the job's
`&` in the same command, in any form - bare (the current job), `disown %N`, `disown -h`, `disown -a`, `disown $!` - is refused WHATEVER
`wait` follows, since a disowned job leaves the shell's job table and no `wait` covers it: `sleep 3 & disown; wait` returns in
0.0005 s and `wait %1` after `disown` reports no such job, while `sleep 2 & disown -h; wait` still waits 2.0 s (measured 2026-11-20,
method: `bash -c` runs of the three, timed by `$EPOCHREALTIME`; the plan review measured the first two, round 3). So `disown -h`
alone keeps the job in the table, but FR-008 names `disown` without exception, so it is refused too. The guard does not work out which job a
`disown` names: any `disown` after a make or cargo job's `&` refuses the call. The `&` form passes only where a `wait` that COVERS the job follows
it: `wait` at a command position (never a word, so `make static & echo wait` is refused), a command of the same list as the job's `&`
in the same shell (not in a `( )` or `$( )` of its own: `make static & (wait)` waits for nothing), run unconditionally (not the right
side of `&&` or `||`, not in an `if` or `case` branch the job is outside of: `make static & false && wait` skips it) and not itself
backgrounded (`make static & wait &` returns at once), and either bare (it waits for every job) or
`wait $!` with no other `&` between the job's `&` and the `wait` (so `$!` is still that job: `make static & sleep 5 & wait $!` waits
for the sleep and is refused), or `wait %N` where N is that job's number among the command's backgrounded jobs. Such a call does not
return before the run ends, so the harness tracks it. A wait on a saved pid (`P=$!; ...; wait $P`) is not one of these forms and is
refused: one of five of R4's tracked runs re-read took that form (observed 2026-11-20, method: R4's commands re-read for their `wait`), and it
is written `wait $!` or bare `wait`, or carries `DETACH_OK`. Following the assignment instead was priced and not taken: it is more
parsing for one observed run, and the plan review's fix named the three forms (T01 round 1, 2026-11-20).

**D13 - A main-session wait slower than its check** (FR-008; R5). In `no_poll_hooks`, on both permitted paths - the POLL_OK-escaped
loop and the file-watching wait - before either returns: a payload with no `agent_id` whose loop body's longest `sleep` is over
`POLL_CHECK_S` (GUESS, 60 s) is refused naming the same loop with every sleep at 60 s or less; `SLOW_POLL_OK` escapes. The red fixture
is the observed form (R5).

**D14 - Where the knobs are recorded** (spec Assumptions; R12). Each constant carries `GUESS` and the spec's reason at its point of
change, and `docs/guards.md` gains a knob table (knob, value, label, the data that retunes it: FR-004's tokens, the static counts, the
waits, the shard times). `make tunables` is not extended to the tooling crates: its walk skips them on purpose (claims are the
engine's), and the spec names it only as where retuning happens. Named for the plan review.

**D15 - The deferral's form** (FR-009; R9). `lint::refusal` gains `deferral_unformed`: a `**Found and left?**` item that is not `none`
must carry why it is not fixed in this task, a task id `T<n>` and an order "lands before T<n>", each refused when missing:

- **Both ids name an OPEN task**: an unticked box of the feature's `tasks.md`, judged when `make decide` judges the item. A made-up id
  is refused like a missing one (FR-009's "its filed task id"), and so is a ticked box or an entry of `tasks-done.md`: a deferral to a
  task already done, or ordered before one, defers to nothing.
- **The order's id differs from the deferral's own**: "T123 lands before T123" orders nothing and is refused.
- **Judged once, at the decision.** `lint::refusal` has two callers, `make decide` on the task's section and `make plan-delta` on every
  changed block (observed 2026-11-20, method: its callers read, `rust/gate/crates/plan/src/plan.rs` lines 195 and 245; the tick and
  the landing call neither). So `deferral_unformed` in `lint::refusal` holds the timeless parts - the reason, both ids present, the
  order's id not the deferral's own, both ids filed in `tasks.md` or `tasks-done.md` - and the OPEN test runs in `decide` alone, after
  it. A section already decided is not refused later because a task it names has since landed: a later `plan-delta` over its block
  finds both ids still filed.

An item or fix naming a class of defect
("every writer", "every form", "every file of a kind", "each of the ...", "all ...") must carry a line `observed <date>, method: ...`
saying how every instance was found. The template's `**Found and left?**` placeholder states the form. `DEFER_FORM_OK` on `make
decide` escapes, through `$(LOGESCAPE)`. It holds on the `plan-delta` path too, since `lint::refusal` runs there: `make decide` under
the escape records it in the guard log naming the feature and the task, and `make plan-delta` reads those records and does not run
`deferral_unformed` on that task's section, so a section decided under the escape is not refused when its block later changes;
`make plan-delta` also takes `DEFER_FORM_OK` itself, through `$(LOGESCAPE)` (a held Makefile line), for a section never decided. No
open section of any plan is refused by it today (R9).

**D16 - The landing's commas and task-add's quick check** (FR-011; R7, R8). `land.rs::main` splits `T=` on commas and whitespace.
`task-add` runs `make quick`'s checks after it writes; on a red it withdraws what it wrote and runs them again, and COMPARES the two
runs' failures: where the with-line run has any failure the without-line run lacks, the line stays withdrawn and task-add refuses,
naming those failures and that the line was withdrawn; only where the failures are the same is the line restored, the failure
reported as already there. Two things make the comparison real:

- **Every check runs to its own end in both runs.** The `quick:` recipe is sequential lines, and make stops at the first that fails, so
  a failure already there in an earlier check (ruff, say) would hide the line's own in a later one (spec-lint) and the two runs would
  look the same. task-add takes the check lines from `make -n quick` (the recipe stays the one list), sets aside the `$(STATE)
  green-local` stamp and the closing `printf`, and runs each line as its own process. Not `make -i quick`: it would still stamp quick
  green.
- **Findings are compared, not checks.** A failure is a check's line and each finding it prints, with line and column numbers masked
  (the new line shifts every later finding in the file it writes), compared as a multiset; a check that fails in both runs with a
  new finding in the with-line run is a new failure.

`QUICK_OK` on `make task-add` escapes, through `$(LOGESCAPE)`.

**D17 - Shards** (FR-010; R10). A suite may be split into `tests/hooks/test-<name>.<k>.sh` beside nothing else of that name: the runner
(`make hooks-test` and `tests/hooks/hookrun.sh`) treats each shard as a job keyed by the suite's stamp key and stamps the suite green
when every shard is, and its companion check accepts shards for a guard's companion. `entry-gate.sh` splits by its two cases; the
other two by their case groups, until each shard's kept seconds is about 20 or less in a full run (`SHARD_BAR_S`, GUESS, measured as
`.git/hooks-test/<shard>.s`, never a gate).

## Task sections

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T03 (FR-001: 210 of the window's tool-minutes booked "other tool", observed 2026-11-20, method: the `ms` of the log's PostToolUse lines since 14:00Z summed by `cat` - research R1)

- **Approach**: D2, in the writer. Held: `rust/guard/src/guards/event_log_hooks.rs` (`make guard-edit` first). The table's rows are
  `data-model.md`'s, finished from the Makefile's targets, `format`, `render-sync` and `map` among them (R1's largest after the tests),
  each row commented with why. Red first: `make static`, `make rust-test`, `make hooks-test` and `l7r-gate.sh rust test --crate
  rust/guard` class as tests, `make land` as land, `make frobnicate` as other; a subagent's call carries its meta file's task, a `make
  land T=T05` line carries `T05`, a main-session call the clone's active task.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the table, the task field | n/a - no map | n/a | none | n/a |

### T03 Approach (checklist part A)

1. **The goal, in the world.** No map changes; every make run of a window is booked under its bucket and its task.
2. **The constraints.** FR-001; D2; the hook never refuses and never prints; one meta-file read a subagent call at most.
3. **Where each comes from.** G: the approved categories; O: research R1 (the targets and their minutes), R2 (the meta file).
4. **Do they describe the world here?** R1's minutes by target name the rows that matter most.
5. **The order.** After T02; before T07, T08 and T14, which read the table and the task field.
6. **The exits.** Green: the red cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The red cases green; a real `make static` in the clone logs `cat` tests and its task.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new rows and a new field.

**Found and left?**
- The bundle crate's coverage depends on the caller's environment. With `SPECIFY_FEATURE` exported, `make static` fails cover on
  `rust/gate/crates/bundle/src/record/helpers.rs` line 537: `consulted::context`'s error arm, which a test reaches only when no
  feature is set. Without the export the crate's cover is clean (observed 2026-11-20, method: `make static` with and without the
  export, then `l7r-gate.sh rust cover --crate rust/gate/crates/bundle`). Not fixed here because the crate is outside T03's files; filed as T24 (the test given its own
  environment), which lands before T08 reads the columns.
- Two features' lanes share this clone, and `.specify/feature.json` names 449. So the hook writes this clone's lines to the 449 log,
  whichever feature's work they are. A 451 builder's `T03` in the 449 log then reads as 449's T03: the `task` field names the task but
  not its feature. Not fixed here because the line's feature is chosen where the line is filed, the same field T26 corrects: filed as T26 (each line
  filed under the feature of the task it carries), which lands before T07, T08 and T14, the readers of the task field. The lines written
  between T03's landing and T26's are re-filed by T26 itself: a line whose task names no task of its log's feature but one of another
  feature's is moved to that feature's log - the two features' ids never collide (451's are two digits, `T03`; 449's three, `T003`;
  observed 2026-11-20, method: the task ids of both features' tasks.md and tasks-done.md) - so no reader books one feature's time to the other's.
- An Agent dispatch line with no `T=` carries the clone's active task (its dispatcher's) until T07 reads the task from its
  `description` (D6).
- The live hooks run the mirror's guard binary, so lines written before this lands still say `other tool`. "Done, measured" was
  replayed through the clone's hook shim: this session's `make static` call logged `cat` `tests` and `task` `T03` (observed
  2026-11-20, method: the call's payload piped to `tests/hooks/event-log-hooks.sh` with `L7R_EVENTS_DIR` pointed at a scratch
  directory). It is owed again on a live line after landing.
- `T="T1,T2"` books only `T1` (T18).
- The readers still book by the frozen `cat`, and `where_time.rs` only learned the new `tests` word. Booking by `make` through
  `bucket_of` is T08's.
- `data-model.md`'s rows `push-checks` and `make-docs` are not make targets. They are kept as rows that never match.

**Performance work?** no

### T04 (FR-002: no line marks a background run's end, so a wait cannot be booked to the run behind it - research R2)

- **Approach**: D3's writer half: `bg` on a backgrounded PostToolUse, the `BgEnd` line from a notification prompt, `inflight` on Stop
  and SubagentStop; D4's `append_row`, public for the gate's tools; and the one reader's guard against the new kinds:
  `rust/gate/crates/measure/src/measure/events.rs::load_events` sets `BgEnd` and `Phase` lines aside from the time-gap stream (else a
  `Phase` line inside a `make static` call would book the rest of the call "thinking", and a line of no session would form a session of
  its own, the T207 failure) and returns them for T08 and T09. Held: `rust/guard/src/guards/event_log_hooks.rs` (`make guard-edit`
  first); the tool fields move to `event_log_hooks/fields.rs` if the file would pass the file cap. Red first: a fixture notification
  prompt (R2's observed shell form) writes a `BgEnd` with its tool-use id, status and exit code; an agent notification writes none; a
  Stop payload with two `background_tasks` writes both under `inflight`; a log holding a `BgEnd` and a `Phase` line gives `make
  where-time` and `make feature-report` the tables the log without them gives.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the end line and the in-flight runs | n/a - no map | n/a | none | n/a |

### T04 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a background run's start and end are both in the log.
2. **The constraints.** FR-002; D3, D4; the hook never refuses and never prints; today's readers unchanged by the new kinds until T08 and T09 read them.
3. **Where each comes from.** G: the GM's approval of "logs that end from its completion notice"; O: research R2 (the schema, the notification texts).
4. **Do they describe the world here?** The notification's `<tool-use-id>` was read from the window's own transcript queue rows (observed 2026-11-20, method: research R2).
5. **The order.** After T03; before T05 and T06 (`append_row`) and T09, which reads the lines.
6. **The exits.** Green: the fixture cases pass. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The three red cases green; one real background run in the clone writes its `BgEnd` (read off the log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - new lines, no defect.

**Found and left?** none

**Performance work?** no

### T05 (FR-003: a make run's compile, tests and coverage are one span in the log - research R6)

- **Approach**: D4's rust half in `rust/gate/crates/rustc` (not held): a `Phase` line at each step's end through `append_row`. Red
  first: a fixture crate's `rust test` and `rust cover` runs in a scratch tree write `build`, `test`, `cover-build` and `cover-run`
  lines whose spans nest inside the call's.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the rust checks' phase lines | n/a - no map | n/a | none | n/a |

### T05 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a `make static` run's compile and test time are told apart.
2. **The constraints.** FR-003; D4; a kept green result writes no phase (it ran nothing).
3. **Where each comes from.** G: the GM's "how much time are we spending on recompiling things"; O: research R6 (family builds, side-by-side runs).
4. **Do they describe the world here?** R6 read the build and run sites in `cover.rs`, `side.rs` and `Verdict::ask`.
5. **The order.** After T04 (`append_row`).
6. **The exits.** Green: the fixture's phase lines. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture case green; one real `make rust-test CRATE=rust/gate/crates/plan` writes its phases.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T06 (FR-003: a landing's cheap pass, gate, claims round and push are one span - the spec's User Story 1)

- **Approach**: D5 in `rust/gate/crates/land` (not held). Red first: the land tests' fake world writes `cheap`, `gate`, `claims`,
  `push` and `end` lines in order, a refused landing's `end` with its non-zero code; a landing of `T="T1 T2"` writes an `end` whose
  `tasks` is both ids (T13 and T14 read a landing from this line).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the landing's phase lines | n/a - no map | n/a | none | n/a |

### T06 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a landing's time is split by step and a refused one is counted.
2. **The constraints.** FR-003; D5; a failed landing still writes its `end`.
3. **Where each comes from.** G: the approved "make land its phases' seconds"; O: `land.rs`'s pass order read.
4. **Do they describe the world here?** The steps are `land.rs`'s own passes.
5. **The order.** After T04.
6. **The exits.** Green: the land tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fake-world case green; this task's own landing writes its phases (read off the log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T07 (FR-004: no agent's token cost is logged, nor the task it served - research R2)

- **Approach**: D6 in the writer. Held: `rust/guard/src/guards/event_log_hooks.rs` (`make guard-edit` first). Red first: a fixture
  agent transcript with a repeated `message.id` sums each call once; its meta file's "T202: ..." description gives `task: T202`; an
  Agent dispatch "T08: ..." records `task: T08`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the agent's cost and task | n/a - no map | n/a | none | n/a |

### T07 Approach (checklist part A)

1. **The goal, in the world.** No map changes; each agent's tokens are in the log under its task.
2. **The constraints.** FR-004; D6; the hook never refuses.
3. **Where each comes from.** G: the approved "records it at each agent's stop"; O: research R2 (the stop payload, the dedup, the meta file).
4. **Do they describe the world here?** R2 summed a real builder transcript with the dedup.
5. **The order.** After T04; before T10.
6. **The exits.** Green: the fixture cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture cases green; one real agent's stop in the clone carries `tok` (read off the log).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T08 (FR-005: `make where-time` booked most of the window as "waiting on work" and every gate and test column zero - the spec's Why)

- **Approach**: D7's columns in `rust/gate/crates/measure` (`where_time.rs` and a new `where_time/columns.rs`, not held): D2's booking
  by `make`, D4's compile split, and `UNTIL=`. Held: the root `Makefile` (the `where-time` recipe's `--until`; `make guard-edit
  FILE=Makefile` first). Red first: User Story 1's acceptance scenarios 1 and 3 as fixtures - `make static`, `make rust-test` and `make
  hooks-test` under tests; a `make static` whose cover-build phase is two thirds of its span split into compile and tests - and a past
  log re-booked by its `make` field.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the columns, the compile split, UNTIL | n/a - no map | n/a | none | n/a |

### T08 Approach (checklist part A)

1. **The goal, in the world.** No map changes; one command reads off where a window's time went.
2. **The constraints.** FR-005; SC-001; D2, D4, D7; the arbiter's bundle and `feature-report` read the same event reader unchanged.
3. **Where each comes from.** G: the GM's retrospective request; O: research R1 (the readers read the frozen `cat`), R6.
4. **Do they describe the world here?** The fixture is built from R2's and R6's observed line shapes.
5. **The order.** After T02-T07.
6. **The exits.** Green: the fixture sums. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture green; `make where-time F=451 SINCE=<this task's start> UNTIL=<now>` books this task's own runs under their columns.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The readers book by the frozen `cat`, so a past log can never be re-booked - a tool answering wrongly; fixed by booking by `make`.

**Found and left?** none

**Performance work?** no

### T09 (FR-002, FR-005: a wait cannot be booked to the run behind it - the spec's User Story 1 scenario 2, research R2)

- **Approach**: D3's reader half in `where_time/columns.rs` (not held): a launch paired with its end - the log's `BgEnd`, else the
  subagent transcript's `queued_command` row holding its `<tool-use-id>`, else open to the window's end - and a between-turns wait
  booked to the runs its `Stop` line names `inflight`, else to the launch whose span holds it. Red first: a background `make land`, its
  `BgEnd` and the wait it caused booked to land; a subagent's run ended by its transcript's attachment; a run with no end booked open
  from its start, never zero.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the background column | n/a - no map | n/a | none | n/a |

### T09 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a wait is booked to the run that caused it.
2. **The constraints.** FR-002, FR-005; D3, D7; the spec's edge case (a run whose notice never came is open, not zero).
3. **Where each comes from.** G: the approved "which run a wait was waiting on"; O: research R2 (where each kind of end is found).
4. **Do they describe the world here?** R2 found the subagent ends in the subagent transcripts, not in any hook.
5. **The order.** After T08.
6. **The exits.** Green: the three fixture cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture green; a real background run in the clone booked to its target.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T10 (FR-005: the wall clock on the critical path apart from the agent-minutes, the agents' tokens, the rework)

- **Approach**: D7's critical path, agents and rework in `where_time/columns.rs` (not held). Red first: a fixture with two agents
  overlapping a main-session wait books the wait once on the critical path and both agents' spans and tokens under their tasks; a
  landing `end` with code 1 and a second `spec-fidelity` dispatch count as rework.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the critical path, the agents, the rework | n/a - no map | n/a | none | n/a |

### T10 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the report says what held the day and what was spent beside it.
2. **The constraints.** FR-005; D5, D6, D7.
3. **Where each comes from.** G: the approved breakdown; O: the 2026-11-19 retrospective's own split of wall clock and agent-minutes (spec Why).
4. **Do they describe the world here?** The fixture overlaps agents as the window's builders did.
5. **The order.** After T09.
6. **The exits.** Green: the fixture. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture green.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T11 (FR-005: `make feature-report` reads the same columns)

- **Approach**: `feature_report.rs` and `feature_report/tables.rs` (not held) read T08 and T10's `columns` in process, its `UNTIL=`
  kept. Red first: the same fixture through `feature-report` gives the same sums as through `where-time`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the report's columns | n/a - no map | n/a | none | n/a |

### T11 Approach (checklist part A)

1. **The goal, in the world.** No map changes; both reports agree.
2. **The constraints.** FR-005; D7 (one place).
3. **Where each comes from.** G: the approved "where-time and feature-report read those new lines".
4. **Do they describe the world here?** One fixture read by both.
5. **The order.** After T10.
6. **The exits.** Green: equal sums. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture's two readings equal; `make feature-report F=451` shows the columns.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T12 (FR-006: builders past a large context slowed the window's critical path - the spec's User Story 2, research R3)

- **Approach**: D8 and D9, a new guard `context_cap_hooks`. Held: `rust/guard/src/guards/context_cap_hooks.rs` (new),
  `rust/guard/src/guards.rs`, `rust/guard/src/lib.rs` (its place in `guards()`, after `event_log_hooks`) (`make guard-edit` on each
  first); with its link `tests/hooks/context-cap-hooks.sh` -> `guard-shim.sh`, its suite `tests/hooks/test-context-cap-hooks.sh`, its
  `docs/guards.md` row and knob, its `rust/guard/CLAUDE.md` mention. FIRST STEP: capture one real subagent PreToolUse payload (a
  one-shot dump from the guard under `L7R_GUARD_DUMP`, removed before the landing) and pin it as the fixture, confirming `agent_type`
  and the derived transcript path (R2's "schema, not yet observed"). Red first: a builder fixture past the cap refused naming the
  handoff path; under it passes; its Write of the handoff passes, alone and through the whole guard chain; a defined agent past it
  passes; the main session passes; `CONTEXT_OK` in a Bash call and a `make context-ok` permit each pass and are recorded. Held too: the
  root `Makefile` (`make context-ok`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the cap | n/a - no map | n/a | none | n/a |

### T12 Approach (checklist part A)

1. **The goal, in the world.** No map changes; no builder works on with a context past the cap.
2. **The constraints.** FR-006, FR-012; D8, D9; constitution XVIII (fires and stays quiet, escape first).
3. **Where each comes from.** G: the approved "a fresh builder per stage, with a handoff file"; R: none; O: research R2, R3; the cap a GUESS knob (spec FR-006).
4. **Do they describe the world here?** R3 counted which agents pass the cap by type.
5. **The order.** After T11; the first refusal.
6. **The exits.** Green: the five cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's five cases; the check deleted, the firing case red.
10. **Before moving a constant.** n/a - a new knob, labeled GUESS.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a - a new refusal.

**Found and left?** none

**Performance work?** no

### T13 (FR-006: a SendMessage resuming a builder past the cap, or one whose task has landed)

- **Approach**: D10 in `context_cap_hooks`. Held: `rust/guard/src/guards/context_cap_hooks.rs` (`make guard-edit` first). Red first:
  a SendMessage to a builder fixture past the cap refused; to one whose task is ticked refused; to one whose meta `description` names
  NO `T<n>` (its task found through D2's chain, the `task-starts.jsonl` entry in force at its dispatch) and whose task landed after its
  dispatch refused, while a later `task-starts.jsonl` entry for another, open task stands in the log and the builder's later lines
  carry that open task (its first line's task is the one read); to one whose task landed in a background `make land` (its `end` line
  after the land call returned) refused; to one whose task's only landing
  after its dispatch was refused (`end` code 1) passes; to one under the cap with no task found anywhere passes and writes its `no task`
  record; to one past the cap with no task found refused (the cap check needs no task); to a
  defined agent passes; to a builder under the cap with its task open passes; `CONTEXT_OK` in the summary passes and is recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the resume | n/a - no map | n/a | none | n/a |

### T13 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a builder serves one task and stays small.
2. **The constraints.** FR-006, FR-012; D10.
3. **Where each comes from.** G: the approved "one task a builder"; O: research R2 (`to` is the agent id).
4. **Do they describe the world here?** R2 read the window's SendMessage inputs.
5. **The order.** After T12, and after T03 (the `task` on each line) and T06 (the landing's `end` line naming its tasks).
6. **The exits.** Green: the ten cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases; the check deleted, the firing cases red.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T14 (FR-007: `make static` was the edit loop - the spec's User Story 3)

- **Approach**: D11, a new guard `static_runs_hooks`. Held: `rust/guard/src/guards/static_runs_hooks.rs` (new),
  `rust/guard/src/guards.rs`, `rust/guard/src/lib.rs` (`make guard-edit` on each first); its link, suite, `docs/guards.md` row and knob,
  `rust/guard/CLAUDE.md` mention. Red first: a fixture log with two `make static` lines of T06 after its start refuses a third, naming
  the changed crates' checks; a run after a landing of T06 that succeeded (an `end` line of code 0 whose `tasks` names T06, written
  after a background land call returned) passes; a run after a refused landing of
  T06 (`end` code 1) counts on and a third is refused; a task with no landing counts from its FIRST start; two runs of T06, then a
  second `task-starts.jsonl` entry for T06, then a third run: refused (a second `task-start` resets nothing); `STATIC_OK="..."` passes
  and is recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the count | n/a - no map | n/a | none | n/a |

### T14 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the crate-scoped checks are the edit loop, `make static` the check before landing.
2. **The constraints.** FR-007, FR-012; D2 (the task field), D11.
3. **Where each comes from.** G: the approved "a crate-scoped check while iterating, with make static once at the end"; O: research R6.
4. **Do they describe the world here?** R6 timed the log read the guard makes.
5. **The order.** After T13; needs T03's `task` on each line and T06's landing `end` line naming its tasks.
6. **The exits.** Green: the six cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases; the check deleted, the firing case red.
10. **Before moving a constant.** n/a - a new knob, labeled GUESS.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T15 (FR-008: T225's `make static` with a plain `&` sat untracked - the spec's User Story 4, research R4)

- **Approach**: D12 in `no_poll_hooks`. Held: `rust/guard/src/guards/no_poll_hooks.rs` (`make guard-edit` first). Red first: R4's
  observed `(make static > /tmp/t225-static.log 2>&1; echo END >> ...) & sleep 1` refused naming `run_in_background`; `nohup make
  rust-test` refused; `for c in git setsid make; do ...` passes (a word, not a command); `make static > log 2>&1 & wait $!` passes;
  `make static & echo wait` refused (a `wait` that is a word); `make static & sleep 5 & wait $!` refused (`$!` names the sleep); `make
  static & P=$!; wait $P` refused (a saved pid, D12); `make static & (wait)` refused (another shell's wait); `make static & false &&
  wait` refused (a conditional wait); `make static & wait &` refused (a backgrounded wait); `(make static > log) & make decide F=449
  T=T121 | tail -40; wait` passes (R4's observed bare form); `sleep 30 & make static & wait %2` passes (`%2` names the make job,
  the sleep no make or cargo); `setsid make static` refused; `make static & disown` refused; `make static & disown; wait` and `make static & disown;
  wait $!` refused, each going red when the disown check is deleted (the covering wait would pass them); `make static & disown -h;
  wait` and `make static & disown %1; wait` refused; `{ make static; } &`, `VAR=x make static &` and `env X=1 make
  static &` each refused (D1's detector reads the target past `{`, `VAR=` and `env`); `make static` with `run_in_background` passes; `DETACH_OK="..."` passes and is
  recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the detached run | n/a - no map | n/a | none | n/a |

### T15 Approach (checklist part A)

1. **The goal, in the world.** No map changes; every long run is one whose end wakes the session.
2. **The constraints.** FR-008, FR-012; D1 (the detector), D12; constitution XVIII (a mention is not an invocation).
3. **Where each comes from.** G: the approved "a guard refusing that pattern"; O: research R4.
4. **Do they describe the world here?** R4's cases are the session's own commands.
5. **The order.** After T14.
6. **The exits.** Green: the twenty-three cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases; the check deleted, the firing cases red.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T16 (FR-008: the main session's waits checked every 420 to 600 s, observed 2026-11-19, method: the wait commands of the main session's transcript - the spec's User Story 4, research R5)

- **Approach**: D13 in `no_poll_hooks`. Held: `rust/guard/src/guards/no_poll_hooks.rs` (`make guard-edit` first). Red first: R5's
  observed POLL_OK loop with `sleep 60` then `sleep 420`, from the main session, refused naming the knob's form; the same loop at
  `sleep 60` throughout passes; the same slow loop from a subagent (`agent_id` set) passes; a file-watching wait from the main
  session sleeping past the knob refused; `SLOW_POLL_OK="..."` passes and is recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the slow wait | n/a - no map | n/a | none | n/a |

### T16 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the main session learns of an idle agent within a minute.
2. **The constraints.** FR-008, FR-012; D13; the existing no-poll cases unchanged.
3. **Where each comes from.** G: the approved "a shorter poll loop on my side", made a refusal by the GM's "real enforcement"; O: research R5.
4. **Do they describe the world here?** R5's loops are the session's own.
5. **The order.** After T15 (the same file).
6. **The exits.** Green: the five cases and the no-poll suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases; the check deleted, the firing cases red.
10. **Before moving a constant.** n/a - a new knob, labeled GUESS.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T17 (FR-009: two of the window's first-round plan-review blocks were deferrals with no order - the spec's User Story 5)

- **Approach**: D15 in `rust/gate/crates/plan` (`lint.rs`, `plan.rs::decide` for the open test, `template.rs`; not held) and `make decide`'s `DEFER_FORM_OK`. Held: the root
  `Makefile` (`make guard-edit FILE=Makefile` first). Red first: User Story 5's five cases and seven more - a deferral with no task id
  refused; task and order but no reason refused; a reason, `T123` and "lands before T124" passes, both unticked boxes of the fixture
  feature's `tasks.md`; `none` passes; a class fix with no labeled line refused and with one passes; a deferral whose task id `T999` is
  filed nowhere refused; one whose "lands before" id is filed nowhere refused; one whose own id is a ticked box (or in
  `tasks-done.md`) refused; one whose "lands before" id is ticked (or in `tasks-done.md`) refused; "T123 lands before T123" refused; a
  reason and a filed open task id with no "lands before" refused; and the passing section, decided, then T124 ticked: `make
  plan-delta` over its block does not refuse it; a deferral with no order decided under `DEFER_FORM_OK`, then its block changed:
  `make plan-delta` does not refuse it (the guard log's escape record read); `DEFER_FORM_OK` on `make plan-delta` passes and is
  recorded.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the deferral's form | n/a - no map | n/a | none | n/a |

### T17 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a deferral is fixed in the task by default, and a class fix is complete up front.
2. **The constraints.** FR-009, FR-012; D15; constitution XIV.
3. **Where each comes from.** G: the approved "briefs that default to fixing in the task, and that ask for full coverage up front"; O: research R9.
4. **Do they describe the world here?** R9 found no open section the rule would refuse.
5. **The order.** After T16.
6. **The exits.** Green: the fourteen cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The plan crate's cases; the check deleted, the firing cases red.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T18 (FR-011: `T="T1,T2"` read as one task - research R7)

- **Approach**: D16's first half in `rust/gate/crates/land/src/land.rs` (not held) and `make land`'s help. Red first: `T="T1,T2"`
  lands both in the land tests' fake world; `T="T1, T2"` too.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the commas | n/a - no map | n/a | none | n/a |

### T18 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a comma list lands.
2. **The constraints.** FR-011; D16.
3. **Where each comes from.** G: the approved "Accept commas in T="; O: research R7.
4. **Do they describe the world here?** Feature 448's plan wrote the comma form.
5. **The order.** After T17.
6. **The exits.** Green: the two cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The land tests' cases.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A comma list is refused as one unknown task - valid input refused, a defect.

**Found and left?** none

**Performance work?** no

### T19 (FR-011: a task-add line that `make quick` refuses was found only at the landing - research R8)

- **Approach**: D16's second half in `rust/gate/crates/task/src/task_add.rs` (not held) and `make task-add`'s `QUICK_OK`. Held: the root
  `Makefile` (`make guard-edit FILE=Makefile` first). Red first: a fixture task-add line citing a bare requirement id another feature defines is
  withdrawn and refused; a clean line stays; a quick already red for another reason in an EARLIER check (a fixture ruff failure) plus
  the line's own spec-lint failure: the line withdrawn and refused, naming the spec-lint failure alone (the case a sequential `make
  quick` would hide); a quick already red where the line adds no failure - the existing finding sits below what task-add wrote in the
  same file, its line number shifted - keeps the line and reports the failure as already there.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the quick check | n/a - no map | n/a | none | n/a |

### T19 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a task line that would refuse a landing never lands in `tasks.md`.
2. **The constraints.** FR-011, FR-012; D16.
3. **Where each comes from.** G: the approved "run make quick after task-add"; O: research R8.
4. **Do they describe the world here?** R8 read the crates task-add builds on.
5. **The order.** After T18.
6. **The exits.** Green: the four cases. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The task crate's cases; the check deleted, the firing case red.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

### T20 (FR-010: three suites set the floor of every `make hooks-test` - research R10)

- **Approach**: D17's runner and the first split. Held: the root `Makefile` (`make guard-edit FILE=Makefile` first); not held:
  `tests/hooks/hookrun.sh`, `tests/hooks/test-entry-gate.sh` split into `test-entry-gate.1.sh` and `.2.sh` by its two cases. Red first:
  a scratch roster with a sharded fixture suite runs both shards, stamps the suite only when both are green, and its companion check
  passes.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the shard form, entry-gate | n/a - no map | n/a | none | n/a |

### T20 Approach (checklist part A)

1. **The goal, in the world.** No map changes; no one suite holds the run's wall time.
2. **The constraints.** FR-010, SC-004; D17; every case of the split suite still runs.
3. **Where each comes from.** G: the approved "Split the three slowest hook suites"; O: research R10.
4. **Do they describe the world here?** R10 read the kept seconds of a full run.
5. **The order.** After T19.
6. **The exits.** Green: each shard's kept seconds about 20 or less in a full run. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test HOOKS_ALL=1`, then `.git/hooks-test/test-entry-gate.*.s` read.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** yes - its answers below.

### T20 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** One suite's cases run one after another inside its job.
2. **Removes work, or only moves it?** Moves it onto idle jobs; the cases are unchanged.
3. **What do you expect it to save, and why?** The run's wall time falls toward the next slowest suite's.
4. **How does the work grow with the settlement?** n/a - no settlement.
5. **What did the before and after show, and under what conditions?** The kept seconds of a full run before and after, with the host's load.
6. **Did any map move, and does it still keep the research?** No map.

### T21 (FR-010: the other two of the three slowest suites)

- **Approach**: D17's split of `tests/hooks/test-l7r-gate.sh` and `tests/hooks/test-sync-with-main.sh` (not held) by their case groups.
  Red first: none new - every case of both suites still runs (the case count before and after equal) and each shard is green.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the two splits | n/a - no map | n/a | none | n/a |

### T21 Approach (checklist part A)

1. **The goal, in the world.** No map changes; no shard past the bar.
2. **The constraints.** FR-010, SC-004; D17.
3. **Where each comes from.** G: the approved split; O: research R10.
4. **Do they describe the world here?** Measured in the same full run as T20.
5. **The order.** After T20.
6. **The exits.** Green: each shard's kept seconds about 20 or less in a full run. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make hooks-test HOOKS_ALL=1`, then the shards' `.s` files read.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** yes - as T20's.

### T22 (the close: SC-001, SC-002, SC-005 on real work, and the feature report)

- **Approach**: after T02-T21 have landed and a full day of work has run on them: `make where-time F=<the day's feature> SINCE= UNTIL=`
  read against SC-001; the day's per-task table reproduced from the log against a hand join of the transcripts for SC-002; the static
  runs per task and the builders' largest contexts read for SC-005, each escape listed; `docs/guards.md`'s knob table checked complete;
  `make feature-report F=451 WRITE=1`.

### T22 Approach (checklist part A)

1. **The goal, in the world.** No map changes; the retrospective is one command and the six fixes hold.
2. **The constraints.** SC-001, SC-002, SC-003, SC-005; D14.
3. **Where each comes from.** G: the GM's request; the bars are the spec's GUESS targets.
4. **Do they describe the world here?** Measured on the first full day after landing.
5. **The order.** Last.
6. **The exits.** Green: the measurements recorded in `report.md`, each against its bar; a bar missed is reported with its number and the knob it retunes. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `report.md` written by `make feature-report F=451 WRITE=1`, with the three measurements.
10. **Before moving a constant.** A knob retuned names its data and its old and new value in `docs/guards.md`.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** no

## Project Structure

### Documentation (this feature)

```text
specs/451-time-retro-and-efficiency/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/refusals.md
└── tasks.md
```

### Source Code

```text
rust/guard/src/shared/make.rs                       # T02 (held)
rust/guard/src/guards/event_log_hooks.rs (+ fields.rs)   # T02, T04, T07 (held)
rust/guard/src/guards/context_cap_hooks.rs          # T12, T13 (held, new)
rust/guard/src/guards/static_runs_hooks.rs          # T14 (held, new)
rust/guard/src/guards/no_poll_hooks.rs              # T15, T16 (held)
rust/guard/src/{guards.rs,lib.rs}                   # T12, T14 (held)
rust/gate/crates/rustc/src/rustc/{cover,side,kept}.rs   # T05
rust/gate/crates/land/src/land.rs                   # T06, T18
rust/gate/crates/measure/src/measure/where_time.rs (+ columns.rs), feature_report*   # T08-T11
rust/gate/crates/plan/src/plan/{lint,template}.rs   # T17
rust/gate/crates/task/src/task_add.rs               # T19
Makefile                                            # T08, T17, T19, T20 (held)
tests/hooks/{hookrun.sh,test-entry-gate*.sh,test-l7r-gate*.sh,test-sync-with-main*.sh,test-context-cap-hooks.sh,test-static-runs-hooks.sh}
docs/guards.md, rust/guard/CLAUDE.md, rust/gate/CLAUDE.md
```

**Structure Decision**: the existing guard and gate crates; two new guard modules, nothing else new.

## Complexity Tracking

None.

### T23 (two builders' cargo runs in one clone corrupted each other's coverage: T02's `make static` beside T234's cargo failed on corrupt or missing coverage profiles in seven crates, observed 2026-11-20, method: T02's `make static` log)

- **Approach**: every `l7r-gate rust <cmd>` (`l7r-rust`) joins a record in each directory it writes - the clone's target directory
  `~/.cache/l7r-cargo-target/<clone>` (the coverage families' `cover-*/view/<crate>` directories are under it), and the cargo target
  and coverage directory an override names, sorted - for its whole length: `rust-checks-run.json`, edited under the short `flock` of
  `rust-checks-run.lock` (`l7r_guard::shared::tool::flock_within`, no guard source edited). A RUN is the outermost `make` above the
  process (`/proc`'s parent chain), so the checks one `make done` runs side by side (`static` in the background beside `counters-inert`
  at `rust-only`) and a run nested in a run's tests share it; with no `make` above, the process is its own run. A member is a process by
  pid and start time, gone when the process is, so a killed run leaves nothing to clear. Another run's live member is waited for: a line
  on stderr at once and every 30 s (a GUESS knob) naming the holder (pid, its check, its run's make line and pid, since when) and the seconds waited;
  past the ceiling (`L7R_RUST_LOCK_CEILING`, default 1800 s, a GUESS knob) the check refuses, naming the holder and `kill <run pid>`. A usage error
  takes no lock. The lock is per process, not per crate: `rustc/side.rs`' and the coverage pass's threads run inside it. New:
  `rust/gate/crates/rustc/src/rustc/runlock.rs`, its tests `rustc/tests/runlock.rs`; `rustc.rs`' `cli` goes through `locked_dispatch`.
  Red first: `two_runs_in_one_target_directory_take_turns` - two runs of `lint` over a two-crate fixture on one scratch target, a fake
  cargo that notes an entry while another call is inside it:
  - before (`locked_dispatch` a bare `dispatch`): 3 overlaps, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/rustc`).
  - after: 0 overlaps, 61 tests in 1.16 s, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/rustc`).
  - the two takers given one run id: 5 overlaps, measured 2026-11-20 (`make rust-test`, the red still firing at the 0.1 s fake).
  Real cargo, 12 pairs of concurrent `rust cover --crate tests/fixtures/rust/fixture` (`L7R_RUST_FRESH=1`, one scratch target a pair):
  - pre-T23 binary: 2 of 12 pairs failed, measured 2026-11-20 (`/tmp/t23/pair.sh`, `t02-base`'s `l7r-rust`).
  - their failure: `llvm-cov` "failed to load coverage ... No such file or directory", observed 2026-11-20, method: the pair's stderr.
  - with the lock: 0 of 12 failed, 12 of 12 second runs printed a wait, measured 2026-11-20 (`/tmp/t23/pair.sh`, this tree's binary).
  The `make done` shape, `rust cover` and `rust test-counters` started together under one parent named `make`:
  - one run joined, 0 wait lines, both exit 0, measured 2026-11-20 (`/tmp/t23/side-inner.sh` under a copy of bash named `make`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the run's lock | n/a - no map | n/a | none | n/a |

### T23 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a builder's Rust checks never share a target directory with another builder's run
   at the same moment, so a red coverage result is the code's, never a collision.
2. **The constraints.** T23's line (one lock a target directory for the length of a run, the second waiting named and timed rather
   than racing, red first with two concurrent runs); `make done` and `make static` keep running their checks side by side; the
   time rule (what a single run pays measured).
3. **Where each comes from.** O: the real-cargo collisions above; the task as filed (T23's line); O: T02's failed `make static`:
   seven crates' coverage profiles corrupt or missing, observed 2026-11-20, method: T02's `make static` log.
4. **Do they describe the world here?** The cover pass's `view/<crate>` reset (`rustc/cover.rs` `run_one`) and the test binaries run
   directly (`side.rs`, `cover.rs`) are outside cargo's own build-directory lock; the pre-T23 binary's failure named exactly the
   removed `view` binary.
5. **The order.** Independent of T03-T22; before any other task's `make static` runs beside a builder's in this clone.
6. **The exits.** Green: the red-first test green, `make rust-test` on the crate, `make quick`, `make static`, `make hooks-test`.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The runlock tests green and the crate at 100% of its lines (measured 2026-11-20 (`make static`, its cover step)):
   - 9 runlock tests, 61 of the crate's, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/rustc`; `make static` cover).
   - the lock's cost, 2.2 ms median a call, measured 2026-11-20 (one binary with a temporary lock-off switch, 60 alternating runs each).
   - with the lock 129.03 ms median, p90 136.45 ms, measured 2026-11-20 (`rust test --crate tests/fixtures/rust/fixture`, kept result).
   - without it 126.85 ms median, p90 136.28 ms, measured 2026-11-20 (the same runs, the switch on).
   - `make static`, 4 calls, so about 9 ms of it: 7 s, measured 2026-11-20 (`make static` wall clock, kept results standing).
10. **Before moving a constant.** n/a - new knobs, each labeled GUESS beside it: the ceiling 1800 s (`L7R_RUST_LOCK_CEILING`), the
    30 s between wait lines, the 0.5 s poll, the record lock's 10 s.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of a builder's log sees a wait line instead of a coverage failure that was another run's; nothing
    on a map.

**Found and left?** none

**Performance work?** no

### T24 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T24 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or each item with its visible effect or the research finding it breaks; an item with neither is not a defect and is not filed>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T25 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T25 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or each item with its visible effect or the research finding it breaks; an item with neither is not a defect and is not filed>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T26 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T26 Approach (checklist part A)

1. **The goal, in the world.** <the place as it should be>
2. **The constraints.** <the FRs, decisions and pages it holds to>
3. **Where each comes from.** <G: the GM's words; R: a page; O: a measurement>
4. **Do they describe the world here?** <how it was measured>
5. **The order.** <before and after what>
6. **The exits.** Green: <the measurement that lands it>. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** <none, or what the probes showed>
8. **The budget.** One landing.
9. **Done, measured.** <the measurement that says it is done>
10. **Before moving a constant.** <n/a, or the claim it moves>
11. **Before fitting things into room.** <n/a, or the room given first>
12. **Before any fix.** <what a reader of the map would see differently, or the finding or check it breaks; nothing: not a defect, restate the claim (constitution XIV)>

**Found and left?** <none - or each item with its visible effect or the research finding it breaks; an item with neither is not a defect and is not filed>

**Performance work?** <no - or yes, and its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

