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
clone's last `task-starts.jsonl` entry for the feature. AMENDED by T161 (2026-11-23, the plan review's T161-chain ruling): that last rung is
the main session's own lines' alone; an agent's line whose description names no task takes its builder's reading (its prompt's first line,
else its dispatching builder's), a page session's its brief's, and a line none of them names carries no task - the mark booked another
builder's four edits to T317 and refused a CLEAR, committed bundle at its landing.

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
`task-add` runs `make quick`'s checks after it writes; on a red it withdraws what it wrote and runs them again, and COMPARES both
runs' failures: where the with-line run has any failure the without-line run lacks, the line stays withdrawn and task-add refuses,
naming those failures and that the line was withdrawn; only where the failures are the same is the line restored, the failure
reported as already there. Two things make the comparison real:

- **Every check runs to its own end in both runs.** The `quick:` recipe is sequential lines, and make stops at the first that fails, so
  a failure already there in an earlier check (ruff, say) would hide the line's own in a later one (spec-lint) and both runs would
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
<!-- plan-archive: T225 to T225 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
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

<!-- plan-archive: T23 to T02 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T23 to T23 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
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
### T49 (gate-write's `own_args` blanks every literal handed to a function the program defines, so a write through that function into the tree passes a running gate: T33's after8 gate replay let through window#170's `replace_note("citations/urban-features.html", ...)`, writing `R / path` with `R = pathlib.Path("research")`, and window#172's `sub(<the built page of research/contents.json#trades-and-services>, ...)`, writing `pathlib.Path(f)`, under its stand-in `make done`, observed 2026-11-20, method: `/tmp/t33/scripts/cmp8.sh`; the shape is 16 of T93's 9,646 commands, 11 of them writing into a clone's tree, measured 2026-11-21 (`/tmp/t49/scripts/measure.py`, the corpus streamed in one process))

- **Approach**: THE FIX WAITS ON T96, THEN T110. The reading it needs (a call's literal bound to the parameter of a function the
  program defines, joined onto a module-level literal root) is T110's, in `shared::tree::program`, the one place it lives (the
  session's note, 2026-11-21: T110 "binding a function's parameter to each call's literal and joining it to a module-level root";
  T110's line: "T49 builds on the same reading"), so gate-write builds no second copy. The measured design:
  - THE MEASUREMENT, measured 2026-11-21 (`/tmp/t49/scripts/measure.py` over T93's `/tmp/t93/replay-cmd.jsonl`, 2026-11-20 12:09Z
    to 2026-11-21 17:09Z, one line at a time, and over T33's 1,134 fixture rows from `/tmp/t42/scripts/rows.py`; every hit's
    function read by hand, `/tmp/t49/t93.txt`, `/tmp/t49/fx.txt`):
    - T93's corpus: 144 Python programs define a function and hand it 303 string literals, 258 of them text that reaches no
      write, so blanking those stays right; 45 literals in 16 commands are the path the function writes, each the parameter
      written as given (`open(p, 'w')` 36, `p.write_text(` 9), none onto a root. 11 of the 16 write into a clone's tree (`cd
      <clone>/rust/gate/crates/land/src && python3 - <<'EOF'` ... `def edit(p, pairs):` ... `open(p,'w').write(s)` ...
      `edit('land.rs', ...)`), 5 into a `/tmp` worktree.
    - The fixtures: 806 literals handed to a program's own function, 712 text; 77 in 20 commands the parameter written as
      given; 8 in 2 commands (window#169, #170) onto a module-level literal root (`R = pathlib.Path("research")`, `p = R /
      path`, `p.write_text(...)`); 9 in 1 command (window#72) onto an f-string (`p = f"{R}/{rel}"`), which stays let through.
      The 94 writes' sinks: `.write_text(` 78, `open(.., 'w')` 9, `Path(p).write_text(` 7.
    - No hit rebinds its parameter (`p = f"{R}/{p}"`, window#72's class of false refusal): 0 of the 17 hit functions in T93's
      corpus, 0 of the 23 in the fixtures, measured 2026-11-21 (each hit function's body searched for an assignment to it).
    - None of the 11 in-tree writes ran under a gate of this clone, measured 2026-11-21 (an approximation: the event logs'
      `make done` and `make land` Phase lines of `diagram-backlog`, merged where 180 s apart or less, 35 runs, against each
      command's time): the hole had no victim in the corpus; T33's stand-in replay is where it shows.
  - THE READING, as these measurements need it of T110:
    - the binding: a call `F(<literal>, ...)` of a function the program defines once (`def F(params)`, found on `masked`'s copy,
      past strings and comments, as `own_args` finds it now), the literal bound by its position or its keyword to a parameter P;
      a `*args` parameter, or a second `def F`, binds nothing.
    - the reach: P, or a name the body assigns exactly `Path(P)`, `pathlib.Path(P)` or `P`, as a write's path: `open(N, <a mode
      holding w, a or x>)`, `N.write_text(` or `N.write_bytes(`, `Path(N).write_text(` - the three forms that hold every hit
      above. Another sink (`shutil.copy`, `os.replace`) is read as no write: a limit recorded, met 0 times in either corpus.
    - the root: `N = ROOT / P`, `os.path.join(ROOT, P)` and T110's `ROOT + P` (T92's builder's `root='<clone>/rust/gate/crates/'`,
      `p=root+path`), ROOT a top-level name bound once to a literal (`"x"`, `Path("x")`): the call's literal is placed at ROOT's
      literal joined to it.
    - the rest fails open, as `own_args` fails open now: an f-string (window#72), a root the program computes or binds twice, a
      parameter rebound to anything else, a function that hands P on to another function.
  - GATE-WRITE'S OWN PART, once T110 lands: `own_args`'s blanking (T33's window#72 rule) gives way to the reader's placement - a
    literal handed to a program's own function counts only where the shared reader places it, at the path the function writes;
    every other literal of such a call is blanked as now. Whether `own_args` stays for the unbound literals or retires into the
    reader's `placed` reading is T110's API to settle; make-only, fail-closed, keeps counting any literal.
  - RED FIRST, then: the case pinning window#172's shape as let through (`a_running_gate_lets_through_what_writes_outside_the_tree`,
    `def edit(p): open(p, 'w')`, marked "Found and left, T49") moves to the refused list, beside #170's shape (`R =
    pathlib.Path("l7r")`, `def f(path): p = R / path; p.write_text('x')`, `f("x/b.py")`); window#72's f-string case and a
    parameter only read stay let through.
  - THE REPLAY'S PREDICTION, measured 2026-11-21 (T33's after9 build's verdicts, `/tmp/t33/rp/gate-after9.t.gate-write-hooks.tsv`,
    for the fixtures' 22 call-through commands): 7 are refused already for another literal (window#84, #169, #220, #223,
    parse#142, #143, #196), so at most the file they name moves; 15 are let through, 13 of them because they `cd` into
    `.clones/<name>`, which T33's replay mirror ignores, so the fix moves exactly window#170 and #172 allowed -> refused there.
    T96's replay is vacuous for this guard: 0 of its 9,646 gate-write verdicts are other than silent, measured 2026-11-21
    (`/tmp/t96/replay-now-fixed.jsonl`: no `make done` stands in the row's tree), so T93's 11 in-tree commands need T33's
    stand-in gate in a git tree of the clone's shape to show their refusals.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the design measured; the fix waits on T96, then T110's shared reading | n/a - no map | n/a | none | n/a |

### T49 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A running gate refuses a Python program's write into its tree made through a
   function of the program's own, to a path the call names literally, as it refuses `open('<path>', 'w')`; every other verdict
   is unchanged.
2. **The constraints.** T49's line (the literal placed by reading the function's body; a base the program computes fails open,
   so window#72 stays let through; red first on #170's and #172's shapes; the replay's moves accounted); T110's line (the
   binding lives in `shared::tree::program`, and T49 builds on it); the brief (T96's reader not built on before it lands, its
   module not edited; the files gate_write_hooks, its tests and suite, docs/guards.md's row and this section); the gate's rule
   that a path it cannot resolve fails open; constitution XIII (no known regressions, by the replay); 100% line coverage of the
   guard crate by its own tests.
3. **Where each comes from.** O: the corpus counts, the sink forms, the rebinding search, the under-a-gate check and the after9
   verdicts, each measured 2026-11-21 (Approach); R: T49's and T110's lines, T33's section (plan-done.md) and its after8 replay;
   G: none (T110 as the reading's one place is the session's note of 2026-11-21, a process ruling).
4. **Do they describe the world here?** The corpus is this clone's own builders' commands (T93's), read whole; each of the 16
   hits' function bodies was read by hand and the 11 in-tree ones resolved against their `cd`, measured 2026-11-21
   (`/tmp/t49/t93.txt` and its cwd join).
5. **The order.** After T96 (the reader in `shared::tree::program`) and T110 (the binding there); T49 is gate-write's half of
   T110's reading, landed on its own.
6. **The exits.** Green: the red cases failing on HEAD and passing with the change, and the gate replay moving exactly window#170
   and #172 under gate-write. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through
   `make arbiter-ask`.
7. **The search smell.** none - the shapes are few and regular: three sinks hold every hit, one root form in the corpora and
   T92's `+` beside it; a sink outside them is a recorded limit.
8. **The budget.** One landing.
9. **Done, measured.** The red cases' log and the green one; the gate replay against HEAD: window#170 and #172 allowed ->
   refused, every other row's verdict unchanged, a refused row's named file moving accounted row by row.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome: under a running gate, a builder's heredoc that edits files through its own `edit(path,
    ...)` rewrites the tree the gate checks, so the gate's verdict is void ("the tree moved while the gate ran") and the whole
    gate is paid again, as T34's landing was by a `cp` (T33's line); the guard reads such a write as none.

**Found and left?**
- docs/guards.md has no row for the gate-write guard (`grep -n 'gate-write\|gate_write\|T024' docs/guards.md` finds only the
  event log's row, measured 2026-11-21), so a session it refuses finds no rule, mechanism or escape there: fixed in this task,
  the row written with the reading it lands, before this task's landing - not now, because an uncommitted hunk in
  docs/guards.md would go into T96's commit of the same file, whose line-67 edit is uncommitted in this clone.

**Performance work?** no.


<!-- plan-archive: T50 to T33 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
<!-- plan-archive: T50 to T50 moved to plan-done.md, 2026-11-21 (feature 375 FR-044) -->
### T51 (a Python program run from a script file, `python3 <path>.py`, is read by neither make-only's guard-write nor the gate's shell-write check (T33's line); measured 2026-11-21 (`/tmp/t51/rp-src/main.rs`, T93's corpus and T33's fixtures each streamed in one process, 23.8 MB peak): reading the script's text at the call would move 16 make-only rows, none a correction - window#215 carries `GUARD_EDIT_OK` on its own run, so HEAD escapes it, not lets it through - and 80 gate-write rows under a stand-in running gate, 12 of them would-be corrections and 68 false, the false ones the reader's shapes, which HEAD refuses on the stdin route today)

- **Approach**: MEASURED, NOT BUILT; T51 waits on T118. The design: a script run's text - the command's own heredoc that writes
  that path before the run, else the file at the call (a regular file of at most 1 MB, a CONVENTION) - handed to `program_names` unchanged at
  the call site, in gate-write's `shell_write` beside the walk's targets, behind a test that the named file is a regular file
  (the candidate: `/tmp/t51/cand/script.rs`, built into a scratch copy, never into the clone). Nothing lands from the call
  site, because no call-site rule meets the let-through baseline. The 12 false gate-write rows the regular-file test keeps come
  from a hook's argv list bound to a name and run (`old = ['<clone>/scripts/hooks/l7r-guard.sh', ...]` then
  `subprocess.run(old)`). window#306's read through a join (`(root / "scripts" / "house-style-hooks.sh").read_text()`) would also
  be refused at the call, and make-only refuses that read for window#305, #306 and #309. Both shapes sit inside
  `shared::tree::program`'s reader, and HEAD refuses the same programs run from stdin today. T118 (filed here) teaches the reader
  both shapes and counts gate-write's own file test, red first; T51 then replays and lands gate-write's script route. Make-only
  gains the route only if that replay shows a correction: none here, and every guard-file write through a script in both
  corpora carried `GUARD_EDIT_OK` (17 of 17). T112 landed during the measurement (`b4ab4e5a79`), which ends the brief's edit
  collision but leaves the reader outside this task's files.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the script route measured; the design waits on T118 | n/a - no map | n/a - nothing built | none | n/a |

### T51 Approach (checklist part A)

1. **The goal, in the world.** No map changes. Under a running gate, a scratch Python script that rewrites a tracked file is
   refused as `open('<file>', 'w')` from stdin is. A script that only reads, or runs a hook, is let through, and so are the four
   shapes T33 named false (window#302, #305, #306, #309). Make-only's verdicts do not move until a measured correction asks them
   to.
2. **The constraints.** T51's line (measure first, the script file's text read at the call, the 4 false shapes the let-through
   baseline, red first where a move is a correction). The brief: the files make_only_hooks, gate_write_hooks, their tests and
   suites, docs/guards.md's rows and this section; `shared::tree`'s tree.rs and program.rs not edited; a computed or absent
   script fails open, as HEAD does; no live fetch. Constitution XIII (no known regressions) and XIV (a defect is a wrong outcome).
3. **Where each comes from.** O: the replays, probes and counts of item 4. R: T33's section (plan-done.md) and its pairs
   (`/tmp/t33/sg/pairs.txt`). G: none.
4. **Do they describe the world here?** Each measured 2026-11-21 by its method:
   - THE HARNESS: `/tmp/t51/rp-src/main.rs` runs over a scratch copy of the guard (`git archive 4a282e258c`, with wrappers
     `/tmp/t51/cand/t51.rs` and the candidate reader `/tmp/t51/cand/script.rs`), giving per row make-only's verdict, gate-write's
     verdict and, for each script run read, both guards' readings of its text, ungated and gated by py_c's writer judgment (the
     walk on a stdin stand-in), with gate-write under a stand-in gate - a fake `/proc` holding a `make done` in the row's tree,
     `unseen` stubbed to "seen", the answer the gate's preflight gives with no snapshot (`would_write`) - and its rerun over
     T112's landed HEAD (`b4ab4e5a79`) differs on 0 of 9,646 and 0 of 1,134 rows, at 23.8 MB and 21.5 MB peak, measured
     2026-11-21 (`/tmp/t51/m2-*.jsonl` against `m-*.jsonl`, `/usr/bin/time -v`).
   - THE TEXT AT THE CALL: 38 of T33's 48 script-and-writer pairs run the script in the command that writes it (`cat > P
     <<'EOF'`, its body, then `python3 P`), so the file is absent or stale at PreToolUse and the reader takes the command's own
     heredoc for that path first, else the file - T33's rows carrying the text earlier rows' heredocs left as the disk's
     stand-in, T93's rows reading each file as it stands today as the stand-in for its text at the call - measured 2026-11-21
     (`/tmp/t51/scripts/pairs.py`, `/tmp/t51/scripts/overlay.py`).
   - THE DENOMINATORS: T93's corpus has 450 runs in 390 rows - 4 with a computed path, which fails open, 446 literal, of them
     430 read and 16 not (absent at the call, or the run inside a body or a quote) - and T33's has 148 runs - 40 computed (19 of
     them quoted, each holding `$`), 108 literal, 25 read and 83 not (43 the repository's own `scripts/`, `tests/`, `l7r/` or
     `rust/` files, which T33's replay reads only from the overlay, never the disk, 21 scratch under `/tmp`, 19 elsewhere) -
     so every figure below is over the 455 scripts read and the 83 are owed to the resumed replay, measured 2026-11-21
     (`/tmp/t51/scripts/shapes.py`, the denominator probe over both m2 replays, the 83 bucketed by path).
   - T33'S 41 RECOVERED BODIES AGAINST 25 READ: of its 48 pairs, 10 run outside their writer's row and 38 inside it - 8 of those
     with a computed path, which fails open, 10 literal ones the candidate did not read (8 run after a `cd` the walk did not
     place, 2 whose writing heredoc it did not match) and 20 read - so the 10 unread literal pairs are owed to the resumed
     replay, measured 2026-11-21 (`/tmp/t51/scripts/pairs.py` against the m2 replay).
   - MAKE-ONLY'S MOVES (HEAD `ok`, then a guard file named with reads exempted, every move gated by py_c too): 16 rows, 0
     corrections, all false - T93's 13 are t67's `corpus.py` and `replay-log.py` running a hook's argv list (12) and t58's
     `commits.py` using a path prefix in a filter (1), T33's 3 are window#305, #306 and #309 reading through a join, ungated 2
     more are false (window#310, and t08's `hand.py` with reads not exempted), and window#302 fails open on `$S/walk.py` -
     measured 2026-11-21 (`/tmp/t51/scripts/moves.py`, `judge.py`, each script's naming lines read by hand).
   - NO CORRECTION FOR MAKE-ONLY: every row whose script names a guard file and whose HEAD verdict is not `ok` is
     `guard-edit-ok`, 16 of T93's (t79's eight fix scripts, `own_args_edit.py`, `wire.py`, `edit_filed.py` and others) and
     T33's window#215, whose `python3 <scratch>/desc195.py` carries `GUARD_EDIT_OK="feature 195 FR-002: <its reason>"`,
     measured 2026-11-21 (the m2 replays, rows with `mo != ok` and a guard file named).
   - GATE-WRITE'S MOVES (gated): 80 rows - T93's 75 hold 12 would-be corrections, scratch edit scripts each binding a tracked
     file and writing it (the plan 4 times, `hookrun.sh` twice, `gate_write_hooks.rs`, `static_runs_hooks.rs`,
     `test-static-runs-hooks.sh`, `filed.rs`, `dispatches.rs`, `rust/guard/CLAUDE.md`), and 63 false from 14 scripts (a
     directory literal such as the fixtures, `specs` or `rust/guard`, a `~/` literal placed under the cwd, t67's argv lists, a
     dotted word in a test such as `'plan.md' in cmd`, `"e.g"`, `'subprocess.run'`, `'.log'` or `'static.log'`), and T33's 5
     are all false (main-tree#18 reads `SOURCES.md`, #132 uses `"fields.html"` as a key, window#305 and #309 test
     `"gm-request.md" in path`, #306 is the joined read) - measured 2026-11-21 (`judge.py`, the scripts' write calls grepped).
   - T33'S SEVEN GATE-SEEN PAIRS: none of their writes moved, each for its own reason (main-tree#18's row moved only on its
     false read of `SOURCES.md`, counted above) - main-tree#18, #89, window#215, #392 and #393 run in the
     mirror and write into another clone under the mirror's ignored `.clones/`, which this tree's gate never sees, main-tree#99
     writes its script and does not run it, and window#80's run is `$S/restore_quotes.py`, computed - so no reader shape is owed
     for them, measured 2026-11-21 (each body's binding and write lines).
   - HEAD ALREADY REFUSES THE FALSE SHAPES FROM STDIN: window#305, #306, #309 and t67's `corpus.py` run as `python3 - <<EOF`
     are refused by make-only and gate-write, and t79's `stream.py` and t46's `resid.py` by gate-write, measured 2026-11-21
     (`/tmp/t51/probe-stdin.jsonl` through the scratch build).
   - A CALL-SITE FILTER (the named file a regular file): it keeps 10 of the 12 corrections against today's tree and all 12 at
     the call (the 2 lost, `filed.rs` and `dispatches.rs`, moved since), drops 51 of the 63 false and keeps 12, t67's argv
     lists, and in T33's corpus drops all 5 against today's tree, but window#306's script read
     `/diagram/scripts/house-style-hooks.sh` at the call, so that file stood then and the filter misses the baseline, measured
     2026-11-21 (Python over the m2 replay).
   - THE COST: `scripts` takes a median of 0.26 µs a command (one naming no `.py`) and 1.4 ms at p99 in the corpus run, the
     four slowest took 80 to 162 ms in that run, a cause not identified, and re-timed warm 22 to 54 µs with a first call of 1.8
     to 2.4 ms while the patterns build, measured 2026-11-21 (the harness's `ns`, `/tmp/t51/slow.jsonl` run twice).
5. **The order.** After T118, which makes the reader read a join's read and a run argv list, and counts gate-write's own file
   test. Then T51 replays and lands gate-write's script route.
6. **The exits.** Green: after T118, the replay moves gate-write's 12 corrections' shapes from allowed to refused, red first, and
   lets through window#302, #305, #306 and #309 in both guards. Red: what failed recorded and the task set down, a claim that it
   cannot be done ruled through `make arbiter-ask`. This round's exit: the baseline fails at the call site, so the task is set
   down, waiting on T118.
7. **The search smell.** none. The false shapes are five and regular: a join's read, a run argv list, a directory literal, a
   `~/` literal and a dotted word in a test. A sixth false shape found at T51's replay is fixed in T51 when it lies in T51's
   files, else filed with its id and `lands before T51`, T51 set down through the red exit until that task lands; it is never
   landed as a limit.
8. **The budget.** One landing.
9. **Done, measured.** The red cases' log and the green one, then the replay of both corpora against HEAD: the corrections
   allowed then refused, the baseline's four allowed, and every other moved row accounted.
10. **Before moving a constant.** n/a. The 1 MB read cap is a CONVENTION past every script the corpora read (the largest 37,480
    bytes, measured 2026-11-21 (the harness's `len` over both m2 replays)), and it moves no claim.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome for gate-write alone, would-be and not observed: under a running gate, a builder's scratch
    edit script rewrites the plan or a guard source, so the gate's verdict is void and the whole gate is paid again (T33's line).
    The 12 corrections are a stand-in gate's. Make-only shows no wrong outcome on this route: every guard-file write through a
    script was escaped (17 of 17, measured 2026-11-21 (the m2 replays, rows with `mo != ok` and a guard file named)), so its
    unread route is an accepted limitation. The cost is that an unescaped script write of a guard file
    would pass unrecorded. Priced against it were the call-site reading (16 false refusals and 0 corrections) and the
    regular-file filter (it still refuses t67's argv lists). Chosen by T51's builder on the measurement; the design asks again
    after T118.

**Found and left?**
- HEAD refuses correct Python programs run from stdin or `-c`: a read through a join (window#305, #306, #309's shape), a hook's
  argv list bound to a name and run (t67's `corpus.py`), a directory literal and a dotted word under a running gate (t79's
  `stream.py`, t46's `resid.py`), each refused at once, measured 2026-11-21 (`/tmp/t51/probe-stdin.jsonl`). Not fixed here: the
  reader is `shared::tree::program`, outside this task's files, and gate-write's file test moves HEAD's stdin and `-c` verdicts
  uncounted. Filed as T118; lands before T51.
- `make guard-edit FILE=<a path outside the tree>` wrote `l7r-guard-permits.jsonl` into the clone's root, an untracked file, and
  its permit did not take: the Write of that path was refused again at once, observed 2026-11-21, method: T51's guard-edit of
  `/tmp/t51/m/rust/guard/src/guards/make_only_hooks/script.rs`, then the Write, then `git status`; the stray file removed.
  Not fixed here: the guard-edit route is outside this task's files. Filed as T119; lands before T22.

**Performance work?** no.


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
<!-- plan-archive: T80 to T78 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T80 to T80 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T83 to T79 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T83 to T83 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T79 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T87 to T87 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T89 to T79 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T89 to T89 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T79 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T90 to T90 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T100 to T171 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T100 to T100 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
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
<!-- plan-archive: T105 to T113 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T105 to T105 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T106 to T100 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T106 to T106 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T107 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T107 Approach (checklist part A)

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


### T109 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T109 Approach (checklist part A)

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


### T116 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T116 Approach (checklist part A)

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


### T117 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T117 Approach (checklist part A)

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


### T118 (shared::tree::program read three Python shapes as writes and gate-write's file test took a directory literal as a file written, so make-only, gate-write and the event log refused or listed correct work on the stdin and `-c` routes, and would on T51's script route - a read through a `/` join, an argv list bound to a name and run, a literal a test reads, a directory only read (found by T51, measured 2026-11-21, `/tmp/t51/probe-stdin.jsonl`, HEAD b4ab4e5a79); at HEAD 9bd338e244, 45 gate-write and 20 make-only refusals of correct work over T93's 9,646 commands, T33's 1,134 fixtures, T51's 455 script stand-ins and 6 probes, measured 2026-11-21 (the paired replay, `/tmp/t118/scripts/paired.sh`))

- **Approach**: three readings of a literal's use and a narrower directory rule, each measured first over the corpora:
  - THE MEASUREMENT, the paired replay - HEAD 9bd338e244 against T118's rule, both built from the clone's HEAD `rust/` (T118's
    files laid over the after side), one process a corpus, peaks 12.9-24.3 MB - measured
    2026-11-21 (`/tmp/t118/scripts/paired.sh`, `counts.py`, `shapes.py`; the after side rebuilt from T118's final files, split
    layout included, and replayed again by `after.sh` after the plan review's round):
    - refusals, HEAD -> T118: T93's commands make-only 56 -> 56, readme 0 -> 0, gate-write (a stand-in `make done` in the row's
      tree) 794 -> 792; T33's fixtures 86 -> 86, 1 -> 1, 215 -> 212; T51's script stand-ins, each judged in its ORIGIN row's
      tree (178 of T93's 430 had no tree when judged in the script's own directory, the harness's fix), T93's make-only 29 -> 16
      and gate-write 107 -> 76, T33's 4 -> 1 and 5 -> 1; T51's probes 4 -> 0 and 6 -> 1;
    - every moved verdict moved to a let-through, none to a refusal: gate-write 45 - an argv list run 17, a directory 18, a test
      8, a join read 2 - and make-only 20 - an argv list run 13, a join read 6, an affix test 1 (T58's `commits.py`,
      `f.startswith('rust/guard/src/')`);
    - the event log's `writes`, measured 2026-11-21 (`compare.py`): 14 rows lose a name and none gains one - `scripts/hooks/l7r-guard.sh` on t67's 12 argv rows and
      its probe (run, never written), and `/diagram/CLAUDE.md` on main-tree#18's script, where it is only tested:
      `f.endswith(('SOURCES.md','README.md','CLAUDE.md'))` keeps it OUT of the files the program writes (`open(f, 'w')` over the
      research glob of another clone) - a correction, no real write lost;
    - 5 rows moved in their names alone, verdicts unchanged, measured 2026-11-21 (`compare.py`, each read by hand): window#54, #56
      and #65 (`sys.path.insert(0, "scripts")` in a program writing no computed path), #388 (`"../" * n`, an href), refusals#80
      (`"4c." not in t`); window#393's script, whose reader-reports root the first rule dropped, is named again beside its
      `io.open(P, "w")`;
    - each moved row read by hand, measured 2026-11-21 (the rows' programs, `unread.py`): every directory row only reads or runs its directory (`Path("specs")` globbed, `json.load(open(
      f"{FX}/x.json"))`, a `git log -- rust/guard` argv, `sys.path.insert`; T93's 13 script rows are 3 scripts), and the 24 rows
      whose directory T118 dropped hold no writer the reader does not read onto a computed path (`/tmp/t118/scripts/unread.py`:
      1 hit, window#393's `io.open(P, "w")`, `P` a literal the guard still names); t46's `e.g` and `i.e` are a set bound to `AB`
      and never used and an element of `w in {"e.g", ...}`, both tested. Every move a correction.
  - THE FIX (`shared::tree::program`, `program/uses.rs`): `chain_read` - a literal that is a part of a `/` join read whole (its own
    parenthesis or `Path(`'s, closed by `.read_text(` or `.read_bytes(`) is read; `display_run` - a literal of a list, tuple or set
    bound to a name on its line, the name's every use a subprocess argv (`RUNS`), a `for` whose variable is only run, a test, or
    none, is run (an f-string placeholder of the name fails closed); `tested` - `'x' in s`, `'x' not in s`, an element of what
    `in` tests, an argument of `.startswith(`/`.endswith(` or an element of the tuple one takes - is text under `placed`
    (gate-write, readme, the event log) and, for make-only, fail-closed, only in a program that writes no path it computes, which
    the tested literal could name the landing of; and gate-write's `file_named(p, computed)` takes a directory only beside such a
    write (`writes_computed`: a write target holding a name - `holds_name`: not `Path`, not a string prefix save an f-string's with
    a placeholder - a method write on a receiver it cannot read, or a writer it does not read, `UNREAD_WRITERS` - `shutil.copy`,
    `os.replace`, an extraction - or a dotted `open` with a write mode), so window#170's `p = R / path`, `p.write_text(..)` and
    refusals#144's `rglob` rewrite, true writes into `research` and `l7r`, stay refused (the plain directory rule let both through
    on the first replay). The plan review's first round (BLOCKED, 2026-11-21) found make-only still refusing T58's read-only
    `commits.py` on `f.startswith('rust/guard/src/')`: the single-argument affix test and make-only's reading came from it, and
    the writers it does not read from its note of the gap a `shutil.copy` into a named directory left.
  - THE SPLIT, file-scale's 1,000-line bar (the coordinator's note, 2026-11-21): `program.rs` 1,276 lines -> 438, its parse on the
    mask in `program/parse.rs` (601) and a literal's uses in `program/uses.rs` (265), moved by line range, measured 2026-11-21
    (`wc -l`; `l7r-gate.sh check file-scale` exit 0).
  - THE COST, measured 2026-11-21 (`/tmp/t118/scripts/cost.py`, T96's method: HEAD's and T118's release binaries alternating, 3
    runs a command, user + sys CPU medians, load 6-21): the event log's end on 200 of T93's Python programs +0.00 ms median (T96's
    bar 0.09 ms), p90 1.16, mean 0.03, on 200 of T93's commands +0.01 ms median, and make-only's start -0.03 ms median on the
    Python programs and -0.01 on any command, measured 2026-11-21 (`cost.py` on T118's final binaries; the first version's run read
    +0.02, -0.09, +0.04 and -0.04). The tail: make-only's p90 on the 151 moved and stand-in rows is 11.27 ms, measured 2026-11-21
    (`cost.py`), and 8 of them add 13-19 ms, each a row HEAD refused and T118 lets through, measured 2026-11-21 (`cost_tail.py` on
    the first version's binaries, 7 runs a binary),
    and with window#305's guard-file literals renamed both binaries cost the same, 11.51 and 11.62 ms, measured 2026-11-21
    (`cost_var.py`, 9 runs): the time is make-only reading each literal past the first guard file, where HEAD's refusal stopped,
    not T118's scans (`BUILDS`: a join read builds its pair's pattern, an argv list or a test none).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a read, a run, a test and a directory only read named by none of make-only, readme, gate-write and the event log | n/a - no map | n/a | none | n/a |

### T118 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A correct Python program run from a heredoc or `-c` - a hook read through a `/`
   join, an argv list bound to a name and run, a literal a test reads, a directory it only reads - passes make-only, readme and
   gate-write while a gate runs, and the event log lists none of them as written; a true write into the tree stays refused.
2. **The constraints.** T118's line; FR-012 (red first); T96's and T110's readings kept (their tests unchanged and green); T129's
   `tree.rs` patterns and T89's `py_c` left alone; T118's files only - `tree/program.rs`, `tree/program/{parse,uses,tests}.rs`,
   `gate_write_hooks.rs` and its tests, `docs/guards.md` row 67, `rust/guard/CLAUDE.md`'s `tree` entry, this section and T138's
   line; nothing committed or pushed.
3. **Where each comes from.** O: the replay's counts, the hand reads, the writer search and the cost (Approach, each measured
   2026-11-21 by the script named there); R: T118's line and T51's probes; the call names `RUNS` and `UNREAD_WRITERS`, the string prefixes
   `rRbBuUfF`, the mode letters `rwaxbt+` and the receiver `Path`/`pathlib` are CONVENTION knobs, Python's own spellings; the directory rule's `writes_computed` a GUESS
   knob fitted on the replay's two true writes (window#170, refusals#144).
4. **Do they describe the world here?** Measured over every row of T93's corpus, T33's fixtures, T51's script stand-ins (each in
   its origin row's tree) and probes, each moved row read by hand, measured 2026-11-21 (`/tmp/t118/scripts/compare.py`,
   `shapes.py`, `unread.py`).
5. **The order.** After T110 (landed); before T51, whose script route reads through these readings, and T138 before T51 too.
6. **The exits.** Green: the unit tests red on HEAD's code and green on T118's, the replay with no new refusal and every move a
   correction, `make rust-test` and the lint of both crates, the cost's median under T96's bar. Red: what failed recorded
   and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the shapes came from T51's probes and the replay's refusals, and the directory rule narrowed once,
   on the plain rule's two regressions the replay showed.
8. **The budget.** One landing.
9. **Done, measured.** Red: HEAD's code with T118's tests, measured 2026-11-21 (`/tmp/t118/scripts/red.sh`, its stubs HEAD's own
   readings under the new names, `/tmp/t118/red-rust.log`): `l7r_shared` 5 failed - the join read, the argv list, the dotted test,
   `BUILDS`, `writes_computed`'s literal cases - and `l7r_guard` 2 - gate-write's let-through and file tests; the plan review's
   round, each new case red on the code before it, measured 2026-11-21 (`/tmp/t118/red2-rust.log`: the writers it did not read
   and make-only's tested literal, 2 failed; `/tmp/t118/red3-rust.log`, `red3.sh`: the single-argument affix test, 1 failed).
   Green, measured 2026-11-21 (make): `make rust-test CRATE=rust/guard/shared` 417 passed, `CRATE=rust/guard` 446,
   `l7r-gate.sh rust lint` clean on both, `make quick` green, `l7r-gate.sh check file-scale` clean.
10. **Before moving a constant.** n/a - no constant moved; the knobs of item 3 are new.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A session sees a correct program let through where it was refused - 45 gate-write and 20 make-only
    refusals of the replay - and the event log no longer naming a hook it ran or a file it excluded as written; no check breaks.

**Found and left?**
- t79's stdin probe stays refused by gate-write (a correct replay driver refused while a gate runs) on three names: `tests/hooks/fixtures`,
  a directory only read through f-string joins beside the program's computed writes into a tempdir; `run.`, a keyword argument
  (`tempfile.mkdtemp(prefix="run.", dir="/tmp/t79")`); and `.gitignore`, an argument of a local wrapper of subprocess (`git =
  lambda *a: subprocess.run(["git", *a])`), which the event log also lists as a write of the clone's `.gitignore`; T33's window#68
  and #69 stay refused on `scripts`, a `shutil.copytree` source, for the first reason - each refused at HEAD too, measured
  2026-11-21 (the paired replay, `/tmp/t118/pair-after`; the second and third shapes in that probe alone of its 11,241 rows).
  Not fixed here: the keyword argument and the wrapper are none of T118's shapes, and the directory, one of them, sits beside computed writes
  whose landing the reader does not follow, so the rule that keeps window#170's true write refused keeps it refused too.
  Filed as T138; lands before T51.
- A writer the reader did not read (`shutil.copy(a, 'l7r/')`, `os.replace`, a dotted `io.open(P, 'w')`) was no computed write, so
  under the first version of the directory rule a directory beside one alone named none, where HEAD refused that program by the
  directory's literal - 0 of the 24 rows whose directory T118 dropped held one onto a computed path, measured 2026-11-21
  (`/tmp/t118/scripts/unread.py`), and the plan review named the gap: fixed here, each such writer counted a computed write
  (`UNREAD_WRITERS`, `dotted_open_writes`), red first in `a_write_of_a_computed_path_is_told_from_a_literal_one`.

**Performance work?** No - a correctness task; its cost measured above.


### T120 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T120 Approach (checklist part A)

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


### T121 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T121 Approach (checklist part A)

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


### T122 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T122 Approach (checklist part A)

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


<!-- plan-archive: T123 to T80 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T123 to T123 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
### T125 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T125 Approach (checklist part A)

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


### T126 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T126 Approach (checklist part A)

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


### T127 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T127 Approach (checklist part A)

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


### T128 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T128 Approach (checklist part A)

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


<!-- plan-archive: T129 to T83 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T129 to T129 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
### T130 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T130 Approach (checklist part A)

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


### T131 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T131 Approach (checklist part A)

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


### T132 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T132 Approach (checklist part A)

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


### T133 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T133 Approach (checklist part A)

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


### T134 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T134 Approach (checklist part A)

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


### T135 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T135 Approach (checklist part A)

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


### T136 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T136 Approach (checklist part A)

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


### T137 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T137 Approach (checklist part A)

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


### T138 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T138 Approach (checklist part A)

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


### T139 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T139 Approach (checklist part A)

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


### T140 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T140 Approach (checklist part A)

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


<!-- plan-archive: T142 to T142 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T141 to T141 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
### T143 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T143 Approach (checklist part A)

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


### T144 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T144 Approach (checklist part A)

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


### T145 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T145 Approach (checklist part A)

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


### T146 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T146 Approach (checklist part A)

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


<!-- plan-archive: T147 to T147 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
### T148 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T148 Approach (checklist part A)

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


### T149 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T149 Approach (checklist part A)

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


### T150 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T150 Approach (checklist part A)

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


### T151 (make ledger-owed traced no check-wave unit to the session that ran it: 35 impl-drift passes of 449 T249's re-check stayed owed after the session's write and refused every landing)

- **Approach**: measured first, then the trace and the reply of a Workflow agent taught to `reviews`' `ledger_passes/rows.rs`:
  - HOW A PASS IS TIED TO A SESSION, measured 2026-11-22 (reading `ledger_passes.rs`, `rows.rs`, `settle.rs`, `trace.rs` and the
    guard's `ledger/cost.rs`): `make ledger-owed WRITE=` passes `--session $CLAUDE_CODE_SESSION_ID`, and `write_owed` keeps a pass
    where `rows::session_of` names that session - the agent's transcript's parent's parent. The transcript is found by
    `cost::transcript`, which lists `<project>/<session>/subagents/agent-*.jsonl` only. A check-wave unit's transcript sits at
    `<session>/subagents/workflows/<run>/agent-<id>.jsonl`, measured 2026-11-22 (`ls` of the session's directory: 13 runs under
    `subagents/workflows/wf_*`), so it was never found: `session_of` gave "", and the pass was "not traced to it". Had it been found,
    its parent's parent is `workflows`, not the session.
  - WHERE A UNIT'S REPLY STANDS, measured 2026-11-22 (`tail` of a unit's transcript and its run's `journal.jsonl`): the transcript
    ends in the StructuredOutput call's tool result, no text; the run's `journal.jsonl` holds one `{"type":"result","agentId":...,
    "result":{label, verdict, text}}` line per unit, `text` the unit's reply and `label` its bundle's name (`claims-rust-...`, the
    same name as the `/tmp/l7r-check/<name>/` its prompt reads, checked on one unit's first user message).
  - THE FIX (`rows.rs`): `wave_transcript` finds `<project>/<session>/subagents/workflows/<run>/agent-<id>.jsonl`; `session_of`
    names a hand-dispatched agent's session as before and a wave unit's as the directory above `subagents/workflows/<run>/`;
    `filled_row` takes a wave unit's reply and place from its run's journal (`journal_reply`: the last result line naming the agent,
    its `text` and `label`, or the result itself where it is text), and fills the same cells a hand-dispatched pass gets - the
    verdict by `verdict_of` on the reply, its first line, `nothing` or `judgment`, the acted-on cell from `WRITE=`.
  - THE VERDICT CELL, a decision, labeled (parity): read from the reply as a hand-dispatched pass's is, not from the journal's
    `verdict` field, so an all-IN-STEP impl-drift reply reads `findings` as the session's hand-dispatched impl-drift rows already do.
  - THE COST CELLS, a decision, labeled (an accepted limitation): the costing (`settle::settled`, through `cost::subagent_files`) is
    left looking where it looked, so a wave pass keeps its logged cells. Cost: a wave unit's cells are the hook's, not recomputed from
    its finished transcript (how far they differ was not measured). The alternative priced: teaching the costing the wave directory
    recomputes the cells of the ~342 wave passes already answered (377 in the log, 35 owed, measured 2026-11-22 by `grep -c` of the
    clone's `check-passes.jsonl`), and a row answers a pass by its cost cells, so those rows would answer nothing and the passes
    would be owed again. Chosen by the T151 builder.
  - THE WRITE, measured 2026-11-22 (`make ledger-owed WRITE=` in the clone, the new binary): 41 rows written for c6fd72d1 - the 35
    impl-drift units, each with its bundle's label and its reply's first line, and 6 passes launched after the brief (a
    building-review, a glyph-check and a size-audit of 449 T265, two escalation-checks, one spec-fidelity `ARBITER_OK` dispatch); 40
    plan reviews refused as their landings' own (451 T105). `WRITE=` was the session's earlier rows' full text, which begins with the
    brief's ("each pass's verdict recorded by its tool: make claims-checked into dev/claims-index.json") and names where the other
    checks' verdicts are recorded, so the 6 later rows' acted-on cells are true. After, `make ledger-owed` lists 40 passes, every
    one a MODE 4 plan review, measured 2026-11-22 (its listing, `grep -vc "MODE 4"` = 0).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the trace and the reply | `ledger_passes/tests.rs`' `a_sessions_write_takes_its_own_check_wave_units_from_the_journal` (a check-wave unit under `s/subagents/workflows/wf_r/` with its journal is written for session `s` from the journal's label, verdict and first line; another session's unit stays owed and is written for its own) - red before the fix, measured 2026-11-22 (`make rust-test CRATE=rust/gate/crates/reviews`: `0 row(s) written for s; 2 pass(es) not traced`); `rows/tests.rs`' `a_wave_unit_s_text_result_is_its_reply` (a text result, a structured result with no `text`, a journal with no result for the agent, a pass with no agent) | n/a - no engine code | none | n/a |

### T151 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A session's `make ledger-owed WRITE=` writes the rows of the check-wave units it ran,
   so they no longer refuse every landing.
2. **The constraints.** T151's line; FR-012 (red first); 451 T105 (the by-hand write refuses the landing's plan reviews); 451 T147's
   uncommitted `left.rs` built on; feature 371 (a row answers a pass by its check and cost cells).
3. **Where each comes from.** G: none beyond the task line. O: the measurements above, each dated with its method. R: none -
   tooling, no research question.
4. **Do they describe the world here?** Yes: the session's own 13 runs and the 35 owed passes, measured 2026-11-22 (`ls` of its `subagents/workflows/`, `make ledger-owed` in this clone).
5. **The order.** Measured first; the pin written and shown red; the fix; the crate's tests green; the write; the listing after.
6. **The exits.** Green: the pins pass and the crate's tests, lint and cover are clean; the write leaves only plan reviews owed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: `transcript(` callers under `rust/gate/crates/reviews` found by grep; `trace.rs`' `unit_prompt` already
   walks the wave directory for a feature's write and is unchanged.
8. **The budget.** One landing.
9. **Done, measured.** `make closing-checks T=T151 F=451` green; the after-listing above (40 owed, all MODE 4).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A defect: every landing refused on 35 passes no command could write, measured above.

**Found and left?** none.

**Performance work?** no.



### T152 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T152 Approach (checklist part A)

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


<!-- plan-archive: T153 to T153 moved to plan-done.md, 2026-11-22 (feature 375 FR-044) -->
<!-- plan-archive: T154 to T154 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T155 to T155 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T159 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T159 Approach (checklist part A)

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


<!-- plan-archive: T160 to T161 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T163 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T163 Approach (checklist part A)

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


### T164 (observed 2026-11-22: with three builders in one clone, the 449 T312 bundle's verify gate went red or "tree moved" four times on other builders' half-done edits, and seven of its ten finished review verdicts were rewritten NOT-REVIEWABLE because a page session and a test-file edit wrote into the clone while they ran; the T289 bundle's reviews earlier waited hours on a stale engine another bundle's edit caused, which also dropped its new-element units without a word)

- **Approach**: `make verify T=<task(s)> [F=] [FILES=] [REVIEW_TREE_OK=]` runs `scripts/gates/review-tree.sh`. It takes the bundle's own files using land-alone's attribution (`split`, read from `scripts/land-alone.sh` so the rule has one copy), makes a temporary commit on HEAD through a scratch index (the clone's HEAD and index untouched), and puts the clone's one review tree `<clone>-review` at it, adding it or resetting it. It draws every map `reviews owed --undrawn` names there, snapshots the owed units into the clone with `tree.json`, and starts `make done` detached there, with the record `.git/review-trees/<commit>.json`. `reviews prereq` and the pair guard judge a snapshotted unit by that record's gate at its key, and judge every other unit by the clone's stamp, as before. `reviews owed` names a map that is not current with its stale engine and the units it hides (`owed/hidden.rs`). The bare `make verify` is refused and names `T=`. The cost, measured on 2026-11-22 (method: each step's own timer in the log, `du -sh` of the target, `df`):

| step | figure | what it says |
|---|---|---|
| first run, tree added (verify1, 21:44) | setup 130 s, worktree 2.0 s, seeding 19.2 s, 7 maps drawn 128.5 s (the engines' first build into the new target), measured 2026-11-22 (its step's own timer in the run's log) | the first tree's cost is the engines' build; the gate went red at preflight in seconds (owed.rs past the 1,000-line bar, docs/make-targets.html stale), both fixed here |
| first full gate (verify3, 21:55) | setup 5.0 s and `make done` about 3 min to red (static, format, hooks-test), measured 2026-11-22 (its step's own timer in the run's log) | the kept check results seeded from the clone (`rust-checks`, `hooks-test`, keyed by content) serve every unchanged crate, so a "cold" review tree compiles only what the bundle changed |
| warm runs (verify4-verify6, 22:00-22:16) | setup 3-6 s, gate 75 s to red on format (verify4), 256 s to red on cover (verify5), 60 s to GREEN (verify6, only owed.rs changed since verify5), measured 2026-11-22 (its step's own timer in the run's log) | the warm gate costs about a minute over the crates a fix touches, measured 2026-11-22 (its step's own timer in the run's log) |
| the target's disk | 1.6 GB after verify1, 4.0 GB after verify3, 9.3 GB after verify5 and verify6 (the changed crates' coverage builds), 64-67 GB free throughout, measured 2026-11-22 (`du -sh` of the target, `df`) | not a third ~35 GB cache, measured 2026-11-22 (`du -sh` of the target, `df`): the kept results mean the review target holds only the tool builds and the changed crates' test and coverage builds |
| sharing the landing target, measured on a scratch copy of its `tool/` | cargo names artifacts the same across worktree paths and judges freshness by mtime: after the review tree built l7r_guard, the landing tree's build read `Fresh l7r_guard` although `pair_hooks/review.rs` and `state.rs` differ between the two trees | REJECTED: a shared target serves one tree the other's binaries, which is a wrong outcome (the gate would judge other code). One review tree per clone, with its own target, reset each run, never piled up |
| seeding the clone's 6.2 GB `.gencache` | 31 entries in the review tree were its own and 31,067 were seeded, and no seeded entry served a map, observed 2026-11-22, method: `find .gencache -type f -newermt` the tree's first run, counted each side. An entry is keyed by its engine binary's build id, and each tree's binary embeds its own source path (`strings tool/hamlet` names `diagram-backlog-review/rust/phases/...`), so the clone's build ids never match, observed 2026-11-22, method: `readelf -n` of each target's `tool/hamlet` and `tool/l7r-mode-a`, ids differing in every target | DROPPED (19.2 s and 6.2 GB a tree): the review tree's own `.gencache` is kept across resets (`clean -e .gencache`); the seeded entries were deleted (6.2 GB to 12 MB), measured 2026-11-22 (`du -sh` of the target, `df`) |

### T164 Approach (checklist part A)

1. **The goal, in the world.** A map review's verdict stands or falls on the bundle's own work. Another builder's edit in the clone neither turns its gate red, voids its key nor colors what it reads, and a stale engine is named, never silent.
2. **The constraints.** FR-013 (the builders' loop faster). 451 T158's disk floor and cleanup: a worktree and its cache are reused or removed, never left to pile up. Land-alone's attribution in one copy. The review is paired with the gate (feature 151, the GM 2026-08-29). Verify keeps `T=` working for the 449 sheet bundle (T328-T340).
3. **Where each comes from.** O: the T312 and T289 incidents (2026-11-22, the tasks.md line). G: T158's cleanup ("make sure that we clean up after ourselves in terms of the file system"). O: the cost table above.
4. **Do they describe the world here?** Yes: the incidents are this clone's, the figures above were measured in it, and the gate was run five times in the review tree.
5. **The order.** After T160/T161 (land-alone's `split`, which it reads), before the 449 sheet bundle's `make verify T=`.
6. **The exits.** Green: the review tree's `make done` green on T164's commit, the new tests green, MODE 4 CLEAR. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make verify T=T164` green in the review tree (verify6, commit 9abb99a2f3). `make rust-test CRATE=rust/gate/crates/reviews` 181 pass, `CRATE=rust/guard` 469 pass, and `tests/hooks/test-review-tree.sh` 22/22. RED FIRST (2026-11-22, the review tree put at HEAD af418b90c5 with only the test files over it, reusing its warm target where a scratch tree would have been a third cold build; then reset to the green commit): `rust-test CRATE=rust/gate/crates/reviews` fails to compile (`no Sides in reviews::snapshot`), `CRATE=rust/guard` fails to compile (`cannot find function snapshot_key in module state`), and `tests/hooks/test-review-tree.sh` gives 3 passed, 19 failed. The 3 that pass are the negative cases (nothing written, the clone untouched), which hold vacuously with no script. The tests of `owed/hidden.rs` and `prereq/tree.rs` are child modules of files HEAD lacks, so they are red by absence.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: verdicts recorded NOT-REVIEWABLE, and a gate red on code the bundle did not touch (T312's four reds, seven voided verdicts). Both are wrong outcomes.

**Found and left?**
- `engine_freeze_hooks` still refuses every engine edit in the clone while a map review this session launched is running. A snapshotted review reads its review tree's gate, key and content now, so for such a review the freeze holds a builder's engine edits for the whole review and gains nothing. That is a cost, not a wrong verdict. Not fixed here: it is a guard's rule change with its own measurement (a review beside an engine edit that keeps its verdict), and this task has enough to land. Filed as T165; lands before T154.
- The review tree's `make done` writes the shared `gate-green-<area>` stamps in the clone's common git directory (`stamp.rs` `stamp_path`, `common_git_dir`), as land-alone's landing worktree does. Each stamp is a content key of what that gate ran over, and the push compares it with HEAD's key, so a stamp the review commit wrote matches only where the pushed tree has the same content in the area. A stamp written over is a missed reuse at most, never a wrong pass: not a defect, the claim restated here.
- `.claude/agents/{building-review,fix-check,glyph-check,settlement-review,size-audit}.md` told the reviewer to run a bare `make review-paired-gate`, which reads the clone's gate, not the unit's snapshot. A snapshotted unit would then read red under another builder's edit and write NOT-REVIEWABLE, which is the incident itself. Fixed here: each now reads `make review-paired-gate UNIT=<your unit>`, and the pair guard's two refusals name `UNIT=` and `make verify T=` (observed 2026-11-22, method: `grep -rn review-paired-gate` over `.claude/agents`, `rust/`, `scripts/`, every hit outside `specs/` and `dev/`).
- `scripts/gates/review-tree.sh` recorded none of its runs (check-tool-signals, the gate's hooks-test). Fixed here: `# TOOL_RECORD:` names its record file and the event log.

**Performance work?** yes. It makes the builders' loop faster: a review's gate no longer goes red and its verdicts are no longer voided by another builder's edits (T312: four reruns, seven verdicts of about 10 minutes each, observed 2026-11-22, method: the T312 bundle's gate logs and its review ledger rows).

### T164 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the reruns and the re-reviews the shared tree forced (T312: four gate reruns, seven reviews voided). In the review tree, the time goes to the gate itself (60 s warm) and, on a first tree only, to the engines' first build (128.5 s), measured 2026-11-22 (its step's own timer in the run's log).
2. **Removes work, or only moves it?** It removes work: no gate is rerun and no review redone for an edit that is not the bundle's. The seeding that never served (19.2 s, 6.2 GB) is removed too, measured 2026-11-22 (its step's own timer in the run's log).
3. **What do you expect it to save, and why?** Each voided review (about 10 minutes of an agent's time, observed 2026-11-22, method: the T312 bundle's review ledger rows) and each gate rerun that another builder's edit caused. For the cost: the review tree adds about 5 s of setup a run and 9.3 GB of disk, measured 2026-11-22 (its step's own timer in the run's log).
4. **How does the work grow with the settlement?** It does not: the setup grows with the bundle's files and with the maps it redraws, not with the size of a settlement.
5. **What did the before and after show, and under what conditions?** Before: the T312 incident (2026-11-22, the host shared with three builders). After: the cost table above, measured on the same host with the other builders running. This is evidence, not a pass.
6. **Did any map move, and does it still keep the research?** No map moved: the tooling only, and the drawings it makes in the review tree stay there.


<!-- plan-archive: T165 to T172 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T167 (observed 2026-11-23: 449 T330's page sessions' event-log lines were booked to the clone's mark, T312 and then T328, and a 451 landing of T160 and T161 was refused "review passes with no ledger row" on a T330 page-session pass that 451 T157's `whose.rs` should have left to T330)

- **Approach**: two changes, each with a test that is red on HEAD.
  - **The event log** (`event_log_hooks/filed.rs`). A line is a page session's when its environment names `L7R_PAGE_SESSION`, as before, or when the clone's `page-sessions/index.txt` lists the line's own `session_id` (new). The new check is `set_down_hooks::page_session_listed`, split out of the shared `page_session_brief` reader so there is still one copy. The line is booked to the task its brief names. A listed session whose brief names no task carries no task, and never the mark's. The index is read only for a line that no earlier link has booked, and at most once per line.
  - **The ledger's left reading** (`ledger_passes/left/whose.rs`). A source that names a task gives way to the next source when that task was never started in its feature: the subject, then the meta file's description, the builder, and the page session's brief. Before this change, the first source that named any task won. The bundle `q-0123-quote-check-t330a` carries its page session's letter, and `BUNDLE` read it as `T330a`. No task T330a was ever started, so the pass refused and the page session's brief (T330) was never read.
- **How each was traced**, measured 2026-11-23:
  - **The event log** (method: the 449 log's lines of the four T330 session ids from `index.txt`, counted by `task` and `by`). Session 7e3b (t330a-checks) had 1,254 lines, all booked to T312 or T328 but 7, measured 2026-11-23 (the 449 log's lines of its id, counted by task). Session 2647 (t330b-write) had 141 of 144 on T328, measured 2026-11-23 (the same count). Session f1d2 (t330b-checks) had 216 of 296 on T328, measured 2026-11-23 (the same count).
  - **Why the T161 binary did not catch them** (method: the mtime of `~/.cache/l7r-cargo-target/diagram/l7r-guard.good` against the T161 commits and the transcripts' timestamps). The sessions ran from 02:23Z to 03:38Z on 2026-11-23. T161 reached main at 03:18Z, and the mirror's guard binary was rebuilt at 03:38Z. So the hook that booked them predated T161's `L7R_PAGE_SESSION` link. The session id is in every payload, so the new link does not depend on the environment or on which binary is running.
  - **The ledger** (method: `l7r-gate reviews ledger-owed --refuse --landing 451-time-retro-and-efficiency --tasks "T160 T161"`, run against a detached worktree at the landing's tree, af418b90c5, with the pass log cut to the passes whose transcripts ended by 02:33:40Z, the time of the refusal). The only T330 pass it kept was the `-t330a` quote-check; every other T330 pass was left to T330 already. The "29 passes" in the filing were the "29 pass(es) not traced to it" line of the `make ledger-owed WRITE=` run before the landing. That is the write path's tracing, not the left reading.

### T167 Approach (checklist part A)

1. **The goal, in the world.** A page session's work is booked to its brief's task. That covers its edits, its reads and its check passes, whatever the clone's mark names and whatever the session's environment says. A landing of another task then neither snapshots its pages as someone else's nor refuses on its passes.
2. **The constraints.** 451 T161: a line belongs to its editor, and the mark is only for the main session's own lines. 451 T157: a pass is left only to a STARTED, open task that the landing does not land. A pass naming nothing, a ticked task, a task never started with no other source, or one of the landing's own tasks still refuses. The writer and `make events-refile` share their readers (451 T56).
3. **Where each comes from.** O: the three traces above. O: the coordinator's filing (tasks.md T167). O: the 449 brief files' first lines: `t330a-checks.md` reads "feature 449 T330 and T333.5", and `t330b-checks.md` reads "feature 449 T333 and the 0116 pointer".
4. **Do they describe the world here?** Yes. The fixtures copy this clone's shapes: a brief named `t05a-checks.md` whose first line names T05 while the mark names T09, and a bundle suffix `-t2a` and `-t2b` whose briefs name T2 and T4.
5. **The order.** After T161, whose shared reader it reuses, and T157, whose reading it corrects.
6. **The exits.** Green: the two new tests, the crates' suites and coverage, lint, format and the hook suites all green, and MODE 4 CLEAR. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST (2026-11-23, at HEAD with only the test files changed, `make rust-test`):
   - `CRATE=rust/guard/shared`: `a_page_sessions_line_is_booked_by_its_session_id` failed, `left: ("451-a", Some("T09"))` against `right: Some("T05")`, with 444 others passing.
   - `CRATE=rust/gate/crates/reviews`: `a_page_session_pass_naming_its_session_letter_is_left_to_its_briefs_task` failed, `left: (1, [true, true, true])` against `right: (1, [false, false, true])`, with 181 others passing.
   - GREEN (2026-11-23, after the fix): `make rust-test CRATE=rust/guard/shared` passes 445, and `CRATE=rust/gate/crates/reviews` passes 182. `l7r-gate.sh rust format`, `lint` and `cover` run on both crates, and `make closing-checks T=T167 F=451` runs.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** These are wrong outcomes. Another task's landing snapshotted a task's pages as not its own, and a landing that owed nothing was refused.

**Found and left?**
- The 449 log's lines already booked to T312 and T328 for T330's sessions stay as filed. `make events-refile` moves lines across features, and does not re-task them within one. These lines are inside 449's own log, and 449's two bundles are being landed from it now. Effect: `make where-time` credits those minutes to T312 and T328, not to T330. Not fixed here: it would mean rewriting a log another landing is reading, with a rule the re-file does not have. Filed as T168 (a `[perf]` task, the same measurement rule); lands before T22.

**Performance work?** yes, for the event-log half, which is `[perf]` for scheduling under the GM's measurement rule (2026-11-20, while T08 was being built: "I would also like for this kind of measurement task to be counted as a performance task for the purpose of scheduling and coming first ... even if the task itself doesn't improve performance"). That half exists so that `make where-time` credits each task its own minutes. The ledger half (`whose.rs`) is not performance work: it corrects a landing's refusal. No before-and-after timing is owed, because neither half makes any step faster.


### T168 (observed 2026-11-23, 451 T167's plan section: 449 T330's page sessions' lines sat under T312 and T328 in the 449 log, and `make events-refile` moves lines across features but never re-tasks one within a feature)

- **Approach**: `make events-refile RETASK="<session id> ..."` (`--retask <sid>`, repeatable) is a new mode of the existing refile command (`rust/gate/crates/measure/src/measure/event_log/refile/retask.rs`, called from `refile::cli_in`; the Makefile target passes `RETASK`).
  - Each named session's lines in its brief's feature log are set to the task its brief names. The feature and task are the shared reader's (`set_down_hooks::page_session_brief`, 451 T161), so the tool and the writer cannot disagree about what a brief names.
  - Idempotent: a line already on the brief's task is not rewritten, so a second run re-books 0. `DRY=1` counts and writes nothing. The log is rewritten through the refile's own `write_back`, which carries over a line a live hook appends meanwhile. A session the index does not list, or whose brief names no task, is reported and left.
- **Measured**, 2026-11-23, `make events-refile RETASK=... ` on the 449 log, backed up first to `.git/l7r-events/449-rust-codebase.jsonl.pre-t168` (lines of each session, by task):
  - 7e3b (t330a-checks, brief names T330): before T312 475, T328 778, T330 7; after T330 1260; 1253 re-booked.
  - 2647 (t330b-write, brief names T333): before T328 140, T333 3; after T333 143; 140 re-booked.
  - f1d2 (t330b-checks, brief names T333): before T328 215, T333 80; after T333 295; 215 re-booked.
  - A second run re-booked 0 for all three. The briefs of 2647 and f1d2 name T333 on their first line ("feature 449 T333 and the 0116 pointer"), not T330, so those lines book to T333.
  - `make where-time F=449 SINCE=2026-11-23T02:00 UNTIL=2026-11-23T04:00`: the agents table now has T330 at 180 agents, 76.2 agent minutes, and T333 at 78 agents, 6.8 minutes, measured 2026-11-23 (that command's second table). The first table's T330 row stays 0 because it books the main session's own wall time, not its subagents'.

### T168 Approach (checklist part A)

1. **The goal, in the world.** A page session's minutes are credited to the task its brief names, in the log as in the writer's new lines (T167).
2. **The constraints.** The log is append-mostly and live: the rewrite uses the refile's `write_back`. A re-run must change nothing. The brief reader is T161's, not a copy (451 T56's rule).
3. **Where each comes from.** O: the 449 log counts above. O: T167's plan section. O: the briefs' first lines.
4. **Do they describe the world here?** Yes, measured on the real log, dry run first.
5. **The order.** After T167, whose hook books new lines right. Before any landing that reads 449's per-task time.
6. **The exits.** Green: the new tests, the crate's suite, format, lint and cover (100% of the new file) clean, the real run's counts above, a second run re-booking 0, measured 2026-11-23 (the runs above). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The tests were written with the code, not before it, so no red run was recorded; each asserts the re-booked counts, the untouched other session and junk line, the second run's 0, the dry run's unchanged bytes, the unlisted and task-less sessions, and a missing log's exit 1. GREEN, measured 2026-11-23 (`make rust-test CRATE=rust/gate/crates/measure`): 215 passed; format, lint and cover clean.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome: T330's page-session minutes were credited to T312 and T328.

**Found and left?** none.

**Performance work?** yes, `[perf]` for the record it corrects (the time retro's per-task booking); it is not an engine-speed task, so it carries no checklist.


<!-- plan-archive: T169 to T169 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T170 to T170 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T175 to T164 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T175 to T175 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T174 to T177 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T174 to T174 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T173 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T173 Approach (checklist part A)

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


### T176 (observed 2026-11-23, 449's T351 bundle: the county's spec edit moved the engine key, which covers every pool sheet's spec, and re-owed the building-reviews of the four PASS sheets whose drawing and notes did not change - hayakawa, ochiba, ubame and the round trip)

- **Approach**: The task offered two routes: key a sheet's review to the engine code and that sheet's own inputs, or carry a verdict forward when the sheet's output is the one reviewed. Carrying was chosen. The push's review gate already carries a verdict whose recorded `content_key` (a hash of the sheet's svg and notes, written by `make review-verdict`) equals the sheet's key now (`review-gate.sh`, feature 374 batch 4), so only the three readers that held a verdict to the engine key alone re-owed it. Re-keying would need a new per-sheet engine key in the `tree` crate, in `make engine-key` and in every guard reader, and it would still re-owe a sheet when an engine edit leaves its drawing alone. The change is one predicate, `prereq::carried(v, now)`: a PASS or NEEDS-WORK whose `content_key` is non-empty and equal to the sheet's key now, which is asked only of a record that has one. It is wired into four places. `prereq.rs` `recorded` (FR-002's `reviews prereq recorded`) reads it. A new verb, `reviews prereq answered --clone C --unit U --key K` (exit 0 when answered), reads it. The checkpoint's `answered`, which holds `make tick`, reads it, keeping the owed units' sheets from `all_owed` so that no second owed lookup is made. `review-tree.sh`'s busy check, which holds `make verify`, asks the gate's `answered` about a unit whose verdict is at another key, and only while the tree's gate is green. `unit_content_key` and the checkpoint share `content_key_on`: the review tree's snapshot copy where it took the unit (451 T164), else the pool's sheet. What it does not see: a building-review also reads `docs/building-programs.md` and `docs/buildings.md`, so a change to those alone still carries the verdict, as the push's gate has since 374 batch 4.

| step | figure | what it says |
|---|---|---|
| before | 4 re-owed: `make verify`'s busy check listed the building-reviews of hayakawa, ochiba, ochiba-roundtrip-test and ubame (each PASS at engine key 41f26913b19c; the tree's key is 0e6a69cceff6), measured 2026-11-23, method: HEAD's busy-check program run read-only on the live record `.git/review-trees/7e08b45d82....json` and the clone's `.git/review-verdicts` | the engine key alone re-owes the unchanged sheets |
| after | 0 re-owed: the same record through the new busy check and the fixed gate. `reviews prereq answered --key 0e6a69cc...` exits 0 for all five building-reviews, because the four content keys equal their PASS records (hayakawa 15a07cf04410161b, ochiba b38324983db55c5f, round trip e3bc8d52368e1620, ubame bada673513715e41) and the county's verdict is at the tree's key, measured 2026-11-23, method: the same program and records | the four unchanged sheets answer. One glyph unit is carried too, glyph-check--cinnabar-workshop--ochiba-roundtrip-test (PASS at the earlier tree's key cef72b9db8d3, its sheet unchanged), as the push already reads it; the waiting glyph units go from 51 to 50 |

### T176 Approach (checklist part A)

1. **The goal, in the world.** One sheet's spec edit re-owes no review of a sheet whose drawing and notes did not change, at the tick, at `make verify` or at the push.
2. **The constraints.** FR-013 (the builders' loop faster). FR-002 (a review is recorded at its key). The push's carry (374 batch 4), which every reader now reads the same way. T164's snapshot copies.
3. **Where each comes from.** O: the T351 incident (2026-11-23, the tasks.md line). O: the table above.
4. **Do they describe the world here?** Yes: measured on the live review tree record of the bundle that filed it.
5. **The order.** After T164 (the snapshot copy it reads); independent of T170.
6. **The exits.** Green: `make crate-checks CRATE=rust/gate/crates/reviews` green, `tests/hooks/test-review-tree.sh` green, the after at 0. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make crate-checks CRATE=rust/gate/crates/reviews` green: 195 tests, lint, format and cover at 100%, measured 2026-11-23 (its own report). `tests/hooks/test-review-tree.sh` 24/24. RED FIRST, 2026-11-23, on the unfixed readers: `a_verdict_at_an_older_key_answers_while_its_sheet_hashes_as_reviewed` (checkpoint, held where it should answer) and `a_verdict_at_an_older_key_is_carried_while_its_sheet_hashes_as_reviewed` (prereq, `(1, 2)` where `(0, 0)` was expected) both failed, and `test-review-tree.sh` gave 22 passed and 2 failed. The after measure is 0 against 4 before.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: four reviews re-owed on unchanged sheets, each one a redispatch or an escape. That is a wrong outcome; no map changes.

**Found and left?**
- `tests/hooks/test-review-tree.sh` runs in no gate (observed 2026-11-23, method: grep of the Makefile, `scripts/` and `tests/hooks` for its name, no runner). `hooks-test`'s roster does not list `scripts/gates/review-tree.sh`, so a regression in `make verify`'s busy check or snapshot would land unseen. Not fixed here: the roster is in `hooks-test`, the target 451 T170 is editing now. Filed as T178; lands before T22.

**Performance work?** yes. It makes the builders' loop faster: four building-reviews, plus a glyph check, are no longer redispatched (or escaped) because another sheet's spec moved the engine key.

### T176 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In the reviews re-owed: each is a reviewer's dispatch on a sheet it already passed, or a `REVIEW_TREE_OK` escape and its record.
2. **Removes work, or only moves it?** It removes work: a carried verdict needs no dispatch. Each reader's added cost is one hash of a sheet's svg and notes, asked only of a verdict at another key.
3. **What do you expect it to save, and why?** On the T351 bundle, five dispatches (four building-reviews and one glyph check) whose sheets did not change, measured 2026-11-23 (the table above).
4. **How does the work grow with the settlement?** It does not: the hash grows with one sheet's files, not with a settlement's size.
5. **What did the before and after show, and under what conditions?** 4 re-owed before and 0 after, on the same live record, read-only, with the other builders running on 2026-11-23. This is evidence, not a pass.
6. **Did any map move, and does it still keep the research?** No map moved: the tooling only.


### T179 (observed 2026-11-23, 449 T377's builder: `round:spec-fidelity|plan:specs/449-rust-codebase#T377@3` - the feature's path where its directory name is the form - was ruled in 451's log and its accept recorded 18 of 451's owed plan blocks CLEAR; and T177's builder: the mirror's feature "" entry for `reversal:.../context_cap_hooks.rs`, ruled in the clone, held every builder's check dispatch for days)

- **Approach**: Three changes, one for each wrong outcome. (a) A trigger's feature is resolved once, in the arbiter crate's new `home.rs`. `named` reads the feature a trigger's own words name: a plan round's `<NNN-slug>#<Tnn>` (a directory under specs/ and one of its tasks), a spec round's `<NNN-slug>`, an ask's `ask:<NNN>-` (exactly one directory). It refuses, naming the form, a trigger whose feature or task does not resolve, and an ask with REVIEW=plan may name only tasks of its feature. `resolve` files a ruling in that feature, else in the feature its owed row was owed in, else in the active one, else refuses. `make arbiter-ask`, `make arbiter-bundle` and `make arbiter-ruled` (one trigger and a batch) ask it before writing anything. The old refusal's `plan:<feature dir>`, which misled the 449 builder, now reads `plan:<NNN-slug>#<Tnn>@<n>`. (b) The plan crate's `accept_scope` reads a task with no section as the whole plan's only where every named task is a task of this feature (`plan::feature_task`: a box line of its tasks.md or tasks-done.md). T377, a task of 449, now clears nothing in 451. A task id is read in either case (`plan::task_ids`, which the ask's filing check reads too): `ask:449-t383-plan-round3`'s accept read no task in "t383" and was read as the whole plan's, marking 39 other tasks' blocks CLEAR and dropping 264 archived rows of 449's plan-review.json (observed 2026-11-23, restored by hand; the round arbiter's fix, filed in 449's log); the after row's replay, run again reading ids in either case (2026-11-23), still refuses the malformed trigger alone and reads that ask as T383. DECISION, a kept earlier ruling: T92's whole-plan reading of a feature's own task with no section (its plan-stage review) stays as T92 ruled it. (c) A ruling clears its trigger from two owed files: the ruling clone's, and the mirror's where the mirror's entry is this feature's or feature "" (`home::pop_everywhere`; another feature's entry of the same id stays). A sibling clone's own owed file is not reached (Found and left, below). A tripwire is filed under a feature or not at all (the shared crate's `try_trip_row`): the root's active feature, the one its words name, or, for a reversal, the feature the event log filed the Edit under (`trip_as(..., filed)`). Where none resolves it is refused and nothing is filed. `asked_feature` reads a spec round's feature too, so its readers read the log where its ruling is filed.

| step | figure | what it says |
|---|---|---|
| before | 18 of 451's plan blocks recorded CLEAR by one accept on 449's T377 (repaired by hand); the mirror's feature "" entry holding every check dispatch from 2026-11-20 to 2026-11-23 (removed by hand); on HEAD's code the arbiter crate's new tests 34 passed, 5 failed - the malformed trigger ruled and its row written, a ruling owed in 449 filed in the active feature, the mirror's entry left, the orphan ask filed, the bundle taking the path form, measured 2026-11-23, method: a detached worktree at HEAD with the new tests copied in (public API only), `make rust-test CRATE=rust/gate/crates/arbiter` | a trigger's words are not read for its feature, and a ruling clears one owed file of two |
| after | 0 blocks cleared outside the trigger's task; the same trigger refused at ask, bundle and ruling, naming the form; a ruling pops the mirror's entry; a trip with no feature refused. Replay of every trigger in specs/*/arbiter.jsonl through `named`'s rules: 693 read, 692 accepted, 1 refused - the malformed one (29 of them REVIEW=plan asks, none refused), measured 2026-11-23, method: a python3 copy of `named`'s patterns over the clone's tree | only the malformed form is refused; no ruling in the record would have been |

### T179 Approach (checklist part A)

1. **The goal, in the world.** A ruling lands in the feature its trigger names and clears only that task's plan blocks; a ruled trigger is cleared from the ruling clone's owed file and the mirror's matching entry, so it holds no builder through either (a sibling clone's own copy stays: Found and left).
2. **The constraints.** Feature 375's arbiter (one binding ruling per trigger, append-only logs). Feature 409 (a REVIEW=plan accept stands as the plan review's verdict). T92 (an accept names its task's blocks and verdict). T38 (`_in` readers take their environment).
3. **Where each comes from.** O: the two incidents (the tasks.md line, 2026-11-23). O: the before/after table above.
4. **Do they describe the world here?** Yes: the incident rows are on the live record, and the replay read all 693 triggers, measured 2026-11-23 (a python3 copy of `named`'s patterns over the clone's tree).
5. **The order.** Independent of T174 and T182; T182 builds on the same arbiter crate and lands beside it.
6. **The exits.** Green: `make crate-checks` over the plan, arbiter, shared and guard crates green, the replay refusing the malformed trigger alone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `make crate-checks` over the plan, arbiter, shared, reviews, task, land and guard crates green - tests (plan 175, arbiter 41, shared 461, reviews 197, task 87, land 94, guard 493), lint, format and cover at 100% - measured 2026-11-23 (its own reports). RED FIRST, 2026-11-23: the plan crate 173 passed, 1 failed (`whole: true` on T377); the shared crate 459 passed, 2 failed (the spec round's feature, the orphan trip filed); the arbiter crate on HEAD's code 34 passed, 5 failed (the before row); the id in lowercase, on the code before `task_ids`, the plan crate 174 passed, 1 failed (`a_task_named_in_lowercase_is_that_task`, the round arbiter's fix's test) and the arbiter crate 40 passed, 1 failed (`999-t377-q` filed), `make rust-test CRATE=`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: 18 plan blocks recorded CLEAR that no review read, and a ruled trigger refusing dispatches for days. Both are wrong outcomes; no map changes.

**Found and left?**
- A round tripwire hit in a root with no active feature and no `SPECIFY_FEATURE` (the mirror, never a workspace) is now refused at filing, where it was filed with feature "". The round guard's refusal still names `make arbiter-bundle`, which then says no feature resolves. No wrong outcome: such a root has no log to rule in, and every builder's clone names its feature.
- A trigger owed in a sibling clone's own owed file stays there when another clone rules it: `pop_everywhere` clears the ruling clone's file and the mirror's. Not observed: no wrong outcome seen in any incident, so nothing is filed.

**Performance work?** no - a wrong outcome of the arbiter's record; the time it cost (dispatches refused for days) goes with it.

<!-- plan-archive: T182 to T177 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T178 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T178 Approach (checklist part A)

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


### T180 (observed 2026-11-23, 449's T351 and T358 bundles landing alone: land-alone's commit 832cedd0fc held 449 T377's filled plan section and its BLOCKED plan-review verdict, though the landing's T= named 21 tasks and not T377, and 7 of the 21 ticks were then refused on T377's heading block, measured 2026-11-23 from `git show --stat 832cedd0fc` and `/tmp/land351/land1.log`)

- **Approach**: Two defects, both fixed. (1) `scripts/land-alone.sh`'s step 2 (`stage`) widened the landing's tasks by every `Filed as T<n>` in their own sections, then took plan.md's sections, tasks.md's lines and plan-review.json's verdicts for the widened set. T351's section files T377, so T377's builder's uncommitted section and verdict went into the commit (its subject lists 9 tasks the T= did not: T371-T373, T377, T380, T386, T389-T391). Now a filed task lands only its tasks.md line, which the deferral rule needs open in the landed tree (451 T17). Its plan section and verdict are never taken, and the subject names the filed tasks apart. (2) The tick's scope (`rust/gate/crates/plan/src/plan/status.rs`, `in_scope`, 451 T84) is right to judge the asked task, the tasks ticked before it and the blocks outside every task's section, but its notion of ownership leaked. `plan_text`'s sections make a task with no heading of its own the owner of every heading that names it. T377's filled heading names T351 (`ask:glyph-occasions-emit-449-T351`). Once T368's tick archived T351's section, T351's "section" was T377's heading block, and T351, ticked, is in every later tick's scope. So T358, T360, T361, T362, T369, T370 and T379 were refused on `### T377 (the round arbiter's ...`: the heading block alone, never T377's Approach block, which the mention's span does not reach. Now a block inside a task's own section answers only for its own tasks, and a heading that only names a task owns a block only where no own section does. The fix is in the plan crate, not in `plan_text` (`rust/guard/shared`, 451 T170's files).

| step | figure | what it says |
|---|---|---|
| before | 2 files staged by the old `stage` on the clone's working 449 files, T377's section and verdict among them (plan.md +21/-17 in T377's section, plan-review.json +164 of T377's verdict), measured 2026-11-23 (HEAD's script's `PYLIB` run as `stage` with the landing's 21 tasks in a `--shared` scratch clone at bf5f252ca3 (the commit before 832cedd0fc) with the clone's working plan.md, tasks.md and plan-review.json copied in, `/tmp/t180/replay-result.txt`) |
| prediction | 0 files staged: the 21 tasks' own pieces were already committed in 085f4598c3, so only T377's differed, observed 2026-11-23, method: `git show --stat 085f4598c3` and the before replay's diff |
| after | 0 files staged, HEAD unchanged at bf5f252ca3, measured 2026-11-23 (the same replay with the fixed script's `PYLIB`) |

### T180 Approach (checklist part A)

1. **The goal, in the world.** A landing alone commits only the plan sections and verdicts of the tasks its T= names, and a tick is refused only on its own task's blocks, the ticked tasks' and the blocks outside every task's section.
2. **The constraints.** 451 T101 (a task's own sections committed apart). 451 T84 (a tick answers for its own section, the ticked ones and the shared blocks). 451 T17 (a deferral's filed task open in tasks.md). FR-013 (the landings faster).
3. **Where each comes from.** O: 832cedd0fc and `/tmp/land351/land1.log` (2026-11-23). O: the replay in the table above.
4. **Do they describe the world here?** Yes. The replay ran on the clone's own working files of the feature that landed, and the tick's refusal names the block the mention's span holds.
5. **The order.** Independent of T170, T175 and 449 T377. It lands before the 449 bundles' next landing alone.
6. **The exits.** Green: `make crate-checks CRATE="rust/gate/crates/land rust/gate/crates/plan"` green and the replay at 0. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, 2026-11-23: `land::alone::tests::filed::a_filed_task_lands_its_line_but_never_its_builder_s_section_or_verdict` failed on HEAD's script, with T3's section in the landed plan.md (`/tmp/t180/red-land.saved.log`, `make rust-test CRATE=rust/gate/crates/land`, 89 passed, 1 failed). `plan::tests::mention::a_ticked_task_named_in_an_open_task_s_heading_owns_none_of_its_section` failed on HEAD's `in_scope`, with T05's tick refused on `## T06 (filed by T04's review) the wells`, the incident's refusal in small (`/tmp/t180/red-plan.saved.log`, 172 passed, 1 failed). After the fix, `make crate-checks CRATE="rust/gate/crates/land rust/gate/crates/plan"` was green: land 90 tests, plan 173, lint, format and cover clean, measured 2026-11-23 (`/tmp/t180/green.log`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: a landing carried another builder's unreviewed decisions and then refused its own ticks on them, and needed an orchestrator's hand to undo. That is a wrong outcome; no map changes.

**Found and left?**
- The tick's mention leak (defect 2 above): fixed here, observed 2026-11-23, method: the tick's refusal read against `section_spans`' rule for a task with no heading of its own, and every `in_scope` owner path covered by the new test.

**Performance work?** yes. It makes the landings faster: a landing alone no longer commits another builder's open section and stops on it, which cost the 449 landing a 499 s run, an undo and a held lander, measured 2026-11-23 (`/tmp/land351/land1.log`, its `exited 2 (499.0 s)` line).

### T180 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In a landing that commits another task's unreviewed block: its whole gate (499 s, measured 2026-11-23 (`/tmp/land351/land1.log`)), the refused ticks, and the orchestrator's undo or a wait on the other task's CLEAR.
2. **Removes work, or only moves it?** It removes work. Nothing of another task's is committed, and no tick waits on another task's review.
3. **What do you expect it to save, and why?** One failed landing each time a landing task's section files a task whose builder has started, as T351's did. On 2026-11-23 that was one landing's 499 s and its rerun, measured 2026-11-23 (`/tmp/land351/land1.log`).
4. **How does the work grow with the settlement?** It does not: the tooling only.
5. **What did the before and after show, and under what conditions?** 2 files staged before and 0 after, measured 2026-11-23 (`/tmp/t180/replay-result.txt`), on the same working files in a scratch clone, read-only to the live clone. This is evidence, not a pass.
6. **Did any map move, and does it still keep the research?** No map moved: the tooling only.


<!-- plan-archive: T183 to T183 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
### T181 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T181 Approach (checklist part A)

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




<!-- plan-archive: T184 to T184 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T196 to T184 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T196 to T196 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->

<!-- plan-archive: T193 to T184 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T193 to T193 moved to plan-done.md, 2026-11-23 (feature 375 FR-044) -->
<!-- plan-archive: T195 to T195 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T197 to T184 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T197 to T197 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T198 to T200 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T201 to T193 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T202 to T198 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T202 to T202 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T192 to T187 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T192 to T192 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T218 to T218 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T206 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T206 Approach (checklist part A)

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



### T208 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T208 Approach (checklist part A)

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


<!-- plan-archive: T209 to T209 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T210 to T210 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T211 to T192 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T211 to T211 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T212 to T212 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T213 (the cascade test's T400 miss: relabeled_only passes a MISLABELED claim's rewritten account)

- **Approach**: `relabeled_only` (rust/gate/crates/claims/src/claims/index.rs) passed any claim whose row read `verdict: MISLABELED` once the unit's body was unchanged (385 T23 D45), so a comment edit could restate the account freely. Its MISLABELED arm now passes only a relabel, the account unchanged: the stored claim's account equal to the claim's now, word for word (`account_of`: after the first ` - `, after the backing's first `: `, as `parse_claim` splits it), the backing - its class, or the question it cites - free to change; a row storing no claim is no relabel. `relabel_answered` (the push's carry, `carry.rs`) reads it, so a restated account no longer answers a MISLABELED verdict there either. Labels still cascade mechanically (the GM, the convergence talk): a relabel alone owes nothing, and T204's item naming is untouched (its own arms, before this one). Two fixtures asserted the defect - an account rewrite passing as a relabel - and are restated as true relabels: the stored claim each row read, an account rewrite before, now the claim's own account under another class (`index::tests::a_relabel_alone_owes_nothing_and_answers_its_mislabel` stores `gap - CONVENTION: relabeled` where it stored `gap - NONE: before`; `carry::more`'s `introduced` stores `reach - CONVENTION: within GAP, relabeled` where it stored `before`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a MISLABELED claim's account is checked | `index::tests::a_mislabeled_claim_s_restated_account_is_owed` (red on HEAD: the restated account owed nothing and answered the verdict, `/tmp/t213-red.log`) | none: record tooling | none | n/a |

### T213 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A claim marked MISLABELED that is relabeled as prescribed owes nothing; one whose account is restated is sent to impl-drift like any other changed claim, so a restated account is never unchecked.
2. **The constraints.** The task line; the GM 2026-11-24 ("Yes let's fix all 6 of those before we resume."); the convergence talk ("Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?" - labels cascade mechanically); T204 (naming an item owes nothing); the coordinator's brief (only a change of the label or citation alone passes; red first; 100% coverage; only this crate's files).
3. **Where each comes from.** G: the GM's words above. O: the cascade test (cascade-test-2.md, the T400 miss, line 68) and `claims-owed` before and after. R: none, tooling.
4. **Do they describe the world here?** Yes: `claims owed` over this clone's committed tree (09f4bfc0cb) with the unfixed and the fixed binary, 2026-11-24.
5. **The order.** After T204; beside T210 and T211.
6. **The exits.** Green: the T400 claim owed, the claims it newly owes read. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** 2026-11-24, `claims owed` at 09f4bfc0cb: unfixed, no claim owed; fixed, 8 owed `code changed`, each a MISLABELED row (17 in the index) whose account was restated since its check: `emit.rs::grounds#office front, residence rear` (the T400 miss), `emit.rs::shed_posts#the open shed on six posts`, `emit.rs::stables#grooms' room open to the passage`, `fixtures.rs::BOARD#the gate board drawn`, `audit/roads.rs::DESTINATION_KINDS#a way walked to a well or clearing`, `caption_place/search.rs::MEMBERS_TRIED#the parts tried`, `driver/plan.rs::KNOBS#the knobs' tables`, `seat/exit.rs::BEARINGS#the straight runs`. All 8 are the miss this task names: unchecked restatements, owed their impl-drift once T213 lands.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The defect's visible effect: 8 claims' accounts, the T400 one among them, were restated with no check that the code does what they now say.

**Found and left?** none - the 8 claims it owes are this task's own effect, owed impl-drift at its landing (the landing's claims round), not a deferral.

**Performance work?** no: it adds checks the defect skipped; filed `[perf]` with the cascade test's six.


<!-- plan-archive: T214 to T214 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->

<!-- plan-archive: T215 to T210 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T215 to T215 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T216 to T216 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->

<!-- plan-archive: T217 to T217 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->

<!-- plan-archive: T203 to T200 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T219 to T219 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T220 to T33 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T221 to T221 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T222 to T222 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
### T223 (the round arbiter's process-fault, `ask:mixed-build-241-claims`, 2026-11-24: a green landing of 449 T423 T424 T418 T422 was refused at the push because T197's rule owed its unchanged doc claims a full impl-drift, the only route offered)

- **Approach**: A landing alone reads each row a mixed build's triage answered at the answer before it, and owes the claim what its own build finds since. The refused landing took 920 s and listed 241 claims, measured 2026-11-24 (`/home/agent/.claude/jobs/c6fd72d1/tmp/arbiter-mixed-build.md`).
  - **Why the row cannot be triaged again as it stands.** A triage clear overwrites the row's `research`, `pages`, `section`, `code` and `core` with the tree it judged. The mixed row holds no "before", so a re-triage of it sees no change.
  - **Where the before is.** In the repository: `dev/claims-index.json`'s own history holds the row as the last clean build left it. `rust/gate/crates/claims/src/claims/landing.rs` (`read`) walks the index's history from HEAD as far as `checked_at` does, and takes the newest row whose build is not mixed. That is 60 commits, observed 2026-11-24, method: `WALK` in `landing.rs`.
  - **What is withdrawn.** Only the fields a triage writes: `research`, `pages`, `section`, `code`, `core`, `reads`, `triaged`, `cleared`, `triage`, `build`. The verdict, note, date, claim and rests stay.
  - **What each mixed answer owes at a landing.**
    - A tool's clear (`cleared`) or an agent's (`triaged`): what `claims-owed`'s ordinary rules find between the answer before and the tree. That is nothing where the tree is back where that answer judged it; a triage where a section, page or code moved; a full check where the change is one no triage judges (a rewritten claim, a lost rest).
    - A mixed answer with no clean answer in the walk, or whose claim has no row in a commit of the walk: impl-drift, the files named. It fails closed.
    - A full impl-drift verdict: never re-owed. `reply.rs`'s `verdict_row` builds a fresh row with no `build`, by T197's design, and the ruling keeps the 14 edited claims' verdicts: the judgment is the agent's reading, not the gate's code.
    - The one exception fails closed: a verdict recorded and then cleared again by a mixed build before the index was next committed. The row carries the build, the walk's row is the one before that verdict, and the claim is owed in full. That is the barracks row below, 1 of the 242, observed 2026-11-24, method: each mixed row's verdict, note and claim compared with its row in the walk.
  - **The route.** The landing's first pass writes the withdrawal into the index it commits (`claims rekey`), so the claims it leaves owed are owed in any run after it. Before that commit, `L7R_LAND_ALONE=1 make claims-triage` writes the withdrawal itself, clears again what the tool can, and bundles the rest for the `claims-triage` agent; what the agent names TOUCHES goes on to impl-drift. No command is added (`ask:t197-rejudge-verb` stands). `claims-owed` and the push's gate each say the count, the files and that command.
  - **Outside a landing** the index is read as it stands.
  - **What is retained for the re-triage, measured 2026-11-24 on the clone's HEAD `fd7aa5d6dd`** (a detached worktree, `claims triage-replay`, nothing recorded):
    - the row before: in the index's history, for all 242 mixed rows;
    - the page and section snapshots: `dev/claims-pages.json` is never pruned, and all 6 base sections were in it; the base commit's store is read beside it all the same;
    - the section words: `dev/claims-section-words.jsonl` is pruned to today's index, and 8 of the 100 base blocks were gone from it. All 8 were found in the documents' history, and none was forced. `section_words` now reads the kept words' own history too, for words that reached no commit of their document;
    - a page's kept text (`.git/claims-page-blobs.json`) is the clone's own, as before; a page's history holds it otherwise.

| the 235 mixed doc rows (docs/building-programs.md 143, docs/buildings.md 92) | count |
|---|---|
| owe nothing: the section is back where the last clean verdict judged it | 73 |
| cleared again by the tool | 147 |
| in the agent's bundle | 14 |
| owe impl-drift (`code changed`: the barracks claim, rewritten) | 1 |

  The task line's 241 was 143 and 98, and 6 rows of docs/buildings.md were recorded again since, observed 2026-11-24, method: the index's rows carrying a mixed `build` at `fd7aa5d6dd`. 7 more mixed rows are `rust/phases/src/field/dry.rs`'s, all in the agent's bundle (21 sent in all). Before: 242 owed impl-drift.

### T223 Approach (checklist part A)

1. **The goal, in the world.** A landing judges a mixed build's clears again with its own build, and a claim nothing changed for owes nothing.
2. **The constraints.**
   - T197: a landing alone never trusts an answer judged with code that is not its own.
   - `ask:t197-rejudge-verb`: no withdrawal verb.
   - T210, T215: a section's removed words are shown from the kept words, never forced where they can be found.
   - T196: a moved pointer's blocks are read as moved; the ordinary owed rules run unchanged on the withdrawn row.
   - The request's convergence rule: only a claim-changing edit re-owes a check.
3. **Where each comes from.**
   - O: the measurement, `/home/agent/.claude/jobs/c6fd72d1/tmp/arbiter-mixed-build.md`.
   - R: the round arbiter, `ask:mixed-build-241-claims`, process-fault, its `tooling_fix`.
4. **Do they describe the world here?** Yes: the replay above, on the rows that refused the landing.
5. **The order.** Before the landing of 449 T423 T424 T418 T422 is run again. The coordinating session commits this, then re-judges.
6. **The exits.** Green: `make closing-checks T=T223 F=451`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, 2026-11-24: the three tests of `commands/tests/landing.rs` failed on HEAD's code in a detached worktree (`/tmp/t223/red-first.log`, 191 passed, 3 failed: a mixed clear listed with T197's full reason, not `section triage`). After: 196 passed (`/tmp/t223/test5.log`), with two more tests: the kept words' history, and the page-move clear's stamp.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: the gate answered wrongly. It owed a full check to claims whose text, pages and code stood as last judged, and refused a green landing on them. No map changes.

**Found and left?**
- A withdrawn row that owed nothing kept its mixed stamp in the index, since only a landing's triage wrote the withdrawal and nothing prompted one. Effect: past the walk's reach the unchanged claim would owe a full check. Fixed here: `claims rekey`, which a landing's first pass runs and whose index it commits (`land/cheap.rs`), writes the withdrawal in a landing alone. A deferral of it was ruled NOT LEGITIMATE by the plan delta's MODE 4, observed 2026-11-24, method: the verdict recorded in `plan-review.json`; the task filed for it was taken out before any commit.
- The page-move clear (`clear_page_moves`, feature 432) never stamped its build: a mixed build's clear went unmarked, and a clean build's clear of a row already marked stayed marked. Effect: the landing's check answers wrongly either way. Fixed here (`stamp_build`).

**Performance work?** no: it corrects what a landing owes; the landing's saved impl-drift rounds are its effect, not a speed change of any tool.



<!-- plan-archive: T224 to T197 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->
<!-- plan-archive: T15 to T225 moved to plan-done.md, 2026-11-24 (feature 375 FR-044) -->

<!-- plan-archive: T226 to T226 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
### T227 (page session P7's cascade, 2026-11-24: record-format was dispatched on 0097 four times across features and the counter held 0 rounds; 2026-11-25: modal-form ran three rounds on sheet/barracks in four minutes and `make arbiter-bundle BATCH=1` said no round trigger was owed)

- **Approach**: The round cap (`rounds::cap_refusal`, `ROUND_CAP` 2) was sound. Two things kept it from being reached, and one more kept its ruling from being read.
  - **Cause 1, the feature reset.** `handle::handle_locked` replaced the whole check state with `{feature, dispatches}` whenever the active feature changed. That wiped every unit's `rounds`, `seen`, `own_edits`, `notes_read`, `rebased` and `round_batch`. Observed 2026-11-25, method: the source, and `.git/checks-open.json` of the coordinating clone. Its `feature` was 451 and it held no `record-format|q:0097` count, although its `dispatches` kept 13 record-format rows on q:0097, 4 of them dated 2026-11-24.
  - **Cause 2, a hand fix read as a first look.** `first_look` (374 wave 120, the arbiter on 0190) let a round go uncounted when its unread sentences were none of the check's own EDITs. Its stated rule is "text OTHER checks' edits added", but it tested the opposite: anything not its own. It also asked whether the own-EDIT text contained the whole sentence, and an EDIT that replaces a span inside a sentence never does. Observed 2026-11-25, method: the barracks rows of the same state (dispatch toolu_01QzUrB5 `counted` [barracks]; toolu_01HDWmSu `counted` [marsh] only; toolu_01TWD7L7 `counted` []), the three kept replies (round 1's EDIT "and a gate rowhouse was tiled; ...", rounds 2 and 3 with `EDIT: none`), and `git diff 32d0d88c55 6557ee05b7` of `sheet/barracks.md` (the EDIT applied inside a longer sentence, a Guesses bullet added and then taken out by hand). Each of rounds 2 and 3 was read as a first look, so `rounds` stayed at 1 and no third round was held.
  - **The fix: what survives a feature change.** Nothing is wiped. Every key of the state is keyed by unit or subject, not by feature, so a count follows its unit. A unit's HOME is the feature its count began in (`round_home`, written when its first round is counted, and for a unit counted before this change, the state's old `feature` at the switch). Its triggers are filed under its home (`arbiter::trip_under`), and its `continue` and `accept` are read from there (`arbiter::rulings_of`, `continues_of`, `closed_of`), as 451 T240 reads a plan round's rulings from its trigger's feature. `arbiter-ruled` already files a ruling where the owed row names it (`home.rs`). An owed record round (`round:<record check>|q:NNNN@N` or `|modal:...@N`) is every feature's to hold and batch (`arbiter::record_round` in `mine`). So `make arbiter-bundle BATCH=1` lists it under any feature, and `blocking` holds only that unit's dispatch. Why a home and not every feature's log: counts restarted with each feature, so the same trigger is ruled in two features 10 times today, for example `round:record-format|q:0047@3`. Reading every log would let an old `continue` lift a new cap, and would make a new trigger "already ruled".
  - **The fix: what counts as a first look.** A round is a first look only when every unread sentence carries another check's EDIT words on that subject and none carries its own. Matching is sentence by sentence, an EDIT's sentence inside the page's or the page's inside it. Text the session wrote between rounds, a finding fixed by hand, is the fix loop and is counted.
  - **The gate's readers.** The arbiter bundle's `counted` returned 0 unless the state's feature was the active one. It now reads the count whatever feature is active. Its counter section and the rounds line no longer say "in this feature".
  - **The refusal** reads "round N of `<check>` on <subject> passes its cap of C - ...". "in this feature" is cut, because it is no longer true.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| no state wiped on a feature change; a unit's home filed, ruled and batched | `a_record_round_follows_its_unit_across_features` (handle) red on HEAD: the third round under the next feature let through (""); `a_new_feature_keeps_the_counts_their_home_and_the_dispatches` restated; arbiter `a_held_gate_and_a_batch_are_told_apart`'s record-round case | n/a: tooling | none | n/a |
| a first look only for other checks' EDIT text | `a_session_s_own_fixes_between_rounds_count_the_next_round` (rounds) red on HEAD: round 2 `counted` [] where [barracks] was wanted; `first_looks_and_fresh_readings_are_no_repeat`'s hand-written case | n/a: tooling | none | n/a |
| the arbiter bundle's count read under any feature | `the_round_counters` restated (sections) | n/a: tooling | none | n/a |

### T227 Approach (checklist part A)

1. **The goal, in the world.** A record check's third round on one page or pop-up is refused until the round arbiter rules, whatever feature is active and whether the session fixed the last round's findings by EDIT or by hand. The refusal names `make arbiter-bundle`, and the ruling, filed in the unit's home feature, lifts the hold under any feature.
2. **The constraints.** The root CLAUDE.md's tripwire: "a check's third round on one subject" owes the round arbiter's ruling. 375 FR-010 and FR-011 (the cap, one ruling per trigger). 374 wave 120's first-look rule, for text other checks' EDITs added. The batch rule from 2026-10-12 (c5db336fd3: "count afresh only in a later batch, never on a batch's own edits"), unchanged here. 451 T240's pattern: rulings are read where the trigger is filed.
3. **Where each comes from.** G: the CLAUDE.md tripwire line. R: the 0190 ruling (`specs/374-match-the-research-continued/arbiter.jsonl`, `round:quote-check|q:0190@3`). O: the coordinating clone's check state, its kept replies and the barracks diff, 2026-11-25.
4. **Do they describe the world here?** Yes, measured 2026-11-25. The two red tests replay each case's sequence through the real `dispatch`/`launched`/`returned` and, for case 1, through the hook's `handle`: rounds under 999-x, then the active feature moved to 998-y, measured 2026-11-25 (`make rust-test CRATE=rust/guard/shared`). Case 2 replays the barracks texts as the coordinating clone's state recorded them, measured 2026-11-25 (the state's rows, kept replies and `git diff 32d0d88c55 6557ee05b7`): round 1's EDIT applied inside its sentence, a bullet added by hand, then taken out.
5. **The order.** No dependency. T240 fixed the plan-review counter the same way. T229 is in parallel and touches other files.
6. **The exits.** Green: `make closing-checks T=T227 F=451`. Red: what failed is recorded and the task set down, and a claim that it cannot be done is ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, measured 2026-11-25 (`make rust-test CRATE=rust/guard/shared` on HEAD's code with the two new tests): 483 passed, 2 failed. Case 1 failed with "the third round is held under the next feature: " and an empty refusal. Case 2 failed with "the round after the session's own fixes is a repeat", `left: []`. After the fix both pass, and so do both crates' suites: `make crate-checks CRATE="rust/guard/shared rust/gate/crates/arbiter"` gave 485 and 41 passed, with lint and format clean. FIRES-PROOF, measured 2026-11-25. Each fix was disabled in turn with the rest kept, and the shared crate was run each time. (a) `first_look` with its other-checks condition made always true: 483 passed and 2 failed, the barracks replay and `first_looks_and_fresh_readings_are_no_repeat`. (b) The old feature wipe put back in `handle_locked`: 2 failed, the cross-feature replay and `a_new_feature_keeps_...`. (c) The cap's rulings read from the active feature, not the home: 1 failed, the cross-feature replay at "the continue ruled in its home feature lifts the hold". Logs are in the session scratchpad (`t227-red-head.log`, `t227-fires1.log` to `t227-fires3.log`).
10. **Before moving a constant.** n/a: `ROUND_CAP` stays 2.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: the tripwire the root CLAUDE.md requires did not fire. Third and later rounds ran without the arbiter's ruling (record-format on 0097, modal-form on barracks). No map changes.

**Found and left?**
- The arbiter bundle counted no rounds of a unit unless the state's feature was the active one (`arbiter/bundle.rs` `counted`). Effect: `misnumbered` told the session to ask about `@1` for a unit at round 3. Fixed here.
- The real 2026-11-24 record-format rounds on 0097 crossed two `origin/main` batches (05:15-05:25Z and 17:15-17:23Z, with ten moves between). The next round would have followed a move at 18:08Z (method: the clone's `origin/main` reflog against the dispatch times). The batch rule (`new_cause`) restarts the count on any move of `origin/main`. Effect: with several sessions landing, a third round in one batch is rare, so case 1's own next round would still not have been held. Not fixed here: it restates a ruled rule (c5db336fd3), needs a measured test of what counts as the subject moving, and its fix differs from this one. Filed as T248; lands before T22.
- The record bundle's "Earlier rounds" section (`bundle/earlier.rs`, feature 393) still lists only this feature's rounds, its rulings read from the active feature. Effect: none on the cap. It is what a reviewer is shown, and feature 393's contract words it "in this feature". Not a defect of the counter, so not filed.

**Performance work?** no: it holds a review round. Only a capped repeat reads one extra `arbiter.jsonl`.


<!-- plan-archive: T228 to T228 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T229 to T219 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
### T230 (449 T224's builder, 2026-11-24, and 449 T433's, 2026-11-25: `make closing-checks T=<task>` printed "BLOCKED: every error static printed is in another task's files - ()" on errors in the task's own files; T239 is the same fault filed again and ticks with this task)

- **Approach**: The cause is the attribution's awk in `scripts/gates/closing-checks.sh` (`theirs`), not the parsing of the error lines.
  - **What the lines say.** Every error line naming a file in the clone's red static logs is in one of two forms, both parsed already. One is clippy's `-->` at two or three spaces, its path from `rust/` (`  --> phases/src/driver/check.rs:84:18`, T433's run 0859Z). The other is rustfmt's `Diff in <absolute path>:<line>:` (T431's run 0836Z, T433's 0900Z). Eight of the 25 logs held such lines, observed 2026-11-25, method: `grep -E -- '-->|Diff in'` over `.git/closing-checks/*/static.log`. Those logs are pruned after `CLOSING_CHECKS_KEEP_MIN` (a GUESS knob, 360 minutes, T72), so the durable evidence is the suite's cases, which carry those lines verbatim.
  - **Each form static prints, from the source.** `make static`'s recipe stops at its first red step, so one run's lines come from one step. Every red step was enumerated, observed 2026-11-25, method: the `static` recipe in `Makefile` and the `writeln!`s and `Ran`s of `rust/gate/crates/rustc/src/rustc.rs`. `lint` names its files by `-->`, and `format` by `Diff in`. `cover` prints `<path> - lines no test reaches` (parsed since T95), and a failing test's `thread '<name>' panicked at <path>:<line>:<col>:` (Rust 1.73's form; not parsed before). `dead` prints `  pub fn <name>: nothing in Rust calls it`, which names no file. The tree-wide text checks run before them and name no crate's file.
  - **Why the list came out empty.** `theirs` read another task's files with `NR == FNR`. In T433's two runs the clone held no other task's file: `others` was empty in 24 of the clone's 25 runs, observed 2026-11-25, method: `wc -c` of each run's `others`. T224's run, 2026-11-24, is pruned. Its cause is inferred from the same printed line. With an empty first file, `NR == FNR` holds on stdin too, so each error path was stored as one of another task's files and none was printed. No line began with `-` (the caller's mark), so "every error is another task's" held vacuously, and the one empty line printed as ` ()`. Reproduced in mawk, the clone's awk.
  - **The fix.** `theirs` tells the list apart by its file name (`FILENAME == o`) and skips an empty line. `blocked` returns on an empty attribution, never BLOCKED. A red whose lines name no file now says so: "no error line static printed names a file - none could be attributed, so all are counted as yours", followed by its first 8 failure lines, an APART crate's left out. This is said for static alone: hooks-test and quick stay counted whole (T86), so their reds carry no note. The BLOCKED line already names each file and its task once the attribution is read.
  - **The arrow.** A path is read only from a line that OPENS with the arrow (`^ *-->`) or with `Diff in`. Before, an arrow anywhere in a line counted, so a source line quoted under an error (`5 | let s = "a --> mine/src/lib.rs";`) was read as a path.
  - **The failing test.** The panic line's path is read as an error's. Without it, a cover red was BLOCKED whenever another task's file was named and the caller's own test failed: "nothing of yours was judged there", the same vacuous answer one level up.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| `theirs` by file name, `blocked` on an empty attribution | the suite's two empty-`others` cases red on HEAD's script | n/a: tooling | none | n/a |
| the arrow opening its line | the quoted-source case red on HEAD's script | n/a: tooling | none | n/a |
| the panic line read | the mixed cover case and the panic-alone case red on HEAD's script | n/a: tooling | none | n/a |
| the unattributed note, static's counted lines | the no-file case and the APART-lines case red on HEAD's script | n/a: tooling | none | n/a |

### T230 Approach (checklist part A)

1. **The goal, in the world.** A builder whose closing run is red on its own files is told it is red on its own files. BLOCKED appears only when every named file is another task's, and it names those files.
2. **The constraints.** 451 T86: another task's red is reported apart, and a miss costs a saving, never a wrong verdict. 451 T95: cover lines are attributed like the errors. The BLOCKED red stays red.
3. **Where each comes from.** O: the two builders' runs, the clone's 25 static logs and static's own source, 2026-11-25. R: T86's header in `closing-checks.sh`: a file no line names is the caller's.
4. **Do they describe the world here?** Yes. The suite's new cases use those runs' own lines, copied from `.git/closing-checks/` logs.
5. **The order.** No dependency. It lands alone. T239 ticks with it.
6. **The exits.** Green: `make closing-checks T=T230 F=451`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, measured 2026-11-25 (the suite run on HEAD's script and on the fix): the suite `tests/hooks/test-closing-checks.sh` gained ten cases. Run against HEAD's `closing-checks.sh`, it gave 53 passed and 7 failed. The two empty-`others` cases each printed "BLOCKED ... -  ()". The quoted-source, unattributed, mixed-cover, panic-alone and APART-lines cases also failed. The tenth case, a red hooks-test given no note, pins what HEAD already did. After the fix: 60 passed, 0 failed. Both runs' logs are kept in the session's scratchpad (`t230/red2.log`, `t230/green2.log`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: the gate told a builder its own errors were another task's, so the builder could wait on a re-run that would never go green. No map changes.

**Found and left?**
- An arrow inside a quoted source line was read as a path. Effect: a red on another task's file alone, quoting such a line, went untagged. Fixed here (`^ *-->`).
- A failing test's panic line was not read. Effect: another task's error beside the caller's own failing test was BLOCKED. Fixed here.
- A red whose lines named no file was passed over in silence. Fixed here: it says the red is unattributed and lists the error lines.

**Performance work?** no: it corrects a verdict's wording; no check runs faster or slower.


### T231 (449 T418's and T422's plan-review rows were written by hand to land on 2026-11-24 while `make ledger-owed WRITE=` refused them as the landing's own; on 2026-11-25 nearly every push and commit of the coordinating session printed `ledger-owed: N check pass(es) have no row` naming MODE 4 plan reviews of tasks not yet landed, and spec-only pushes carried those rows forward)

- **Approach**: one reading of whose a ledger row is - `ledger_passes/left.rs`'s split, which the push's check (`--refuse`) and the landing's check (`--refuse --landing --tasks`) already asked - asked by every reader and writer of the rows.
  - **Where each side read ownership**, measured 2026-11-25 (the code, and replays of the real pass log and ledger). Four readers, three rules. (a) The push's check (`push.rs`'s `ledger-owed --refuse`) and the landing's check (`cheap.rs`) leave a MODE 4 pass of an open task to that task's landing (451 T147). (b) The push's write (`sync-with-main.sh`'s `--write-plan-reviews`, every push route) wrote the row of EVERY recorded plan review, open task or not. (c) `make ledger-owed WRITE=` (`--by-hand`) refuses every recorded plan review as "the landing's own" (451 T105). (d) The listing and a commit's notice (`--brief`, `ledger_hooks.rs`) asked no ownership at all and named every such pass as owed, with "write them: make ledger-owed WRITE=", which (c) refuses.
  - **What that did.** Today's six 451 T243 plan-review rows were written by four unrelated pushes (d2a61853be 09:49, 9a1c8cd121 10:22, fdce5cc36f 10:40, 546cd2b775 11:18, each "the plan reviews' ledger rows, written at landing (feature 385 T72)") before T243 was ticked at f1458390c3 (11:24), measured 2026-11-25 (`git log --grep "385 T72" -p -- dev/review-ledger.md`, each row's cost cells matched to its pass in `check-passes.jsonl`). The coordinator's transcript holds the line "ledger-owed: N check pass(es) have no row" 906 times since 2026-11-12, measured 2026-11-25 (a count of that line in the session's transcript, tool results and their echoes alike); the one push refusal of today read (2026-11-25 14:50Z) left T243's review correctly and refused on an escalation-check pass, which was owed.
  - **The task line's premise, corrected.** The 2026-11-24 hand write fixed nothing: the refused T423-T418-T422 landings wrote both rows in their worktree each time (3214651875 and 4e4e315222, "the review passes' ledger rows, written at landing (make land)", in `diagram-backlog-land`'s reflog) and were refused on page session P7's 15 passes; the clone's listing named the two rows as owed because a refused landing's commits stay in its worktree, and the session read the listing, not the refusal, observed 2026-11-25, method: the coordinator's transcript at 2026-11-24 17:25-17:27Z and the landing worktree's reflog (and replayed 2026-11-25: `--write-plan-reviews` then `--refuse --landing 449-rust-codebase --tasks "T423 T424 T418 T422"` on the ledger and `plan-review.json` of 7f5d85fef7^ write both rows and refuse nothing). The landing's check never disagreed with `WRITE=`; the listing did.
  - **The rule as built.** A MODE 4 plan review naming its feature and task whose task has an OPEN line (`- [ ] T<n>`) in that feature's `tasks.md`, and is not a task this landing lands, belongs to its task's landing: the push that carries its tick (`make land`'s own write, `cheap.rs`'s `write_ledger`, now `--write-plan-reviews --landing <feature> --tasks <its tasks>`). Every other reader leaves it and names it in the existing note line (`the passes of N open task(s) left to their own landings and sessions`): the push's write (`--write-plan-reviews` with no landing), the push's and landing's checks (unchanged), and the listing and commit notice, which no longer offer it to `WRITE=`. A recorded plan review whose task has no open line - ticked, withdrawn, absent, or a block review naming no task - belongs to the next push, whichever it is; the listing names it as such (`N recorded plan review row(s) the next push writes`), never as `WRITE=`'s. `WRITE=`'s refusal (T105) stays, its message naming both owners.
  - **Open is an open line, not "ticked in neither file".** `left.rs` read a plan review's task as open while no `- [x]` line named it, so a withdrawn or renumbered task was open for ever; harmless while only the checks left it, its row would never be written once the push's write left it too. The open test is now `- [ ] T<n>` in `tasks.md`. `whose.rs` (T157, other checks' passes of a STARTED task) keeps its own ticked test: a started task's session writes those rows itself, and nothing here changes who writes them.
  - **Red first**, measured 2026-11-25 (`make rust-test CRATE=rust/gate/crates/reviews`, the two new tests in `ledger_passes/left/tests.rs` against HEAD's `ledger_passes.rs` and `left.rs`): an unrelated push's `--write-plan-reviews` wrote 2 rows where the open task's must be left ("ledger-owed: 2 plan review row(s) written", want 1 and the left note), and the `--brief` notice named a recorded ticked task's review as "1 check pass(es) have no row ... WRITE=". After the fix the crate passes 206 of 206, and `make rust-test CRATE=rust/gate/crates/land` passes with the landing's write asserted to carry `--landing 449-x --tasks T1`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the push's write leaves an open task's plan review; its landing's write takes it | `an_open_task_s_recorded_plan_review_is_its_own_landing_s_and_no_other_push_s`, red on HEAD; `land::tests` asserts the write's `--landing --tasks` | n/a: tooling | none | n/a |
| the listing and notice leave it and name a recorded one as the next push's | the same test's listing and `--brief` loop; `a_recorded_plan_review_no_landing_writes_is_listed_as_the_next_push_s`, red on HEAD | n/a: tooling | none | n/a |
| open means an open line | the first test's T7 (no line) written by the push | n/a: tooling | none | n/a |

### T231 Approach (checklist part A)

1. **The goal, in the world.** A plan review's ledger row is written once, by the push that lands its task, and no other push, listing or commit notice treats it as owed elsewhere; a push of unrelated work neither writes nor asks for it.
2. **The constraints.** Feature 371 and 385 FR-019 (every pass owes its row, the push refuses without it); 385 T72 (a recorded plan review's row written by the push routes); 451 T105 (a hand write must not write a row a landing writes again); 451 T147 and T157 (another open task's passes left to its landing or session).
3. **Where each comes from.** G: the task line (`one of the two writes them`) and the coordinating session's brief of 2026-11-25. O: the replays and git history above.
4. **Do they describe the world here?** Yes: the real pass log, the ledger at 7f5d85fef7^, the landing worktree's reflog and today's push commits, read 2026-11-25.
5. **The order.** No dependency. T245, built beside it in its own worktree, touches no file of this task.
6. **The exits.** Green: `make closing-checks T=T231` green, the reviews and land crates' tests covering every new line. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The two new tests red on HEAD's code and green after, and the land test's write arguments, measured 2026-11-25 (above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: rows of tasks not yet landed written by unrelated pushes, a notice telling the session to write rows its own command refuses, and rows written by hand that the landing had already written, observed 2026-11-25, method: the measurements above. No map changes.

**Found and left?** none.

**Performance work?** no: it changes who writes ledger rows; nothing runs faster.


### T232 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T232 Approach (checklist part A)

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


### T233 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T233 Approach (checklist part A)

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


<!-- plan-archive: T234 to T234 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T235 to T235 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
### T239 (T230's duplicate: the same empty BLOCKED list, filed again from 449 T433's builder, 2026-11-25)

- **Approach**: T230's fix and tests, nothing of its own. T230's plan section holds the cause, the fix and the red-first proof. It ticks in T230's landing (`make land F=451 T=T230,T239`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| T230's | T230's | n/a: tooling | none | n/a |

### T239 Approach (checklist part A)

1. **The goal, in the world.** T230's.
2. **The constraints.** T230's.
3. **Where each comes from.** O: the same runs as T230's.
4. **Do they describe the world here?** Yes, per T230's.
5. **The order.** Lands with T230.
6. **The exits.** Green: `make closing-checks T=T230 F=451`. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** None of its own: T230's landing.
9. **Done, measured.** T230's red-first and green suite runs, 2026-11-25.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T230's.

**Found and left?** none.

**Performance work?** no.


### T240 (449 T432's builder, 2026-11-25: spec-fidelity MODE 4 was dispatched a third time on T432's section after two BLOCKED rounds and no guard refused it; the arbiter, asked after, ruled no fault, ask:449-T432-plan-round3)

- **Approach**: The guard already held a plan review's third round on one task (`review_round_hooks.rs`, `PLAN_ROUND_CAP`). What failed is its count. `plan_rounds` counts the task's rows of `plan-review.json`'s `block_reviews` back to the last CLEAR, and a section review never wrote a BLOCKED row.
  - **The cause, from the source.** `make decide`'s dispatch (`plan::bundle::task_prompt`) has the reviewer record by `make plan-verdict TASK=`, which is `record::record_task`. That function wrote the verdict to `tasks.<id>`, overwriting the last one, and reached `record_blocks` only on CLEAR. A BLOCKED section verdict therefore left no `block_reviews` row. Only `make plan-delta`'s block reviews (`BLOCKS=1`) wrote BLOCKED rows: 449's record holds 4 BLOCKED rows and 383 CLEAR, and 451's holds 7 and 258, all from block reviews. Observed 2026-11-25, method: `jq` over both `plan-review.json` files, and the T432 rows in the history of 449's record (`git log` of the file, `jq` of each commit), which hold two CLEAR rows and no BLOCKED one. T432's two BLOCKED rounds counted 0, so its third dispatch was "round 1" and was let through (`permitted/other-mode` in `make guard-log GUARD=review-round`). The arbiter bundle's `plan_rounds` (`arbiter/bundle/reviews.rs`) reads the same rows, so it showed the arbiter none of a section's BLOCKED rounds either.
  - **The fix: what counts.** `record_task` appends a `block_reviews` row for a BLOCKED section verdict. The row names the section's blocks (the same keys the CLEAR path computes), and its `tasks` lists the task and any bundle member that shares the section. The blocks' own verdicts stay unwritten, because only a CLEAR is their review. The count is taken from the recorded verdicts, not from the dispatch log. A round is a verdict: T432's NOT-REVIEWABLE return recorded nothing, and the session's own ask counted it out ("a NOT-REVIEWABLE dispatch that does not count", the `asked` text of ask:449-T432-plan-round3; the ruling did not dispute it), while a dispatch log would count it, along with any dispatch another guard refused. The same verdict recorded again on unchanged bytes (the same `tasks.<id>` entry) is the same round, not another.
  - **The fix: the subject.** The guard took its subject from `plan door active-task`, the `.git/active-task` mark under `.specify/feature.json`'s feature. It now takes it from the section the dispatch names ("feature <NNN-slug>, task <T>", `task_prompt`'s words) when that feature is in the clone. A block review's dispatch (`plan::bundle::delta_prompt`) names its feature ("of feature <NNN-slug>'s plan") and, in its bundle's directory `plan-<NNN-slug>-blocks-<T05-T07>-<8 hex>`, the tasks whose blocks it holds: each named task is counted and the first past its cap holds the dispatch (the MODE 4 review of this section, round 1: a third `make plan-delta` round under another active feature went unheld). Only a dispatch naming neither, a hand-written prompt or a block review of no task's blocks, falls back to the active task. A `continue` or `accept` on a plan round is read from the feature its trigger names, where `make arbiter-ruled` files it (`checks::arbiter::continues` and `closed` read `rulings(root, prefix)`, no longer the active feature's). Before this change, a hold under another active feature could never be lifted.
  - **The refusal** reads "BLOCKED: round 3 of <T>'s plan review. Nothing was dispatched.", followed by `checks::arbiter::refusal`'s `make arbiter-bundle TRIGGER="round:spec-fidelity|plan:<NNN-slug>#<T>@3"`. Its first line lost the tripwire's rule, which the next line states (message-check's BREVITY cut, 2026-11-25).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a BLOCKED section verdict written as a `block_reviews` row | `a_blocked_task_section_is_a_round_of_its_blocks` red on HEAD, measured 2026-11-25 (`make rust-test CRATE=rust/gate/crates/plan`: 0 rows, 1 wanted); suite case 12 "the third dispatch is refused" red on HEAD | n/a: tooling | none | n/a |
| the subject read from the dispatch, a section's or a block review's | `a_section_dispatch_counts_the_section_it_names`; suite case 12 "held under another active feature" and "...and a block review of its blocks" red on HEAD | n/a: tooling | none | n/a |
| a plan round's rulings read from its trigger's feature | the shared crate's `rulings_and_owed_triggers_read_back`; suite case 12 "the arbiter's continue releases round 3" red before it | n/a: tooling | none | n/a |

### T240 Approach (checklist part A)

1. **The goal, in the world.** The third MODE 4 dispatch on one task's section, after two BLOCKED verdicts, is refused until the round arbiter rules. The refusal names `make arbiter-bundle` with the trigger.
2. **The constraints.** The root CLAUDE.md's tripwires: "a check's third round on one subject" owes the round arbiter's ruling before the next check. Feature 432: the ruling stays in the arbiter's log. 451 T141: one review of a bundle is one round of each of its tasks.
3. **Where each comes from.** G: CLAUDE.md's tripwire line. R: ask:449-T432-plan-round3 in `specs/449-rust-codebase/arbiter.jsonl`. O: the recorder's source and the two records' rows, 2026-11-25.
4. **Do they describe the world here?** Yes, measured 2026-11-25 (the suite run on HEAD's code and on the fix): the suite's case 12 plays T432's sequence through the real `l7r-gate plan record-task` and the real hook: a BLOCKED round, a dispatch whose return recorded nothing, a second BLOCKED round, then the third dispatch.
5. **The order.** No dependency. T227 (the record checks' counter, kept per active feature) is separate. This task's counter no longer has that flaw: a section review and a block review each name their subject. Only a dispatch naming neither falls back to the active task.
6. **The exits.** Green: `make closing-checks T=T240 F=451`. Red: what failed is recorded and the task set down, and a claim that it cannot be done is ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, measured 2026-11-25. On HEAD's code, the plan crate's new test failed, measured 2026-11-25 (`make rust-test CRATE=rust/gate/crates/plan`): `block_reviews` held 0 rows where 1 was wanted. `tests/hooks/test-review-round-hooks.sh` gave 88 passed and 2 failed: "the third section round was not held (rc=0)" and "the held round followed the active task (rc=0)". After the fix it gave 90 passed and 0 failed. With the cap disabled (`plan_cap_held` returning ""), it gave 87 passed and 3 failed. The block-review case, added after the MODE 4 review's round 1, failed with the block subject disabled (90 passed, 1 failed: "the block review's round followed the active task (rc=0)"), and the final code gives 91 passed, 0 failed. Logs are in the session scratchpad.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: a tripwire the root CLAUDE.md requires did not fire, so a third review round ran without the arbiter's ruling. No map changes.

**Found and left?**
- A plan round's `continue` or `accept` was read from the active feature's `arbiter.jsonl`, not from its trigger's. Effect: a hold under another active feature could not be lifted by its ruling. Fixed here.
- The arbiter's bundle listed none of a section review's BLOCKED rounds. Effect: the arbiter ruled on a third round without seeing the first two. Fixed here by the same row.
- The shared arbiter refusal (`checks::arbiter::refusal`) offered `ARBITER_OK="<reason>"` without its two-word bar (`escape::enough`). Effect: a one-word reason was refused again with no hint why (message-check's FIDELITY finding, 2026-11-25). Fixed here: `<reason, two words or more>`, in the one function that writes it, observed 2026-11-25, method: `grep -rn 'ARBITER_OK=' rust/` (the other hits, in `checks/handle.rs`'s tests, are a different text). The guards' wordings that carry it are reviewed again by message-check.

**Performance work?** no: it holds a review round; no check runs faster or slower.


<!-- plan-archive: T29 to T06 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T242 to T240 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T242 to T242 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T245 to T245 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->

### T246 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T246 Approach (checklist part A)

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


### T247 (451 T229's builder in a parallel worktree: the tool target's l7r-gate rebuilt inside a cover run's environment after a gate source edit, and 21 tests of clone-sync-hooks.sh and sync-with-main.sh then failed on 'uncommitted changes' from the default_*.profraw files in their fixture clones, observed 2026-11-25, method: T229's builder's hook-suite run; seen by T235's, T231's and T229's builders)

- **Approach**: `scripts/gates/l7r-gate.sh` builds a stale tool with the coverage environment cleared, and removes a binary that comes out instrumented anyway rather than run it.
  - **The cause, measured.** A crate's coverage tests run with `rustc/cover.rs`' environment (`cover_env`, then the run's own `LLVM_PROFILE_FILE`): `cargo llvm-cov show-env`'s five variables (RUSTFLAGS, LLVM_PROFILE_FILE, CARGO_LLVM_COV, CARGO_LLVM_COV_SHOW_ENV, CARGO_LLVM_COV_TARGET_DIR; its output in this tree, 2026-11-25), with `workspace_only` moving `-C instrument-coverage` out of RUSTFLAGS into a RUSTC_WORKSPACE_WRAPPER script. A test that calls the launcher inherits it, and the launcher's cargo built the tool in `~/.cache/l7r-cargo-target/<tree>/tool/` under it. The builder's workaround (`env -u RUSTFLAGS -u CARGO_ENCODED_RUSTFLAGS`) does not clear the flag, measured 2026-11-25 (a toy two-crate workspace in the scratchpad, real cargo): a release build under that wrapper alone gave a binary holding `__llvm_prf_cnts` that wrote `default_<id>_0_<pid>.profraw` into the directory it ran in, and the plain rebuild after it (0.05 s, the plain artifacts at their own metadata hash) put back a binary without the section.
  - **The fix: the build's environment.** `build()` runs cargo under `env -u` of every variable show-env sets, every flag channel cargo reads (RUSTFLAGS, CARGO_ENCODED_RUSTFLAGS, CARGO_BUILD_RUSTFLAGS, RUSTDOCFLAGS, CARGO_ENCODED_RUSTDOCFLAGS), both wrapper channels (RUSTC_WORKSPACE_WRAPPER, RUSTC_WRAPPER: no config or script of this tree sets one, `grep -rn RUSTC_WRAPPER` 2026-11-25) and CARGO_LLVM_COV_BUILD_DIR. The tool's flags then come from `.cargo/config.toml` (rust-lld, T96), as at every build outside a cover run.
  - **The fix: never left as the tool.** After a successful build and before the `touch` and the build id, a binary holding `__llvm_prf_cnts` is removed with its `build.json`, and the launcher exits 1 with "l7r-gate: <bin> came out instrumented for coverage, so it is removed and nothing runs on it ..." and where to look (a config's rustflags or rustc-wrapper). `L7R_GATE_PRINT_FRESH` names no binary then. The scan runs only at a build: 0.038 s over the 33 MB l7r-gate, measured 2026-11-25 (`time grep -qaF`), per call it would cost that on every one of a suite's hundreds of calls. The detector was checked for false positives: 0 of the 19 tool binaries in every clone's target hold the section (2026-11-25, `grep -caF` over each `tool/` program), so no plain build is refused.
  - **A binary instrumented before this fix**: none exists (the same scan). One that did would run until a source newer than it rebuilds it, which the toy shows comes out plain. Accepted, the GM not asked (no cost to a map or a verdict; the scan is the evidence): the alternative priced was a `<bin>.plain` stamp the launcher requires as fresh - one stat a call, a rebuild of every program in every clone on the first call after landing, and the stamp in three suite fixtures (FT, HT, BT), observed 2026-11-25, method: `grep -n L7R_GATE_TARGET` over the suites - for a state the scan finds nowhere.
  - **The guards' wrapper is left**: `scripts/hooks/l7r-guard.sh` builds the same way into the same target, but nothing runs it inside a cover environment - Claude Code's hooks and `make hooks-test` start it, and no Rust test does (`grep -rn l7r-guard.sh rust/`, 2026-11-25: three mentions in text and a fixture string). Its build also writes `l7r-guard`, not the gate's programs.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the build's coverage environment cleared | `tests/hooks/test-l7r-gate.1.sh` "a cover run's build: cargo is handed none of the coverage environment" and "a later call drops no profile where it runs", red on HEAD's launcher (2026-11-25) | n/a: tooling | none | n/a |
| an instrumented build removed, never run | the same suite's "an instrumented build: refused", "removed, not left as the tool", "the refusal says why", "print-fresh names no binary", red on HEAD's launcher | n/a: tooling | none | n/a |

### T247 Approach (checklist part A)

1. **The goal, in the world.** A gate call never leaves a profile file where it runs: the tool binaries in the tool target are never coverage-instrumented, whatever environment the call that built them came from.
2. **The constraints.** The task's line in tasks.md (rebuild with the instrumentation flags cleared; an instrumented binary never left as the tool; red-first on a cover-run environment). Feature 449 T61: the launcher fails closed. T205: no extra work on a fresh call.
3. **Where each comes from.** O: T229's builder's 21 failures (tasks.md T247), the show-env output and the toy workspace, 2026-11-25. G: the task as filed.
4. **Do they describe the world here?** Yes: the fixture replays the cover's environment as `cover_env` and the run build it (show-env's variables plus RUSTC_WORKSPACE_WRAPPER), and the toy measured that the wrapper alone instruments.
5. **The order.** No dependency. T232, built in parallel, touches other files.
6. **The exits.** Green: `make closing-checks T=T247 F=451`. Red: what failed is recorded and the task set down, and a claim that it cannot be done is ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, 2026-11-25: on HEAD's launcher `tests/hooks/test-l7r-gate.1.sh` gave 7 failures in the new group (cargo saw RUSTFLAGS, CARGO_ENCODED_RUSTFLAGS, RUSTC_WORKSPACE_WRAPPER, LLVM_PROFILE_FILE and the three CARGO_LLVM_COV variables; a later call left `default_1_0.profraw`; the instrumented stub ran, stayed and was named fresh). With the fix the shard passes whole.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: gate calls dropped profile files that failed 21 hook-suite tests. No map changes.

**Found and left?** none.

**Performance work?** no: one scan of the binary at a build, none on a call.

### T248 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T248 Approach (checklist part A)

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
