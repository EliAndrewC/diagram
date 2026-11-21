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
<!-- plan-archive: T48 to T46 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T77 to T77 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
<!-- plan-archive: T111 to T111 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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
<!-- plan-archive: T76 to T74 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T48 to T76 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T78 to T77 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T78 to T78 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T79 to T50 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T79 to T79 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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


<!-- plan-archive: T81 to T79 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T81 to T81 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T82 to T48 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T82 to T82 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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


<!-- plan-archive: T84 to T84 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T85 to T85 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T86 to T86 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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


<!-- plan-archive: T88 to T88 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
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


<!-- plan-archive: T92 to T84 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T92 to T92 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T94 (the land crate's tests read the session's `PLAN_REVIEW_OK` and write the real guard log, measured 2026-11-21 by T84 (the guard log's `plan-gate` rows naming the land tests' fixture feature `449-x`: 20-odd `plan-review-stale 449-x` blocks and `plan-review-ok 449-x: 451 T41 and T43 reviewed CLEAR ...`, the session's own escape text, taken by a fixture's tick during a landing's `make done`))

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T94 Approach (checklist part A)

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


<!-- plan-archive: T95 to T88 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T95 to T95 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T96 to T96 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T96 to T96 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T98 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T98 Approach (checklist part A)

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


<!-- plan-archive: T99 to T88 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T99 to T99 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T100 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T100 Approach (checklist part A)

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

<!-- plan-archive: T101 to T97 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T101 to T101 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T102 (the Stop hook's free-slot refusal named T22, which waits on a measured day, in each of its 4 refusals of 2026-11-21 18:48-19:39Z, each with 2 builders running, measured 2026-11-21 (the session transcript's refusal texts, deduplicated by time); T98, measured only after a night of rolling dispatch, the next it would name)

- **Approach**: a task line carries its wait, and the one reading of "can this task start now" skips a task whose wait is not met:
  - THE CLAUSE (`rust/guard/shared/src/guards/set_down_hooks.rs`, `WAITS`, `waits`): `(waits: <when>)` right after the id's
    bracketed tags, where FR-013's `[perf]` is read (`PERF_TAG`), so a line that only quotes the clause in its prose - T102's own,
    "a 'waits:' clause" - waits on nothing. `<when>` is:
    - a landing: `T88 lands` or `T02-T21 land` (a range is every task numbered in it), met when none of them is open;
    - a day after one: `a full day after T02-T21 land`, met 24 hours past the latest landing of the tasks it names, read from the
      feature's event log - each land `end` line with `landed` true, at its `t1`, for each of its `tasks` (a batch lands several),
      else its `task`; a task ticked before the log carried those lines (451 T02-T05) landed long ago. The 24 hours is a CONVENTION,
      chosen by T102's builder as the plain reading and the algorithmically easier route (the record is silent): T22's "first full day
      of work after T02-T21 land" is the 24 hours after the last of them. Priced and not taken: the end of the next whole UTC day,
      which waits up to 24 hours longer for nothing T22's or T98's measurement needs.
    - anything else in the parentheses: no wait. It fails toward a start the session sees named, never a task hidden from the hook
      for good (a CONVENTION, as T88's line naming nothing fails toward a start).
    - a bare date: deliberately not a form, on T102's plan review (D7e, 2026-11-21: NOT LEGITIMATE): the clock against a typed
      date, with no landing behind it, would take a performance task out of FR-013's refusal with no reason recorded, and no line
      needs one (T22's and T98's days are each a full day after a landing). The brief's date form was built first and dropped on
      that ruling.
  - ONE READING, THREE READERS: `waits` is the clause, `after T<n>` an open task (T88's rule, moved in from `next_independent`), and
    an open task's line saying it `lands before` it (found here: 4 open lines say "lands before T22" - T52, T96, T98, T99 - measured
    2026-11-21, a grep of tasks.md; without it T22 would be named at its day while they are open, the same defect a day later). It
    is applied in `next_independent` (the free slot), in `next_performance` (`make task-start`'s FR-013 picker and the Stop hook's
    "performance work first") and in the nothing-running refusal's fallback (it named the feature's first box, T22 again). So
    FR-013's escape "a performance task waiting on another task's landing" is read rather than escaped: one rule, not two, and
    `task_start.rs` is unchanged (it calls `next_performance`). The free slot's `PERF_LATER_OK` reason now reads "is started or
    touches a running task's files": a waiting task is no longer named there.
  - THE TWO LINES SET:
    - T22 `(waits: a full day after T02-T21 land)`: the last of T02-T21 to land was T11, at 2026-11-21T08:00:27.560Z, measured
      2026-11-21 (the 451 event log's land `end` lines, `landed` true; T02-T05 have none, their ticks the commits of 2026-11-20
      01:47-02:57 EST by `git log`, before T06's end line), so T22 waits until 2026-11-22T08:00:27.560Z, and while T52, T96, T98 and
      T99 are open.
    - T98 `(waits: a full day after T88 lands)`: T88 landed at 2026-11-21T18:40:27.980Z, measured 2026-11-21 (the same lines), so T98
      waits until 2026-11-22T18:40:27.980Z - a full day, which holds a night of rolling dispatch (T88's before window was a night
      of 07:50-17:30Z), a CONVENTION chosen by T102's builder.
  - THE CLOCK: `L7R_WAITS_NOW` (an ISO time), the tests' seam, as `L7R_PERMIT_NOW` is the permit's; else the system clock.
- **Red first**, measured 2026-11-21: the three new tests on the unchanged hook - 357 passed, 3 failed (`make rust-test
  CRATE=rust/guard/shared`, `/tmp/t102/red.log`): the free slot named T04, a task waiting on a full day; the picker named T04 before
  its day; the nothing-running refusal named T02, waiting on 2999-01-01. With the change: 360 passed (`/tmp/t102/green-1.log`).
  After the plan review dropped the date form, those cases wait on landings instead (each first assertion still names a task the
  unchanged hook named first; not rerun red), and a bare date is pinned as no wait (`/tmp/t102/green-3.log`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the free slot, the nothing-running refusal and task-start's picker skip a task whose `(waits: ...)`, `after T<n>` or another's `lands before` is unmet | n/a - no map | n/a | none | n/a |

### T102 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A freed builder slot is never filled with a task that cannot start yet - T22 before
   its measured day, T98 before its night - so the session no longer skips the hook's named task by hand; and `make task-start`
   refuses other work only for performance work that can start.
2. **The constraints.** T102's line; FR-013 (performance work first, its escape for a performance task waiting on another's
   landing); FR-012 (red first); T88's free slot and its order; `task_start.rs` unchanged (outside the files: the shared picker
   carries the rule); T101's condition in `speckit.rs` kept (the clause is parsed in `set_down_hooks.rs`, not there); the launcher's
   files only (`set_down_hooks` and its tests, `docs/guards.md`, T22's and T98's lines, this section); nothing committed or pushed.
3. **Where each comes from.** O: the 4 refusals naming T22 (the session transcript), T11's and T88's landings (the event log's land
   `end` lines), the 4 "lands before T22" lines (tasks.md), each measured 2026-11-21; R: T102's line as filed and its brief; the
   24 hours a CONVENTION (Approach).
4. **Do they describe the world here?** The landings are this clone's own log, measured 2026-11-21 (a Python read of
   `.git/l7r-events/451-time-retro-and-efficiency.jsonl`, `landed` true lines by `tasks`). The clause read on the real T22 and T98
   lines, measured 2026-11-21 (this task's guard binary, the nothing-running Stop on a fixture of those lines beside a plain T200
   and a copy of 451's event log, `L7R_WAITS_NOW` set, `/tmp/t102/real-lines.txt`): T22 alone is skipped at 2026-11-22T08:00:27Z and
   named at 08:00:27.560Z; beside T98 it stays skipped at its day, since T98's line says it lands ahead of T22; T98 alone is skipped
   at 2026-11-22T18:40:27Z and named at 18:40:27.980Z.
5. **The order.** After T88 (the free slot it changes); beside T101 (the land crate, `land-alone.sh`, the root CLAUDE.md) and T99
   (`test-idle-tests-hooks.sh`), touching none of their files.
6. **The exits.** Green: the red-first pair and this task's closing checks (`make closing-checks T=T102 F=451`). Red: what failed
   recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one rule, read where the three readers already read a task's line.
8. **The budget.** One landing. The Stop hook's added read: the feature's event log, only for a full-day wait whose tasks have all
   landed, once a Stop (`Lands`, read per feature); in 451 today only T98's (T22 is held by the "lands before T22" lines with no
   read), 10.4 MB, measured 2026-11-21 (`ls -l`). Its CPU, the nothing-running Stop on a fixture copy of 451 (its tasks.md, plan.md
   and event log): 0.00-0.02 s user+sys for the old binary and the new, 6 runs each, measured 2026-11-21 (`/usr/bin/time`,
   `/tmp/t102/timing-fx-cpu-2.txt`), once `performance()`'s text check was in (Found and left).
9. **Done, measured.** The red-first pair: 357 passed and 3 failed on the unchanged hook, then 360 passed (`/tmp/t102/red.log`,
   `/tmp/t102/green-1.log`), and 361 after `performance()`'s text check (another builder's new test among them; lint and cover clean
   on `rust/guard/shared`, `/tmp/t102/pre2.rc`), measured 2026-11-21. On the real clone, the Stop guard replayed with nothing
   running (an empty transcript, the guard log sent to `/tmp/t102/guardlog`): the live binary named "T22 [perf] (waits: a full day
   after T02-T21 land) ... make task-start F=451 T=T22", this task's named T96, the next performance task that can start, measured
   2026-11-21 (`/tmp/t102/replay0-before.err`, `replay0-after.err`). The free-slot replay was not discriminating: T22's line names
   `docs/guards.md`, which this task's edits make busy, so both binaries named T96 (`/tmp/t102/replay9-*.err`, `L7R_BUILDERS=9`).
   The closing checks, measured 2026-11-21: the first `make closing-checks T=T102 F=451` RED, 1 of 3 (`/tmp/t102/closing-1.log`,
   `.git/closing-checks/20261121T195632Z-3426745/`) - static on T103's `rust/guard/shared/src/shape/tests/builds.rs` format alone
   (its BLOCKED tag: nothing of T102's judged there), hooks-test GREEN (57 suites), quick clean.
10. **Before moving a constant.** n/a - `DAY_MICROS` is a full day by definition; the 24 hours and T22's and T98's days are the
    CONVENTIONS of the Approach, each labeled.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session sees the free slot name a task that can start, or none, where it named T22 in each of its 4
    refusals of 2026-11-21.

**Found and left?**
- The nothing-running refusal named the feature's first box, T22, whatever its wait: fixed here (it names the first task that can
  start, or says none can).
- An open task's line saying it lands ahead of T22 held nothing, so T22 would be named at its day while T52, T96, T98 and T99, the
  four such lines, are open: fixed here (`waits` reads it), observed 2026-11-21, method: a grep of 451's tasks.md for "before T" and
  a number (4 open lines, each naming T22, and 3 lines naming T13, T16 and T21, tasks already landed).
- `performance()` built a pattern and ran it over the whole plan.md for every box it was asked of, so once the picker walked past a
  waiting T22 the nothing-running Stop cost 0.09-0.16 s of CPU where it had cost under 0.01 s, and 0.01-0.02 s with the plan emptied,
  measured 2026-11-21 (`/usr/bin/time` user+sys, 6 runs each of the old and new binary on a fixture copy of 451's tasks.md, plan.md
  and event log, `/tmp/t102/timing-fx-cpu.txt`): fixed here (the heading looked for as text first, the pattern run only where it is
  there).
- SC-006's count of starts made while an open performance task waits would read such a start as an unescaped one, since a wait
  leaves no escape row: not a defect here - no reader of 451's SC-006 exists, observed 2026-11-21, method: a grep of `rust/` for
  `SC-006` (one hit, feature 240's settlement review); whoever builds it reads the waits clause beside the escape log, as T102's
  plan review notes.

**Performance work?** yes - a `[perf]` task (451 FR-013): the builders' loop (rolling dispatch names only work that can start); not
engine speed, so no checklist.


<!-- plan-archive: T103 to T93 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T103 to T103 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T104 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T104 Approach (checklist part A)

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


<!-- plan-archive: T108 to T103 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T108 to T108 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T106 (a builder the coordinator re-numbered mid-task kept its brief's task on every event-log line: T101's builder, briefed `451 T100` and told "Your task is T101, not T100" by a SendMessage 20 s into its run, filed all 229 of its own lines (227 tool lines, its start and its stop) under T100, its Write and Edit lines of `speckit.rs`, `ready.rs` and `land-alone.sh` among them, so land-alone's list at T82-T101's landing named none of them and its closing checks would have set them apart as T100's, a wrong green - measured 2026-11-21 (a streamed Python read of the 451 log's lines by `by`, against the session transcript's SendMessage calls))

- **Approach**: the correction is kept per agent and read on each of its later lines; its earlier lines stay as filed:
  - THE MEASUREMENT, the night's 136 builders (session `c6fd72d1`, each subagent whose meta file's `description` names `451 T<n>`),
    measured 2026-11-21 (three streamed Python reads of the session transcript, the subagents' transcripts and meta files, and the 451
    log, under 15 MB each; `/tmp/t106/census.py`, `measure3.py`, `sends.py`):
    - re-numbered: 1 of 136 - `a30ac631e43ef6d1c`, T100 to T101; its own calls, heredocs stripped, name a task its brief does not in
      that one builder alone, and no builder's `decide`, `task-start`, `tick` or `land` line in the log carries one;
    - the 230 lines naming it (its 229 and the coordinator's dispatch): all T100; 8 before the SendMessage (18:48:55Z) - the
      dispatch, its start and 3 Bash calls, none a write; its Edit of `speckit.rs` at 19:04:02Z, Write of
      `ready.rs` at 19:05:37Z and of `land-alone.sh` at 19:09:50Z all after it, measured 2026-11-21 (the 451 log's lines by `by`);
    - the signals, earliest first: the coordinator's SendMessage (summary "Your task is T101, not T100"), before every write; its
      `make guard-edit WHY="451 T101 - ..."` at 19:03:56Z (guard sources only, not a candidate); its handoff `T101-builder.md` at
      19:01:01Z, a Bash heredoc with no agent id in its name; its one own call naming T101, `(make closing-checks T=T101 F=451 ...)`
      at 19:16:58Z, after every write of the three files; no `decide` or `task-start` of its own; its context-cap handoff
      `T100-a30ac631e43ef6d1c.md` at 19:18:56Z, named by `context_cap_hooks` from `filed_at`'s task, so an output of this same chain,
      not a signal;
    - the own calls across builders: `decide` 98 of 136, `closing-checks` 22, `task-start` 0; 1,113 of the 1,695 Write and Edit lines
      of the 101 builders with both came before the builder's first such call, and 3 builders' first call preceded every write;
    - the messages: 117 SendMessage calls, 108 to an agent whose brief names a task, 40 of those naming another task, 1 a correction;
      `T<n>, not T<m>` matched 2 - the correction's summary, and "filed as T43, not T42" to T40's builder, `T42` not its task;
    - the rule replayed over the night's 31,888 builder lines, its own steps read from the builders' transcripts: 221 of
      `a30ac631e43ef6d1c`'s lines move to T101 (40 of them writes); and, before the brief rule below, 64 lines of
      `ac1aa778c0f1068d8`, briefed `451 T28+T29`, would have moved to T29 after its `make decide T=T29`, 6 of them writes
      (`tests.rs`, `plan.md`) that T28's closing checks would then set apart, the same wrong green the other way,
      measured 2026-11-21 (`/tmp/t106/replay.py`).
  - THE CHOICE, from it: the SendMessage FIRST and the builder's own closing step second - the reverse of the task line's order - since
    an own call alone at write time leaves every one of the three files T100's (all three before 19:16:58Z), and re-filing the
    earlier lines is out of reach: both splits are inline Python reading each line's raw `task` (`scripts/land-alone.sh`, T96's,
    and `scripts/gates/closing-checks.sh`), `make events-refile` is the measure crate's, and a hook rewriting the log under live
    appends - 11.5 MB, measured 2026-11-21 (`ls -l`) - would lose lines (a task id's length can change, `T99` to `T100`, so no
    general rewrite is in place). Earlier lines stay as the writer filed them: T101's 8 lines before the send wrote nothing,
    measured 2026-11-21 (the 451 log's lines by `by`), so neither split had anything of them to read (its lines already
    written were re-filed once, by hand: Found and left).
  - THE CORRECTION (`event_log_hooks/filed.rs`, `renumbered`): the main session's delivered SendMessage (its `PostToolUse`) to an
    agent id whose summary or message reads `T<new>, not T<old>`, `T<old>` the task the agent is filed under now (its correction,
    else its meta file's brief's `T<n>`) - the GUESS-knob pattern `CORRECTION`, fitted on the one case; or the builder's own `make
    closing-checks`, `make decide` or `make task-start` `T=` naming a task neither its brief names nor it is filed under now
    (`own_step`, heredocs stripped) - so a two-task brief's second task is the builder's own and moves nothing.
  - THE STORE (`event_log_hooks/dispatches.rs`): `record`, which `append` already calls on every payload, writes the new task to
    `<events dir>-dispatches/<sid>.tasks/<aid>`, one file an agent, overwritten by the next; `corrected` reads it (a missing-file
    open in the common case). Not a row of the dispatches side file: the tail a start reads of it (`TAIL`, T53's knob) would
    drop a long builder's correction.
  - THE CHAIN (`filed`): a command's own `T=` (a tick's, a task-start's, a decide's, a land's, and now a closing-checks' on its own
    line); else an Agent call's own words (its description's `T<n>`, its prompt's first line's); else the agent's correction; else the
    brief's `T<n>`; else the prompt's first line's; else the task-start in force. The task only: the feature stays the brief's, so
    `make events-refile`'s BY BRIEF rule, which moves a line only across features, leaves a corrected line where it is.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a re-numbered builder's later lines under the corrected task | n/a - no map | n/a | none | n/a |

### T106 Approach (checklist part A)

1. **The goal, in the world.** No map changes. Once the coordinator re-numbers a builder, or the builder's own closing step names
   another task, every later line of that builder carries the new task, so land-alone's list and the closing checks' split read its
   files as the new task's and `make where-time` books its time there.
2. **The constraints.** T106's line; FR-012 (red first); T26's and T53's chain kept for every agent no correction names; the files
   T106's brief allows - `filed.rs`, `dispatches.rs` and their tests (`tests/renumbered.rs`, `mod renumbered;` in `tests.rs`),
   `docs/guards.md`'s event-log row (the correction's form, which the coordinator writes), this section; none of T96's (`fields.rs`, `tests/writes.rs`, `shared::tree::program`, `tree.rs`, `interp.rs`, `land-alone.sh`, the land
   crate's alone tests), T113's or T111's; `event_log_hooks.rs` untouched (`record`, already called on every payload, carries the
   write); nothing committed or pushed.
3. **Where each comes from.** O: the census, the timeline and the message counts (Approach, each measured 2026-11-21 by the reads
   named there); R: T106's line and its brief; the `CORRECTION` pattern a GUESS knob (one case fitted).
4. **Do they describe the world here?** The pin replays T101's real sequence through `append`: its brief `451 T100: land any ready
   task, its own section alone`, an orientation Read (T100), the coordinator's SendMessage with its real summary and message, then
   the `PostToolUse` Edit and Write ends of the three files, each asserted on what both splits key on (`ev` PostToolUse, `cat` edit,
   `path`, `task` T101, no `fallback`, 451's log); the negatives are the night's own messages ("filed as T43, not T42" to T40's
   builder, "Fold both deferrals into T06" to T06's), measured 2026-11-21 (the session transcript's SendMessage inputs). End to
   end, the same sequence piped through the guard binary (`--only event-log-hooks`) into a scratch repository whose three files are
   uncommitted, then both real splits run on its log - the closing checks' Python block and land-alone's `split`, each cut from its
   script: the old binary set all 3 files apart as `T100@451-a` (an `other T100` row in land-alone's), the new judged all 3 as T101's
   (`own` each in land-alone's), the orientation Read still T100,
   measured 2026-11-21 (a replay through both binaries, `/tmp/t106/e2e/run.sh`).
5. **The order.** After T26, T53, T74 and T96 (the chain, the side file, the clone, the event log's `writes` and land-alone's
   list, none of whose files it touches); lands before T22.
6. **The exits.** Green: the red-first pair and this task's closing checks (`make closing-checks T=T106 F=451`). Red: what failed
   recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one more link read where the chain already reads a line's brief.
8. **The budget.** One landing. The hook's added work: on a subagent's line one open of its task file, missing in the common case;
   on a main-session `SendMessage` end and a builder's own closing-step call, one meta-file read and at most one small write. Its
   cost was not resolved above the noise: in the quietest of three interleaved rounds the old binary and the new took 3.82 and
   3.93 ms for a builder's Read, 14.43 and 13.97 ms for its `make closing-checks`, 2.27 and 2.37 ms for a `SendMessage` end,
   while the same call spread 3.8-16.0 ms across rounds under the other builders' load - medians of 41 each, measured 2026-11-21
   (`/tmp/t106/time/time.py`, the guard binary `--only event-log-hooks`, `L7R_EVENTS_DIR` a scratch directory,
   `/tmp/t106/time/timing-2.txt`).
9. **Done, measured.** The red-first pair: 377 passed and 4 failed on the unchanged writer (`/tmp/t106/red-2.log`; the fifth new
   test, the negatives, passes on both), then 381 passed (`/tmp/t106/green-1.log`), measured 2026-11-21. The closing checks: run 1
   RED on static alone, clippy's `doc_markdown` and `similar_names` in this task's three files (hooks-test and quick GREEN,
   `/tmp/t106/closing-1.log`); run 2 RED on static's rustfmt alone, lint clean on 34 crates (hooks-test GREEN in 55 s, quick GREEN
   in 6 s, `/tmp/t106/closing-2.log`), measured 2026-11-21. With a third `make static` refused (T14), the crate-scoped checks once
   after rustfmt and the brief rule: format, lint, 383 tests and coverage clean on `rust/guard/shared`, and `rust/guard`'s tests
   green on the same build, measured 2026-11-21 (`/tmp/t106/scoped-2.log`, `/tmp/t106/guard-crate-2.log`; an earlier scoped run,
   `scoped-1.log`, failed only on another builder's `mod triples;` whose file it had not yet written). End to end, both splits
   on the replay (item 4).
10. **Before moving a constant.** n/a - no constant moves; `CORRECTION` is new, a GUESS knob labeled at its definition, its open
    side a correction worded otherwise, which the builder's own closing step then files from that call on.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A reader of the landing sees a re-numbered builder's files in its own task's commit list and its own closing
    checks, not set apart as the old number's (T101's three files, a wrong green before); no map changes.

**Found and left?**
- The 229 lines `a30ac631e43ef6d1c` had already filed under T100 (its 227 tool lines, its start and its stop, 18:48:35Z-19:19:12Z)
  booked T101's half hour to T100 in `make where-time F=451` - fixed here: each line's `"task":"T100"` rewritten to `"T101"` in place,
  one byte at its offset, so no line moved and the hooks' live appends were untouched (`/tmp/t106/patch.py`, its offsets kept in
  `/tmp/t106/patch-offsets.json`), observed 2026-11-21, method: every line of the 451 log whose `by` is that agent, or a start or stop
  whose `aid` is, read back after the write (0 mismatches); the coordinator's own dispatch line of it keeps its brief's T100.
- `context_cap_hooks` named the corrected builder's handoff `T100-a30ac631e43ef6d1c.md` (19:18:56Z) from `filed_at`'s task, which is
  this chain's, so a corrected builder's handoff now takes its new number - fixed here, observed 2026-11-21 (the 451 log's Write lines
  of `a30ac631e43ef6d1c` and `context_cap_hooks.rs`'s handoff path read).

**Performance work?** yes - a `[perf]` task (451 FR-013): the builders' loop, a re-numbered builder's closing checks and landing judging
its own files; not engine speed, so no performance-checklist answers.


<!-- plan-archive: T112 to T96 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T112 to T112 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T114 to T108 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T114 to T114 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T115 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T115 Approach (checklist part A)

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

