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
`UserPromptSubmit` whose prompt opens with a `<task-notification>` naming a `<tool-use-id>` before any `<result>` writes a `BgEnd` line:
that id, the task id (`bg`), its status and exit code (`exit`, the summary's last `exit code N`, absent where it names none). That is
only for a notice that is NOT an agent's: an agent's notice names its tool-use id too (R2), so a notice whose summary opens `Agent "`, or
whose launch line is an Agent call, writes none, its `SubagentStop` being its end. A shell's, a Workflow's and a Monitor's notice each
end a run the session can wait on, and each writes one. The line is FILED BESIDE ITS LAUNCH: in the log holding the launching call's
line, whose `make`, `cat`, `task` and `fallback` mark it copies and whose `t` is its `t0`, since a notice names no command or brief and
T26's chain would file it in feature.json's log, away from a launch filed by its `F=` or brief. A launch no log holds ends beside the
prompt's line, under its task and mark. Its `t` is when the notice reached the session, not when the run ended: a notice waits in the
queue while the session is mid-turn (T04's section). Every `Stop` and `SubagentStop` line records `inflight` from `background_tasks`. The readers (T08) pair a launch
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
task; the REWORK counts refused landings (D5's `end` lines whose `landed` is false: a push that went out with a later raise, or
exit 3 with its ticks standing, is a landing whatever its code) and plan re-rounds (a later round of one review on one subject, keyed by
agent and manifest subject as the rounds table keys it; T10's plan review, 2026-11-21). `feature-report` reads the same columns
through the same functions (one place: `where_time.rs`'s new `columns` module), keeping its existing `UNTIL=`.

**D8 - Who is a builder** (FR-006; R3). A payload with `agent_id` whose `agent_type` names no `.claude/agents/<agent_type>.md` in the
clone. Measured, this catches every builder that passed the cap and, among defined agents, one call; it also catches a general-purpose
agent dispatched without a task, which is judged by the same cap (the spec defines a builder as "an agent dispatched with a task's
brief, not a defined review agent"; every general-purpose dispatch here is one with a brief, and requiring a `T<n>` in it would let a
builder with an unnamed brief pass). Named for the plan review.

**D9 - The context cap** (FR-006; R2). A new guard, `context_cap_hooks`, PreToolUse `*`. For a builder it reads its transcript's tail
(`<transcript_path without .jsonl>/subagents/agent-<agent_id>.jsonl`, backwards to the last `usage`) and, past `CONTEXT_CAP_TOKENS`
(GUESS, 300,000 tokens, the spec's knob), refuses every tool call but a Write, Edit or Read of `<git common dir>/l7r-handoffs/<task>-<agent id>.md` (the Write tool reads a file
before it overwrites one; any file there ending `<agent id>.md` counts, so a task changed between refusal and Write still agrees; T12),
naming that path and the next step: write what is done and what is left, then stop; the session dispatches a fresh builder with it.
The main session and a defined agent are never read. The escape (FR-012): `CONTEXT_OK="<reason>"` in a Bash command, or, for any
tool, a permit the session grants for that agent (built with T13, the resume it serves), `make context-ok AID=<agent id> WHY="<reason>"` (the guard-edit permit's mechanism,
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
- **A landing** (one definition, D11's too) is a `make land` of the task that SUCCEEDED: D5's `end` line whose `landed` is true (its
  push went out - code 0, or 3 with its ticks standing, or a raise after the push; T06) and whose `tasks` names it. The
  `end` line names its own tasks, so no span is matched: a `run_in_background` landing's call returns at once and its `end`
  falls outside the call. A refused landing is not one. Any such landing after the dispatch
  refuses the resume; so does the task ticked in the feature's `tasks.md` or archived in `tasks-done.md`, whatever the log holds (a
  landing the log missed still refuses).
- **No task found at all** (no `T<n>`, no line carrying one, no `task-starts.jsonl` entry before the dispatch): the LANDING check
  passes, and the pass is written to the guard log as `context-cap: resume, no task` with the agent id, so it leaves a record. The cap
  check does not need a task: a builder past the cap with no task found is still refused.

**D11 - The third `make static`** (FR-007; R6). A new guard, `static_runs_hooks`, PreToolUse Bash, where `invoked` (D1) holds `static`:
it counts this call's task's (D2) `make static` runs that RAN - a `PreToolUse` line whose `make` (or, since T14, `makes`, every target a
call runs) holds `static` and that has its `PostToolUse` or `PostToolUseFailure` line, so a call another guard refused, which ran
nothing, does not count (T14, 2026-11-20) - since its last landing (D10's definition: a `make
land` naming it whose `end` reads `landed` true, so a refused landing resets nothing), or, where it has never landed, since its FIRST
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
("every" or "all the" before writer, reader, form, file, caller, instance, copy, site or guard, or "each of the ..."; a bare "all" is
not one - "all tests pass" is correct text; T17) must carry a line `observed <date>, method: ...`
saying how every instance was found. The template's `**Found and left?**` placeholder states the form. The built form (T17): an item passes as `none`, `fixed here` (or fixed before the task's tick) or `not a defect`; a deferral states
`Not fixed here: <why>`, `filed as T<n>` (or `added to` / `folded into`) and `lands before T<m>`. `DEFER_FORM_OK` on `make
decide` escapes, read from the environment and recorded by the tool itself (the guard log and `dev/bypass-log/`), as T28's escape is. It holds on the `plan-delta` path too, since `lint::refusal` runs there: `make decide` under
the escape records it in the guard log naming the feature and the task, and `make plan-delta` reads those records and does not run
`deferral_unformed` on that task's section, so a section decided under the escape is not refused when its block later changes;
`make plan-delta` also takes `DEFER_FORM_OK` itself, the same way, for a section never decided. No
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
when every shard is, and its companion check accepts shards for a guard's companion. T20 builds the form, proved on `test-parts.sh`; T21 splits
the three - `entry-gate.sh` by its two cases, the other two by their case groups - until each shard's kept seconds is about 20 or less in a full run (`SHARD_BAR_S`, GUESS, measured as
`.git/hooks-test/<shard>.s`, never a gate).

## Task sections

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T33 to T44 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T09 to T09 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T11 to T11 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
  recorded. A compound that runs in another shell - a pipeline's part (`for t in a b; do make $t & done | cat; wait`, `{ make x & }
  | cat; wait`), a `( )`, a backgrounded loop, one in `$( )` - is refused, since a later `wait` covers none of its jobs; a bare `wait`
  after a loop, `if` or `case` body run in the same shell covers it (the plan review's ruling, LEGITIMATE, 2026-11-20).
- **The shared readers, fixed here** (T30 folded in; the plan review of 2026-11-20 ruled leaving them NOT LEGITIMATE). Held also:
  `rust/guard/src/shared/shape.rs`, `rust/guard/src/shared/make.rs` (`make guard-edit` first). Each red first in its own tests:
  `strip_heredocs` takes a heredoc whose opener line goes on past its delimiter (`cat <<'EOF' > f`), keeping those words;
  `strip_quotes` keeps a quoted string only after an interpreter's `-c`, its flags joined too (`bash -lc`, `sh -ec`, `python3 -c`),
  never `grep -c` or `git -c`, and blanks the strings quoted inside a kept one; `invoked` reads `setsid [opts]` as a word that runs
  what follows, `make;` as a call, and a goal-less make as `.DEFAULT_GOAL` (a goal it cannot read, `make $T`, still names none).
  `no_poll_hooks` reads through them, its own heredoc and quote readers retired. Every guard reading them is replayed on the frozen
  corpora before and after, each moved verdict named.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the detached run | n/a - no map | n/a | none | n/a |

### T15 Approach (checklist part A)

1. **The goal, in the world.** No map changes; every long run is one whose end wakes the session.
2. **The constraints.** FR-008, FR-012; D1 (the detector), D12; constitution XVIII (a mention is not an invocation).
3. **Where each comes from.** G: the approved "a guard refusing that pattern"; O: research R4.
4. **Do they describe the world here?** R4's cases are the session's own commands.
5. **The order.** First in lane B (the GM 2026-11-20 order, FR-013); it needs only T02's make detector, landed.
6. **The exits.** Green: the twenty-three cases, grown in the suite to 35 refused and 28 passed (cargo, `disown -a`, `disown $!`, the mentions, `&&`, `&>`, `2>&1`, `|&`, a non-make job), with the plan review's 6 compound-in-a-pipeline cases refused and 2 waits inside the part passing - measured 2026-11-20 (the case arrays of `no_poll_hooks/tests.rs`, counted). The four frozen corpora through `detached`: 1,134 commands, 16 refused, each a real `setsid nohup make done ... &` or `nohup make done ... &` launch read by hand, so 0 false refusals - measured 2026-11-20 (`detached` over `tests/hooks/fixtures/*.json`). The 14 of the first replay grew to 16 as the shared readers were fixed: one launch chained after a heredoc whose opener went on past its delimiter, one after a line continuation into `setsid nohup make done`. Every guard before and after the shared fix, on the same corpora: 3 of 1,134 verdicts moved, each a correction - no-poll refuses the `setsid nohup make done &` launch; no-poll brackets a `pkill -f "pytest"` it missed, the old `strip_quotes` having kept `grep -c "[p]ytest"` and knocked its quote pairing out of line; main-tree honors a `# MAIN_TREE_OK:` reason the same misreading swallowed after a `python3 -c "..."`, so `tests/hooks/fixtures/main-tree-refusals-2026-09.json` row 130, recorded under the misreading, is re-labeled `rewrote` to `allowed` and its split 109/64 to 110/63 (the suite's own case: an escaped command is allowed, not rewritten) - measured 2026-11-20 (the `l7r-guard` binaries built just before and just after the shared fix, all guards, one PreToolUse call a command, inside a scratch clone, each in a fresh HOME, results diffed; the same binary twice gave 0 differences). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite's cases. Red first: 2 of the 2 new guard tests failed on the code before the check; the check deleted, 35 of 35 firing cases red; the disown check alone deleted, the 6 `disown ...; wait` cases red; after the review's fixes, the check deleted again, 35 of 35 red - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, four logged runs). The plan review's 6 compound-in-a-pipeline cases were refused before they were added, so not red first; with the pipeline's subshell cut deleted, 5 of the 6 red, the sixth (`( make x & ) | cat; wait`) a shell of its own either way - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, one logged run). The shared readers' 2 new tests (`shape`'s, `make`'s) failed before their fix - measured 2026-11-20 (`make rust-test CRATE=rust/guard`, one logged run). Their callers in the gate held: `land`'s `run_target` and `rustc`'s skip a goal-less make's `.DEFAULT_GOAL`, as they skipped its empty goal before (`land`'s test went red on it and green with the skip). The walk is a small shell parse in `no_poll_hooks` (`Shell`), reading through `shared::shape` and `shared::make::invoked`; a bare `wait` after a loop, `if` or `case` body in the same shell covers its jobs (the plan review: LEGITIMATE), `wait $!` and `wait %N` only in the job's own list.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** n/a.

**Found and left?** none

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: T16 to T16 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T17 to T17 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
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

**Performance work?** yes - a `[perf]` task (FR-013): it makes the work after it faster; no engine timing, so no checklist

<!-- plan-archive: T19 to T19 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T20 to T20 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T21 to T21 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
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

**Performance work?** yes - a `[perf]` task under FR-013's measurement clause (the GM 2026-11-20): it measures where the time goes; no engine timing, so no checklist

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

<!-- plan-archive: T24 to T02 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T28 to T28 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T29 (`make set-down` left the feature's started-task mark: 449 was set down with T241 parked while `.git/active-task` still named 449 T241, so every push touching 449's specs was held and T06's landing refused, observed 2026-11-20, method: T06's refused landing and the revert of its ticks, `git log`)

- **Approach**: `set_down.rs` gains `clear_mark`: once the set-down's row is written, the clone's `active-task` mark is removed when it
  names the set-down feature, and the reply says so ("its started-task mark (T241) cleared"). A refused set-down, another feature's
  mark, or a mark that cannot be read or names no feature, is left as it stands and fails nothing. The next `make task-start` of the
  feature writes the mark again, as it always has.
  - red first, the test before the code: 1 failed of 60 (the mark still there after the set-down), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/task`, `/tmp/t29-red.log`).
  - green: 60 of 60, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/task`, `/tmp/t29-green.log`); the clear deleted: 1 failed of 60, measured 2026-11-20 (the same command, `/tmp/t29-deleted.log`).
  - the incident replayed in a scratch repository: `speckit-todo --holding` named "T241 ... the active task" before the set-down and nothing after it, the mark gone, measured 2026-11-20 (`scripts/gates/l7r-gate.sh speckit-todo --holding` and `set-down 449`, `/tmp/t29-replay.LoEu/`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the mark cleared at a set-down | n/a - no map | n/a | none | n/a |

### T29 Approach (checklist part A)

1. **The goal, in the world.** No map changes; a feature set down holds no push touching its specs as a started task's.
2. **The constraints.** T29's line (the mark cleared when it names the set-down feature, a later task-start restoring it, red first);
   100% line coverage of the task crate by its own tests.
3. **Where each comes from.** O: T06's refused landing, observed 2026-11-20, method: its landing's refusal and the reverted ticks;
   O: the replay above, measured 2026-11-20 (`speckit-todo --holding` before and after).
4. **Do they describe the world here?** The holding box reads the mark through `shared::speckit::active_task`, which answers no task where the mark is missing, read 2026-11-20 (`rust/guard/src/shared/speckit.rs`); the replay's holding list went from one line to none, measured 2026-11-20 (`/tmp/t29-replay.LoEu/after.log`).
5. **The order.** With T28 (the same tool); independent of the other lanes.
6. **The exits.** Green: the red test green, the clear deleted and red, `make rust-test` on the task crate, `make quick`, `make
   static` (once), `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Every reader of the mark was found: `shared::speckit::active_task`, `plan door active-task` (`plan/task.rs`)
   and `task_start.rs`, its one writer; each reads a missing mark as no task, read 2026-11-20 (`grep active-task` over `rust/`).
8. **The budget.** One landing.
9. **Done, measured.** The replay's holding list empty after the set-down, measured 2026-11-20 (`/tmp/t29-replay.LoEu/after.log`).
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map; a set-down no longer leaves a push touching the feature's specs held as its parked task's.

**Found and left?** none.

**Performance work?** yes - a `[perf]` task in FR-013's sense: a push held by a stale mark cost T06 a refused landing and its ticks
reverted. Not filed with `PERF=1`: no engine stage's counted operations or time.

<!-- plan-archive: T30 to T30 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T31 to T15 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T33 to T33 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T36 (T17's replay, 2026-11-20: thirteen archived sections of plan-done.md deferred work with no filed task or order - 449 T156, T200, T201, T208, T218, T219, T221, T224, T239 and 451 T02, T03, T16, T26)

- **Approach**: each section's deferral read by hand (its `**Found and left?**`, and for 451 T02, whose answer was `none`, the class its fix named) and given one verdict per deferred defect: **carried** (an open or ticked task covers it), **fixed** (a later commit), **still open** (filed now, `make task-add`), or **not a defect** (no visible effect and no research finding broken, so not filed - constitution XIV). History is not re-judged: a ticked task's work is taken as its tick says. Three tasks filed: 449 T243, 451 T52, 451 T53.

| section | deferral | verdict | task or commit |
|---|---|---|---|
| 449 T156 | the sheet driver and the pool walk's rebuild (the pool index listed 6 of the pool's maps) | carried | T157 through T220 (the walk, `pool/index.html` listing every map; ticked 06b493d8d7) and T221 (one sheet driver; ticked 6fa4bd0fc7) |
| 449 T200 | the derivation template refused a Mode A derivation's form | carried | T201 (ticked 9e98737b4d) |
| 449 T201 | (a) `make work-budget` did not read the Mode A counts; (b) a pool-sheet stage had no change, raise or accept path | (a) not a defect; (b) still open | (a) `make work-budget` still reads only the roll's `stages` (`trials/src/measure/work_budget.rs`, `budgets["stages"]` alone; `budget_change/sheets.rs`'s header: it reads the table "as the roll's alone"), by design the hamlet's record at 10/20/40/80 households - and the Mode A counts are read and held by `make work-budget-review` (T224, 68b8772bb7: `work_budget_review.rs` re-counts each pool-sheet stage through `SHEET_COUNTERS` and holds it on each sheet to twice its budget), whose counters cover all three `sheet_stages` keys (`placer`, `compound`, `pipeline`), measured 2026-11-20 (`work_budget.rs` and `work_budget_review.rs` read at HEAD, `dev/work-budget.json`'s `sheet_stages` keys listed), and `make budget-sheets` compares given counts per sheet - no Mode A stage goes uncounted or unheld, so no wrong outcome; (b) filed as 449 T243 - `budget_change/sheets.rs`'s header still says change, raise and acceptance are not built, read 2026-11-20 |
| 449 T208 | (a) the county program read off the drawn sheet; (b) the reviewer's notes (an unstated radius, a "ten zones" slip, the fire gap at its band's low end) | (a) carried; (b) not a defect | (a) T152 (76221da67f, reads the program itself); (b) no total moved by more than a few operations (T208's reading) and T152's `make budget-sheets PHASE=compound` held both sheets within twice; the slip stays in the SOUND derivation's prose (`derivations/T208-compound.md` line 212), no wrong outcome |
| 449 T218 | `.PHONY` names with no rule passing by running nothing, a dead cache-audit guard, a notes-only edit skipping the sweep | carried | T223 (0559cff934; ticked 9a01e65877) |
| 449 T219 | the Mode A page writer reporting only files found; a read first recorded on a miss hashed after the engine read it | carried | T221 (both on its line; ticked 6fa4bd0fc7) |
| 449 T221 | (a) checks reading what no longer exists (the measure probe's pool changes, preflight's roll census, land's census filter) and render-sync's stop on a failing map; (b) the Python cache's old entries under `.gencache/<map>/` | (a) carried; (b) not a defect | (a) T222 (all four on its line; ticked c531976060); (b) nothing reads them - the Rust cache's directory is `.gencache/rust` (`rust/gate/crates/pool/src/cache.rs`'s `DIR`); the mirror's `.gencache` holds only `rust/`, 16M, and this clone's 6.2G, measured 2026-11-20 (`ls` and `du -sh` of both) - disk only |
| 449 T224 | `waterward.polder` counting about a twentieth of its accepted figure; the pipeline stage's counters | carried | T226 (f82828450e; ticked ecd61b81ef) and T220 (its counters added to the counted set; ticked 06b493d8d7) |
| 449 T239 | (1) `polder_checks` tests only the seat's middle, so it cannot catch ground over the dike; (2) a malformed `placement-changed` line owing a `glyph-check--` unit; (3) nothing ties the seat to 0019's landward shore | (1) carried; (2) fixed; (3) carried | (1) and (3) 449 T240 (open; both on its line, (3) read on the page and measured first); `polder_checks` unchanged at HEAD, read 2026-11-20 (`rust/phases/src/driver/check.rs`); (2) T238, e89fa942bc (`declared.rs`'s `nothing_named` refuses it) |
| 451 T02 | the class: one reading of which make targets a command runs, shared by the log and every guard - no instance count | still open | 13 guard modules read command text through `shared::make` and 10 command-text readers keep their own reading of a make call, measured 2026-11-20 (a grep of `rust/`, `scripts/` and the Makefile, each hit read and sorted; `git grep -l shared::make HEAD -- rust/`; a grep of `rust/` at HEAD for `"make` literals outside tests); filed as 451 T52 (below) |
| 451 T03 | the bundle's cover by environment; lines filed by `feature.json`; an Agent line with no `T=`; the live-line check owed; `T="T1,T2"`; booking by `make`; `data-model.md`'s `push-checks` and `make-docs` rows | carried, fixed or not a defect | T24 (781f577faf), T07 (aea9e74ea4) and T18 (781f577faf) fixed; the lines filed by `feature.json` carried by T26 (0f7583f1b5), remainder T53; booking by `make` carried by T08 (open); the live line fixed - the 451 log's `make static` lines carry `cat` `tests`, 66 of them, measured 2026-11-20 (the 451 log's Bash lines counted by `cat` and `make`); the two rows not a defect (a row that never matches books nothing wrong) |
| 451 T16 | `POLL_CHECK_S` into D14's knob table | carried | T22 (open; its line: `docs/guards.md`'s knob table complete, D14) |
| 451 T26 | (a) `make events-refile` owed once more; (b) two re-file judgment calls (427's and 405's briefs); (c) `make static` stopped on `rust/phases`; (d) the indexes not naming `filed.rs`, `refile.rs`; (e) T07 owing the prompt's first line | (a), (d) still open; (b), (c) not a defect; (e) fixed | (a) and (d) filed as 451 T53: 19 lines still to move, 17 of them written after T26's writer landed, measured 2026-11-20 (`make events-refile DRY=1`, the 449 log joined by hand to the subagents' meta files); (b) history, a booking between closed features' reports, the pre-re-file copy kept; (c) another builder's uncommitted work, no defect of the tree; (e) T07, aea9e74ea4 |

The T02 class, by kind (the grep's hits, each read):
- **Command text read for a make call, through `shared::make`** (`invoked`, `targets`, `POS`): 13 modules, measured 2026-11-20 (the grep, each hit read) - `event_log_hooks` and its `fields.rs`, `make_only_hooks`, `no_poll_hooks`, `gate_write_hooks`, `gate_hooks`, `pair_hooks`, `static_runs_hooks`, `budget_change_hooks`, `blocked_fetch_hooks`, `clone_sync_hooks`, `record_edit_gate`, `shared/checks/handle.rs`; handled.
- **Command text read for a make call, its own reading**: 10, measured 2026-11-20 (the grep, each hit read; a grep of `rust/` at HEAD for `"make` literals outside tests, each hit read) - `shared/checks/rounds.rs`'s `APPLY`, `ledger_hooks`'s `appended`, `claims_file_hooks`'s `VERB`, `make_only_hooks`'s `LANDING` and `LABEL_TARGET`, `measure/stepback_bundle/words.rs`'s `MAKES`, `measure_hooks`' `has("make done")` (a substring of the quote- and heredoc-stripped command; each counts a mention - `echo make append` - as a call), `phase_source_hooks/search.rs` (`make phase-read` at the head past its own wrapper list, no `timeout` or `flock`), `shared/tree.rs` (a segment headed by `make` past its own wrappers and `timeout N`, no `flock` or subshell) and `gate_write_hooks`' `head_of` (line 364: a walked segment headed by `make` left to the `shared::make` check above it, past its own wrapper list - `sudo`, `env`, `command`, `exec`, `nohup`, `time` - no `timeout` or `flock`, so a wrapped make's segment is judged as a shell write); not handled - whether any gives a real command a wrong verdict is unmeasured, so T52 is measure-first.
- **Set apart**: the process-table readers (a live process's argv - the watchdog, the running-gate probe, the finished-run check, `tree`'s lock, `land`'s and `rustc`'s phase locks, `ci`'s `via_make`, `idle_tests`' `pgrep`), where a wrapper is a process of its own - `land/phase.rs`'s `goal_of` and `rustc/phase.rs`'s `run_target` read that argv through `shared::make::invoked`, the gate's only users of it, measured 2026-11-20 (`git grep -l shared::make HEAD -- rust/`: those two beside the 13 guard modules and two test files); the cheap prefilters (`contains("make")`), supersets that only skip work; `batching_hooks`' `NOT_RECON` `"make "`, no prefilter but the verdict itself (a Bash call holding it is no bare read), set apart because every make call holds it, wrapped or not, and a mention only leaves one read uncounted, so it can fail open but never refuse wrongly, read 2026-11-20 (`batching_hooks.rs` lines 26 and 145); the log-field readers (`where_time/columns.rs`, in the T08 builder's uncommitted tree, reads the log's `make` field and only `shared::make::DEFAULT_GOAL`); the research prepass's prose. T02's constraint named `measure` and `shell-check` among `shared::make`'s readers: at HEAD neither is - `measure_hooks` keeps its own reading (above) and `shell_check_hooks` reads no make call, measured 2026-11-20 (a grep of both for `make` outside tests). None in `scripts/` or the Makefile, which run make but read no command for one.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the thirteen read | n/a - no map | n/a | none | n/a |

### T36 Approach (checklist part A)

1. **The goal, in the world.** No map changes; every deferral the replay found has a verdict and a name - a carrier, a commit, a filed task, or the reason it is no defect.
2. **The constraints.** T36's line (history not re-judged; read by hand once); 451 D15 (a class fix carries how every instance was found); constitution XIV (a difference with no wrong outcome is not filed).
3. **Where each comes from.** O: T17's replay of plan-done.md, observed 2026-11-20; O: the readings in the table.
4. **Do they describe the world here?** Yes: each carrier's line read for the deferral's words, each fix's commit found by `git log`, and each still-open one re-read at HEAD (`sheets.rs`, the event logs, the `CLAUDE.md` rows), measured 2026-11-20 (the readings in the table).
5. **The order.** After T17; before T22 (the close), which the two 451 filings land before.
6. **The exits.** Green: the table complete, the filings in `tasks.md`, `make decide` and `make quick` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** The T02 count's grep covered `rust/`, `scripts/` and the Makefile, the class's every home, rechecked by `git grep -l shared::make HEAD -- rust/` and a grep of `rust/` at HEAD for `"make` literals outside tests, which moved the own-reading count from 8 to 10 (`measure_hooks`, `gate_write_hooks`' `head_of`), measured 2026-11-20 (both greps, each hit read).
8. **The budget.** One landing, specs only.
9. **Done, measured.** 13 sections, 13 verdict rows, 3 tasks filed, measured 2026-11-20 (the table above and `git -C` diff of the tasks files).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No fix here; each filing names its wrong outcome or is measure-first where none is shown yet (T52, T53), and the not-a-defect rows say why.

**Found and left?** none - the three still-open deferrals are filed in the table (449 T243; 451 T52 and T53).

**Performance work?** no.


<!-- plan-archive: T37 to T18 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T37 to T37 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T38 to T32 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T38 to T38 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T42 to T31 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T42 to T42 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T44 to T42 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T44 to T44 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T45 to T42 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T45 to T45 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T47 to T44 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T47 to T47 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T48 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T48 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T49 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T49 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T50 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T50 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T51 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T51 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T52 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T52 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T53 to T26 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T54 (the stale-terms search refused the FR-013 amendment's spec review with 66 candidates on the backticked `end` read as an ordinary word, escaped with `STALE_TERMS_OK`, measured 2026-11-21 (the guard log's `blocked/stale-terms` row of 2026-11-21T02:55:57Z and the refusal's text in the session transcript))

- **Approach**: measured first, from the guard log and the refusals' own text; then the subject read in the sense the change moved it in,
  in `rust/gate/crates/record/src/record/stale_terms.rs` (not held; the call site in `review_round_hooks.rs` is unchanged, and no
  stale-terms list exists to edit - the subjects are read from each change).
  - THE LOG: 87 `blocked/stale-terms` and 135 `rewrote/mode-3-preamble-stale-ok` rows of the review-round guard, 2026-09-20 to
    2026-11-21, measured 2026-11-21 (`~/.claude/guard-log` read, `/tmp/t54/follow.py`). After a refusal the feature's next row in that session was an escape 78 times (2 of them a `spec-round-cap`
    refusal, which comes after the token), a clean dispatch 8 times and a second refusal once, measured 2026-11-21 (the rows of
    `~/.claude/guard-log` read in order, `/tmp/t54/follow.py`). The refusal's text survives in the transcripts for the 36 from
    2026-10-17 on (`/tmp/t54/extract2.py`). The rest were reconstructed from the commits before the round's snapshot and before the
    refusal: `l7r-gate record stale-dirs` over a `git archive` of each, 82 of the 87 reconstructable (`/tmp/t54/rustrecon.py`). That
    is an approximation, since uncommitted work at either time is missing: 451's 66 reconstructs as 67, measured 2026-11-21 (the same
    command over 76635031f1 and 62a9b98d44).
  - WRONG FIRES, a plain word in its ordinary sense, measured 2026-11-21 (the refusals' text and the reconstructions,
    `/tmp/t54/measure_b.py` and `/tmp/t54/recon-summary.txt`):
    - 451's `end`: 56 of the 67. Of those, 24 are inside another word (Independent, `append_row`), 15 are the bare word ("a
      sentence's end", "The end is filed") and 17 are the span `end` beside a re-wrapped old value (these three figures are
      `/tmp/t54/replica.py`'s, the Python replica over the same two commits, not the binary's).
    - 328's `well`: 92 candidates, of which 63 are inside a word, 19 bare and 3 the span.
    - 291's `street` and `edge`: 11 candidates, all bare, then 19, one of them the span.
    - 284's `drawn`: 3 bare, beside `12` and `24` found inside longer numbers.
    - 266's `kind`, `text` and `angle`: 12 of 21.
    - 444's `meta`, 415's `full`, 438's `Done` and 261's `rag`, each named as an ordinary word in its escape.
  - RIGHT FIRES, all kept, measured 2026-11-21 (the transcripts' edits, and the reconstructions before and after the next commit):
    - 427's `request.md`: working-notes.md's hold line, rewritten before the next dispatch. Kept by rule (a path is a name, read
      bare or in a span), not shown by the replay: its two reconstructions find 0 candidates and none, measured 2026-11-21
      (`/tmp/t54/rust-before.json`).
    - 261's `m:mizuguchi-r17-copse` and its `BELT_DEPTH_FT` 105.
    - 267's `inventory.md` 51, 276's `FreeGround`, 278's `hamletgen/homesteads/boundary.py` and 374's `request.md`.
    - On BARE text, 283's `780 sq ft` (the sheet's old size) and 285's `GUESS` ("The word GUESS" rewritten as "The label GUESS").
    Each was gone at the next dispatch. One more was inside 451's own 66: `contracts/refusals.md:12` defined a landing as "D5's
    `end` line of code 0", the definition plan.md replaced with `landed` true. The escape passed it; the session has since restated
    it (Found and left).
  - THE FIX: `names(text, subject)`, asked for a candidate's hit.
    - A subject that is one plain word, letters alone and capitalized at most at its start (`plain_word`), is named only as that
      code span.
    - Any other term (a phrase, a path, a number, an identifier, a capitalized label) is named bare or in a span. Neither of its ends
      may run on into a longer word, where that end is a word's character (a letter, a digit, `_` or `-`).
    - A code span is read with its backticks paired in order (`spans`). The regex scan paired the closing backtick of a span too
      short to keep (`t`) with the next opening one, which made the prose between two spans a subject. An empty span is no subject.
    - A plain word's span is read as the literal `` `word` ``, not a span paired in order: a line that opens inside a span wrapped
      from the line before pairs every backtick after it the wrong way, so 451's plan.md:107 ("done" closing line 106's span, then
      "a last `end` line") named nothing under the paired reading (Red first, the fourth case).
    - 442's rewritten-from check keeps its plain containment: a line this change rewrote from one that wrote the subject's word in
      any form was revisited on purpose. Reading the old block by `names` too was tried: over the replay below it added one
      candidate, 274's "Only three named kinds ... naming the split" rewritten as "Only four named kinds are exempt (... `split`
      ...)", which its escape says states the new rule, and no real catch, measured 2026-11-21 (the replay with each variant).
  - NOT CHANGED, the value side: the old values are still the words the old LINE had and the new line lacks. So a word re-wrapped
    onto the next line of the rewritten passage stays an old value (451's `tasks`, `names` and `plan`). Reading the values from the
    whole replaced block was priced: in 451 it leaves 6 of 67 and drops `contracts/refusals.md:12`, whose "code 0" survives in the new
    block as one case of three, so it would lose a real catch. Not done, measured 2026-11-21 (`/tmp/t54/replica.py`'s block values
    over the same two commits).
- **Red first**: four cases.
  - `a_plain_word_subject_is_named_only_as_its_code_span_and_the_real_catch_stands`: 451's lines verbatim (plan.md's two rewritten
    lines, four of plan-done.md's, `contracts/refusals.md:12`).
  - `a_phrase_or_a_capitalized_name_is_named_bare_but_not_inside_a_longer_word`: 283's and 285's lines, pinned as still refused,
    and `GUESS` not found in GUESSES or XGUESS.
  - `a_line_rewritten_from_one_writing_the_word_in_any_form_was_revisited_on_purpose`: 274's lines, pinning the containment kept
    (green before the change; the stricter variant named 274's line in the replay).
  - `a_plain_words_span_is_read_on_a_line_that_opens_inside_a_wrapped_span`: 451's plan.md:107 verbatim, which opens inside a span
    wrapped from line 106; its `end` is pinned as named.
  - before: the first two failed, the 451 case naming 5 lines where 1 is right and `GUESS` found inside GUESSES, measured
    2026-11-21 (`make rust-test CRATE=rust/gate/crates/record`, `/tmp/t54/red.log`: 86 passed and 3 failed, the third the
    stricter variant's case, since replaced).
  - before, the fourth: with the span-paired reading put back in `names`, 89 passed and 1 failed, the wrapped-span case finding
    nothing, measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust test --crate rust/gate/crates/record`, `/tmp/t54/red2.log`).
  - after: 90 passed, 0 failed, every earlier case unedited; format, lint, test and cover clean on the crate, measured 2026-11-21
    (`scripts/gates/l7r-gate.sh rust format|lint|test|cover --crate rust/gate/crates/record`, `/tmp/t54/crate-checks6.log`, on the
    final code), and `make closing-checks` was green (static 10 s, hooks-test 23 s and quick 1 s, 24 s wall), measured 2026-11-21
    (`/tmp/t54/closing3.log`, on the final code: the task's third `make static`, taken on `STATIC_OK`, "code changed after the task's
    two green closing runs").
- **The log replayed**: the 82 reconstructed refusals were run through the binary before and after the change. 60 of them found a
  candidate (the rest are reconstructions that miss the uncommitted work).
  - Before the change: 497 candidates, and 60 refusals.
  - After it: 299 candidates, and 57 refusals. The three avoided are 284's `drawn`, 291's `street` and `edge`, and 383's
    coincidence of words. 328 goes from 92 to 3, 291's second refusal from 19 to 1, 266 from 21 to 10, 444 from 19 to 4, 262 from 9
    to 2, 261's second from 3 to 2 (plan.md:473's `rag`, a wrong fire, dropped) and 451 from 67 to 28.
  - The literal reading of a plain word's span added 3 over the paired one (296 then): 451's plan.md:107, and two of 328's tasks.md
    lines of the shape the paired reading kept there (the old key, whose own span closes on "the required item is `well`"); no
    refusal came or went with them.
  - Every real catch above is still named, `contracts/refusals.md:12` first among 451's 28; 427's is kept by rule, as above.
  - Measured 2026-11-21 (`/tmp/t54/rustrecon.py before`, `after2` and `after3`, the last on the final code: `l7r-gate record
    stale-dirs` over the same archives, `/tmp/t54/rust-before.json`, `rust-after2.json` and `rust-after3.json`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the stale-terms subject read in its sense | n/a - no map | n/a | none | n/a |

### T54 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A later spec-fidelity round is refused only for a line that names the changed term
   in the sense the change moved it in and still carries its old value. A plain word in prose (`end` as "end", inside Independent,
   `well` inside "as well") names nothing, and every catch the log shows still refuses.
2. **The constraints.** T54's line: measured first (the recent refusals' candidates, how many named text the change made untrue);
   the subject read from what the change moved, not a bare common word; red first on this case. The launcher's file list:
   `stale_terms.rs` and its tests, the `docs/guards.md` row and this section. `review_round_hooks.rs`'s call site is unchanged, and
   no stale-terms list exists, so none was edited. Feature 253's search and 442's rewritten-from rule are kept, and so is FR-013 (a
   `[perf]` task). T69's and T70's files are untouched and nothing is committed.
3. **Where each comes from.** O: the guard log's rows and the refusals' text in the transcripts (Approach, THE LOG); O: the
   reconstructions from commits; O: the red-first run and the replay; the task as filed (T54's line).
4. **Do they describe the world here?** Every figure is from this host's guard log, the transcripts that survive and this clone's
   history, measured 2026-11-21 (the Approach's reads). The red case is 451's own lines, and the pinned catches are 283's and 285's,
   measured 2026-11-21 (their lines read from the reconstructions at the snapshot and the refusal).
5. **The order.** Independent of the open tasks: T69's `event_log_hooks/fields.rs` and the measure crate, and T70's `rust/browser`,
   share no file with it.
6. **The exits.** Green: the cases green with every earlier one unedited; `rust format|lint|test|cover --crate
   rust/gate/crates/record`; the review-round suite (its case 10, `gizmo`, still refused); `make closing-checks`; the replay. Red:
   what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Two.
   - 451's case does not go to zero: 28 of its 67 remain, the span `end` and the other three subjects (`make land`,
     `DEFER_FORM_OK`, `make plan-delta`). Most of them sit beside a word re-wrapped onto the next line (the value side, left: see
     Approach and Found and left).
   - A real catch, `contracts/refusals.md:12`, sat inside the 66 that the session escaped as one class.
8. **The budget.** One landing. The search's work is unchanged in kind: one subject test for each watched line of each changed pair,
   still a substring test for a plain word (its backticked form) and a bounded scan for any other term, where it was a substring
   test of the bare term; the subjects are read by a split on backticks where it was a regex scan. No time figure was taken.
9. **Done, measured.**
   - The red cases are green: 90 passed, 0 failed, measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust test --crate
     rust/gate/crates/record`, `/tmp/t54/crate-checks6.log`, on the final code).
   - The review-round suite: 84 passed, 0 failed, measured 2026-11-21 (`bash tests/hooks/test-review-round-hooks.sh`,
     `/tmp/t54/hooks-final.log`, on the final code).
   - The replay: 497 candidates fall to 299 and 60 refusals to 57, every real catch still named, measured 2026-11-21 (`/tmp/t54/rustrecon.py`,
     The log replayed).
10. **Before moving a constant.** No constant moves. The span bounds (2 to 60 characters) stay. Which characters continue a word is
    a CONVENTION, labeled at `names`: letters, digits, `_` and `-`. A hyphen continues an identifier (`make land-batch`, `FR-001a`); a
    `.` or a `/` does not (a sentence's end, a longer path). A plain word is likewise a CONVENTION, labeled at `plain_word`: letters
    alone, capitalized at most at its start. So `Done` is plain and `GUESS` and `FreeGround` are names.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session dispatching a later spec-fidelity round sees fewer candidates on correct text, and fewer refusals:
    over the replay, 198 of the 497 candidates go and 3 of the 60 refusals, measured 2026-11-21 (The log replayed). Each avoided
    refusal is an escape and a redispatch not spent. Nothing on a map.

**Found and left?**
- `specs/451-time-retro-and-efficiency/contracts/refusals.md:12` stated FR-007's landing as "D5's `end` line of code 0 naming it",
  where plan.md's one definition reads D5's `end` line whose `landed` is true (code 0, or 3 with its ticks standing, or a raise after
  the push), and the 451 refusal named it among its 66. A claim the code does not match (constitution XIV): the guard counts a landing
  by `landed` true, measured 2026-11-21 (`rust/guard/src/guards/static_runs_hooks.rs:247` read). Fixed here (restated by the
  session): the contract's line now reads D5's `end` line whose `landed` is true.
- The value side refuses on correct work: a word re-wrapped onto the next line of a rewritten passage stays an old value, and that is
  most of the 28 left in 451's case (`tasks`, `names`, `plan`). Reading the values from the whole replaced block was priced and drops
  the real catch above (Approach, NOT CHANGED). Not fixed here: no measured rule yet keeps a catch of that shape, and the rule is
  measured first. Filed as T73; lands before T22.

**Performance work?** yes. This is a `[perf]` task (451 FR-013): it makes the builders' loop faster by refusing fewer later
spec-fidelity rounds on correct text, each of which cost an escape and a redispatch. It is not an engine-speed task, so the checklist
does not apply.


<!-- plan-archive: T55 to T55 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T56 (T53's writer gives a start over 72 h old no feature, but `make events-refile` read its own copy of the start rule: 0 lines moved and 23 left in 385's log, measured 2026-11-21 (`make events-refile DRY=1` before the change, its last line))

- **Approach**: the re-file (`rust/gate/crates/measure/src/measure/event_log/refile.rs`) asks the writer's rule instead of its copy:
  - ONE READER: `filed.rs`'s `starts` (the one reading of `task-starts.jsonl`), `in_force` and `started` (the `STALE_START_S` rule,
    72 h, a GUESS knob, 451 T53's item 10) and their `Start` are public, re-exported beside `brief_feature`; the re-file's own parse of the starts, its `in_force` and
    its `started` are deleted. Its time bound stays: it hands the writer's functions only the starts made by the line's time (with
    `START_SLACK`), and the line's `t` as `now`, so a start's age is measured as the writer measured it when it wrote the line. The
    hook's behavior is unchanged (no line of the writer's chain moved, only visibility).
  - THE FALLBACK, the writer's next link: sharing `started` alone moves none of the 23 - it answers no feature, where the old copy
    answered 385, the log's own, so the line stayed either way, measured 2026-11-21 (`verdict` traced over the 23 lines, 385's
    `tasks.md` with no T47 box and the clone's one T47 start, 385's of 2026-10-18T17:01:28Z, read). Where no start names the
    task the writer files the line under feature.json, marked `"fallback": true`; the re-file now does the same with feature.json at
    the line's time, read as the feature of the clone's last start by then (`make task-start` rewrites feature.json), moved only where
    that feature has the task, the line marked as the writer marks it. For the 23 that is 451, whose T45 started at
    2026-11-20T23:36:12Z, the clone's last start before the lines (23:56:18Z to 00:16:22Z) and none between, measured 2026-11-21
    (`task-starts.jsonl` read); 451 has T47 (`tasks-done.md`). The lines' dispatchers agree independently: `ad13155b5a57c77e0`
    "451 T47: the pages coverage flake" and `a100d23716c85dabc` "451 T47 (fresh): the last steps", the parents of the three
    spec-fidelity rounds "T47 plan review", "T47 plan section re-review" and "... re-review 3", measured 2026-11-21 (their meta files'
    `description` and `parentAgentId`). The dispatcher's brief was not made the rule: the writer has no such step, so the two would
    disagree on new lines.
  - The run's line counts the fallback apart: `(0 by brief, 0 by task id, 23 by the fallback)`, the fallback's count printed only where
    it moved a line, so a run with none reads as before.
  - One edit past the task's file list: `event_log_hooks.rs`'s `pub use filed::brief_feature;` widened to the four names, `filed`
    being a private module (`make guard-edit` run on both files).
- **Red first** (`refile::tests::a_task_whose_only_start_is_stale_falls_to_the_feature_of_the_last_start`, the live shape in a small
  world - the log's feature without the task, its only start weeks old, another feature with the task and the last start, the briefs
  naming a task only - and one case per new branch: a fresh start still wins, no start before the line, the fallback's feature without
  the task, the fallback the log's own feature):
  - before: 200 passed and the new case failed, the old copy reading `385-c -> 449-b: 1 lines (0 by brief, 1 by task id)`, `1 lines
    moved`, `5 lines left`, measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/measure`, `/tmp/t56/red.log`).
  - after: 201 passed, 0 failed, the earlier `each_misfiled_line_moves_to_the_feature_of_its_task_once` unedited and green, measured
    2026-11-21 (the same command, `/tmp/t56/green.log`).
- **The runs** on this clone's logs (the logs of `385-approach-checklist` and `451-time-retro-and-efficiency` copied to
  `/tmp/t56/logs-before/` first):
  - the dry run after the change: 239,030 lines read in 28 logs, `385-approach-checklist -> 451-time-retro-and-efficiency: 23 lines
    (0 by brief, 0 by task id, 23 by the fallback)`, 0 lines left, measured 2026-11-21 (`make events-refile DRY=1`,
    `/tmp/t56/dry1.log`).
  - the real run: the same 23 moved, 0 left, measured 2026-11-21 (`make events-refile`, `/tmp/t56/real.log`).
  - the dry run after it: 0 lines moved, 0 left, measured 2026-11-21 (`make events-refile DRY=1`, `/tmp/t56/dry2.log`).
  - 385's log holds 0 lines whose task is `T47` (20,415 lines before the real run, 20,392 after) and 451's the 23, each marked
    `"fallback": true`, measured 2026-11-21 (`wc -l` and `grep -c` over the logs and their copies).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the re-file asks the writer's start rule, then the writer's fallback at the line's time | n/a - no map | n/a | none | n/a |

### T56 Approach (checklist part A)

1. **The goal, in the world.** No map changes. Every event-log line sits in the log of the feature whose task it served, so `make
   where-time F=451` books 451 T47's three plan reviews to 451, and `make events-refile DRY=1` finds nothing to move and nothing left;
   the re-file and the writer file a line alike because they read one rule.
2. **The constraints.** T56's line: the refile shares the writer's rule (one reader, not a copy), a dry run shows the 23 moving, red
   first; then the real refile run once. The launcher's file list: `refile.rs` and its tests, `filed.rs` only to make the rule public,
   this section (one more line, item 1's `pub use`, Approach). T59's `fields.rs` and T64's `order.rs` untouched; nothing committed.
   T53's writer behavior unchanged.
3. **Where each comes from.** O: the dry runs before and after (the Approach); O: the lines left, their meta files and
   `task-starts.jsonl` (the Approach); O: the red-first run (Red first); the task as filed (T56's line) and T53's section (its item 9
   and Found and left, which filed T56).
4. **Do they describe the world here?** Every figure is from this clone's logs, its subagents' meta files and its `task-starts.jsonl`,
   measured 2026-11-21 (the Approach's reads and runs); the red case reproduces the live shape in a scratch world.
5. **The order.** After T53 (whose rule it shares) and T58 (which moved `filed.rs` to `rust/guard/shared`); before T22.
6. **The exits.** Green: the red case green with the earlier re-file test unedited, `make rust-test CRATE=rust/gate/crates/measure`,
   lint, format and cover on `rust/gate/crates/measure` and `rust/guard/shared`, `make closing-checks`, the dry run showing the 23 and
   the dry run after the real run showing 0. Red: what failed recorded and the task set down, a claim that it cannot be done ruled
   through `make arbiter-ask`.
7. **The search smell.** One. The task expected the shared stale-start rule alone to move the 23; traced, it leaves them (it answers no
   feature where the copy answered the log's own), so the writer's next link, the fallback, was shared too, read at the line's time
   rather than from today's feature.json (Approach).
8. **The budget.** One landing. The re-file's added work is a copy of the starts made by a line's time, taken only on a line whose task
   is no task of its log's feature or a BY BRIEF move: 23 lines of 239,030 on this clone, measured 2026-11-21 (the dry run's counts).
9. **Done, measured.**
   - the red case green, 201 passed, measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/measure`).
   - the dry run moves the 23 to 451 and leaves 0, the real run moves them, and the dry run after it moves 0 and leaves 0, measured
     2026-11-21 (`make events-refile [DRY=1]`, The runs).
10. **Before moving a constant.** No constant moves. `STALE_START_S` (72 h, a GUESS knob) is the writer's, now read by the re-file
    through `started`; `START_SLACK` (60 s, a GUESS knob beside it) now also bounds the fallback's last start, the same bound the
    re-file's other start readings take. The fallback's reading of feature.json at a line's time is a CONVENTION, labeled in the code:
    feature.json keeps no history, a feature created between two starts (`make claim`) is not seen, and a move is held to a feature
    that has the line's task.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of `make where-time F=451` or `F=385` sees 451 T47's three spec-fidelity rounds booked to 451, not to
    385, which has no T47. Nothing on a map.

**Found and left?**
- The `fallback` mark has no reader: T53's section says "readers keep a marked line apart", and no reader in `rust/gate/crates` or
  the shared event-log reader (`event_log_hooks/read.rs`) reads the mark, measured 2026-11-21 (`grep -rn fallback` over both).
  Not a defect here: for the 23 the mark's task, T47, is the 451 T47 their dispatchers served (Approach), so they are booked right; whether
  a fallback line elsewhere is booked to a wrong task is unshown, and the readers are not T56's files. Raised with the coordinator.

**Performance work?** yes. This is a `[perf]` task (451 FR-013: it makes the builders' loop faster by booking each feature's time
where `where-time` reads it). It is not an engine-speed task, so the checklist does not apply.


### T57 (the finding as filed, restated by its measurement: `make static` builds and runs no plain test binary - the plain `build` and `test` time is `make rust-test`'s, the builders' loop, measured 2026-11-21 over the event log's Phase lines since 2026-11-20T12:35Z; what is built twice is a crate's tests in `make rust-test` and again in the coverage run, which answers for the plain run only where T111's `unit_tests_only` says the coverage run ran every test `cargo test` runs)

- **Approach**: the coverage run's word for a crate's plain tests (T111: a green coverage pass keeps the crate's `test` result, so a
  later `make rust-test` stands on it and builds and runs nothing) reaches every crate whose whole `cargo test` the coverage run
  (`--lib`) runs. `unit_tests_only` (`rust/gate/crates/rustc/src/rustc/kept.rs`) refused any crate with a binary and any doc fence;
  it now refuses a binary only where it holds a test, a `cfg(test)` or a `mod x;` (`BIN_TEST` over `src/main.rs`, `src/bin/` and each
  `[[bin]]`'s path), and a fence only where it is not a `text` block (`TEXT_BLOCK`). Eleven crates join the keep - the guard,
  `rust/gate`, `pool`, `cohort`, `measure`, `pages`, `reviews`, `rust/mode_a`, `rust/phases`, the browser and the embedder; `checks`
  (a `cfg(not(coverage))` test) and `rustc` (its tests' `cfg(coverage)` text) stay out, observed 2026-11-21, method: the new and the
  old predicate run over every crate's manifest and sources. `make static` itself is unchanged (it ran no plain test to drop), and
  `make rust-test`'s runs are unchanged but for its doctest reading (`has_doctests`, `side.rs`), which takes the `text` blocks out as
  `unit_tests_only` does (one reading, `holds_doctest`), so the five crates whose only blocks are `text` ones - `cohort`, `measure`,
  `pages`, `reviews` and `rust/mode_a` - run no `cargo test --doc`, a pass that ran no test, observed 2026-11-21, method: the old
  and the new reading run over every crate's sources. Nothing reads the plain run's output but the readers that book `build` as
  compile.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the coverage pass's word for a crate's plain tests | n/a - no map | n/a | none | n/a |

### T57 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A crate's tests are built and run once for one state of its inputs wherever one run
   answers for both: after a green coverage pass (`make static`, `make closing-checks`, `make land`'s gate), `make rust-test` on a
   crate whose whole `cargo test` that pass ran stands on it.
2. **The constraints.** T57's line: measured first what the plain run catches that the covered run does not; static's plain build and
   test dropped where the covered run answers; `make rust-test`'s fast uninstrumented loop unchanged; red first on a failing test
   caught by the covered run alone. T111's premise (every test target in `--lib`, no code reading `cfg(coverage)`). FR-013. T58 owns
   `rust/guard`'s layout and the gate crates' `Cargo.toml` in this clone; neither is touched.
3. **Where each comes from.** O: the event log's Phase lines and Edit and Write lines since 2026-11-20T12:35Z (item 4); O: `cargo
   tree -e features`; O: the crates' targets, sources and fences read; O: the red-first run and the guard's run (item 9); G: FR-013
   (the GM 2026-11-20, request.md: "can we in general priotitize performance improvements going forward?"); the task as filed
   (T57's line).
4. **Do they describe the world here?** Measured, not assumed:
   - `make static` runs `rust lint`, `format --check`, `cover` and `dead` and no `rust test`; its Phase lines are `cover-build` 31.4
     min, `lint` 26.4, `cover-run` 20.8 and `format` 0.3, and no `build` or `test` line, measured 2026-11-21 (the Phase lines of every
     clone's event logs since 2026-11-20T12:35Z, by their `make`).
   - The plain `build` 83.7 min (733 lines) and `test` 44.1 min (687) are all `rust-test`'s, `make rust-test` or `l7r-gate.sh rust test`
     with no make above, measured 2026-11-21 (the same lines).
   - `land`'s plain 5.2 and 1.2 min are `counters-inert`'s `--all-features` run of `pool`, `rust/mode_a` and `rust/phases`, a cfg the
     coverage run (default features) does not answer, measured 2026-11-21 (the same lines).
   - The line's cover-build 73 and cover-run 44 min sum each step over every target (`rust-cover`, `static`, `land`,
     `closing-checks`), measured 2026-11-21 (the same lines).
   - The guard's share of the plain time is 53.6 min of build and 36.9 of test, T111 keeping no guard result since its `src/main.rs`
     refused it, measured 2026-11-21 (the same lines, by crate).
   - What `cargo test` runs that the coverage run does not, each read from the crates' manifests, targets, sources and doc fences:
     - binaries: eight crates have one (`src/main.rs`, `src/bin/hamlet.rs`), none holding a test, a `cfg(test)` or a `mod x;`, their
       test-cfg compile the lint's (`clippy --all-targets`), measured 2026-11-21 (each binary's source read).
     - doctests: none - 10 fenced blocks in 10 files, every one `text`, and no indented block, measured 2026-11-21 (every
       `//[/!]` line opening a fence listed, and the indented form searched).
     - integration tests, examples and benches: none, measured 2026-11-21 (each crate's `tests/`, `examples/`, `benches/` and
       manifest read).
     - `cfg(coverage)`: one test, `checks`' `every_pointer_in_the_repository_resolves_to_a_fragment` (`cfg(not(coverage))`), whose job
       the gate's preflight `check research-pointers` and the push's `research-pointers` row also do, so `checks` stays out of the
       keep, measured 2026-11-21 (the sources searched for the cfg).
     - features: a family's coverage build is one cargo call, which unifies features across its crates - `l7r_gate_owed` resolves with
       `testkit` for `claims` built beside `arbiter`, with none alone, measured 2026-11-21 (`cargo tree -e features -p ...`); the plain
       build is a crate's own (found and left, below).
     - time bounds: 4 tests assert one, floors or a 5 s ceiling, stricter under instrumentation and never looser, measured
       2026-11-21 (every `elapsed()` in an assertion read).
     - environment: both runs inherit the session's environment, run from the crate's directory and give its tests their own
       `TMPDIR` (`leak_checked`), measured 2026-11-21 (`run_in`, `cover.rs`'s `run_one` and `side.rs` read).
   - What the plain run caught: nothing the covered run misses. 15 plain test reds came after a green coverage run of that crate
     with no Edit or Write in the clone between, and each was read in the session's transcript at its time: 14 followed a shell edit
     of the crate's own sources, a builder's red-first test or deliberate break by `python3`, `sed -i` or `cat >>` (`land`, `plan`
     twice, `task`, `owed` five times, `pages` twice, `measure` twice and this task's `rustc`), its key moving so the plain run was
     owed either way; the 15th, the guard's, was a `FRESH=1` run with the feature's variables exported (T32's sweep for tests reading
     the session's environment, 17 failing), measured 2026-11-21 (each red's command and failures
     read from session `c6fd72d1`'s transcripts). No key carries the environment, the plain run's own neither, so that exposure is
     T93's, not new with T57, and T32 fixed the tests it found, observed 2026-11-21, method: `verdict_key_with` (kept.rs) read - its key is the command, the compiler and the input files - and T32's box read ticked.
   - What the keep can save: on the eleven crates it adds, 112 plain `build` and `test` lines, 13.7 min of the plain 127.8, came after a
     green coverage run with no edit between, measured 2026-11-21 (the same lines; an upper bound, as an edit made by the shell, or of
     the tree a crate's tests read, is not seen there). The guard's own repeated loop is most of the rest (T58's ground).
5. **The order.** After T55 (the closing step this task closes with); beside T58 (a different crate); before T22, the close.
6. **The exits.** Green: the red-first test green, `make rust-test`, lint, format, cover and dead on `rust/gate/crates/rustc`, `make
   quick`, `make closing-checks`.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the task line's premise (a plain run inside `make static`) did not hold; the Phase lines' `make` field
   was read per target before any code, and the finding restated above rather than a plain run invented to drop.
8. **The budget.** One landing.
9. **Done, measured.**
   - Red first: `a_failing_test_is_caught_by_the_covered_run_alone_and_a_green_one_answers_for_the_plain_run` (the fake cargo: a crate
     whose binary holds no test, its covered test failing) and the new cases of `a_crate_whose_unit_tests_are_its_whole_cargo_test`
     failed on the unfixed code, 2 failed and 77 passed - the covered run's failure named the crate, the plain run after it still owed,
     and after a green pass the plain run did not stand - measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/rustc`); 79 passed
     after, measured 2026-11-21 (the same).
   - The doc pass, red first: the `text` cases of `a_crate_whose_unit_tests_are_its_whole_cargo_test`, now asking `has_doctests` the
     same as `unit_tests_only`, and a `text`-only library beside a fenced one in
     `a_crate_with_a_doctest_runs_cargo_s_doc_pass_with_its_features` (one `test --doc` call, not two) failed on the unfixed reading,
     2 failed and 77 passed, measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/rustc`, `/tmp/t57/doc-red.log`); 79 passed
     after, with the crate's format, lint, cover and dead clean, measured 2026-11-21 (the same, and each check on the crate).
   - The doc pass's cost, each crate's `test` Phase span under `make rust-test CRATE=<crate> FRESH=1`, two runs before and two after,
     at load average 19 before and 20 to 23 after on 22 cores, measured 2026-11-21 (the event log's Phase lines, `uptime` after each
     set):
     - `measure` 2.8 and 3.3 s, then 0.8 and 0.8 s, measured 2026-11-21 (the same).
     - `rust/mode_a` 14.2 and 12.4 s, then 7.9 and 7.2 s, measured 2026-11-21 (the same).
     - `cohort` 2.1 and 0.5 s, then 0.5 and 0.5 s, measured 2026-11-21 (the same).
     - `pages` 0.2 and 0.2 s, then 0.3 and 0.4 s, measured 2026-11-21 (the same).
     - `reviews` 1.6 and 1.5 s, then 3.4 and 3.5 s, measured 2026-11-21 (the same).
   - The change takes a cargo call away and adds none, so the rises are the host's load, and about 2 s a run is saved on `measure`
     and 5 s on `rust/mode_a`, observed 2026-11-21, method: the spans above, and the fake cargo's calls in the red-first test.
   - The guard on the real tree, its key moved by a scratch file under `scripts/` its tests read: `rust cover --crate rust/guard` 11.1
     s, then `make rust-test CRATE=rust/guard` 0.18 s ("test unchanged on rust/guard - its last green result stands"), where the plain
     run that coverage pass now answers took 6.0 s (711 tests, its binary already built), measured 2026-11-21 (each timed by `date`
     around it, the file removed after).
   - `make static`, warm, before the change: 7.27 s, `checks`' and `task`'s coverage owed and 130 results kept, measured 2026-11-21
     (`make static`, timed by `date` around it).
   - `make static`, warm, after: 27.2 s for the same work - `checks`' and `task`'s coverage owed, 130 results kept - its coverage tests
     4.7 s and 5.7 s against 0.6 s and 0.8 s before, on a machine at load average 29.6 on 22 cores, measured 2026-11-21 (`make static`
     under `STATIC_OK`, timed by `date` around it, `uptime` after). The change moves nothing `make static` runs, so its time is not the
     task's measure: the saving is the `make rust-test` after it, measured above. In `make closing-checks` it took 45 s beside
     `hooks-test` and `quick`, three crates' coverage owed (the gate's binary rebuilt over the `rustc` edit), measured 2026-11-21
     (`make closing-checks`' table).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No reader of a map sees anything differently; the change is when a builder's `make rust-test` reruns a
    crate's tests, and every test it no longer reruns ran green in the coverage pass over the same inputs.

**Found and left?**
- The coverage build of a family unifies its crates' features, so a crate's covered tests may run with a dependency's `testkit` its
  own build lacks (`owed` for `claims`, `land`, `trials` and `rust/gate` beside `arbiter`, `bundle` or `record`), and T111's keep
  stands on that run - observed 2026-11-21, method: every `cfg(feature)` gate of the gate crates read (one switches behavior,
  `owed`'s `entry_lines` seam; the rest add items, which a crate naming them without the feature fails to compile in its own lint)
  and `cargo tree -e features` for one pair. Not a defect: a difference with no wrong outcome shown - a crate's lint runs on its own
  features, and the gate (`make done`, the push) already rests on the coverage run alone for these crates' tests.
- The clone-claim backstop refused this builder's first Edit of the clean clone (T62 measured it: the first edit of a clean clone, the main session's included, not every Edit and Write) in its own dispatcher's clone (a `kind: bg` job, which
  `forked_from` does not know), so the edits went through exact-replacement scripts. Not fixed here: the fix is in
  `rust/guard`'s `clone_sync_hooks`, where T58 is working in this clone, and a guard edit rebuilds the gate crates T58 is counting.
  Filed as T62; lands before T22.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop faster - a crate's plain tests not built and run
again after a green coverage pass answered for them); not engine speed, so no checklist answers.


<!-- plan-archive: T58 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T59 to T59 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T60 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T60 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T61 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T61 to T61 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T63 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T67 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T67 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T68 to T12 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T68 to T68 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T69 (the finding as filed, restated by its measurement: a row carrying an advisor call holds `usage.iterations` of the builder's own call, the advisor's and the builder's own again, its top level the builder's two summed; the event log's `tok` and T10's transcript reader read the top level, so the advisor's own tokens - 82,254,728 input and 6,504,729 output over the session's subagent transcripts, 23,629,763 and 2,273,188 of them in the 223 agents of 451's window - were in no figure, measured 2026-11-21 (`/tmp/t69/rows.py` and `/tmp/t69/cross.py`, the `advisor_message` iterations summed one row per `message.id`))

- **Approach**: The `SubagentStop` writer (`rust/guard/shared/src/guards/event_log_hooks/fields.rs`) writes beside `tok` a sibling
  `adv` field, the same four keys (`in`, `cached`, `created`, `out`) summed over the agent's `advisor_message` iterations, each
  `message.id` once as `tok` counts it (`advisor_of`, a second parse of a row only where it names the type; `Tally` keeps one `adv`
  entry a call beside `calls`, replaced with it). It is written wherever `tok` is, zero where the agent called no advisor, so a stop
  before T69, which carries none, reads as uncounted, not zero. T10's reader (`rust/gate/crates/measure/src/measure/where_time/columns/spent.rs`)
  gives `Tok` an `adv: Option<Adv>`: `of_usage` sums a transcript row's `advisor_message` iterations, `Tok::of` reads a stop's `adv`
  (`flight.rs`, one argument), and `render` shows `k advisor in` and `k advisor out` beside `k tokens in` and `out` in the task table
  and the agent table, and the advisor's figure beside the agents' in the summary line - which `make feature-report` shows through
  `where_time::columns_text`, one renderer. `tok`, `ctx`, `context.rs`, T59's wait and T68's reading are unchanged. A sibling field
  rather than a part of `tok`: `tok` stays the builder's own calls as D6 wrote it, so no reader of it changes meaning (its three exact
  assertions in `tests/cost.rs` stand); the cost is the second read in `flight.rs`. How it was measured: item 4.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the advisor's iterations booked apart, in the writer and the reader | n/a - no map | n/a | none | n/a |

### T69 Approach (checklist part A)

1. **The goal, in the world.** No map changes. `make where-time` and `make feature-report` show what an agent's advisor calls read
   and wrote beside its own model calls, so the cost of a builder that calls the advisor is no longer short by them.
2. **The constraints.** T69's line: both places, a separate figure, red first on an advisor row. FR-004 (an agent's cost on its stop
   line, D6), FR-005 (what was spent beside the critical path, D7), FR-013 (performance work). The builder's edit list: `fields.rs`
   and its tests, the measure crate's `where_time` and `feature_report` and their tests, this section; `context.rs` (T68), T59's wait,
   T54's `stale_terms.rs` and T70's `rust/browser` untouched.
3. **Where each comes from.** O: the row's shape and the session's advisor rows (item 4); O: the red-first and green runs and the
   before and after `make where-time` (item 9); G: FR-013 (the GM 2026-11-20, request.md: "can we in general priotitize performance
   improvements going forward?"); the task as filed (T69's line, from T68's found-and-left).
4. **Do they describe the world here?** Measured, not assumed:
   - The row's shape: `agent-a0234478442863bca.jsonl`'s `msg_011ChAbHEgmj2kXEyQ9QXkyb` holds iterations `message` (2 input, 21,143
     cache read, 8,409 cache written, 1,611 output), `advisor_message` (32,395 input, 7,030 output, `model` `claude-fable-5-2`) and
     `message` (2, 29,552, 2,531, 241), its top level 4 / 50,695 / 10,940 / 1,852 - the two `message` iterations summed, the advisor's
     in neither, measured 2026-11-21 (a Python read of that row). The tests' advisor rows are that row's usage.
   - Over the session's subagent transcripts 588 calls carry an advisor iteration, on 2,722 rows, and every row of one call carries
     the same one (the first row's equal to the last's on all 588), so the writer (the last row of an id) and the reader (the first)
     read one figure, measured 2026-11-21 (`/tmp/t69/rows.py`).
   - None of the 2,722 advisor iterations read from the cache or wrote to it, so the reader's `Adv` keeps its input as one figure,
     measured 2026-11-21 (a Python tally of their cache fields).
   - The session's advisor total is now 82,254,728 input and 6,504,729 output tokens (T68's 81,317,939 and 6,412,906 at its time,
     the session since grown), measured 2026-11-21 (`/tmp/t69/rows.py`).
   - The writer's added work: 14.35 MB (6.9%) of the transcripts' 206.7 MB of `assistant` usage rows, which `call_of` parses, name
     `advisor_message` and are parsed again, measured 2026-11-21 (a Python pass over the session's subagent transcripts, their bytes
     summed by row). They are 2,758 of 53,934 such rows, 36 of them naming it in text alone (an advisor iteration of zero), measured
     2026-11-21 (the same pass, its rows counted). The transcripts hold 816.8 MB, the largest 50.3 MB, measured 2026-11-21 (their
     sizes, the same pass).
   - Before: `make where-time F=451 SINCE=2026-11-20T04:33:00Z UNTIL=2026-11-21T09:25:22Z` read 223 agents, 1,313,884.9k tokens in
     and 6,627.3k out, 0 with no count, and no advisor figure, measured 2026-11-21 (`/tmp/t69/wt-before.log`).
   - An independent tally of those 223 agents' transcripts, rows inside the window, each `message.id` once: the builder's own
     1,313,884,859 in and 6,627,318 out - the command's figure exactly - and the advisor's 23,629,763 in and 2,273,188 out, measured
     2026-11-21 (`/tmp/t69/cross.py` over the before run's agent table).
5. **The order.** After T68 (whose builder found it) and T59 (whose wait is in `fields.rs`, left as it is); beside T54 and T70
   (other files); before T22, the close.
6. **The exits.** Green: the two red-first tests green, the crate-scoped checks on `rust/guard/shared` and the measure crate clean,
   the after run's advisor figure equal to the independent tally and its builder figures equal to the before run's, and
   `make closing-checks` green.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one row shape, measured on every advisor row of the session (item 4).
8. **The budget.** One landing.
9. **Done, measured.** Red first: `an_advisor_calls_own_iteration_is_booked_beside_the_builders` (`event_log_hooks/tests/cost.rs`)
   failed `left: Null`, `right: {"in": 64790, "cached": 0, "created": 0, "out": 14060}` on `adv` - its `tok` assertion, the top level,
   already passing - and `a_stop_carries_its_agents_tokens_context_and_task` failed `left: Null` on its zero `adv`, 319 passed;
   `an_advisor_calls_tokens_are_booked_beside_the_builders_own` (`where_time/columns/spent_tests.rs`) failed on the absent
   `k advisor in` header, its builder columns already the expected 62.6 / 2.0, 5.0 / 1.5 and 67.6 / 3.5, 201 passed; measured
   2026-11-21 (`make rust-test CRATE=rust/guard/shared` and `CRATE=rust/gate/crates/measure`, `/tmp/t69/logs/red-shared.log` and
   `red-measure.log`). After the fix: `rust/guard/shared` 321 tests, the measure crate 202 and `rust/guard` 416 pass, and format, lint
   and cover are clean on `rust/guard/shared` and the measure crate (its format after `make format FILE=` of `spent_tests.rs`, four
   `has(` calls rewrapped), measured 2026-11-21 (the crate-scoped checks, `/tmp/t69/checks.sh`, `/tmp/t69/logs/*.log`). After, over
   the before run's window: 223 agents, 1,313,884.9k tokens in and 6,627.3k out, 0 with no count - the before run's figures unchanged
   - and the advisor's own 23,629.8k in and 2,273.2k out beside them, 0 with no count, equal to the independent tally (23,629,763 and
   2,273,188), measured 2026-11-21 (`make where-time F=451 SINCE=2026-11-20T04:33:00Z UNTIL=2026-11-21T09:25:22Z`,
   `/tmp/t69/wt-after.log`, and `/tmp/t69/cross.py` over its agent table); `make feature-report F=451` over the same window shows the
   same table and line (`/tmp/t69/fr-after.log`, no `WRITE=1`); and to the run's own time, about 09:38Z, the advisor's 23,835.9k in
   and 2,295.7k out beside the agents' 1,337,683.3k and 6,749.9k, measured 2026-11-21 (`make where-time` with `UNTIL` the time of the
   run, `/tmp/t69/wt-after-now.log`). `make closing-checks` ran red on one step alone, `make static`'s format of
   `rust/gate/crates/record` (`stale_terms/tests.rs`, T54's builder's uncommitted file in the same clone, outside this task's files),
   its `hooks-test` and `quick` green, measured 2026-11-21 (`/tmp/t69/logs/closing.log`). Another builder's `make closing-checks` ran
   beside it in the same clone from 09:38:06Z, this one from 09:38:33Z waiting on its run lock, the two writing one
   `.git/closing-checks/`, so its `static.log` holds both runs' lines - the first's lint, format, cover and dead clean on 34 crates,
   then this run's lint clean and the record crate's format red, the record file changed between the two format steps - measured
   2026-11-21 (that log's lock-wait lines, `ps` and the exit file's time). On the final tree format and the tests are green on `rust/guard/shared` and the measure crate, their last green results
   standing for its keys, measured 2026-11-21 (the crate-scoped checks, `/tmp/t69/logs/final.log`).
10. **Before moving a constant.** n/a: no constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. What changes is a feature report's cost: the 223 agents of 451's window read and wrote
    23,629,763 and 2,273,188 tokens through the advisor that no figure showed, measured 2026-11-21 (item 4) - a wrong outcome, a
    builder's cost reported short, so the code is fixed, not the claim.

**Found and left?**
- Two `make closing-checks` runs in one clone share `.git/closing-checks/`: each deletes the other's `.exit` files at its start and
  truncates its logs, so a run can read the other's verdict as its own (observed 2026-11-21, method: this task's run of 09:38:33Z and
  another builder's of 09:38:06Z, whose `quick` verdict came from this run's file). Not fixed here: the closing step is T55's, outside
  this task's files. Filed as T72; lands before T22.

**Performance work?** Yes - a `[perf]` task (451 FR-013): it measures the builders' loop, the advisor's tokens counted in a builder's
cost, so a builder that leans on the advisor is priced as it runs. Not an engine-speed task. Its own cost: the stop's writer parses
6.9% of the bytes it parsed before a second time, measured 2026-11-21 (item 4's Python pass over the session's subagent transcripts).


### T70 (rust/browser's end-to-end test, the one on the real Chromium, failed good work under load: `page.wait_for_function: Timeout 40ms exceeded.` in `make closing-checks`' cover run at 2026-11-21T08:46:27Z; the crate's cover run alone was clean 96 s after, measured 2026-11-21 (the event log's Phase lines))

- **Approach**: the 40 ms was the test build's ceiling on the lit page's raster wait (`rust/browser/src/lit.rs`, `WAITS`), measured
  2026-11-21 (a read of `lit.rs`), which is already the page's own signal: a `Runtime.evaluate` awaiting
  `window.l7rMap.rasterReady()`, polled on each animation frame. The end-to-end test's page readies at once, so the 40 ms covered only
  the answer's way back from a real Chromium just after its load, which came late under load, measured 2026-11-21 (the timer of item 9).
  The ceiling is now the shipped minute (`READY_WAIT`, the Python's `timeout=60000`) in every build; the test build reads it through a
  thread-local (`READY_CEILING`, the crate's `crop::WAIT_DIVISOR` precedent) which only
  `a_page_that_never_readies_or_throws_is_refused`, the one test that waits a ceiling out, shortens to 40 ms on its own thread (a
  CONVENTION: the old test ceiling, kept so that refusal stays fast). The zoom key's settle keeps its test-build 1 ms (a sleep, not a
  wait), measured 2026-11-21 (a read of `lit.rs`). The fake browser (`testkit.rs`) gains `lateready`, a raster answered 50 ms after
  it is asked (a CONVENTION: past the old 40 ms ceiling, short enough for FR-008), and `a_page_slow_to_ready_is_waited_for` pins it.
  Red first: with the old `lit.rs`, the new test alone failed, `"page.wait_for_function: Timeout 40ms exceeded."`, 30 passed and 1
  failed, measured 2026-11-21 (`make rust-test CRATE=rust/browser FRESH=1`, log `/tmp/t70/red-first.log`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the lit page's raster ceiling, the shipped minute in the test build | n/a - no map | n/a | none | n/a |

### T70 Approach (checklist part A)

1. **The goal, in the world.** The browser crate's tests pass on a loaded host when the code is right, and still fail when a page
   never readies: a slow answer is not a defect, a missing one is.
2. **The constraints.** 449 FR-008: a test under a tenth of a second on an idle host, except the crate's one end-to-end test
   (`crop::tests::the_real_chromium_renders_and_crops_a_local_page`, the one that failed, which is exempt; the new fake test is not).
   451 FR-013, a `[perf]` task. Only `rust/browser` changes; T54's builder (`rust/gate/crates/record`) and T69's (`rust/guard/shared`
   `event_log_hooks`, the `measure` crate) are left alone.
3. **Where each comes from.** O: the event log's Phase lines and the load runs below. R: the Python's `page.wait_for_function(...,
   timeout=60000)`, which `lit.rs` ports (feature 449 T150). G: none needed; the ceiling the shipped code already uses.
4. **Do they describe the world here?** Yes. Of the 40 browser runs in the event log (Phase, step `test` or `cover-run`, crate
   `rust/browser`, 2026-11-20T12:01Z to 2026-11-21T09:18Z), 1 was red, measured 2026-11-21 (a script over `.git/l7r-events/*.jsonl`,
   `/tmp/t70/count.py`): 1 of the 8 under `make closing-checks`, 0 of the other 32 (8 `test`, 24 `cover-run`). The Phase lines record no
   load; 9 other crates' cover runs overlapped the red one, measured 2026-11-21 (the same lines' `t0`/`t1` intervals,
   `/tmp/t70/overlap.py`). Reproduced on the old binary: with 44 busy loops on 22 cpus the end-to-end test failed 1 of 10 runs with
   the same message, idle 0 of 5, measured 2026-11-21 (`/tmp/t70/load.sh`, the test run alone by its binary).
5. **The order.** After T68, whose closing run found it; independent of T54 and T69, whose crates it does not touch.
6. **The exits.** Green: the late page passes, the never-readying page still fails, and the end-to-end test passes every run under the
   load that reproduced it. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The other short test-build waits the end-to-end test meets fail nothing when they run out: the
   browser's 300 ms close wait kills the process (`cdp.rs` `close`), and the render's 2 s idle wait returns a `bool` the render does not
   act on (`serve.rs` `render`), measured 2026-11-21 (a read of both functions).
8. **The budget.** One landing.
9. **Done, measured.** The new test green and the never-readying page still refused (`make rust-test CRATE=rust/browser`: 31
   passed), and the end-to-end test green in 30 of 30 runs with 44 busy loops on 22 cpus (load average 10.6 rising to 58.3) and 10 of
   10 idle, measured 2026-11-21 (`/tmp/t70/load.sh` on the fixed test binary, the test run alone). The raster wait's answer took a
   median 4.8 ms and at most 9.6 ms idle, a median 20.2 ms and at most 121.3 ms loaded, 6 of the 30 loaded answers past the old 40 ms,
   measured 2026-11-21 (a temporary timer around the wait in `lit_on`, removed before the closing run); the minute's ceiling is about
   500 times the slowest loaded answer. The new fake test ran in 0.082 s, under 449 FR-008's tenth of a second on a host that was not even idle
   (load average 48.7 at the start), measured 2026-11-21 (`make test-times CRATE=rust/browser`, best of three); the end-to-end test
   took 0.957 s, the one test over the bar, declared end-to-end and exempt, measured 2026-11-21 (the same run).
10. **Before moving a constant.** n/a: the test build's ceiling moves to the shipped one, which no research claim states.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A defect: the closing checks went red on correct code (a wrong outcome, constitution XIV), and a builder who
    reads that red re-runs or chases a fault that is not there.

**Found and left?** none.

**Performance work?** yes - a `[perf]` task (451 FR-013): the builders' loop loses no closing run to a false red. Not an
engine-speed task.


### T71 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T71 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T72 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T72 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T73 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T73 Approach (checklist part A)

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

**Found and left?** <none - or a `- ` item each, with its visible effect or the research finding it breaks (an item with neither is not a defect and is not filed), fixed in this task by default and saying `fixed here`; a deferral says `Not fixed here: <why>. Filed as T<n>; lands before T<m>.`, both open tasks of tasks.md (`make task-add`); a fix of a class of defect (every writer, every form) carries `observed <YYYY-MM-DD>, method: <how every instance was found>` (451 T17, D15)>

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>

