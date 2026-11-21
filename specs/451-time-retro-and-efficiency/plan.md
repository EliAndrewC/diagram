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
### T48 (the bundle read ids inside a clause naming another feature by its number as the reviewed feature's, filed by the round arbiter on `ask:451-T46-fourth-round` (accept, 2026-11-20) to be measured first; measured 2026-11-21: 4 of the 5 real such clauses across every plan handed the reviewer the reviewed feature's same-named id, unmarked, method below)

- **Approach**: `named` in `rust/gate/crates/plan/src/plan/bundle.rs` reads a run of ids followed by a clause naming a feature by its number (`in N's`, `of feature N`, `from N`) as N's. `QUALIFIED` gains a third branch, a run no number names with that clause after it, all of it the clause's feature's, where a numbered run is cut: no number claims its head, every such run among the 8 measured holds one id, and a misread costs a line marked with the clause's feature or a NOT FOUND line, never this feature's text unmarked; `ANOTHER` captures the clause's number, so the part of a numbered run that `own_run` cuts off at such a clause is that feature's too, where it fell to the bare reading; `Named::claim` keeps this feature's ids in the text, to be carried, and takes another's out, so `foreign` carries it from that feature or names it NOT FOUND. A clause naming the reviewed feature reads as before, and so does one naming a source by another name ("in house style's"), its part left bare.
  - the measurement, measured 2026-11-21 (`/tmp/t48-scripts/measure.py`: `named` emulated regex for regex over every `specs/*/plan.md` and `plan-done.md`, 327 files, 282 and 45): 8 such clauses, 2 naming the reviewed feature (451's own, in T46's section) and 6 another. Of the 6, 1 is a quoted test string in T46's section, naming a feature with no directory, and 5 are real: 319 plan.md line 213, 443 plan.md line 25, 415 plan-done.md line 91, 449 plan-done.md line 967 and 133 plan.md line 15. Each names its id once in its block, only in the clause; none of the 8 reads a count as a feature number.
  - the bundles, measured 2026-11-21 (each block put as a task section of a scratch copy of its feature, `/tmp/t48-tree`, with the named features' directories beside it, and built by `scripts/gates/l7r-gate.sh plan decide <F> T900`; before `/tmp/t48-scripts/bundles-before/`, after `/tmp/t48-scripts/bundles-after/`): on HEAD 4 of the 5 real ones (319, 443, 415, 449) carried the reviewed feature's own same-named requirement or decision as the cited one, with no "may mean either" line, each a different rule from the named feature's (319's carried its pilot-order rule where 134's is "the SVG and PNG are unchanged"), and 133's carried nothing. With the fix, 319's, 415's and 133's carry the named feature's text (134's, 207's and 132's), and 443's and 449's name it NOT FOUND (435 holds no such id; 239 writes its requirements unlisted, Found and left). T46's quoted string now names its two decisions NOT FOUND where it carried 451's, and T46's "in 451's sections" carries the same two decisions, byte for byte. The only other lines that moved are two ids already named with 132's number, NOT FOUND in the before-bundles because the scratch tree held no 132 when they were built, and, in `spec-index.md` of 319, 443 and 449, the reviewed feature's own id, back in the index now that no block cites it.
  - red first, the test before the code: `ids_in_a_clause_naming_another_feature_are_that_feature_s` (`bundle/tests.rs`: the 319, 415 and 133 shapes, a numbered run cut at another feature's clause, this feature's run cut so, and a clause naming this feature) failed on HEAD, 157 passed and 1 failed, measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/plan`, `/tmp/t48-scripts/red.log`); green, 158 of 158, measured 2026-11-21 (`/tmp/t48-scripts/green.log`). T46's own test passes unchanged: its fixture feature is 999, the reviewed one, so its clauses name the reviewed feature.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `named`'s clause reading | n/a - no map | n/a | none | n/a |

### T48 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A plan reviewer handed a block that names another feature's requirement or decision in a clause after it reads that feature's text, or a NOT FOUND line saying so, never the reviewed feature's same-named one.
2. **The constraints.** T48's line (measured first across every plan and `plan-done.md`; fixed only if a real clause hands a reviewer the wrong text, red first; read as N's, carried or named NOT FOUND); the round arbiter's ruling `ask:451-T46-fourth-round`; T46's reading, untouched but for a clause naming a feature by its number; constitution XIV; 100% line coverage of the plan crate by its own tests; only `bundle.rs`, its tests and this section edited (the brief).
3. **Where each comes from.** O: the measurement of 2026-11-21 (the Approach); G: none - the ruling and the brief are the coordinator's.
4. **Do they describe the world here?** Yes: the real bundles of the 5 real clauses, built by HEAD's binary, carried the wrong text in 4 (measured 2026-11-21, the Approach).
5. **The order.** None needed: T78's and T79's files are untouched.
6. **The exits.** Green: the plan crate's tests, lint, format and cover clean, and `make closing-checks` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - `named` is the one reader of whose ids a block names (`cited_text`'s and the amendment reading's in `build`). The clause's other branch, a source named by another name, measured 2026-11-21 (the same corpus and script): 2 real (273 plan.md line 58, 414 plan-done.md line 102), each naming the feature's own work, so no wrong outcome.
8. **The budget.** One landing.
9. **Done, measured.** 158 of 158 in the plan crate (measured 2026-11-21, `/tmp/t48-scripts/green.log`); the after-bundles as the Approach says (measured 2026-11-21). `make closing-checks` in this clone red on `static` and `hooks-test` alone by another builder's half-edited `rust/guard/shared/src/tree.rs` (E0061 and E0057, T79's), `quick` green (measured 2026-11-21, `/tmp/t48-scripts/closing.log`), so measured again on HEAD `fbbe56cc97` with this task's three files alone, in a detached worktree (`/tmp/t48/t48wt`): `static` green (2,321 s), `quick` green, and the plan crate's lint, format and cover clean (measured 2026-11-21, `/tmp/t48/wt-closing.log`, `/tmp/t48/wt-lint.log`, `wt-format.log`, `wt-cover.log`). Its `hooks-test` was red on 45 suites, every one because the fresh worktree's guard binary was built during the run, then on 2 when run again (`/tmp/t48/wt-hooks2.log`), and each of those 2 green alone: `no-poll-hooks.sh` 144 of 144, its 3 liveness cases red only under the full fan-out's load, and `test-l7r-gate.3.sh` once given the mirror's model cache, which a worktree outside the clones has none of (measured 2026-11-21, `/tmp/t48/wt-nopoll.log`, `/tmp/t48/wt-gate3.log`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reviewer of 319's Constitution Check block or 443's Performance bookends block (and, while they were live, 415's T04 and 449's T050 sections) read the reviewed feature's own requirement or decision as the one cited - the T42 failure; after it, the named feature's text or a NOT FOUND line.

**Found and left?**
- The clause reading - fixed here, observed 2026-11-21, method: every clause of the form across every `plan.md` and `plan-done.md` (the Approach's measurement).
- A requirement a spec writes as an unlisted bold id (a bold id at a line's start with no list dash) is not read by the bundle's requirement reader (`requirements`), so a block citing one gets a NOT FOUND line where the text exists: 449's T050 clause against 239, observed 2026-11-21; 24 specs write some requirement that way, all of features 129 to 271, measured 2026-11-21 (`grep -lE '^\*\*(FR|SC)-[0-9]{3}' specs/*/spec.md`). A NOT FOUND line where the text exists tells a reviewer the requirement is missing, a wrong outcome. It predates T48 - a citation by the feature's number alone gets the same line. Not fixed here: the requirement reader is a separate reader from the clause reading T48 changed, and whether a live plan cites such a requirement is measured first. Filed as T82; lands before T22.
- 443's plan.md line 25 cites an id its named feature does not hold - now named NOT FOUND, which is no wrong outcome; left as written, 443's plan being outside the brief.

**Performance work?** no.


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


<!-- plan-archive: T50 to T33 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T50 to T50 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
<!-- plan-archive: T54 to T54 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T56 to T53 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T56 to T56 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
<!-- plan-archive: T60 to T59 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T60 to T60 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T67 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T67 to T67 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T71 (the finding as filed, restated by its measurement: the 2 `phases.log` waits T61 left as "an agent's own separate calls, no process between them" each had a live producer, measured 2026-11-21 (each wait's launching transcript read for the Bash calls that write the file, with each call's `backgroundTaskId` and `timedOutAfterMs`): T178's a script run in the background, which T61's walk already reads alive, and T151 part B's the agent's own foreground call that the harness moved to the background at 180 s, which the walk read gone because the call OPENS with its assignment (`B=<dir>, ... | tee -a $B/phases.log`) after the quote of the harness's `eval '...'`, measured 2026-11-21 (the two producers replayed as stand-ins on the real `/proc`, `/tmp/t71/replay.sh` and `/tmp/t71/probe.sh`))

- **Approach**: neither of the two shapes the brief offered (the wait reading the waiter's own transcript as the writer; the no-poll
  guard refusing a wait on the session's own next write) is built, because the measurement found no wait of that kind and the
  first would hide a dead run: of the 114 traced rewrites whose file has a writer, 0 watched a file only the agent's own foreground
  calls write and 15 had a background writer BESIDE the agent's own appends (T178's among them), where "your session writes it"
  would answer alive over a killed run. The defect behind the one false "gone" left is in the walk: `ASSIGN`
  (`finished_run_hooks/runs.rs`), which `expanded` reads a command's simple assignments by, took an assignment only after the
  text's start or a blank or `;&|(`, and the harness runs every command as `eval '<command>'`, so the assignment a command opens
  with follows a quote - `$B` stayed unexpanded, `written` dropped the target as holding a `$`, and the live call read as no run.
  `ASSIGN`'s leading class takes a quote too (`'` or `"`). `expanded` serves `files_named` as well (feature 295's live runs and
  their output files), which now reads the same assignment.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| an assignment that opens the harness's `eval '...'` is read | n/a - no map | n/a | none | n/a |

### T71 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A backgrounded wait on a file that a live call appends to through a variable the call
   assigns first - the shape every agent's scratch log takes (`S=<scratch>; ... >> $S/phases.log`) - runs until its line comes,
   including a foreground call the harness moved to the background; a waiter and a reader opening the same way are still no run, so
   a dead run's wait still ends with exit 3 and the "gone" line.
2. **The constraints.** T71's line (measure first how many rewritten waits watch a file only an agent's own calls write; then the
   check asks what stands for that agent's life, red first on a phases log quiet between an agent's calls); the brief's two options
   and its rule to choose the simpler that is right; FR-013; the feature 227 ruling the helper serves (the GM 2026-09-12: a wait on
   output that does not check its producer is alive gets the second proof of life from the hook); never a process pattern (the
   2026-07-25 `pgrep -f "make done"` defect); T61's walk and its reader rule (naming the file is no proof). The brief's files:
   `writer-alive.sh`, `finished_run_hooks`, `no_poll_hooks`, their tests and suites, the `docs/guards.md` rows, this section; T74's
   `shared` `event_log_hooks` and T73's `rust/gate/crates/record` untouched.
3. **Where each comes from.** G: the GM 2026-09-12 (the helper's header); O: the session's transcripts and task outputs (item 4);
   O: T61's replayed rewrites (`/tmp/t61/watched.json`, from the guard log's `proof-of-life` rows); O: the red and green runs
   (item 9); the task as filed (T71's line; T61's found-and-left).
4. **Do they describe the world here?** Measured 2026-11-21 (each of the 2 `phases.log` waits' launching transcript read for every
   Bash call naming the file, and the wait's task output): T178's wait (`be0ovktos`, `until grep -q "before h175 end"
   $S/phases.log`, gone at 167 s quiet) waited on a line `before.sh` wrote - a script the agent ran by path in the background 9
   minutes before (`b0cyou1k5`), its text `echo "before $h end ..." >> $S/phases.log`, the line written about a minute after the
   wait ended. Measured 2026-11-21 (the same reading of T151 part B's agent's transcript, with each call's result): its wait
   (`bcmk2v816`, `until grep -q "pointers rc=" .../phases.log`, gone at 207 s quiet) waited on a line its own foreground call of
   11:47:30Z wrote (its `echo "pointers rc=$?" | tee -a $B/phases.log`, after a `make quick`), which the harness moved to the background
   after 180 s (`brqu4wm0y`, its result's `timedOutAfterMs` 180000, `subagentCapApplied`), alive at 11:51:01Z (its agent's own `ps`,
   3 min 30 s old). So neither waited on its own next write. Measured 2026-11-21 (`/tmp/t71/replay.sh`, T61's stand-in rows on the real `/proc`): T178
   read alive under T61's walk (`alive <pid> runs .../before.sh which writes it`), T151 gone (the verb printed nothing), each gone
   with only a Monitor-shaped reader. Measured 2026-11-21 (`/tmp/t71/probe.sh`, 5 stand-ins in the harness's wrapper on T151's
   file): T151's recorded command, `B=<dir>; echo x | tee -a $B/phases.log` and `B=<dir>; echo x >> $B/phases.log` read gone; the
   same after `true; ` and a literal path read alive - the assignment opening the `eval` is what the walk missed. Measured
   2026-11-21 (`/tmp/t71/measure.py`: each of T61's 368 rewrites matched to the Bash call that launched it in its session's
   transcripts, every call of that transcript writing the watched file classed - a background launch, its command or the script it
   runs writing the file; a foreground call the harness moved to the background; a plain foreground call): 190 untraceable (the
   transcript swept, or no call with the rewrite's command), 1 with no path; of the 177 traced, 15 a task output, 48 no writer seen
   (a make target's own log, a page session's run, a script swept since), 114 with a writer - 94 a background launch, 12 one beside
   the agent's own foreground appends, 3 a moved call and a launch beside its own appends, 2 a moved call, 1 a moved call and a
   launch, and 2 classed as the agent's own calls alone, both `p19/fresh-cohort.log` of 2026-10-25, whose producer on reading was
   `bash probe19-fresh.sh`, launched in the background, its text written by a foreground heredoc and swept since. So 0 of 114,
   measured 2026-11-21 (that classing, the 2 read by hand).
   Measured 2026-11-21 (the same waits, the last background writer launched before each, its command wrapped as the harness wraps
   it and read by HEAD's `ASSIGN` and the fix's): of 101 (the 114 less 13 whose only background writer was launched after the
   wait, or none was), 11 had their write behind an opening assignment (9 launched, 2 moved), T151's among them; 90 read already.
5. **The order.** After T61, whose found-and-left filed it; beside T73 and T74, whose files it leaves; before T22.
6. **The exits.** Green: the runs tests' new case, the no-poll suite's 6b with its two new cases, the finished-run suite, the guard
   crate's tests and crate-scoped lint, format, cover and dead, `make closing-checks`, and the two replays (T151 and T178 alive,
   each gone under a reader alone). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through
   `make arbiter-ask`.
7. **The search smell.** None: the walk is T61's, by pid; one character class changes.
8. **The budget.** One landing.
9. **Done, measured.** Red first, measured 2026-11-21 on HEAD's walk with the new tests: (`make rust-test CRATE=rust/guard`) 422
   passed, 1 failed - `a_command_that_opens_with_its_assignment_writes_through_it`, at its first assertion, `written` over T151's
   recorded command in the harness's wrapper naming no `phases.log`; (`tests/hooks/test-no-poll-hooks.sh`) 143 passed, 1 failed -
   "a live call whose command opens with its assignment and tees into it: alive", rc=1, the "gone" answer - while its dead-side pin,
   "a waiter and a reader opening with their assignment, and no run: still gone", passed. Green, measured 2026-11-21 on the final
   files: (`make rust-test CRATE=rust/guard`) 423 passed, 0 failed; the first run of the two suites beside it read the wrapper's
   binary while it was rebuilt (built 07:10:37, the no-poll suite done 07:10:38: the same alive case red, and 5 of the finished-run
   suite's Stop cases red), and run again on the built binary: (the no-poll suite) 144 passed, 0 failed; (`tests/hooks/
   test-finished-run-hooks.sh`) 68 passed, 0 failed, as T61 left it. The replays, measured 2026-11-21 on the built binary:
   (`/tmp/t71/probe.sh`) all 5 stand-ins alive, `<pid> writes it`; (`/tmp/t71/replay.sh`) T151 alive (`alive <pid> writes it`)
   and T178 alive (`alive <pid> runs .../before.sh which writes it`), each gone with only a Monitor-shaped reader. The crate-scoped
   checks, measured 2026-11-21 (`l7r-gate.sh rust lint`, `format --check`, `cover`, `dead` `--crate rust/guard`): each clean, the
   first cover run having named the new test's assertion message (a line only a failure reaches, folded onto its assertion).
   Measured 2026-11-21 (`make closing-checks`, on the final files): GREEN, all three - static 111 s (format, lint, cover and dead
   clean on 34 crates), hooks-test 73 s (55 guard suites green, 3 unchanged), quick 2 s; its first run was red on the new test's formatting alone (`make format FILE=`).
10. **Before moving a constant.** No constant moved (the 45 s belt, the helper's `STALE` knob, and `SCRIPT_BYTES`, a GUESS and a knob, stand).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** What a session sees differently: a wait on a scratch log its live call appends to through the variable the
    call opens with - a foreground call the harness moved to the background, or a background launch - no longer ends early with exit
    3 and "the run that was producing it is gone" (T151 part B's at 207 s quiet, measured 2026-11-21 (its task output, `bcmk2v816`)),
    and a wait whose run is gone still ends at the belt. No map, no research claim. T61's item 4 classed the 2 `phases.log` waits
    as the agent's own calls with no process between them: restated here, as measured, by its producers (item 4); `plan-done.md`
    keeps T61's words.

**Found and left?**
- Fixed here, the class of a live call whose write reaches the file through the assignment it opens with: observed 2026-11-21,
  method: every traced rewrite's last background writer before its wait, wrapped as the harness wraps it and read by HEAD's
  `ASSIGN` and the fix's (item 4: 11 of 101); a quote is the one character the harness puts before a command's first word.
- Not built, and not a defect: a wait on a file only the waiting session's own later calls write. Measured 0 of 114 (item 4); such a
  wait, backgrounded, deadlocks nothing (it ends when the session writes the line) and costs one exit-3 notice; the two answers
  priced - the waiter's transcript read as the writer (a wrong answer in the 15 waits with a background writer beside the agent's
  own appends: alive over a killed run) and a refusal at the wait's start (nothing measured to refuse, and at the start a producer
  may not have begun) - were not built; chosen by the builder on the measurement.

**Performance work?** Yes, a `[perf]` task (451 FR-013): it makes the builders' loop faster - a wait over a live call no longer ends
early, so the builder does not re-wait or stop a run it was told was gone. Not an engine-speed task, so no
docs/performance-checklist.md answers.


<!-- plan-archive: T72 to T69 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T72 to T72 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T73 to T54 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T73 to T73 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T74 to T21 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T74 to T74 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T76 (the mirror's `.git/l7r-events/_unassigned.jsonl`, written from /diagram before T74 filed a call under its session's clone, held 15 lines the refile's rules place: 1 to 405, 11 to 430 and 1 to 449, none of them in this clone's logs, and 2 to 451 that T74's merge had already put in the clone's 451 log in their re-filed form, measured 2026-11-21 (the refile run without `--from` on a scratch copy, `/tmp/t76/scratch-refile.log`, and an exact-line count of each moved line in each clone's log); and, once T74 landed, no 451 log in the mirror to re-merge, measured 2026-11-21 (`ls` of the mirror's `.git/l7r-events/`))

- **Approach**: `rust/gate/crates/measure/src/measure/event_log/refile.rs` gains `--from <events dir>`. The logs it re-files are read
  from that directory and their kept lines written back there; the moved lines are appended to `--dir`'s logs. Without `--from` the
  source is `--dir`, as before.
  - Why the refile and not `merge.py`: the refile already places each line, skips a line already in its target, and rewrites its
    source of exactly the lines it moved, carrying over a live hook's late bytes. `merge.py` merges one whole file into one target, so
    it would have needed the split, three runs and a removal step added. The change is one field and one argument, its 100% coverage
    one test, measured 2026-11-21 (`git diff -U0`: 5 code lines added and 4 changed, the usage text among them).
  - Only a line the rules send to a feature other than its source log's name moves; a line they leave stays in the source. So a
    mirror's log of the clone's own feature is not merged by `--from` (T74's 451 log needed `merge.py`), as the module doc says.
  - A deliberate deviation from T76's line, labeled: the moved lines are APPENDED to their targets, the refile's own write, not
    inserted in time order by the T74 merge's rules. WHY: the brief offers the refile route, and the readers sort by `t` (the refile's
    module doc). What it costs: one out-of-order adjacent pair at each appended block, 405 1 to 2, 430 0 to 1, 449 290 to 291, 451 100
    to 100 (nothing appended), measured 2026-11-21 (`/tmp/t76/verify.py`'s count of each `t` against the line before it,
    `/tmp/t76/verify.log`). Who chose: the builder, on that count and the brief.
  - `make events-refile` takes `FROM=<events dir>` (wired by the session after the run, its dry run of the mirror 0 to move, measured 2026-11-21); the run itself, before the wiring, was `scripts/gates/l7r-gate.sh
    measure event-log refile --root <clone> --dir <clone>/.git/l7r-events --from /diagram/.git/l7r-events`, every path explicit, as
    T74 ran `--dir`.
- **Red first** (`refile::tests::a_second_directorys_log_is_refiled_into_the_clones_logs`). The scratch world is the clone's two
  features plus a mirror directory whose `_unassigned.jsonl` holds a line by brief whose re-filed form is already in the clone's 451
  log, one by brief that is not, one by task id to a log the clone does not have, and two lines no rule places. A dry run counts 3 and
  writes nothing in either directory. The run appends the 2 new lines once, rewrites the source to the 2 kept lines, creates nothing
  beside it, and leaves the clone's own misfiled lines where they are. A second run moves 0, and `--from` with no value is usage 2.
  - before: 202 passed and the new case failed, the refile answering its usage (code 2) where 0 was asserted, measured 2026-11-21
    (`make rust-test CRATE=rust/gate/crates/measure`, `/tmp/t76/red.log`).
  - after: 203 passed, 0 failed, measured 2026-11-21 (the same command, `/tmp/t76/green.log`).
- **The run** (`.git/l7r-handoffs/T76-scripts/backup/`, outside any `l7r-events` directory: the mirror's file as
  `_unassigned.before.jsonl`, 5,296 lines, measured 2026-11-21 (`wc -l`), and this clone's 405, 430, 449 and 451 logs as
  `<feature>.before.jsonl`):
  - the dry run against the mirror: 5,296 lines read; 1 to 405, 11 to 430 (10 by brief, 1 by task id), 1 to 449, 2 to 451, 15 moved,
    measured 2026-11-21 (`/tmp/t76/dry.log`).
  - the run, with `MAIN_TREE_OK` and its reason: the same counts, 15 moved, measured 2026-11-21 (`/tmp/t76/run.log`). Of the 15, 13
    were appended and 2 were already in the 451 log, measured 2026-11-21 (`/tmp/t76/verify.log`).
  - the check: the mirror's file equals its snapshot less exactly the 15 raw lines, 5,281 lines, measured 2026-11-21
    (`/tmp/t76/verify.py`, `/tmp/t76/verify.log`). Each of the 13 re-filed lines is in this clone's 405, 430 and 449 logs exactly once, the 2 in its 451 log exactly once, and 0 backed-up lines are missing from any
    of the four, measured 2026-11-21 (`/tmp/t76/verify.py`, `/tmp/t76/verify.log`, exit 0).
  - a second dry run: 5,281 read, 0 moved, measured 2026-11-21 (`/tmp/t76/dry2.log`).
- **Which clone**: every line went to this clone's log, measured 2026-11-21 (`ls /diagram/.clones/*/.git/l7r-events/`):
  - 405's log is also in `diagram-backlog-pages`, another session's clone, which was not written (last written 2026-10-22, measured
    2026-11-21, `stat`). Its one line is session `d2dc8c63`'s, whose claim map names this clone.
  - 430's and 449's logs are only in this clone. The 1 line from session `f16cf709` (claim map `diagram-memories`, no such clone now)
    is in this clone's 430 log, measured 2026-11-21 (`/tmp/t76/verify.log`, the claim maps under `.clones/.session-clones/`).
- **The re-merge** (T76's second part): nothing to move. The mirror's `.git/l7r-events/` held only `_unassigned.jsonl` after T74
  landed (12:31Z), last written 2026-11-21T04:33:35Z, 5,296 lines, T74's count, measured 2026-11-21 (`ls`, `stat`, `wc -l`). So no 451
  log was written there in the gap, and `merge.py` had nothing to merge or move to the backup.
- **`make where-time F=430 SINCE=2026-10-26T15:00:00Z UNTIL=2026-10-26T18:00:00Z`**, after the run:
  - T08's agent `a7b6ff002c779b263` (escalation-check, from 16:11 UTC) booked at 1 agent-minute, 56.8k tokens in and 2.1k out, the
    window's agents 2 over 3 agent-minutes, measured 2026-11-21 (`make where-time`, `/tmp/t76/where-after.log`).
  - No before run: where-time reads each clone's log under the fixed `/diagram/.clones` (`events::CLONES`) and ignores
    `L7R_EVENTS_DIR`, so a before needs the live log edited. An empty `L7R_EVENTS_DIR` gave the same report, measured 2026-11-21
    (`make where-time` with it, against `/tmp/t76/where-after.log`). Before the run, none of that agent's 9 lines were in any log
    the report reads, all 9 only in the mirror's `_unassigned.jsonl`, measured 2026-11-21 (a `grep -c` of the agent id over every
    log in each clone's `.git/l7r-events/` and the backups).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the refile's `--from` source directory | n/a - no map | n/a | none | n/a |

### T76 Approach (checklist part A)

1. **The goal, in the world.** No map changes. Every line a session wrote into the mirror's `.git` that the refile's rules place is
   in the log of its feature in the clone that holds that log, and gone from the mirror, so `make where-time` for 405, 430 and 449
   in this clone books it. The mirror's file keeps only what no rule places.
2. **The constraints.** T76's line and its brief:
   - the mirror's lines the refile's rules file to other features, and those already merged into this one, put home with a dry run
     first and backups, the mirror's file emptied of exactly what moved;
   - this clone's copy only, never another session's clone;
   - red first, since the refile gains the second source;
   - the re-merge of any of this feature's lines written in the mirror in the gap;
   - files: `refile.rs` and its tests, this section. T77's `planhold.rs` and T50's `tree*` are untouched, and nothing is committed.
3. **Where each comes from.** O: the scratch refile and the exact-line counts (the heading); O: the red and green runs (Red first); O:
   the dry run, the run, the check and the second dry run (The run); O: `ls` and `stat` of the clones and the mirror (Which clone,
   The re-merge); the task as filed (T76's line) and T74's Found and left, which filed it.
4. **Do they describe the world here?** Every figure is from the mirror's file, this clone's logs and the clones' `ls`, with this
   clone's rules (its `specs/`, `task-starts.jsonl` and the sessions' subagent briefs), measured 2026-11-21 (The run). The red case
   reproduces the live shape, including a line already merged in its re-filed form, in a scratch world.
5. **The order.** After T74 (which landed the writer's fix and found these lines) and T26/T56 (the rules it reuses); before T22.
6. **The exits.** Green: the red case green with every earlier case unedited, `make rust-test CRATE=rust/gate/crates/measure`,
   `make closing-checks`, the check with 0 missing and the mirror's file its snapshot less the 15, and a second dry run of 0. Red:
   what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The scratch run and the dry run against the mirror agreed on the counts, 1, 11, 1 and 2, and the
   mirror's file after the run equals the scratch run's remainder, measured 2026-11-21 (`/tmp/t76/scratch-refile.log`,
   `/tmp/t76/dry.log`, `/tmp/t76/verify.log`).
8. **The budget.** One landing. The added work is none per line: the source directory is read in place of `--dir`, one path, measured
   2026-11-21 (the code read).
9. **Done, measured.**
   - the red case green, 203 passed, measured 2026-11-21 (`make rust-test CRATE=rust/gate/crates/measure`).
   - 13 lines appended to this clone's 405 (1), 430 (11) and 449 (1) logs, 2 already in 451, the mirror's file 5,296 to 5,281 lines,
     0 missing, measured 2026-11-21 (`/tmp/t76/verify.log`).
   - the measure crate's format, cover and dead clean, measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust <check> --crate
     rust/gate/crates/measure`, `/tmp/t76/measure-static.log`), and lint clean on all 34 crates, measured 2026-11-21 (`make
     closing-checks`' static leg, `/tmp/t76/closing2.log`).
   - `make closing-checks` red in 2 of its 3 legs on files that are not this task's: static's format on `rust/guard/shared`
     (`planhold.rs` and its tests, T77's), and hooks-test's `idle-tests-hooks.sh`, 3 of 34, which passed in the run before with
     this task's code in. quick green, measured 2026-11-21 (`/tmp/t76/closing2.log`). The second red in a row, so no third run.
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of `make where-time F=430` in this clone sees the T08 escalation-check of 2026-10-26 booked, the
    agent at 1 agent-minute, where none of its lines were in a log the report reads, measured 2026-11-21 (`/tmp/t76/where-after.log`,
    a `grep -c` of the agent id over every log in each clone's `.git/l7r-events/` and the backups). Its dispatch, its start, its
    three Bash calls and its stop, and session `f16cf709`'s Bash call of 16:28, are now in the 430 log, and 405's and 449's logs each
    gain one Bash `PreToolUse` line (T07 of 2026-10-23, T127 of 2026-11-12), measured 2026-11-21 (`/tmp/t76/verify.log`, the moved
    lines read). Nothing on a map.

**Found and left?** none.

**Performance work?** Yes, a `[perf]` task (451 FR-013): it makes the builders' loop faster to measure, since `make where-time` books
the lines where it reads them, as T74 did. Not an engine-speed task, so no docs/performance-checklist.md answers.


### T77 (the plan hold refused an Edit of the heading after a held section, found by T73's builder on 2026-11-21: `edit_hits` in `rust/guard/shared/src/checks/planhold.rs` read `a <= start + t.len()`; the guard log holds 3 refusals of that shape, measured 2026-11-21, method below)

- **Approach**: `edit_hits` asks whether the edit's text OVERLAPS held text, both ends exclusive - `a < start + t.len() && start < a + old.len()` - in place of `start <= a && a <= start + t.len()`; the `replace_all` clause (`old` inside held text) stays. That fixes two wrong outcomes: an edit starting at the next section's heading was refused, and an edit starting before the held section and ending inside it passed the pre-call refusal (caught only by the write-back after a live hold's call; the task line said it was "still refused" - on HEAD it was not).
  - red first, the test before the code: `an_edit_is_held_only_where_it_overlaps_the_section` (six cases on the suite's fixture: the next heading and an edit ending at the section's start pass; an edit running in from before it, the last held byte, one starting inside and running past, and the heading itself are refused) misjudged 2 of 6 on HEAD - `"## T02 other"` refused and `"# plan\n\n## T01 the bath"` passed - 322 passed, 1 failed, measured 2026-11-21 (`make rust-test CRATE=rust/guard/shared`, `/tmp/t77/red2.log`).
  - green: 323 of 323, measured 2026-11-21 (`make rust-test CRATE=rust/guard/shared`, `/tmp/t77/green.log`).
  - the log, measured 2026-11-21 (every `~/.claude/guard-log` entry naming the hold's refusal text; each Edit's `old_string` from its builder's transcript; each placed on the last commit of the plan before it, as the guard read the working tree this is an approximation): 26 record-edit refusals by the hold from 2026-10-19 to 2026-11-21, 6 Edit and 20 Bash. Of the 6 Edit refusals, 3 have T77's shape - T60 held and T67's heading edited (10:24:01 and 10:25:02, one edit retried, so 2 distinct edits), T71 held and T73's heading edited (12:15:52, T73's builder's) - each starting exactly at the held section's end on commits `fe0e24b02b` and `30f5b415f6`; the other 3 edited inside the held section (T15's and T44's placed by git history, T62's by its own builder on its own section). The fix passes the 3 and still refuses the 3.
  - the Bash path, a defect for a live hold and a foreground call (round 1 of this section's plan review, 2026-11-21, decision 6), not fixed here (Found and left): a write to `plan.md` through a tool is refused when its command names a held heading, a held line of 16 or more characters, or a quoted string held text contains. Replayed on the 18 task-held Bash refusals (the 2 on block holds not replayed; same approximation): 8 matched text found only in the held section, 7 only text every section shares (the template's `|---|---|---|---|---|` and `8. **The budget.** One landing.`, an anchor `**Found and left?**` or `**Performance work?**`), so a write to ANOTHER section was refused - T44 held while T46's was written, T67's while T75's, T73's while T74's - and 3 could not be replayed (the held text was uncommitted then). The written text cannot be placed before the call runs - a program computes it, or reads it from a file (T46's `/tmp/t46-scripts/t46-section.md`) - and after it runs the write-back already places it exactly, but only for a LIVE hold (`snapshot` keeps only those) and a call that ends before its PostToolUse: the pre-call refusal is a pending hold's and a backgrounded write's only guard, and a template line is how it sees a rewrite of the held section anchored on short or computed text. For those two the refusal on shared text is the guard failing closed (round 1's decision 5). The 7 were neither: each names a launched agent with no "looks dead" tail (a live hold, from the log) and its call carries no `run_in_background` (foreground, from each call's transcript), measured 2026-11-21 - a check refusing good work, as the Edit shape did. The fix it wants: for a live hold and a foreground call, count only text standing in the plan inside held text alone (`live(&h, now)`, `snapshot`'s own filter, and `crate::wait::background`), leaving a change made through shared text to the write-back; it passes the 7 and keeps the 8. It is not built here because the write-back it would rest on does not run after every such call: `checks_hooks` (`rust/guard/src/guards/checks_hooks.rs`) runs `after` on `PostToolUse` and `SubagentStop` alone (its `events`, read 2026-11-21), so a foreground command that writes the held section and then exits non-zero (`PostToolUseFailure`) is written back by nothing, and today the pre-call refusal is its one guard. The fix spans that file, outside T77's brief, and is filed as T78.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `edit_hits`'s overlap bound | n/a - no map | n/a | none | n/a |

### T77 Approach (checklist part A)

1. **The goal, in the world.** No map changes. While a plan review runs, a builder's Edit of the section after the held one - its heading included - goes through, and an Edit that would change held text, wherever it starts, is refused before it runs.
2. **The constraints.** T77's line (the bound exclusive at the section's end, red first on an edit starting at the next heading, an edit inside the held section still refused); its brief (an edit ending inside it refused too; the guard log measured for others of the shape; the Bash path ruled, left if right; only `planhold.rs`, its tests, the record-edit suite, the `docs/guards.md` row and this section edited); feature 385 T85's hold; FR-012 (a refusal fixed red first).
3. **Where each comes from.** O: T73's builder's refusal of 2026-11-21 and the guard log's 26 (measured 2026-11-21, the Approach); G: none - the brief is the caller's.
4. **Do they describe the world here?** Yes: the 3 Edit refusals of the shape start exactly at the held section's end on the commits before them, and the fixture's six cases reproduce both wrong outcomes on HEAD (measured 2026-11-21, `/tmp/t77/red2.log`).
5. **The order.** None needed: T76's refile and T50's `tree*` files are untouched.
6. **The exits.** Green: the shared crate's tests, lint, format and cover clean and `make closing-checks` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - the one reader of an Edit's place is `edit_hits`; the Python twin `hm_planhold.py` is gone (`scripts/hooks/lib/` checked 2026-11-21).
8. **The budget.** One landing.
9. **Done, measured.** 323 of 323 in `rust/guard/shared` (measured 2026-11-21, `/tmp/t77/green.log`); the crate's lint and line cover clean (measured 2026-11-21, `scripts/gates/l7r-gate.sh rust lint` and `rust cover`, each `--crate rust/guard/shared`, `/tmp/t77/lint.log`, `/tmp/t77/cover.log`); its format check red on two rewraps, clean after `make format` on the two files (measured 2026-11-21, `/tmp/t77/fmt2.log`); `make closing-checks` red on `static` alone, by another builder's half-edited `rust/guard/shared/src/tree.rs` (3 E0308 at lines 414-422 and its red tests, T50's), `hooks-test` and `quick` green (measured 2026-11-21, `/tmp/t77/closing.log`); so the crate was measured again on HEAD `cabf09c2ae` with this task's two files alone, in a detached worktree: 323 of 323, lint and format clean (`/tmp/t77/wt.log`), and line cover clean once the test's failure message no longer stood on a line of its own (`/tmp/t77/wt2.log`), measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust test`, `lint`, `format --check`, `cover`, each `--crate rust/guard/shared`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder's correct edit was refused (3 refusals in the log, each a lost call), and an edit that changed held text passed the pre-call refusal - for a pending hold, with no write-back, it would have voided the review's verdict unseen.

**Found and left?**
- An Edit starting before the held section and ending inside it was not refused before it ran (the task line's "still refused" did not hold on HEAD) - fixed here, observed 2026-11-21, method: the fixture's case `"# plan\n\n## T01 the bath"`, red on HEAD; every reader of an Edit's place is `edit_hits`.
- A live hold's pre-call refusal of a foreground Bash write to ANOTHER section, on text every section shares (7 of the 18 replayed task-held refusals, all live and foreground, measured 2026-11-21; each a builder's lost call). Not fixed here: narrowing it is safe only once the write-back runs after a failed call too, in `checks_hooks.rs`, outside T77's brief. Filed as T78 (the write-back on `PostToolUseFailure` first, then the narrowing in `planhold.rs`); lands before T22.
- A foreground Bash call that changes held text and then exits non-zero is never written back: `checks_hooks` has no `PostToolUseFailure` in its `events` (read 2026-11-21), so only the pre-call refusal stands between it and a voided verdict. Not fixed here: the same file, outside the brief. Filed as T78; lands before T22. Unmeasured: whether a foreground call the harness moves to the background at 180 s (observed 2026-11-21, method: T71's measurement of t151's call) gets its `PostToolUse` at the move or at its end - T78 measures it first.

**Performance work?** no.


### T78 (the plan hold refused a shell write that shares only template text with the held section, found by T77 on 2026-11-21: 7 of the 18 replayed task-held Bash refusals matched only text every section shares, each a live hold and a foreground call; and its write-back ran on `PostToolUse` alone, so a command that changed held text and then exited non-zero was written back by nothing)

- **Approach**: two changes, in order, each red first, after the measurement T77's section asked for.
  - the measurement, 2026-11-21: a Bash command that exits non-zero fires `PostToolUseFailure` and no `PostToolUse` (this builder's `exit 3`, toolu_01VpHJEF57LMjfwfA9pCRy6y: one PreToolUse and one PostToolUseFailure line in the 451 event log). A foreground call the harness moves to the background gets its one `PostToolUse` AT THE MOVE and nothing at its end: this builder's 205 s foreground call (timeout 300 s) moved at 180 s, its `PostToolUse` at 13:22:19.664Z with `ms` 180052 and `bg` beu5tx5ri, its end at 13:22:44.6Z with no line, measured 2026-11-21 (the 451 event log), and the 38 other moves of 170 s or more in the clones' event logs one PreToolUse and one PostToolUse each, no `PostToolUseFailure`, no `BgEnd`, measured 2026-11-21 (`/tmp/t78/moved.py`). A call is moved at its own timeout too (this builder's 120 s scan, observed 2026-11-21). All 39 were subagents' calls; a main-session move is unmeasured (none in the logs). So the write-back stands behind a foreground call for what it changed by its end or its move, never after the move.
  - the write-back on failure: `checks_hooks` takes `PostToolUseFailure` beside `PostToolUse` and `SubagentStop`; a Bash, Write or Edit call runs `after` on either, and a failed Agent or TaskStop call returns before `launched` - booked as a launch, a failed Agent call set its pending hold `running` with no agent to return it, a hold for half an hour. `.claude/settings.json` already registers `PostToolUseFailure` for the dispatcher (read 2026-11-21): no settings change.
    - red first: `a_failed_call_is_written_back_and_a_failed_launch_keeps_its_hold`, driven through `protocol::run` so the guard's own event filter decides, 423 passed and 1 failed on HEAD, the write-back's assertion (measured 2026-11-21, `make rust-test CRATE=rust/guard`, `/tmp/t78/red1.log`); with the event added alone, red again on the failed Agent call's hold read `running` (`/tmp/t78/red1b.log`); green: 424 of 424 (measured 2026-11-21, `make rust-test CRATE=rust/guard`, `/tmp/t78/green1.log`). Through the binary, a `PostToolUseFailure` of a call that changed held text, piped to `l7r-guard --only checks-hooks PostToolUseFailure` on a scratch clone: the mirror's binary exits 0 and leaves it changed, this task's exits 2 and writes it back, measured 2026-11-21 (`/tmp/t78/failure-replay.py`, `/tmp/t78/failure-replay.log`). Unmeasured: whether the harness shows a `PostToolUseFailure` hook's exit-2 text to the caller - the write-back does not rest on it.
  - the narrowing: in `planhold.rs` `refusal`, for a LIVE hold (`live`, `snapshot`'s own filter) and a call without `run_in_background` (`crate::wait::background`), `bash_hits` counts a held heading, line or quoted string only where the plan outside the held text (`outside`: each held text cut out, a NUL in its place) does not hold it too; a pending or dead hold and a background call are refused on shared text as before, and so is a task whose own headings stand apart in the plan (its joined section stands nowhere whole, so `outside` is None and nothing is read as outside it).
    - red first: `a_shell_write_on_shared_text_is_refused_only_where_nothing_writes_it_back` (nine cases on a fixture whose two sections share `8. **The budget.** One landing.`: live and foreground on the shared line pass, for a task hold and a block hold; a background call, a pending hold and a dead hold on it, a held-only line live and foreground for both holds, the held heading, and a pending background call are refused; then a split section refused on the shared line) misjudged 2 of 9 on HEAD - the two live foreground writes on the shared line refused - 330 passed, 2 failed, the other `house_style_hooks`' 20 s bound under load (measured 2026-11-21, `make rust-test CRATE=rust/guard/shared`, `/tmp/t78/red2.log`); green: the test passes, 331 of 332, the one failure `house_style_hooks`' `a_spelling_past_a_million_steps_is_corrected` past its 20 s bound at a load average of 82 (run alone from the same binary it failed at the bound too, the process ending at 20.08 s, and nothing T78 changed runs in it), measured 2026-11-21 (`make rust-test CRATE=rust/guard/shared`, `/tmp/t78/green3.log`; `uptime`).
  - the replay (`/tmp/t78/replay.py`: each of T77's task-held Bash refusals from `~/.claude/guard-log`, its plan at the last commit before it, a scratch clone holding it under a live hold, the call's own `run_in_background` read from its transcript, piped to a built `l7r-guard --only record-edit-hooks PreToolUse`, at a 34 MB peak): through the mirror's binary of HEAD's code as control, 15 of the 15 placeable refused, measured 2026-11-21 (`/tmp/t78/replay-head.log`), and T221's and T33's passed because their held text was not yet committed (T77's 3 unplaceable with T98's of 08:12:02Z; the 2 block holds not replayed); through this task's binary (this clone's build of 2026-11-21 08:46, `/tmp/t78/l7r-guard.t78`, which carries T79's uncommitted `tree*` edits too), the 8 with held-only text stay refused (T98 of 07:50:18Z, T104 of 08:20:18Z, 08:20:50Z and 08:50:31Z, T11's 2, T01, T025) and the 7 on shared text alone pass (T104 of 08:25:08Z, T27, T063, T44's 2, T67, T73), the same 8 and 7 T77's reading named, with T221's and T33's passing as on HEAD, measured 2026-11-21 (`/tmp/t78/replay-t78.log` beside `/tmp/t78/replay-head.log`, a 35 MB peak).
  - accepted, the moved call and the detached writer (who chose: this builder, under T78's brief; the GM may overrule): a live hold's foreground call that outlives its move and then writes held text through shared text alone now passes the pre-call refusal, and nothing writes it back; so does a foreground command that detaches its writer (a lone `&`, `nohup`, `setsid`, `disown`), its `PostToolUse` at the shell's return and its write after - `no_poll_hooks` refuses a detached job for make and cargo alone (451 T15, read 2026-11-21). Its cost, the same for both: `make plan-verdict` refuses the verdict (`record.rs`: a task's `section_sha256`, a block review's `plan_sha256` and each block's digest, read 2026-11-21) and the review runs again, about 1-4 minutes, observed 2026-11-21, method: `HOLD_MAX_S`'s comment in `planhold.rs`, the evening's 42 reviews. Measured 2026-11-21: 0 of the 39 moved calls' commands named `plan.md` with a write shape (`/tmp/t78/moved.py`, each command read from its transcript). Priced and not taken: (a) keeping a moved call's snapshot and checking it at later calls - it needs the move's `backgroundTaskId` in `restore`, which `handle.rs` does not pass, outside the brief, and a subagent's moved call has no end event to check at; (b) no narrowing where the command also runs a make target - it covers make alone, not every long step, for a case measured at 0 of 39; (c) no narrowing where the command detaches - `no_poll_hooks`' reader of a detach is the guard crate's, not the shared crate's `planhold.rs`, and a second reader of it is the search smell item 7 names.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the write-back on `PostToolUseFailure` | n/a - no map | n/a | none | n/a |
| the narrowing to held-only text | n/a - no map | n/a | none | n/a |

### T78 Approach (checklist part A)

1. **The goal, in the world.** No map changes. While a plan review runs, a builder's foreground shell write to another section of the plan goes through even when its command quotes a template line the held section also holds; a write that changes held text through such a line is written back when the call ends, whether it exits zero or not; a pending hold or a background call is still refused on any held text.
2. **The constraints.** T78's line (the write-back on `PostToolUseFailure` first, then the narrowing for a live hold and a foreground call, a pending hold or a background call still refused on shared text, each red first); its brief (the moved call's question measured first; the replay keeps the 8 and passes the 7; only `checks_hooks`, `planhold.rs`, their tests, the record-edit suite, the `docs/guards.md` rows and this section edited; the settings checked); feature 385 T85's hold; FR-012 (a refusal fixed red first).
3. **Where each comes from.** O: T77's replay of 2026-11-21 and this task's measurements of 2026-11-21 (the Approach); G: none - the brief is the caller's.
4. **Do they describe the world here?** Yes: the two failure shapes reproduce on HEAD (`/tmp/t78/red1.log`, `/tmp/t78/red2.log`), and the HEAD binary refuses all 15 placeable refusals of the log (`/tmp/t78/replay-head.log`), measured 2026-11-21.
5. **The order.** The write-back first, then the narrowing that rests on it; T79's `tree*` files and T48's `rust/gate/crates/plan` are untouched.
6. **The exits.** Green: both crates' tests, lint, format and cover clean, the replay's 8 refused and 7 passed, and `make closing-checks` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - the one reader of a shell write to a held plan is `bash_hits`, the one write-back `restore`: `grep -rln "plan_snaps\|bash_hits" rust/ scripts/` (2026-11-21) names `planhold.rs`, `checks_hooks.rs` and four test files alone.
8. **The budget.** One landing.
9. **Done, measured.** 424 of 424 in `rust/guard` (`/tmp/t78/green1.log`) and 331 of 332 in `rust/guard/shared`, the one failure a 20 s bound under a load average of 82 (`/tmp/t78/green3.log`), measured 2026-11-21 (`make rust-test`); the replay's 8 refused and 7 passed (`/tmp/t78/replay-t78.log`, measured 2026-11-21); the shared crate's lint and format checks red only on T79's half-edited `tree.rs` and `tree/tests/words.rs` (a clippy `format_push_string` at `tree.rs:351`, rewraps), this task's four files clean under `make format FILE=` (measured 2026-11-21, `scripts/gates/l7r-gate.sh rust lint` and `rust format --check`, `--crate rust/guard/shared`, `/tmp/t78/lint-rust_guard_shared.log`, `/tmp/t78/fmt-rust_guard_shared.log`); so both crates were measured on HEAD `fbbe56cc97` with this task's five files alone in a detached worktree: `rust/guard` 424 of 424, lint, format and cover clean, `rust/guard/shared` 328 of 328 on the first run, lint, format and cover clean once the test's failure list no longer stood on lines of its own (the second run's tests 327 of 328, the one failure the same 20 s bound at a load average of 52), measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust test`, `lint`, `format --check`, `cover`, each `--crate`, `/tmp/t78/wt-checks.log`, `/tmp/t78/wt2-checks.log`); `make closing-checks` red 3 of 3 on T79's `tree*` not compiling, measured 2026-11-21 (`.git/closing-checks/20261121T135041Z-681465/`), so `make hooks-test` with this change is owed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder's correct write to its own section was refused (7 of the log's 18, each a lost call); a command that changed held text and failed left it changed, a verdict voided unseen until `make plan-verdict` refused it; and a failed Agent dispatch would have held a section for half an hour once the guard took failures.

**Found and left?**
- A shell write to another section refused on shared template text, a live hold and a foreground call - fixed here, observed 2026-11-21, method: every task-held Bash refusal of the guard log replayed through the guard binary (`/tmp/t78/replay.py`); `bash_hits` is the one reader.
- A foreground call that changed held text and exited non-zero was never written back - fixed here, observed 2026-11-21, method: the 451 event log's line for a failing call (`PostToolUseFailure` alone) and `checks_hooks`' `events`; `restore` is the one write-back.
- The write-back of a task whose own headings stand apart in the plan restores nothing and still says "the held text is written back": `write_back` replaces the joined section, which stands nowhere whole (read from the code 2026-11-21, not run; 51 of the 898 task sections in `specs/*/plan*.md`, none in 451's `plan.md`, measured 2026-11-21, `/tmp/t78/split.py`); the change stays, and `make plan-verdict` refuses the verdict. Not fixed here: the fix wants each span of `plan_text`'s `ordered_sections`, outside T78's files. Filed as T80; lands before T22.

**Performance work?** no.


### T79 (shared::tree's walk split a `\`-continued line, a `${VAR}`'s braces and a `$(...)` inside a word into segments of their own, and read a `$(mktemp)` directory toward the mirror, found by T50 on 2026-11-21; and it settled a place it could not resolve two ways - a cp's toward where the shell was last known, one of T50's git forms not placed at all (T50's D-d and D-e) - found by T50's plan review, 2026-11-21)

- **Approach**: the walk reads each word whole, then one rule settles every place it still cannot resolve; measured first on four corpora, each change red first.
  - the corpora, measured 2026-11-21: fx (T33's 1,134 fixture rows), tx (T50's 995 git commands), ux (2,311 transcript commands holding a `\`-newline, a `${` or a `mktemp`, `/tmp/t79/ux-all.jsonl`) and bx (59,116 transcript commands standing in the mirror or naming it, from 6,114 diagram transcripts, `/tmp/t79/bx-all.jsonl`, extracted by `/tmp/t79/scripts/extract_all.py`); replayed one row at a time through a built guard in a fresh scratch mirror by `/tmp/t79/scripts2/stream.py`, one driver streaming its corpus with at most 6 guard processes (byte-identical to T50's `replay.sh` on `head.fx.nobody.main-tree-hooks` and `head.fx.gate.gate-write-hooks`, a 26 MB peak on bx, measured 2026-11-21 (`cmp`, `/usr/bin/time -v`)).
  - the walk (`tree.rs`): a `\`-continued line is one command (`joined`, in `sanitize` once heredocs and quotes are out, and in `env_from`); a `${...}` is one word (`closing`); a `$(...)` inside a word is walked as a substitution before its word's command, the word holding `$__sub_<n>__` - found here, the same split: it let spec 204's own D6 case `cd $(somewhere) && git commit` through at HEAD; a `$(pwd)` or `` `pwd` `` is `.`, where the shell stands; a brace expansion (`/tmp/{a,b}`) stays in its word, only a brace group's own `{` and `}` splitting - found here, the same split: `cp /tmp/{a,b} /diagram/x` from `/tmp` passed at HEAD, its destination cut off (the probe `/tmp/t79/probes-br.jsonl`, measured 2026-11-21); a `$(mktemp ...)` is the place mktemp makes (`mktemp_place`: no template `$TMPDIR` or `/tmp`, `-p D` and `--tmpdir=D` D, `-t` preferring `$TMPDIR`, a relative template unresolved, measured 2026-11-21 (uutils coreutils 0.8.0 `mktemp -u` on each form, `TMPDIR` set and unset)).
  - the one rule (`settled` with `known_place`, and `tree/bind.rs`'s `bound_texts`), the same for a redirect, a file tool and a git form: the walk first RESOLVES what the command's own text resolves and walks each binding of its many-valued names (up to 64), their writes together - each of a `for`/`select` loop's literal values; each value of a name assigned more than once with different values (an assignment that reads its own name, `S=$S/sub` or a prefix `S=$S cmd`, follows the one before); a loop's variable also assigned, its loop's values and its literal assigned ones; a name no one assigns, its value in the guard's environment, else empty, as bash reads it; `${N:?}`, `${N:-W}` and `${N%SUFFIX}` (N's directory); `$(dirname X)` and `$(basename X)` of a known X; a name assigned from `$PWD`, where the shell stands at the assignment. A place whose start the walk then knows lies where that start does (the mirror, a clone or elsewhere; `/$X`, a start the mirror lies under, is nothing known). What stays unknown - a name `read`, `mapfile`, `readarray`, `getopts`, `printf -v` or `+=` sets, a chain assignment after the first, a loop over a substitution or with no `in`, a loop's variable assigned a value the walk cannot read, bash's own names (`$RANDOM`), any name once `source`, `.` or `eval` appears, a substitution's value - keeps spec 204's D6: it lands where the shell was last known, so standing in the mirror it is the mirror's. A target's segment is shown from its command, as the command holds it (`bind::from_command`, `shown`). `git.rs`'s cut reading (T50's D-e) and its filter that left an unresolved git place unplaced (D-d) are gone.
  - the arm for what stays unknown, chosen by measurement and by the plan review (BLOCKED 2026-11-21, `/tmp/sfr-t79/verdict-T79.json`): the first round read a write word nothing is known of as not the mirror's (re), which passed the review's five probes (`/tmp/t79b/p0.r.tsv`), each a write of the mirror standing in it (`echo x > $n.txt`, `for i in 1 2; do echo x > $i.txt; done`, `for f in a.txt b.txt; do echo x > $f; done`, `F=$(ls | head -1); sed -i s/a/b/ $F`, `R=$(git rev-parse --show-toplevel); echo x > $R/f`); D6 for every such word (rd) kept 13 of the corpus's scratch writes refused, measured 2026-11-21 (`/tmp/t79/rp2/rd.b29.{t,nobody}.tsv`). Resolving first and then D6 passes all of the 29 bx rows those variants split on (26 HEAD refusals and 3 HEAD passes, the 3 `mkdir -p $(dirname $F)` on a scratch path, bx#31033, #33626, #55610) through main-tree with sid t and nobody, each by resolution, and refuses the five probes, measured 2026-11-21 (`/tmp/t79/rp2/r4.b29.{t,nobody}.tsv`, `/tmp/t79b/p1.r4.tsv`, through `/tmp/t79/bin-r4`).
    - its measured cost in full - every place it reads otherwise than HEAD where the write is not the mirror's - measured 2026-11-21 (the probes `/tmp/t79b/p1.jsonl` through the HEAD and final binaries, `/tmp/t79b/p1.{head,r4}.tsv`; bash 5.3.9; the replay below): a name assigned twice is judged at each value, so `D=/diagram/x; D=/tmp/y; touch $D/f` standing in the mirror is refused though bash writes scratch - the price of judging a branch's `if ...; then D=a; else D=b; fi` both ways, where HEAD's last value passed `F=/diagram/a; echo x > $F; F=/tmp/b`, a write of the mirror, and no corpus command moves by it; `cd $UNSET` goes home, as bash's `cd` with no word does, so `cd $UNSET && touch f` standing in the mirror writes `$HOME/f`, no longer D6's mirror write; `git clone $R` and `git worktree add --detach $W` with R and W unset are no write (bash 5.3.9: git's "You must specify a repository to clone", and `worktree add`'s usage, rc 129, no tree made), and `touch $UNSET/f` is `/f`; a variable only the Bash tool's shell profile sets is read as empty, since the guard reads its own environment - today `~/.bashrc` exports `BASH_ENV` alone, the newest `~/.claude/shell-snapshots` file `PATH` alone and `/etc/sandbox-persistent.sh` nothing, none a write's place, measured 2026-11-21 (grep of `~/.bashrc`, the newest `~/.claude/shell-snapshots` file and `/etc/sandbox-persistent.sh`); `CLAUDE_PROJECT_DIR` is set in the hook's environment (the hook's own command line reads it) and unset in the Bash tool's shell, measured 2026-11-21 (`env`, `/tmp/t79b/env-shell.txt`), so `echo x > $CLAUDE_PROJECT_DIR/f` is judged at the project's directory though bash writes `/f`, an error in the conservative direction; a `python3 -c` program writing a place it computes from `sys.argv` in a loop's body, now seen, is judged where the shell stands, as HEAD judges the same program outside a loop (bx#54240, bx#58694, ux#2209, each writing scratch; the Python rule's, below); and a guard file's name written into a scratch copy in a loop's body is refused by make-only as HEAD refuses the literal `cp <guard file> /tmp/t42/src-t42/<guard file>` (`/tmp/t79b/judge/pmo-head.tsv`; T87's class).
    - red first: `rust/guard/shared/src/tree/tests/words.rs`'s six tests (a continued line, a braced variable, a substitution in a word, a mktemp place, a brace expansion, and `an_unresolved_place_is_settled_one_way_for_every_tool`, the one rule) on HEAD's `tree.rs` and `git.rs`: 325 passed and 9 failed - the six, the one rule's on its first case (`R=/s/r; for pm in 4 8; do sed s/a/b/ $R/M > $R/M.P$pm; done` read `(None, "main", "shell")` for `(None, "elsewhere", "named")`), and three `tests.rs` pins of the rule (measured 2026-11-21, `make rust-test CRATE=rust/guard/shared` in a detached worktree at HEAD with this task's tests, `/tmp/t79/red3.log`; the first four were red first alone on 2026-11-21, 327 passed and 4 failed, `/tmp/t79/red1.log`); `tree/tests/binds.rs`'s first four tests on the first round's walk, 336 passed and 4 failed (`/tmp/t79b/red.log`), and its four third-round tests each red alone before its fix (`/tmp/t79b/red-kw.log`, `red-pwd.log`, `red-self.log`, and `red-loopset.log` with the old rule put back), and gate-write's `timeout` case (`/tmp/t79b/red-gw.log`, 423 passed and 1 failed); green: 345 of 345 in `rust/guard/shared` (words.rs's seven - the six and `an_unbalanced_parenthesis_ends_the_walk_cleanly`, a coverage test - and binds.rs's nine) and 424 of 424 in `rust/guard` (measured 2026-11-21, `scripts/gates/l7r-gate.sh rust test --crate` in this clone, `/tmp/t79b/t17.shared.log`, `/tmp/t79b/t17.guard.log`).
    - the pins the rule moves, each with why: `tree/tests.rs` - `touch $UNSET/f` standing in the mirror (HEAD's pin from 449 T010) is `/f`, elsewhere, since an unassigned name is empty; `git clone $R` is no write (git refuses a clone with no repository), the unresolved clone now `git clone $(cat url)`; `git worktree add --detach $W` is no write (no path, git's usage), the unresolved one `$(cat w)`, D6; `git -C /x/$U commit` is no write in the mirror (`/x/`), `git -C <mirror>/$U commit` refused in its place; `words.rs`'s one-rule test reads `$RANDOM` for the unknown and resolves its loop; and three suites outside the brief's file list, each because a pin wrote an unassigned name as its unknown: `gm_tree_hooks/tests.rs` (`echo x > $UNSET/gm-assistant` is `/gm-assistant`, no write of the tree; D6 pinned by `cd $(somewhere) && echo x > f` standing in it), `main_tree_hooks/tests.rs` (`cd $UNSET && python3 -c ...` becomes `cd $(somewhere) && ...`, since `cd $UNSET` goes home) and `readme_hooks/tests.rs` (`$NEVER_SET_T67` read first by `read NEVER_SET_T67;`, so it stays unknown and its six fail-closed pins keep their meaning, and `echo x > $NEVER_SET_T67/README.md` is no README of the tree), with `tests/hooks/test-readme-hooks.sh`'s two cases, their shell twins; and `gate_write_hooks/tests.rs`, the third round's (a loop's `sed -i` into the tree refused; a loop's `make`, a `then touch` and `timeout 60 make` passed, as their bare forms are); `tests/hooks/test-main-tree-hooks.sh` pins the five probes (section 2), and its fixture's row 59 moves rewrote -> allowed (a scratch write its loop's values resolve) while row 33 stays rewrote (its S a substitution's value, D6), split 164/9.
  - the replay, the final binary against HEAD's (`/tmp/t79/bin-r4`, built 2026-11-21 from this clone's files on HEAD fbbe56cc97 in `/tmp/t79/wt` by `/tmp/t79b/scripts/sync3.sh` and `/tmp/t79/scripts/build.sh`): fx, tx and ux through each guard that reads the walk and all of them, sid t and nobody, and the gate replay (42 files, HEAD's from T50's `replay.sh`), and bx through main-tree, make-only, gm-tree, readme and house-style, sid nobody, measured 2026-11-21 (`/tmp/t79/scripts2/runall2.sh /tmp/t79/bin-r4 r4`, 8 min 29 s, a 34 MB peak, `/tmp/t79b/runall-r4.log`; compared by `/tmp/t79/scripts2/moves.py head r4`, `/tmp/t79b/moves-head-r4.txt`; each refusal's reason read by `/tmp/t79b/judge/why.py`): 87 commands move, each judged by what it really writes.
    - to allowed, 63: through main-tree 45, every one a scratch or clone write HEAD refused or rewrote - a `$(mktemp -d)` place (tx#877, tx#879, ux#1580, ux#1582, ux#1661, ux#857, ux#863), a known scratch start with a loop's or a substitution's name in it (main-tree#59, ux#675, ux#677, ux#1039, ux#2139, ux#2167, ux#2267), a clone's file named through `$C` (window#277), and bx's 30 (26 of the 29 the variants split on, the other 3 passes at HEAD, and 4 `$(mktemp -d)` places); through gate-write 14 (tx#21, #299, #566, #567, #734, #787, ux#692, #900, #902, #904, #906, #1040, #1056, #2082), each a `timeout N make <target>` HEAD refused as a shell write of `.` and passes as its bare `make <target>` does (`timeout 60 make tick` stays refused by the make rule, `/tmp/t79b/judge/pgw3-*.tsv`); through house-style 4 - window#298, a write into a `$(mktemp -d)` copy HEAD corrected as the project's, and bx#4624, bx#4696 and window#241, the replay world's artifact (its mirror lies under `/tmp`, which house-style's `outside` reads as outside; on their real paths both binaries correct them, a direct run); gm-tree's and readme's bx passes moved none.
    - to refused, 24 (ux#2209 rewritten to the clone with sid t): through gate-write 9 - ux#206 (a `cat >` into the clone's spec from a loop's body), ux#714, #740, #742, #746, #750, #758 and #752 (a `sed -i` into the clone, its word split by a `\`-continued line or a `${...}` at HEAD, or its `f` both assigned and a loop's variable), each a real write of the tree its stand-in gate runs in, and ux#1371, a false refusal: `for i in 1 2 3; do L7R_FEATURE_DIRECTORY=... L7R_PAGE_SESSION=... L7R_CONTINUE=... make rust-test ...; done`, whose `make` lies past the segment's 120-character cut, so gate-write reads no command - HEAD refuses the same line outside a loop (`/tmp/t79b/judge/pgw5-head.tsv`; below); through make-only 12 - tx#953, ux#1106, #1107, #1201, #1202, #1205, #1206, #1207, #2204, bx#34981, #35626 and #35638, a guard file's name (`Makefile`, `dev/work-budget.json`, a guard's source) written into a `$(mktemp -d)` place or a scratch copy from a loop's body, refused as HEAD refuses the same write to a literal scratch path (`/tmp/t79/probes-mk.jsonl`, `/tmp/t79b/judge/pmo-head.tsv`; T87's class); and through main-tree 3 - bx#54240, bx#58694 and ux#2209, a `python3 -c` program writing scratch through `sys.argv` in a loop's body, refused as HEAD refuses it outside a loop (the Python rule's, below).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the walk reads each word whole | n/a - no map | n/a | none | n/a |
| the one rule for an unresolved place | n/a - no map | n/a | none | n/a |

### T79 Approach (checklist part A)

1. **The goal, in the world.** No map changes. main-tree, make-only, gm-tree, readme and house-style see a command's writes where bash puts them: a `\`-continued line, a `${VAR}` and a `$(...)` inside a word read as one word, a brace expansion as one word, a `$(mktemp)` place as scratch, `$(pwd)` as the shell's place; and a place the walk still cannot resolve is judged one way whatever tool writes it - no scratch write refused because a variable stands in its name, and no write of the mirror let through because the walk lost track of where the shell stands.
2. **The constraints.** T79's line (the three word readings and the mktemp place; measured first on a corpus, red first; one rule for every tool); spec 204's D6 and FR-002 (a `cd` the walk cannot read leaves the shell treated as still in the mirror, "the conservative direction, so the fix cannot turn a refusal into a false allow"), kept for the shell's own place; T50's D-d and D-e, superseded by the rule; the brief's bounds (`tree.rs` under 1,000 lines - 975, `tree/bind.rs` 441 beside it, measured 2026-11-21 (`wc -l`); T78's `checks_hooks` and `planhold.rs` and T48's `rust/gate/crates/plan` untouched; the replay streamed, one driver).
3. **Where each comes from.** O: this task's corpora and replays of 2026-11-21 (the Approach); G: none - the brief is the caller's; the D6 direction is spec 204's.
4. **Do they describe the world here?** Yes: T50's four forms reproduce on HEAD (`/tmp/t79/probe2.txt`), the six tests of `words.rs` fail on HEAD's walk (`/tmp/t79/red3.log`), `binds.rs`'s first four fail on the first round's walk (`/tmp/t79b/red.log`) and each of its four third-round tests fails alone before its fix (`/tmp/t79b/red-{kw,pwd,self,loopset}.log`; the loop-and-assigned one with its old rule put back, 344 passed and 1 failed), the probes reproduce through the HEAD binary (`/tmp/t79b/p1.head.tsv`), and the HEAD binary refuses the 30 scratch writes the replay moves (`/tmp/t79/rp2/head.bx.nobody.main-tree-hooks.tsv`), measured 2026-11-21.
5. **The order.** The walk's readings first (each red first), then the rule on top of them, since a word read whole is what the rule's "start the walk knows" reads; T78's and T48's files untouched.
6. **The exits.** Green: both crates' tests, lint, format and cover clean, every replay move judged by what the command really wrote, and `make closing-checks` green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none - the one reader of where a command's writes land is `shared::tree`'s walk (`walk`, `writes_in`, `git_write`); `grep -rln "known_dir\|known_place\|settled(" rust/guard` (2026-11-21) names `tree.rs` and `tree/git.rs`, and one test whose name ends in `stays_settled(` (feature_approval's, unrelated); the bindings are `tree/bind.rs`'s alone, called from `walk_in`.
8. **The budget.** One landing.
9. **Done, measured.** 345 of 345 in `rust/guard/shared` and 424 of 424 in `rust/guard`, each crate's lint, format check and cover clean, measured 2026-11-21 (`scripts/gates/l7r-gate.sh rust test|lint|format --check|cover --crate`, in this clone, `/tmp/t79b/t17.*.log`, `lint6.*.log`, `fmt12.*.log`, `cover6.log`, `cover-guard.log`); `tests/hooks/test-main-tree-hooks.sh` 104 of 104 (`/tmp/t79b/mt3.log`); every replay move judged (the Approach); `make closing-checks` in this clone, started 2026-11-21 (`/tmp/t79b/closing.log`), its result in the handoff.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder's scratch write with a variable in its path, standing in the mirror, was refused (30 of bx's 59,116 commands, each a lost call); `cp /tmp/a ${D}/b` and a `\`-continued `cp` into the mirror passed from `/tmp`; `cd $(somewhere) && git commit` standing in the mirror passed; `cp /tmp/{a,b} /diagram/x` passed from `/tmp`; and `` `pwd`/f `` would have passed a write of the mirror under the rule without the `pwd` reading. The review's five probes (`echo x > $n.txt`, two loops over literal values, `F=$(ls | head -1)`, `R=$(git rev-parse ...)`), each a write of the mirror standing in it, passed under the first round's arm (`/tmp/t79b/p0.r.tsv`); a loop's or an `if`'s body was unseen at HEAD (`for f in a; do cp /tmp/a /diagram/x; done` passed from `/tmp`); and the second round's binding refused a builder's `S=$S/sub` scratch write and gate-write refused a `make` in a loop's body, measured 2026-11-21 (`/tmp/t79b/p1.{head,r2,r4}.tsv`, `/tmp/t79b/judge/pgw-*.tsv`).

**Found and left?**
- A name assigned twice in straight-line code is judged at each value, so `D=/diagram/x; D=/tmp/y; touch $D/f` standing in the mirror is refused though bash writes scratch, a scratch write HEAD allowed - refusing good work, observed 2026-11-21, method: the probe `/tmp/t79b/p1.jsonl` row 22 through `/tmp/t79/bin-r4` (T79's second plan review, `/tmp/sfr-t79/verdict-T79-r2.json`). Not fixed here: the straight-line reading wants the walk to tell a branch from a sequence, a reading of its own beside the bind rule. Filed as T91; lands before T22.
- The bind rule tries at most 64 sets of values (`tree/bind.rs`'s cap, a CONVENTION knob); past it a name falls back to D6, so standing in the mirror a loop over 65 or more literal scratch values is refused though HEAD allowed it (63 values pass), observed 2026-11-21, method: the plan review's probe `/tmp/sfr-t79b/cap.jsonl` through `/tmp/t79/bin-r4`; a mirror value at either end of such a loop is still refused. Not fixed here: judging past the cap value by value is the same reading T91 builds. Filed as T91; lands before T22.
- A `\`-continued line, a `${VAR}` and a `$(...)` inside a word split into commands of their own - fixed here, observed 2026-11-21, method: T50's four probes and the ux corpus (every transcript command holding a `\`-newline, a `${` or a `mktemp`) replayed through the guard; `segments` and `joined` are the walk's one split.
- A `$(...)` inside a word let spec 204's D6 case through - fixed here, observed 2026-11-21, method: the probe `cd $(somewhere) && git commit` standing in the mirror through HEAD's binary (`/tmp/t79/probe2.txt`).
- A place the walk cannot resolve settled two ways (a cp's by D6, a git form's not placed) - fixed here, observed 2026-11-21, method: `grep -rn` of every reader of an unresolved target in `tree.rs` and `tree/git.rs` (`settled` is now the one).
- A quoted word holding a space or a shell character is blanked, and a file tool's destination is then read from the word before it: through HEAD's main-tree, and this task's, `cp /tmp/a "/diagram/x y"`, `echo x > "/diagram/a b"` and `mv /tmp/a "/diagram/(x)"` pass while `cp /tmp/a /diagram/x` is refused; 233 of bx's commands end a cp, mv, tee or redirect on such a word, 11 naming `/diagram`, measured 2026-11-21 (`/tmp/t79/probes-q.jsonl` through `/tmp/t79/bin-head`; a pattern count over bx). Not fixed here: the blanking is what keeps a commit message, a sed script and a quoted program from being read as paths by every guard that reads the walk, so its fix wants its own corpus replay. Filed as T83; lands before T22.
- make-only's guard file list holds a file by its name in any tree, so a builder's scratch fixture writing a `Makefile` or a `dev/work-budget.json` is refused as a guard file written from the shell - at HEAD for a literal scratch path, and with this task's mktemp place for a `$(mktemp -d)` one too (tx#953, ux#2204, ux#1106, ux#1107, bx#34981), observed 2026-11-21 (the probe and the replay). Not fixed here: whether a copy outside the project's trees is held is the guard file list's rule, read by layer 3 and make-only alike, outside the walk. Filed as T87; lands before T22.
- `readme_hooks.rs` substitutes a `$(mktemp ...)` itself before it reads the walk, which the walk now does: no wrong outcome (the two agree), not a defect, not filed.
- A brace expansion split its word, as a brace group's braces do, so `cp /tmp/{a,b} /diagram/x` and `mv /tmp/x{1,2} /diagram/d/` from `/tmp` passed - fixed here, observed 2026-11-21, method: the probe through HEAD's binary and a count of bx's writes through a brace expansion (18 commands, 13 relative or naming `/diagram`); `segments` is the one split.
- A loop's, an `if`'s or a `while`'s body was read with its keyword as its command, so its writes were unseen (`for f in a; do cp /tmp/a /diagram/x; done` and `if true; then touch /diagram/y; fi` passed from `/tmp` at HEAD) - fixed here (`words()` reads past `bind::KEYWORDS`), observed 2026-11-21, method: the probes through the HEAD binary (`/tmp/t79b/p1.head.tsv`, rows 5-7).
- A target's segment kept that keyword at its head, so gate-write's `head_of` read `do` or `if` as the command and refused a `make` or a `touch` it leaves alone as a shell write of `.` - 38 of the ux replay's commands under a stand-in gate - fixed here (`bind::from_command`: a target's segment starts at its command, for every guard that reads its head), observed 2026-11-21, method: the r2 replay's gate-write reasons (`/tmp/t79b/judge/gw-r2.tsv`) and the probes `/tmp/t79b/judge/probe-gw.jsonl`.
- gate-write's `head_of` did not read past `timeout N`, so `timeout 60 make task-add` under a running gate was refused as a shell write of `.`, at HEAD too - fixed here, observed 2026-11-21, method: the same probes (`pgw-head.tsv` row 2).
- A name assigned from `$PWD` after a `cd` took the command's starting place (`cd <clone> && WT=$PWD; touch $WT/f` standing in the mirror was refused at HEAD) - fixed here (`bind::read_where_it_stands`), observed 2026-11-21, method: bx#51888 in the r2 replay and the probe (`/tmp/t79b/p1.head.tsv` row 16).
- A name reassigned twice took its last value for every use (`F=/diagram/a; echo x > $F; F=/tmp/b` passed at HEAD) - fixed here by the every-value binding, observed 2026-11-21, method: the probe (`/tmp/t79b/p0.head.tsv` row 8); and the binding then read a reassignment from the name's own value (`S=/tmp/q; S=$S/sub; touch $S/f`, refused by the second round's binary, window#302's `S=$S python3 $S/walk.py` corrected by house-style as the project's) - fixed here (`reads_itself`: such an assignment follows the one before), observed 2026-11-21, method: the probes (`/tmp/t79b/p1.r2.tsv` rows 11-15).
- A loop's variable also assigned was read as unknown, so ux#752's `f=research/...; sed -i ... $f` beside a `for f in ...` wrote a gated tree unseen - fixed here (its literal assigned values beside its loop's), observed 2026-11-21, method: the r replay against r2 (`/tmp/t79b/moves-r-r2.txt`).
- `cd ""` was read as a `cd` home; bash refuses a null directory and stays - fixed here (an empty quote stays a word, so D6), observed 2026-11-21, method: bash 5.3.9 on `cd ""` ("null directory", rc 1, the shell stays).
- A target's segment was shown as bound (`$f` replaced by a loop's value), which readme_hooks, finding the segment in the command, could not find - fixed here (`shown`: the segment as the command holds it), observed 2026-11-21, method: `readme_hooks`'s tests.
- A `python3 -c` program that writes a place it computes from `sys.argv` is judged where the shell stands (`cd <mirror>/research/questions; python3 -c "...open(sys.argv[2],'w')..." a /tmp/q/a.txt` is refused at HEAD and here), so the three corpus commands that run one in a loop's body, now seen, are refused (bx#54240, bx#58694, ux#2209, each writing scratch). Not fixed here: the program's place is the Python rule's (`py_c`), outside the walk, and its fix wants its own replay. Filed as T89; lands before T22.
- gate-write reads a target's command from its segment, which the walk cuts at 120 characters, so a `make` behind more than 120 characters of `VAR=value` prefixes is read as no command and refused as a shell write of `.` under a running gate (`L7R_FEATURE_DIRECTORY=... L7R_PAGE_SESSION=... L7R_CONTINUE=... make rust-test ...`, at HEAD and here; ux#1371, its loop's body now seen), observed 2026-11-21, method: the probe `/tmp/t79b/judge/probe-gw5.jsonl` through both binaries. Not fixed here: the cut is what readme_hooks's kept-segment rule reads, so the head wants its own field on the target rather than a longer cut. Filed as T90; lands before T22.
- house-style's `outside` is a `/tmp/` prefix, so in the replay world (a mirror under `/tmp/t79`) every resolved place is outside and its replay moves measure only resolved against unresolved: bx#4624, bx#4696 and window#241, rewritten at HEAD and passed by the replay, are rewritten by both binaries on their real paths (a direct run, 2026-11-21). Not a defect of the guard: a limit of the replay, named here so its moves are read as such.

**Performance work?** no.


### T80 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T80 Approach (checklist part A)

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


### T81 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T81 Approach (checklist part A)

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


### T82 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T82 Approach (checklist part A)

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


### T83 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T83 Approach (checklist part A)

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


### T84 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T84 Approach (checklist part A)

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


### T85 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T85 Approach (checklist part A)

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


### T86 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T86 Approach (checklist part A)

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


### T87 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T87 Approach (checklist part A)

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


### T88 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T88 Approach (checklist part A)

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


### T89 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T89 Approach (checklist part A)

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


### T90 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T90 Approach (checklist part A)

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


### T91 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T91 Approach (checklist part A)

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


### T92 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T92 Approach (checklist part A)

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

