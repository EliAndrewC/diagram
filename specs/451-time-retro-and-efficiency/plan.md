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
<!-- plan-archive: T54 to T54 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
### T60 (the context cap named a builder's handoff under its call's cwd: 2 handoffs, T10's `T10-aa6406892e465f0a5.md` and T55's `T55-abe836de838b025ad.md`, in the mirror's `/diagram/.git/l7r-handoffs/`, against 56 entries in the clone's (55 handoffs and the `T59-scripts` directory), measured 2026-11-21 (`ls` of both))

- **Approach**: `rust/guard/src/guards/context_cap_hooks.rs` reads a builder past the cap in the SESSION's clone, not the call's cwd:
  - `seat`: the session's clone (`shared::session`'s `clone_dir`, the resolve `clone_sync_hooks` routes an edit by - the claim map,
    else the session's name) where it is a work tree (a `.git` stands in it), else the tree the cwd stands in, today's answer. It is
    asked only past the cap or on a resume of a builder (`judge` takes it as a closure), so the main session's other calls and a
    defined agent still return before any read.
  - What it gives: the handoff directory (`<its git common dir>/l7r-handoffs`), the task the name carries (`filed_at` asked with the
    payload's `cwd` set to that tree, so the task's starts are the clone's), the `make context-ok` permit key (`<clone>/context-cap:<aid>`,
    which `make context-ok` grants from the clone's top level), and on a resume (D10) the handoff the refusal names and the probe its task
    is read by. The cwd still gates: a call from outside any tree passes, and the defined-agent stat reads the cwd's tree.
  - The live premise, measured 2026-11-21 (a Python count over the mirror's `.git/l7r-events/451-time-retro-and-efficiency.jsonl`, and
    `cat` of the claim map): its 364 lines are all session `c6fd72d1-ab6c-4736-b723-0697a1f5ca51`, whose claim map
    (`/diagram/.clones/.session-clones/c6fd72d1-...`) names `/diagram/.clones/diagram-backlog`, so the claim map resolves the
    builders whose shells were reset to the mirror to this clone.
  - The module doc's THE ONE EXIT paragraph and the `docs/guards.md` row say where the file is.
- **Red first** (`context_cap_hooks::tests::a_call_from_the_mirror_names_the_handoff_in_the_sessions_clone`: a mirror beside the clone,
  its claim map naming the clone for the pinned session, the call's cwd the mirror, a task T60 started in the clone; it asserts the
  refusal names the clone's `T60-<aid>.md`, a Write there passes, a Write to the mirror's path is refused, a resume sent from the mirror
  names the clone's file, a session resolving no clone or a directory that is no work tree keeps today's cwd tree, and the grant
  `make context-ok` keys by the clone lets the mirror's call through; the session built with `Session::with_env`, its seams the fixture's,
  no real `HOME` read):
  - before: 416 passed and the new case failed, the refusal naming `mirror/.git/l7r-handoffs/af3dc58915037d8d6.md` (the mirror's
    directory, no task) where the clone's `clone/.git/l7r-handoffs/T60-af3dc58915037d8d6.md` was asserted, measured 2026-11-21
    (`make rust-test CRATE=rust/guard`, `/tmp/t60/red.log`).
  - after: 417 passed, 0 failed, measured 2026-11-21 (the same command, `/tmp/t60/green.log`).
- **The move**: both mirror files were byte-identical to copies already in the clone's directory (`cmp`); moved with
  `MAIN_TREE_OK="451 T60 moves two misrouted builder handoffs out of the mirror's untracked .git, as its brief asks" mv -v -f` and the
  empty directory removed (`rmdir -v`): after, 0 handoffs in the mirror and 56 entries in the clone, measured 2026-11-21 (`ls`; the
  listing, the `cmp` verdicts and `mv`'s own lines in `/tmp/t60/mv.log`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the handoff's directory, task and permit read in the session's clone | n/a - no map | n/a | none | n/a |

### T60 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A builder past the cap is named, and allowed to write, its handoff in the clone the
   session works in, whatever directory its shell stands in, so the main session finds every handoff in one place and nothing a
   session writes lands in the mirror's `.git`.
2. **The constraints.** T60's line: the handoff directory resolved from the session's clone as `clone_sync_hooks` routes an edit
   (`shared::session`'s resolve), red first on a call from /diagram, the handoff-write permit accepting that path; then the mirror's
   handoffs moved with a recorded `mv`. The launcher's file list: `context_cap_hooks.rs` and its tests, the `docs/guards.md` row, this
   section; T72's `closing-checks.sh` and T67's `readme_hooks` untouched; nothing committed. D8 and D9 hold: the main session and a
   defined agent are not read.
3. **Where each comes from.** O: the two listings and the `cmp` (the heading, The move); O: the mirror's event log and the claim map
   (the live premise); O: the red and green runs (Red first); the task as filed (T60's line).
4. **Do they describe the world here?** Every figure is from this clone, the mirror's `.git` and the session's claim map, measured
   2026-11-21 (the Approach); the red case reproduces the live shape - a builder's call from the mirror - in a scratch world.
5. **The order.** After T12 (the cap), T13 (the resume and the permit) and T68 (its context read); independent of T67 and T72.
6. **The exits.** Green: the red case green with every earlier case of the module unedited but for the new closure argument,
   `make rust-test CRATE=rust/guard`, lint, format and cover on `rust/guard`, `make closing-checks`. Red: what failed recorded and the task
   set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One: the cwd fed more than the directory - `filed_at`'s root (the task in the name), the permit key and the
   resume's `tree_of` - so all four read the one tree `seat` gives.
8. **The budget.** One landing. The added work, past the cap or on a resume of a builder only: one claim-map read (the session's `OnceCell`, shared with the other
   guards that resolve it), one `.git` stat and one copy of the payload, measured 2026-11-21 (the code read).
9. **Done, measured.**
   - the red case green, 417 passed, measured 2026-11-21 (`make rust-test CRATE=rust/guard`).
   - the mirror's `.git/l7r-handoffs/` gone and the clone's directory holding T10's and T55's, measured 2026-11-21 (`ls`, The move).
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of a builder's refusal sees the clone's path, and the main session's dispatch of a fresh builder
    finds its handoff in the clone's `.git/l7r-handoffs/`; before, T10's and T55's sat in the mirror's. Nothing on a map.

**Found and left?**
- The event log files a call's line by its cwd too (`event_log_hooks::append` and `filed_at`, `clone_root(cwd_of(...))`): the mirror's
  `.git/l7r-events/` holds a `451-time-retro-and-efficiency.jsonl` of 364 lines, all this session's (361 a builder's, carrying `aid` or
  `by`, and 3 the main session's), and an `_unassigned.jsonl` of 962,893 bytes, measured 2026-11-21 (`wc -l`, `ls -la`, a Python
  count of the lines by their keys). Visible effect: `make where-time F=451` run in the
  clone books none of those 364 lines, since 0 of them are in the clone's 451 log, measured 2026-11-21 (a Python match of the
  two logs' lines by `t`, `ev`, agent and tool). Not fixed here: `event_log_hooks` is outside T60's files, a shared module the gate's crates call.
  Filed as T74; lands before T22.

**Performance work?** no.


<!-- plan-archive: T61 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T61 to T61 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T58 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T63 to T63 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T67 (T58's builder's `cd /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep && ...` refused as a README write, 2026-11-21T06:30Z; replayed verbatim through the guard, what matched was the DESTINATION, `/tmp/t58/readme.keep` - a README by the guard's name rule, `README` with any extension - outside the tree, not the source's name, measured 2026-11-21, method: the guard log's entry, the command recovered from the builder's transcript and replayed through `tests/hooks/readme-hooks.sh`)

- **Approach**: the guard judged a regex over the whole command text - `>`, `sed -i`, `tee`, `cp X`, `mv X` before a README-named word,
  and `README...").write_text` - so it read heredoc bodies, sed scripts and a copy's flag-shifted source as destinations. It now judges
  the destination (`rust/guard/src/guards/readme_hooks.rs`, `hit`): a Bash command's write targets as `shared::tree::walk_judged` finds
  them, standing in the event's `cwd` (an event with none stands in the tree), each refused when its path is a README by name and in
  the tree (`in_tree`, the next bullet); a program the walk marks a read skipped; git's own targets are
  the directory it runs in, so `git add README.md` passes and `git show HEAD:a.md > docs/README.md` is refused by its redirect; a
  `$(mktemp ...)` named `<its -p directory, else /tmp>/mktemp.scratch` before the walk, so a scratch `cd $d` resolves outside the tree;
  a shell's `-c` program, one blanked word to the walk, walked where the shell stands. A Python program: its triple-quoted text
  blanked, only its lines with a write verb kept (`PY_WRITES`: a write, an open, a move, a removal), their literals read by make-only's
  `interp::program_names` as gate-write reads them (451 T33: a literal that is a path where the program stands, read-only opens
  exempt) - a README there in the tree refused, one resolved outside it passing, and else the old `README...').write_text` rule on
  those lines, failing closed on a README joined onto a base the program computes (`Path(sys.argv[1]) / 'README.md'`). A target the
  walk cannot resolve (`> $UNSET/README.md`, a `cd` to an unknown directory) is judged by the old guard's destination-position rule
  (`UNRESOLVED`) on its segment, which the walk has blanked of quoted text and heredoc bodies - failing closed, while a README such a
  copy only reads (`cp docs/README.md $UNSET/x.md`) passes. A file tool's path takes the same tree rule (a relative path, which no file
  tool sends, counts as the tree's).
  - **The tree** (`in_tree`; the plan review's (b)3, 2026-11-21): the mirror, a clone (`classify`'s path rule), or a COPY of this
    project anywhere else (`copy`), known by what the directory is, never by its path. The repository nearest above the path - its
    `.git` directory, or the git dir a `.git` file names, through that git dir's `commondir` - is a copy when its common git dir is the
    mirror's or a clone's (a builder's `git worktree add /tmp/t58/wt` of the clone, which T58's and T11's builders wrote in), or its
    `origin` is this repository: the mirror or a clone by path (`file://` too), the mirror's own origin read from `<mirror>/.git/config`
    by any scheme (`git@host:o/r.git` and `https://host/o/r` are one, compared whole, so `.../diagram-research` is another), or a local
    repository that is itself a copy, followed three hops. Not the tree: a scratch repository of its own (a `git init`), a clone of
    another repository and a directory in no repository - the narrowing the review ruled LEGITIMATE ((b)1), kept. Read from the disk
    with no process started, and only for a README-named target `classify` puts outside the mirror. A work tree the same command makes
    is not on disk when the guard reads, so it is judged by what it is a work tree of (`made_trees`): a `git worktree add` whose
    repository (its `-C`, else where git runs) is the tree, or a `git clone` of this repository (a URL by the mirror's origin, a path in
    the tree, a copy or a work tree an earlier call of the same command makes, `file://` and past a valued option). A README under the
    new work tree's place then counts as the tree's and one outside it does not - the plan review's (b)3c, round 2, ruled NOT
    LEGITIMATE the first form, in which every README such a command wrote counted, refusing T67's own cp beside a `git worktree add`.
    The place is `worktree add`'s path past its valued options (`-b`, `-B`, `--reason`, by `git worktree add -h`, git 2.53) or the
    clone's directory, else the one git names from its source (`/repo/.clones/c/` is `c`, `git@host:o/project.git` is `project`; a
    source by a variable, `git clone $S`, names one only once the shell expands it, so its place fails closed),
    relative to the `-C` (a variable's or home's word, `$d/wt` or `~/wt`, as the walk expands it where the command stands, never put
    under `.`), a redirect naming none; each source and place resolved by the walk itself where the command stands when it
    runs (the call written as two numbered `touch`es there), and a path compared to it component by component (`/tmp/t58/wt-notes` is
    not under `/tmp/t58/wt`). So `git worktree add /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep`
    passes, while a README written in `/tmp/t58/wt` by its path or after a `cd` into it is refused, and so for a clone and for a work
    tree a shell's `-c` program makes, whichever side of the program the README is written on. A source the walk cannot resolve (`git clone $UNSET y`) counts as this project's; a place it
    cannot resolve (`git worktree add $UNSET/wt`, a `worktree add` naming none, a clone of `$S` naming no directory, a probe past the
    120 characters the walk keeps of a segment) fails closed, every README the command writes refused as before. The call is git's own subcommand - only
    git's global options (its valued ones with their values) between `git` and `clone` or `worktree add` - so a commit message or a
    `git grep` naming either is no such call (the loose form, any words between, refused T67's own cp after `git commit -qm "the clone
    step"`, red in the crate and the suite before this form; over every transcript's Bash commands it matched 519 times, this form
    374, the difference each a mention, `/tmp/t67/makes2.py`), and a match inside quoted text writes its probe there, where the walk
    finds no write. Measured 2026-11-21 (`/tmp/t67/makes.py`, every Bash command in the surviving transcripts, `/tmp/t67/makes4.txt`):
    368 calls make a work tree by this form (129 `worktree add`, 239 `clone`), 13 of them in a command naming a README - each a
    mention or a scratch clone of another repository (`/gm-assistant`, a fresh bare `remote.git`), none a README written into a copy
    it makes. Refusing every README such a command writes, this rule's first draft, refused 2 of the corpus's commands (those
    `remote.git` scratch clones in a `mktemp` directory, `/tmp/t67/corpus3.txt`), so it judges what is copied instead.
    `classify` itself is unchanged, a departure from the brief's "fix `classify`": it is
    every walk's `Target.class`, by which `main_tree_hooks` moves a write it calls the mirror's, so a `/tmp` copy read as the tree there
    would be moved for nothing; the README guard asks the wider question in its own `in_tree`. Measured 2026-11-21
    (`/tmp/t67/copies-guard.sh`: every git work tree under `/tmp` to depth 4 asked of the built guard, `echo x > <dir>/README.md` from
    `/tmp`, `CLONE_MAIN=/diagram`, beside git's own common git dir and origin, `/tmp/t67/copies-guard.txt`): of 1,289 git work trees,
    17 are the tree - 2 worktrees of this clone (`/tmp/t33/wt`, `/tmp/probe-s`: common git dir the clone's), 13 clones of the clone by
    its path (`/tmp/t40/*`, `/tmp/t43/w`, `/tmp/t233/real`, `/tmp/t238-scratch/*`, two under a `mktemp` root), a `file://` clone of
    it (`/tmp/t40/sh1`) and a clone of that (`/tmp/t40/sh2`, one hop) - and the other 1,272 are not: 1,134 repositories git reads,
    none of them this project's by git's own common git dir or origin (scratch `git init`s and test fixtures with an origin of their
    own), and 138 test-fixture stubs whose `.git` git cannot read.
    Pinned by the suite's section 6 on git's own repositories (a worktree of a clone after a `cd`, by its path, standing in it, by a
    file tool and by a Python program; a clone of a clone, a clone of that, an origin by another scheme, a `file://` clone, a
    worktree the command adds and a clone of a clone it makes, refused; an origin sharing a prefix, a scratch repository, a plain
    directory, a scratch clone the command makes of a bare repository of its own and 2026-10-10's whole command, passing; and (b)3c's
    pins: the logged cp beside a `git worktree add /tmp/t58/wt` passing, a README in that worktree by its path, after a `cd` into it
    and from a shell's `-c` program or after it refused, one in a worktree whose place is a variable refused and the logged cp beside
    it passing, a clone of this repository with a README in it refused and one elsewhere outside it passing, a clone of a
    variable's source naming no directory and an unresolvable place failing closed) and by the crate's `a_copy_of_the_project_anywhere_is_the_tree_known_by_what_it_is`
    and `a_work_tree_the_command_makes_is_judged_by_what_it_copies` on hand-written `.git` files, and
    `a_work_tree_the_command_makes_holds_the_readmes_under_its_place` (27 cases and the URL clone's named directory, measured
    2026-11-21 (`make rust-test CRATE=rust/guard`, `/tmp/t67/crate-green-r10.log`): a place or source by a variable or home, valued options,
    a relative place under `-C`, a sibling sharing the place's prefix, a clone's directory named from its source, a redirect, a
    worktree of a clone the command made before it, the scratch clone beside a worktree of the tree, three fail-closed places, a
    `-c` program).
  - **The corpus** (every Bash command naming a README in the surviving transcripts under `~/.claude/projects`, 389 distinct, through
    the mirror's guard and the clone's, measured 2026-11-21, `/tmp/t67/corpus.py`): the first fix disagreed on 21 - 17 the old refused
    (mentions: heredoc and sed text, a copy to `/tmp`, this builder's own probes; and READMEs outside the tree, in `~/this-laptop` and
    `/julie-medical`, which the diagram's guard no longer holds) and 4 only the new refused (a Python fixture's helper literal
    `put(d, "questions/README.txt")`, and a `cd $d` into a `mktemp` scratch directory, failing closed) - those 4 fixed by the
    write-verb lines and the `mktemp` naming. A README's write held as a one-line string's text
    (`write_text('(tmp / "README.md").write_text(1)')`), which the first fix still refused, now passes - the plan review's L1, fixed
    here in the same Python reading (`without_held`): a one-line string that holds a quoted string of its own is the program's text and
    is blanked to `""`, as its triple-quoted text is, the line lexed as Python lexes it (a `#` outside a string ends the code, kept as
    it is; a backslash escapes; a string left open at its line's end kept), while a string holding none is still read - an f-string's
    `f"{d}/README.md"` and `"it's/README.md"` still refused, pinned. T75, filed for it, is moot. The round-2 corpus (486 distinct commands, the transcripts having grown, through the mirror's
    guard and the clone's, measured 2026-11-21, `/tmp/t67/corpus6.txt`): 0 refused by the new guard alone, 21 by the old alone (14
    mentions, 7 READMEs in other repositories), 2 by both, 463 by neither - where the draft that refused every README a work-tree-making
    command writes had 2 refused by the new alone (`/tmp/t67/corpus3.txt`).
    The refusal's text, the escape and the log are unchanged; the refusal now names the resolved path.
  - **The log** (the raw entries under `~/.claude/guard-log/`, measured 2026-11-21, `/tmp/t67/replay-log.py`,
    `/tmp/t67/replay-log3.txt`): 21 readme firings, 2026-08-31 to 2026-11-21, all `blocked/readme-is-the-gm-s`, 0 escaped - 16 when this
    section was first written, 5 since from this task's own builders. 16 carry the whole command in their `command` field (from
    2026-09-07 on) and were replayed whole, with their `cwd`, through the mirror's guard and the clone's; 5 hold only the 200-character
    `detail` (the first round read 12 by their detail and missed the `command` field; corrected here):
    - a README written in the tree, 6, all still refused: 2026-09-05 (a file tool, `diagram-html`'s `research/README.md`, by its
      detail's clone path), 2026-09-07 twice (Edit, `diagram-research`'s `research/README.md`), 2026-09-28 (`cat > README.md <<'EOF'`
      in a clone's `specs/269-research-backfill/briefs/engine/`), 2026-10-01 (`cat > record/README.md <<'EOF'`, a test fixture's
      record in a clone's `tests/tooling/fixtures/brief_load`), 2026-11-07 (`cat > ../parked/README.md <<'EOF'` from `rust/phases`,
      refused naming `/diagram/.clones/diagram-backlog/rust/parked/README.md`).
    - a name the command held, replayed whole, 10, all now passing: 2026-10-18 (a Python program writing a test whose triple-quoted
      text writes `(root / "README")`), 2026-10-19 (`cat >>` a heredoc of test text onto `test_apply_edits.py`), 2026-10-30 (a Python
      program writing a test whose triple-quoted text writes a fixture README), 2026-11-17 (a `sed -i` script naming "README 1"),
      2026-11-21 06:30 (T67's cp), and this task's builders' own edits and probes, 10:19, 10:29, 10:31, 10:50 and 10:57
      (programs and heredocs whose text names a README).
    - a README outside the tree, 1: 2026-10-10, replayed whole - `d=/tmp/claude-1000/-diagram/<session>/scratchpad/livetest && rm -rf
      $d && mkdir -p $d/specs/399-live-test && cd $d && git init -q && printf 'x\n' > README && git add README && git ... commit -qm
      base && ...`. Classified against the tree rule: NOT a copy of this project. The directory is removed and made afresh, `git init`
      gives it a git dir of its own, and the command adds no remote, so its common git dir is neither the mirror's nor a clone's and it
      has no origin; the `specs/399-live-test` it builds is a fixture's shape, not a checkout. It passes by the narrowing ruled
      LEGITIMATE ((b)1), its whole command pinned in the suite's section 6.
    - by their detail only (no `command` field; their transcripts gone, a `grep -rlF` of each detail over every `~/.claude/projects`
      transcript finding only a later session's copy of the same truncated detail), 4 beside 09-05: 2026-09-06 three times (Python heredocs editing the README guard's own suite,
      `scripts/test-readme-hooks.sh`: mentions), and 2026-08-31 (a build in a `/tmp` scratchpad's fresh `simtest` directory, cut
      before any write: unclassifiable, said so).
  - **Red first** (`tests/hooks/test-readme-hooks.sh`, its new section 5, through the built guard): before the fix, 34 passed and 8
    failed - the 6 expected passes refused (the logged cp, `cp -p docs/README.md /tmp/x.md`, the sed script, the `/tmp` scratch README,
    a heredoc's text, the triple-quoted program) and the 2 expected refusals passed (`> $NEVER_SET_T67/README.md`, `rm docs/README.md`);
    after, 42 passed, 0 failed, then 44 with the file tool's two tree cases, measured 2026-11-21 (`/tmp/t67/suite-red.txt`,
    `/tmp/t67/suite-green2.txt`). The crate: 418 passed, 0 failed; lint, format and cover clean, measured 2026-11-21
    (`make rust-test CRATE=rust/guard`, `l7r-gate.sh rust lint|format --check|cover --crate rust/guard`).
    **Round 2** (the review's (b)3 and L1), red first again: the suite's new cases (section 6, the copies; section 5's one-line string)
    before the fix 61 passed and 11 failed - the 10 refusals in a copy outside the tree passed (a worktree of the clone five ways, a
    clone of a clone, a clone of that, an origin by another scheme, a `file://` clone, a worktree the command adds) and the one-line
    string was refused; after, 72 passed, 0 failed, the fixture's 8 repositories asserted to exist (`/tmp/t67/suite-red-r2.txt`,
    `/tmp/t67/suite-green-r3.txt`). The crate before the fix 418 passed, 2 failed (the copy test and the string assertion), after 420
    passed, 0 failed (`/tmp/t67/crate-red-r2.log`, `/tmp/t67/crate-green-r3.log`). That fix's work-tree rule refused every README a
    `git clone` or `git worktree add` command writes; its red was the corpus (2 good commands refused by the new guard alone,
    `/tmp/t67/corpus3.txt`), turned by judging what the call copies: the suite 74 passed, 0 failed with the scratch clone's case and a
    clone of a clone's beside it, the crate 421 passed, 0 failed with `a_work_tree_the_command_makes_is_judged_by_what_it_copies`,
    the corpus 0 by the new alone (`/tmp/t67/suite-green-r4.txt`, `/tmp/t67/crate-green-r4.log`, `/tmp/t67/corpus4.txt`). Its call
    form, red next: the loose form (any words between `git` and `clone`) refused T67's own cp after a commit message naming the clone
    step - the crate 420 passed, 1 failed (3 of 4 mentions refused), the suite 74 passed, 1 failed (`/tmp/t67/crate-red-r5.log`,
    `/tmp/t67/suite-red-r5.txt`); git's options only turned 2 of the 3 (`/tmp/t67/crate-green-r5.log`), and words taking a quote only
    whole the third, a message's closing quote: the crate 421 passed, 0 failed, the suite 75 passed, 0 failed, lint, format and
    cover clean, the corpus 0 by the new alone (`/tmp/t67/crate-green-r6.log`, `/tmp/t67/suite-green-r6.txt`, `/tmp/t67/lint-r6.log`,
    `/tmp/t67/fmtc-r6.log`, `/tmp/t67/cover-r6.log`, `/tmp/t67/corpus6.txt`), measured 2026-11-21.
    **Round 3** (the review's (b)3c), red first: the work tree's place pinned, the suite 79 passed, 2 failed (the two expected passes
    refused: the logged cp beside a `git worktree add`, a clone's README elsewhere), the crate 421 passed, 1 failed (6 of the new
    test's 17 cases); then the `-c` program's made trees, the suite 81 passed, 1 failed, the crate 421 passed, 1 failed; then a
    variable's or home's place and the write after a program, the suite 83 passed, 2 failed, the crate 421 passed, 1 failed (5 of
    25 cases); then a clone of `$S` naming no directory, the suite 85 passed, 1 failed, the crate 421 passed, 1 failed (2 of 27);
    after, the suite 86 passed, 0 failed, the crate 422 passed, 0 failed, lint, format and cover clean, the corpus 0 by the new
    alone (`/tmp/t67/suite-red-r7.txt`, `/tmp/t67/crate-red-r7.log`, `/tmp/t67/suite-red-r8.txt`, `/tmp/t67/crate-red-r8.log`,
    `/tmp/t67/suite-red-r9.txt`, `/tmp/t67/crate-red-r9.log`, `/tmp/t67/suite-red-r10.txt`, `/tmp/t67/crate-red-r10.log`,
    `/tmp/t67/suite-green-r10.txt`, `/tmp/t67/crate-green-r10.log`, `/tmp/t67/corpus9.txt`), measured 2026-11-21.
  - **Refused now that was not**: a README in the tree removed, moved away, touched or `chmod`ed (the walk's file tools write every
    argument), and one past a variable the walk cannot expand. Deliberate: a README is the GM's to write (constitution XVII, GM
    2026-08-24, as the refusal's own text states it), and a guard fails closed on what it cannot resolve; `README_OK` with a
    reason escapes both. A README in a copy outside the mirror, or under a work tree the command makes (or anywhere, where that tree's
    place cannot be resolved), was refused by the old guard too (it refused every README name), so neither is new.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the README guard judges the destination a call writes, in the tree | n/a - no map | n/a | none | n/a |

### T67 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A session is refused a README only where one would land in the tree - the mirror, a
   clone, or a copy of this project anywhere (a builder's `/tmp` worktree, a `/tmp` clone), known by what the directory is - whatever
   route writes it (a redirect, `cp`, `tee`, `sed -i`, a Python program, a file tool), and never for a name its command merely holds:
   a copy's source, a sed script, a heredoc's text, a Python string's text, a `/tmp` scratch file or scratch repository of its own.
2. **The constraints.** T67's line: the guard reads the destination, red first on that cp. The brief's: judge the destination a command
   writes (`shared::tree`'s write targets), a README written anywhere in the tree still refused, a copy whose source is named
   `readme_hooks.rs` or a path outside the tree passing, every real refusal the log shows kept. The plan review's verdict
   (2026-11-21, `/tmp/t67-fidelity-verdict.json`): a copy of this project anywhere is the tree, detected by what the directory is,
   stated with a measurement and pinned by a suite case ((b)3, NOT LEGITIMATE as first written); the one-line string's text fixed
   here or recorded under Found and left in T17's form (L1); a README in a non-project `/tmp` file or scratch repository passing
   ((b)1) and in other repositories ((b)2), both LEGITIMATE. Round 2's (`/tmp/t67-fidelity-verdict-r2.json`): (b)3c NOT LEGITIMATE,
   taken by its option (a) - a README refused only under the resolved place of a work tree the command makes, failing closed where
   that place is unresolved, pinned red first. Its files: `readme_hooks.rs` and its tests,
   `tests/hooks/test-readme-hooks.sh`, the `docs/guards.md` row, this section; `shared::tree` (its `classify`), T72's
   `closing-checks.sh` and T60's `context_cap_hooks` untouched; nothing committed. Constitution XVII (a README is the GM's to write),
   and the root CLAUDE.md's rule for a guard: match invocations, not mentions (What is enforced).
3. **Where each comes from.** O: the guard log's 21 entries, the 16 whole commands replayed, measured 2026-11-21
   (`/tmp/t67/replay-log.py`; the Approach); O: the census of `/tmp`'s git work trees through the built guard and the transcripts'
   work-tree-making calls (`/tmp/t67/copies-guard.sh`, `/tmp/t67/makes.py`); O: the suite's and the crate's red and green runs; R:
   the plan review's verdict; G: constitution XVII, the GM 2026-08-24 (the refusal's own text); the task as filed (T67's line).
4. **Do they describe the world here?** Every refusal the log holds was read, measured 2026-11-21 (the raw entries under
   `~/.claude/guard-log/`): the 16 carrying a `command` field replayed whole with their `cwd`, the 5 holding only a 200-character
   detail classified by it (1 left unclassifiable, said so); the tree rule asked of the real `/tmp`, where this project's worktrees
   and clones are (17 of its 1,289 git work trees); the red cases reproduce the logged shapes in the suite's pinned tree
   (`CLONE_MAIN=/repo`) and, for the copies, in git's own repositories under a `mktemp` root.
5. **The order.** Independent of T60 and T72 (their files untouched); after T33 (make-only's literal reader, reused) and T42 (the
   judged walk's stdin programs). T75, filed for L1, is moot: L1 is fixed here.
6. **The exits.** Green: the suite's sections 5 and 6 green with their red cases turned, `make rust-test CRATE=rust/guard`, lint,
   format and cover on `rust/guard`, `make quick`; the closing checks by the landing's `make done` (a third `make static` since the
   last landing is the static-runs guard's to refuse). Red: what failed recorded and the task set down, a claim that it cannot be done
   ruled through `make arbiter-ask`.
7. **The search smell.** Two. The logged cp's match was the destination's name (`readme.keep`), not the source's as the task line
   read it, so the turning rule is the tree, and the source case (`cp -p docs/README.md /tmp/x.md`, a flag shifting the source into
   the old regex's destination slot) is pinned beside it. And the first census of `/tmp`'s copies, by shell (`git -C "$common"
   config` on a `.git` git could not read), counted 153 copies: an empty common dir made `git -C ""` read the clone's own config, so
   138 fixture stubs whose `.git` git cannot read took its origin, and it missed 2 the guard finds (a `file://` clone of the clone and
   a clone of that); the guard's own census, 17, is the measurement.
8. **The budget.** One landing. The added work, on a Bash call whose input names a README only (the prefilter unchanged): one walk of
   the command, as the tree guards already run, and a literal scan of a Python program's body; for each README-named target
   `classify` puts outside the mirror, a walk up its ancestors reading at most one `.git`, a `commondir` and two `config` files a hop
   (three hops at most, no process), a file tool's path read from the disk only once it is a README by name; and, only where the
   command holds git's own `clone` or `worktree add` call, a read of the mirror's `config` and one more walk of the command, and of
   each shell's `-c` program it runs, with those calls written as `touch`es - measured 2026-11-21 (the code read).
9. **Done, measured.**
   - the suite 86 passed, 0 failed (round 1: 34 passed, 8 failed before the fix; round 2: 61 passed, 11 failed before, then 74
     passed, 1 failed before the call form; round 3, (b)3c: 79 passed, 2 failed before - the logged cp beside a `git worktree add`
     and a clone's README elsewhere, the two expected passes, refused - then 81 passed, 1 failed before the `-c` program's made
     trees, then 83 passed, 2 failed before a variable's place and the write after a program, then 85 passed, 1 failed before a
     clone of a variable's source naming no directory), measured 2026-11-21 (`tests/hooks/test-readme-hooks.sh`,
     `/tmp/t67/suite-red-r2.txt`, `/tmp/t67/suite-red-r5.txt`, `/tmp/t67/suite-red-r7.txt`, `/tmp/t67/suite-red-r8.txt`,
     `/tmp/t67/suite-red-r9.txt`, `/tmp/t67/suite-red-r10.txt`, `/tmp/t67/suite-green-r10.txt`).
   - the crate 422 passed, 0 failed (418 passed, 2 failed before round 2's fix; 420 passed, 1 failed before the call form; round 3:
     421 passed, 1 failed before, `a_work_tree_the_command_makes_holds_the_readmes_under_its_place` with 6 of its 17 cases wrong -
     the cp, the sibling prefix, a clone's README elsewhere and with no directory, the scratch clone beside a worktree, a clone of
     another repository beside one of this - then 421 passed, 1 failed before the `-c` program's, then 421 passed, 1 failed with 5
     of its 25 cases wrong before a variable's or home's place and source and the write after a program, then 421 passed, 1 failed
     with 2 of 27 wrong before a clone of `$S` naming no directory); lint, format and cover clean on `rust/guard`, measured
     2026-11-21 (`make rust-test CRATE=rust/guard`, `l7r-gate.sh rust lint|format --check|cover --crate rust/guard`,
     `/tmp/t67/crate-red-r7.log`, `/tmp/t67/crate-red-r8.log`, `/tmp/t67/crate-red-r9.log`, `/tmp/t67/crate-red-r10.log`,
     `/tmp/t67/crate-green-r10.log`, `/tmp/t67/lint-r10.log`, `/tmp/t67/fmtc-r10.log`, `/tmp/t67/cover-r10.log`).
   - the corpus after round 2: 486 distinct commands, 0 refused by the new guard alone, 21 by the old alone (14 mentions, 7 READMEs
     in other repositories), 2 by both, 463 by neither, measured 2026-11-21 (`/tmp/t67/corpus.py`, `/tmp/t67/corpus6.txt`); after
     round 3, (b)3c, the transcripts grown to 553: 0 by the new alone, 23 by the old alone (16 mentions, the 2 new ones Python
     heredocs editing this plan; 7 READMEs in other repositories), 2 by both, 528 by neither, measured 2026-11-21
     (`/tmp/t67/corpus9.txt`), the clone's shim asked first that it ran the fixed build (the logged cp beside a `git worktree add`
     passing, a README in that worktree refused, `/tmp/t67/ev-r10.txt`, and the 8 probes of a variable's place, a `-c` program
     and a variable's clone each as wanted, `/tmp/t67/probes-r10-after.txt`).
   - the log's 16 whole commands replayed after: the 5 README writes in the tree refused, the other 11 passing, measured 2026-11-21
     (`/tmp/t67/replay-log3.txt`).
   - the `/tmp` census through the built guard: 17 of 1,289 git work trees the tree, each one git itself names a worktree or clone
     of this project, and no repository git reads as this project's passing, measured 2026-11-21 (`/tmp/t67/copies-guard2.txt`).
10. **Before moving a constant.** No constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session copying a guard's source to `/tmp` - in a command that also adds a worktree or clones this project
    too - editing a test whose text names a README, or building a `/tmp` scratch repository of its own is no longer refused; a README
    written in the tree - the mirror, a clone, a copy of this project anywhere, or under a work tree of it the same command makes -
    still is, now named by its resolved path, and a command making a work tree of this project whose place the walk cannot resolve
    still has every README it writes refused. Nothing on a map.

**Found and left?** none. L1, the one-line string's text the first round left refused, is fixed here (the corpus bullet); T75, filed
for it, is moot. The plan review's round-2 (b)3c, every README a work-tree-making command writes refused wherever it lands, is fixed
here too: only a README under the new tree's resolved place is refused, failing closed where the place is unresolved (the tree
bullet). Found while fixing it and fixed here, each red first: a work tree a shell's `-c` program makes was invisible to the rule, its
call quoted text to the outer walk, so `bash -c "git worktree add /tmp/w && echo x > /tmp/w/README.md"` passed, and so did a README
written after the program; the made trees are now read in the command and in every program it runs, and judge every write of it
(the crate 421 passed, 1 failed, the suite 81 passed, 1 failed, then 83 passed, 2 failed for the write after it,
`/tmp/t67/crate-red-r8.log`, `/tmp/t67/suite-red-r8.txt`, `/tmp/t67/crate-red-r9.log`, `/tmp/t67/suite-red-r9.txt`). And a place or
a clone's source by a variable or home was put under `.` - `./$d/wt`, which the walk resolved under the command's own directory - so
`d=/tmp/t58 && git worktree add $d/wt && echo x > $d/wt/README.md` passed (and, from round 2, a clone of `$S`); the word is now the
walk's to expand, under the `-C` only when relative there (the clone's shim, measured 2026-11-21: 5 of 5 such refusals passing
before, 5 of 5 refused after and the cp beside one passing, `/tmp/t67/probes-r9-before.txt`, `/tmp/t67/probes-r9-after.txt`). And a
clone of `$S` naming no directory took `$S` itself, the source, for the place git names, so a README in the clone it makes passed; a
name holding a variable now fails closed (the shim 2 of 2 passing before, `/tmp/t67/probes-r10-before.txt`; the suite 85 passed, 1
failed, the crate 421 passed, 1 failed, `/tmp/t67/suite-red-r10.txt`, `/tmp/t67/crate-red-r10.log`).

**Performance work?** no.


<!-- plan-archive: T68 to T12 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T68 to T68 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T69 to T10 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T69 to T69 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T70 to T70 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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


### T72 (two `make closing-checks` runs in one clone shared `.git/closing-checks/` and read each other's verdicts: T69's builder's run of 09:38:33Z beside another's of 09:38:06Z, the first reading the second's `quick` verdict and its `static.log` holding both runs' lines, observed 2026-11-21 (T69's section in plan-done.md, Found and left); reproduced against the unfixed script, run A's red `quick` read GREEN and run B's green `hooks-test` read RED, measured 2026-11-21 (`tests/hooks/test-closing-checks.sh`, `/tmp/t72/red.log`))

- **Approach**: `scripts/gates/closing-checks.sh` gives each run a directory of its own:
  - ONE DIRECTORY A RUN: `<git dir>/closing-checks/<run id>/`, the run id the start's UTC time and the script's pid
    (`20261121T101614Z-746097`, this task's own run), made with a plain `mkdir`, so an id taken twice fails rather than shares. The
    three logs and `.exit` files go there; the table, the red tails and the stop line read and print that directory alone. The start's
    `rm -f` of the exit files is gone: a new directory has none.
  - THE POINTER: `<git dir>/closing-checks/latest`, a relative symlink to the run started last, swapped in by one rename (`ln -sfn` to
    `.latest.<pid>`, then `mv -T`), so a reader never finds it missing. Beside a parallel builder it may name the other's run, so the
    script's header says to cite the path the table prints.
  - THE PRUNE: at a run's start, every other run's directory, and the old layout's `<check>.log` and `.exit` files at the top level,
    not changed for `CLOSING_CHECKS_KEEP_MIN` minutes (360, a GUESS knob, item 10) is removed; the run's own directory and the one
    `latest` names are never removed, and a file of any other name is left.
  - READERS OF THE OLD PATHS: none in code. The guards name `closing-checks` as a make target only (`static_runs_hooks.rs`,
    `static_runs_hooks/order.rs`, the category table of `event_log_hooks.rs`), `rust/browser`'s `lit.rs` names it in a comment, and
    no file of the measure crate, `docs/`, `.claude/`, the Makefile's `##` line or a `CLAUDE.md` names the path, measured 2026-11-21
    (`grep -rn "closing-checks"` and `grep -rn "closing-checks/"` over the clone, `.git` and `target` left out). The path is named by
    the script's own header and printout, edited here, and by builders' citations in plan-done.md (T55, T64, T68, T69), history that
    keeps its words.
  - The installed script was written to a temp file and moved into place, so a run already reading the old one keeps its own copy.
- **Red first** (`tests/hooks/test-closing-checks.sh` case 4, T69's shape in a scratch world: run A's `quick` and `hooks-test` red,
  its `hooks-test` and `static` held on a release file; run B, all green, started once A's `quick` ended, its `static` held; A released
  after B's `hooks-test` ended; the stub's lines tagged with their run; case 5 the prune; cases 1 and 2 read the run's directory):
  - before: 18 passed, 16 failed; run A RED `1 of 3` with `quick GREEN` (B's file), run B RED with `hooks-test RED (exit 1)` (A's
    file), one directory for both, measured 2026-11-21 (the suite by path against the unfixed script, `/tmp/t72/red.log`).
  - after: 34 passed, 0 failed, and 34 passed in each of three more runs, measured 2026-11-21 (the same command,
    `/tmp/t72/green.log`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| each closing-checks run writes and reads its own directory; `latest` the last started; old runs pruned by age | n/a - no map | n/a | none | n/a |

### T72 Approach (checklist part A)

1. **The goal, in the world.** No map changes. Two builders' `make closing-checks` in one clone each report their own three verdicts
   and keep their own three logs, so a builder never lands on, or sets down for, another builder's result; the latest run's logs are
   found at one stable path, and old runs do not pile up.
2. **The constraints.** T72's line: each run under its own directory (a run id), the combined result read from its own files alone,
   red first on two overlapping runs whose verdicts differ. The launcher's file list: the script, its suite, a reader of the old paths
   (none, Approach), the docs naming the paths (none outside the script) and this section; T60's `context_cap_hooks*` and T67's
   `readme_hooks*` untouched; nothing committed. T55's rules kept: the three at once, one combined result, a TERM stops all three.
3. **Where each comes from.** O: T69's observation (its section's Found and left); O: the red-first run and the green runs (Red first);
   O: the usage records (items 8 and 10); O: the readers' grep (Approach); the task as filed (T72's line) and T55's section.
4. **Do they describe the world here?** The red case reproduces the live interleaving in a scratch world with a stub make, its order
   held by release files rather than sleeps, so the red is the bug's and not a timing's: against the unfixed script it read exactly
   T69's wrong verdict, run A's `quick` from run B's file, measured 2026-11-21 (`/tmp/t72/red.log`). The longest run and the rate are
   this clone's, measured 2026-11-21 (`/tmp/t72/durations.py` over `.git/tool-usage.jsonl`).
5. **The order.** After T55 (the script it fixes) and T69 (whose builder found it); before T22. Beside T60 and T67, touching neither's
   files.
6. **The exits.** Green: the suite green with case 4 red first, and the fixed `make closing-checks` run in this clone. Red: what failed
   recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The task named the fix; the only probe was the readers' grep, which found none in code.
8. **The budget.** One landing. A run's added work is a `mkdir`, a symlink and a rename, and one `find` over the top level of
   `.git/closing-checks/`: at the measured rate of about five runs an hour (27 runs from 04:43:58Z to 10:05:02Z in this clone,
   measured 2026-11-21 (`.git/tool-usage.jsonl`)) and a 360-minute keep, some 30 entries.
9. **Done, measured.**
   - the red case green, 34 passed, 0 failed, measured 2026-11-21 (`tests/hooks/test-closing-checks.sh`, `/tmp/t72/green.log`).
   - the fixed script's own run in this clone wrote `.git/closing-checks/20261121T101614Z-746097/` with `latest` naming it, the old
     layout's six files of 10:05Z left beside it (younger than the keep, item 10), measured 2026-11-21 (`ls -la .git/closing-checks/`
     a minute into the run).
   - that run, 69 s wall: `hooks-test` GREEN in 69 s (56 suites green, this suite among them in 5.8 s) and `quick` GREEN in 5 s, measured 2026-11-21 (the run's table and
     `hooks-test.log`); `static`
     RED in 16 s on one step alone, `rust lint` of `rust/guard`'s `doc_markdown` at `context_cap_hooks.rs:497` and
     `context_cap_hooks/tests.rs:777`, T60's builder's uncommitted files in the same clone, outside this task's files, measured
     2026-11-21 (`.git/closing-checks/20261121T101614Z-746097/`, each check's log). `static` stops at its first red step, so its
     `spec-lint --delta` did not run; `make quick`, which runs it and the house-style delta, was clean over this section after it was
     written, measured 2026-11-21 (`make quick`, `/tmp/t72/quick.log`).
10. **Before moving a constant.** One new constant, `CLOSING_CHECKS_KEEP_MIN`, 360 minutes, a GUESS knob labeled in the script: 36
    times the longest run in this clone, 601 s of 25 paired runs, measured 2026-11-21 (`/tmp/t72/durations.py`, each closing-checks
    end in `.git/tool-usage.jsonl` paired with the latest start not yet paired, 2 of the 27 starts left with no end), so no live run
    is pruned. That pairing can only overstate the longest run: in a run of overlapping runs the first start is paired with the last
    end. The 2 starts with no end are runs that recorded no outcome, their length unknown. Age was chosen over a count or a live-pid
    test: a count prunes a live run when many start at once, and a stopped run leaves no exit file and its pid can be reused. The old
    layout's files are held to the same keep, one rule: what it costs is that they stay beside the run directories up to six hours after
    the change reaches a clone (this clone's until about 16:05Z), read by nothing in code (Approach); the alternative priced, removing
    them at once, would read a still-running old-script run's exit files as missing, a false RED. Chosen by this task's builder.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder sees its own run's verdicts and logs, never a parallel run's: before the fix, a red `quick` read as
    GREEN and a green `hooks-test` as RED (Red first) - a wrong outcome, a landing on another's green or a set-down on another's red,
    so the code is fixed, not the claim. Nothing on a map.

**Found and left?** none.

**Performance work?** Yes - a `[perf]` task (451 FR-013): the builders' loop, a closing check read right the first time rather than
re-run after a verdict that was not its own. Not an engine-speed task, so the checklist does not apply.


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


### T74 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T74 Approach (checklist part A)

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


### T75 (the README guard refused a README path held as the text of a one-line Python string, found by T67's first plan review, 2026-11-21)

- **Approach**: carried by T67 (its L1, fixed there at its plan review's ruling): the guard's Python reading counts a one-line string that holds a quoted string of its own as the program's text, so a program whose `write_text` argument is the text of another `write_text` call passes, and a string holding no quoted string (an f-string path) is still refused - red first in T67's readme suite (61 passed, 11 failed before, 75 passed after, measured 2026-11-21, `tests/hooks/test-readme-hooks.sh`). T75 changes nothing of its own; this section records that T67 carries it.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| T67's L1 | fixed and pinned by T67's suite case | n/a | none | n/a |

### T75 Approach (checklist part A)

1. **The goal, in the world.** A path a program only holds as a string's text is no write.
2. **The constraints.** T67's line and its first plan review's L1 ruling; FR-012 (a refusal pinned red first).
3. **Where each comes from.** O: T67's first plan review, 2026-11-21.
4. **Do they describe the world here?** Yes: T67's suite case reproduces the shape (measured 2026-11-21, its red run).
5. **The order.** With T67, whose code carries it.
6. **The exits.** Green: T67's readme suite green with the case. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing, T67's.
9. **Done, measured.** T67's readme suite 86 passed, 0 failed, the one-line string case among them (measured 2026-11-21, `tests/hooks/test-readme-hooks.sh`, T67's last builder).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A correct Python program was refused; after, it passes and a real write of the GM's file is still refused.

**Found and left?** none.

**Performance work?** no.

