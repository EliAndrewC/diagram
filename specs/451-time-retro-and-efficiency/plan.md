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

<!-- plan-archive: T36 to T351 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T312 Approach (checklist part A)

1. **The goal, in the world.** The bundle, task, land and plan crates' tests give one answer whatever the machine's home directory holds, and read none of its transcripts, guard log or git identity.
2. **The constraints.** 100% line coverage from each crate's own tests; 451 T309's model (`transcripts_base()`); 451 T94 and T207 (a test's guard log is never the live one); the binary's behavior unchanged; no guard message changed; `l7r_shared`'s `test-env` held to the guard's family (`checks`' `feature_sets.rs`, `APART`).
3. **Where each comes from.** G: the task line and the coordinating session's brief of 2026-11-27. O: the census and the empty and planted `HOME` runs above.
4. **Do they describe the world here?** In part: the transcripts dependence is real (red under a planted `HOME`); the guard-log one is not (no write escaped under an empty `HOME`); a dependence the line did not name, the git identity, is (three red).
5. **The order.** No dependency.
6. **The exits.** Green: `make builder-checks` over the bundle, task, land and plan crates green, and their tests green under the empty and the planted `HOME` with nothing written in either. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** 2026-11-27, the same command as above after the fix: under the empty `HOME` 586 of 586 (bundle 87, task 133, land 162, plan 204), no `.claude/` written; under the planted `HOME` bundle 87 of 87.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: tests whose verdict depends on the machine - one red under a planted transcript, three red on a machine without a git identity. No map changes.

**Found and left?**
- The Rust checks' run lock and kept results (`rust-checks-run.lock`, `rust-checks-run.json`) are written under `$HOME/.cache/l7r-cargo-target/<tree>/` even with `CARGO_TARGET_DIR` set, so a run with another `HOME` shares the warm cache but not the live run's lock, observed 2026-11-27, method: `find` over the scratch `HOME` after the empty-`HOME` run. Not fixed here: the rustc crate, outside this task's crates, and its lock's placement wants measuring first. Filed as T440; lands before T302.

**Performance work?** no - test isolation, a defect.


### T312 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T312 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T312's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T312's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T312 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T312 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T312 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T312's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T312's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T312 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T312 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T312 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T312's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T312's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T312 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T312 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T312 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T312's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T312's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T312 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T313 (the GM, 2026-11-26, on the session handing each freed pool tree to the next task by hand: "what you are doing sounds like something that we want our tooling to actually enforce. Because otherwise you just have to remember to keep our tasks in flight"; and the measurement of 2026-11-27, `dev/measurements/2026-11-27/tree-idle/results.md`: the three warm pool trees stood idle 336 of 1,440 tree-minutes (23%) from 2026-11-26T17:00Z to 2026-11-27T01:00Z with the queue never short, measured 2026-11-27 (`tree-idle.py`))

- **Approach**: the builders' queue becomes a file code reads, three commands list it, write it and name its next entry, and a Stop guard refuses a turn's end over a free pool tree and a READY entry. T395 (the queue in a form code reads, so `make builder-done` names the next task) and the first half of T297 (the overlap of two tasks' files named at dispatch) are BUILT HERE, in the same files. The idle figures are the measurement's, measured 2026-11-27 (`tree-idle.py`, read-only over the session's transcript and the 451 event log): 170 of the 336 idle tree-minutes with the session in its own turn, 105 with a landing running, 46 with the session stopped - 321 of the 336, the minutes in idle gaps of 3 minutes or more, which is what the table classes ("gaps of 3 minutes or more, 321 of the 336"); the other 15 fell in shorter gaps and are not classed. The mechanism's effect on them is NOT measured here: the after-measurement over a like window is 451 T401's, not this task's.
  - **The queue** (`rust/guard/shared/src/builder_queue.rs`, new, in `l7r_shared` so the guard and the gate read one module; its doc is the format's and the rules' home). The file is `specs/<feature>/queue.txt`, one entry a line in the order to hand out, `#` a comment: `<task[,task]> <kind> [jobs=<1-3>] [measures=<n>] [load=1] crates=<dir,dir|-> files=<path,prefix|-> [waits=<T<n>,GM,alone>] [note=<rest of line>]`. `parse` names every malformed line by its number; `states` computes each entry's state (landed, built, in flight, waiting on what, READY); `overlap` is T297's rule; `next` is, among the READY entries that overlap nothing in flight, an open performance task's first, then the queue's order (the DECISION below); `idle` is the one rule the Stop guard asks.
  - **The commands** (`rust/gate/crates/task/src/builder_queue.rs`, new; verbs in `rust/gate/crates/task/src/lib.rs` and `rust/gate/src/lib.rs`; the Makefile's `queue`, `queue-add`, `builder-next`): `make queue` lists a queue with each state, `make queue-add` appends one entry through the one parser (refused for a task with no box, and outside the clone), `make builder-next` prints the next entry with its exact `make builder-brief` command (ending `ENTRY=<k>`, the DECISION on built below), each READY entry passed over with why (the in-flight task it overlaps, or the performance entry offered before it), and the pool's count against `L7R_BUILDERS`. `make builder-done`'s step 1 is now that entry (`builder_queue::dispatch`), where T394 left a placeholder: this is the NOTICE AT A BUILDER'S END the task line asks for.
  - **The Stop guard** (`rust/guard/src/guards/pool_idle_hooks.rs`, new, `pool-idle-hooks`, event `Stop`, registered after `research-switch-hooks` and before `shell-check-hooks`; suite `tests/hooks/test-pool-idle-hooks.sh`): the coordinating session's Stop is answered `decision: block` while a pool tree of its clone stands free and on disk, fewer than `L7R_BUILDERS` trees are held, and a queue of the clone holds a next entry. The block names the tree, the task and the one command. It is quiet in a builder or any subagent, in a clone with no pool, with the count reached, with every open entry waiting, and on a queue that cannot be read (recorded `passed`, rule `queue-unread`: a malformed line is `make queue`'s error, never a held session). A `queue.txt` that cannot be read no longer hides a readable one behind it (the closing half; label: tooling convention): the clone holds `specs/269-research-backfill/queue.txt` and `specs/280-modern-only-sweep/queue.txt`, page sessions' queues of another form, which sort before 451's, and the build half's `idle()` returned at the first unread file, so the live guard could never have reached 451's queue. The walk now goes on past an unread file, and the first unread one is the verdict only where no queue has an entry to hand out; red first, measured 2026-11-27 by the closing half (the shared crate's tests and `tests/hooks/test-pool-idle-hooks.sh`, the walk stopping at the first unread file): the shared crate 530 passed, 1 failed, the suite 27 passed, 1 failed. `make queue` and `make builder-next` with no `F=` still stop at such a file (Found and left, T418).
  - **DECISION, THIS REVERSES A RETIREMENT, AND T313'S LATER WORDS GOVERN** (label: deliberate deviation from 451 T183's D10). 451 T88's rolling-dispatch Stop block ("a builder slot is free") and its `L7R_BUILDERS` were retired by 451 T183 on the GM's question of 2026-11-23 whether such hooks were the right approach against a check that "does nothing and adds nothing to the context if we are still active", told that 23 of the session's turns since 14:42 that day were spent only answering such blocks (`request.md`; T183's section in `plan-done.md`). This task brings a Stop-time refusal back. Why it may: the GM's words on T313 are of 2026-11-26, three days later, made with the retirement in force, and ask for enforcement by name ("something that we want our tooling to actually enforce"); the task's line asks for a refusal at Stop with a stated reason as its escape. What is different this time, so that it does not cost what T88's cost: (1) T88's block read the transcript and fired whenever a slot was free and a task was open, which under a ruling that held new work was every Stop; this one fires only on a free tree WITH an entry of the written queue that is READY (it waits on no task, no carry and not on the GM - a held queue is written `waits=GM` once, in the file, and the guard is then silent) and that overlaps no task in flight; (2) it names the one command that ends the block; (3) its escape is one line of the final message, `POOL_IDLE_OK: <reason>`, recorded; (4) its falsifier is written in the audit entry (`dev/audits/pool-idle-queue.md`): the share of the coordinating session's Stops escaped - `POOL_IDLE_OK` on more than 1 Stop in 5 of a day, a GUESS knob - the sign that the block is being answered and not acted on, which is what retired T88's.
  - **DECISION, the rule is deliberately thin** (label: tooling convention). The coordinating session reports that the GM is weighing whether the primary session becomes a pure orchestrator (`request.md` marks it the session's report, not his words). So the guard holds no state and reads nothing of its own: all it judges is `shared::builder_queue::idle`, which the gate's commands read too. Where the coordination moves, the rule moves with the queue, and what would be thrown away is one file, observed 2026-11-27, method: `wc -l rust/guard/src/guards/pool_idle_hooks.rs`, 148 lines.
  - **DECISION, the format is named `key=value` fields after two positional words, in a file of its own** (label: tooling convention), not tab-separated columns and not a fence in `queue.md`: a tab cannot be seen and an editor may write spaces for it, a nine-column row one cell short reads as another row, and a fence in prose breaks with the prose. Only what `make builder-brief` takes as `T=` and `KIND=` is positional; `crates=` or `files=` must be present (`-` says none), and a measurement must name `measures=`, because READY must mean "`make builder-brief` will take it".
  - **DECISION, an entry is ONE dispatch and its state is computed, never typed** (label: tooling convention). The first that holds: landed (every task ticked in the clone's `tasks.md` or archived in its `tasks-done.md`), built, waiting on an earlier entry of its task, in flight (a pool tree of this feature holds one of its tasks), waiting (its task's done commit not carried; a `waits=` task neither ticked nor carried; the GM), READY. `queue.md`'s typed "LANDED" and "In flight" went stale within hours (2026-11-26, 20:10 UTC).
  - **DECISION, an entry is built when a done line NAMES it** (label: tooling convention; the plan review's round 1 objection 2, rebuilt by the round-2 fix in place of the build half's count). The build half told built BY COUNT - as many `done` lines for the task as the queue names that task down to the entry - which misfired both ways where dispatches and `make builder-done` runs differ: two runs for one entry (a builder at its cap and its successor) ended the task's next entry undispatched, and one run ending two entries (a kept tree's build and closing halves) left the second READY after the carry, observed 2026-11-27, method: `state()` walked by hand for both cases by the closing half, the second met on this task's own queue lines. Now an entry's name is its ORDINAL among its first task's lines (`Entry::ordinal`, set by `parse`; stable because a line stays until its task lands). `make builder-next` and the Stop block print `make builder-brief ... ENTRY=<k>`; `make builder-brief` takes `ENTRY=` (a word that is no number above 0 refused before any tree is taken) and writes a `brief` line on `builder-pool.log` beside the take (tree, holder, kind, entry); `make builder-done` writes `"entry": k` on its `done` line from the tree's last `brief` line naming an entry since the tree was last taken, made or adopted - so a successor briefed on the tree it already held (the take logs nothing on that path) inherits the entry. `states` reads each task as ended THROUGH the larger of the count of its done lines naming no entry and the ordinal of the latest entry a done line names (`through`); a bundle's named entry ends each of its tasks through that task's own ordinal at it. So two runs naming entry 1 end entry 1 alone, and one run naming entry 2 ends both, measured 2026-11-27 (`a_done_line_names_the_entry_it_ends`). The larger, not the sum, is the side the fallback errs on: a successor briefed by hand without `ENTRY=` on a tree whose earlier brief named none counts one entry per run, as before; and where a named and an unnamed run mix, the queue re-offers an entry (seen, and refused by `make builder-tree` until the carry) rather than skip one (unseen). A done line naming an entry the queue no longer holds counts as unnamed. What it still costs: a line removed before its task lands renames the entries after it (every queue's header says a line STAYS). This builds 451 T416 whole (Built here, below). Red first, measured 2026-11-27 (`make rust-test CRATE=rust/guard/shared` with the new tests on the count): 531 passed, 3 failed - `a_done_line_names_the_entry_it_ends` at its first assertion (two runs naming entry 1 read both lines built), with the two performance tests below; (`make rust-test CRATE=rust/gate/crates/task` with the shared change and the gate unchanged): 122 passed, 3 failed - `the_entry_a_brief_serves_is_on_the_log_and_on_its_done_line` (no `brief` line written) and two tests whose expected command lacked `ENTRY=1`. Of the new assertions, "one run naming entry 1 ends it alone" and the unnamed-count case hold on the old code too and were not run red.
  - **DECISION, an open performance task's entry is offered first** (label: tooling convention; the plan review's round 1 objection 1, FR-013 under SC-006, the GM 2026-11-20: "can we in general priotitize performance improvements going forward?"). `next` takes, among the READY entries that overlap nothing in flight (`alone` kept), the first naming an open performance task, else the first; each earlier READY entry it passes over for one is listed `<task> (line <n>) is performance work, offered first (FR-013)`. What the code reads: a task's OPEN box in the feature's `tasks.md`, held to `set_down_hooks::performance` - the `[perf]` tag among the bracketed tags after the id, or the `### T<n> Performance checklist` heading `make task-add PERF=1` writes in `plan.md` - the one test `make task-start`'s refusal and the Stop hook's next task already ask. FR-013's measurement clause ("this kind of measurement task to be counted as a performance task", the GM 2026-11-20) is read through that tag, which such tasks carry (T08-T11, T22, T53, spec.md's round-2 note), never from an entry's kind: a `measurement` entry may measure a correctness question, which the spec's own note leaves out. A bundle is performance work when any of its tasks is. It is asked of READY entries' tasks only, `plan.md` read once a queue and only when one has a box (668,405 bytes for 451, measured 2026-11-27, `wc -c`), so a Stop pays for no other box. The free tree belongs to no feature, so `idle()` names a performance entry of ANY queue before another queue's first pick ("in any active feature"); `make builder-done`'s step 1 takes the same any-queue preference (round 3, below), so no limit is left here. WITHIN EACH CLASS THE ORDER IS THE FILE'S, which is the GM's of 2026-11-26 (`queue.md`): *"putting the ones most likely to give us better measurements at the front of the line, followed by the ones most likely to increase our task throughput"*. On today's queue it changes nothing: no task with a `queue.txt` line carries the tag or the checklist while open, observed 2026-11-27, method: the open `[perf]` boxes of `tasks.md` (T22, T341, T342, T364, T365, T394) against `queue.txt`'s tasks - and an open performance task with no line is named first by the next DECISION (built here as T421). Red first, in the counts of the DECISION above: `an_open_performance_task_s_entry_is_offered_before_an_earlier_one` and `the_idle_rule_names_a_performance_entry_of_any_queue_first`, each failing at its first assertion on file order.
  - **DECISION, an open performance task with no queue line is named FIRST, and `make builder-done`'s step 1 prefers performance work of any queue** (label: tooling convention; the round arbiter's binding ruling on this section's round 2, recorded in the feature's `arbiter.jsonl` as `ask:451-T313-plan-round3`: "(1) When an open performance task (FR-013's test, any active feature) has no queue.txt line, the Stop block, make builder-done's step 1 and make builder-next name it first, with the make queue-add command that writes its entry; a performance task given a line with waits=<what> quiets it. (2) builder-done's step 1 uses idle()'s any-queue performance preference rather than the done task's own feature alone. One shared change in builder_queue.rs that meets both is enough"). ONE SHARED CHANGE in `rust/guard/shared/src/builder_queue.rs`, read by all four: `unlisted(clone, common, prefer)` lists every open performance task of every active feature that no line of its feature's `queue.txt` names, in any state, and `offer(boards, prefer)` picks across the queues - a READY performance entry of any queue first, then the `prefer`red feature's pick, then the first queue's. The walk is FR-013's own: `set_down_hooks::open_performance`, new beside `next_performance` and built on its `started`, `active` and `performance` (the preferred feature first, then each active feature by its last start; a held feature's and a parked stage's tasks left out, as `make task-start`'s picker leaves them), collecting every box and WITHOUT the picker's wait skip, so a task that waits (T22) is named until its line says `waits=` - the line, not the title, is what quiets it. A queue file that does not parse (a page session's `queue.txt` of features 269 and 280) names none of its feature's tasks, since it says nothing of them. Each is named with `make queue-add F=<feature> T=<task> KIND=<kind>`, which runs as printed (`crates=- files=-`); its KIND is `build-half` where `builder_brief::mechanism` - the test by which `make builder-brief` refuses `KIND=fix`, MOVED to `l7r_shared::builder_brief` with `targets` so the guard asks the same one - reads a new command or guard in the task's line, else `fix`, and the reader adds `CRATE=`, `FILES=` and `WAITS=` as the line names them. Where they appear: the Stop block opens `<tree> is free. FIRST, <feature> <task> is open performance work with no queue line (<n> more: make builder-next names them). Write its line ...` with the command, then `Then <entry> is READY ...` where one is, and it fires with a free tree under the count even when nothing is READY (the plain block is unchanged where nothing is unlisted); `make builder-next` and `make builder-done`'s step 1 open with `FIRST, open performance work (FR-013) no queue line names - write each one's line ...` and a command a line; `make queue` ends with it. `make builder-done`'s step 1 (`dispatch`) now reads EVERY readable queue, as `idle()` does, the done task's feature's own missing or malformed queue still said on its line. Cost: the walk runs after `idle()`'s early returns (a free tree, the count not reached), and the plan is cut once to its `### ` checklist headings, the only lines `performance` reads of it, so the open boxes do not each search the whole plan (140 open boxes and a plan of 679,113 bytes for 451, measured 2026-11-27, `grep -c` and `ls -la`). THE REVIEWER'S "NOT ASSUMED" POINT, answered by a test: `make builder-brief` runs no `make task-start` (neither `builder_brief.rs` nor `builder_tree.rs` calls it; a task is started by its own `make task-start`), so the block's command meets no FR-013 refusal of its own; and `the_named_brief_for_performance_work_meets_no_performance_first_refusal` takes the command `make builder-next` prints for a performance entry, runs `builder_brief::run` on its words as named (code 0, the tree taken, the marker printed), then `make task-start` on that task (code 0: `perf_first` passes any task FR-013's own test calls performance work), and pins the converse - a non-performance task of the same queue started while it is open is refused naming it, `PERF_LATER_OK="<reason>"` its route (code 0 with one). THE SIX LINES the ruling asks for, written into `queue.txt` by a plain edit (`make queue-add` writes only the clone's file), every box open: T341 `fix` (rust/gate/crates/rustc); T342 a `measurement` (measures=1) then a `fix` (rust/gate/crates/rustc, scripts/container/builder-brief.md); T364 `fix` (rust/gate/crates/rustc); T365 a `measurement` (measures=2); T22 a `measurement` (measures=6) `waits=GM`, GM standing in for "a full day of work after T02-T21 land" as on T401 and T354, its note saying so; T394 `fix waits=T401` (built: what is left is its re-measure, which is T401's line). The mechanism test reads `fix` for all six (no phrase, every `make` target theirs exists); T342's and T365's lines open with a measurement, which the sizing rules split off, so their kinds are the lines' and each line's note says so. Red first, with the change's two halves put back to the old behavior for one run (`unlisted` naming none, `dispatch` reading its own feature's queue alone) and restored from a scratch copy: 4 failed - rust/gate/crates/task 2 of 128 (`an_open_performance_task_with_no_line_is_named_first_and_its_command_runs_as_printed`, `the_next_dispatch_prefers_performance_work_of_any_queue`), rust/guard 1 of 557 (`an_open_performance_task_with_no_queue_line_is_named_first`), rust/guard/shared 1 of 538 (`an_open_performance_task_with_no_queue_line_is_named_with_the_command_that_writes_one`); green after, with `every_open_performance_task_of_every_active_feature_is_listed`, `the_offer_across_queues_is_performance_first_then_the_preferred_queue` and the "not assumed" test, and the suite `tests/hooks/test-pool-idle-hooks.sh` 31 passed with its three new cases.
  - **DECISION, carried is the done ref being gone** (label: tooling convention): a task's done commit waits while `refs/l7r/done/<feature>-<task>` stands (one `git for-each-ref`), not `builder_done.rs`'s fuller test, so the guard needs no gate crate. What it costs: a carry finished by hand reads as waiting until the next `make builder-done` clears the ref - the safe side.
  - **DECISION, the overlap rule (T297's first half)** (label: tooling convention): crates and files are a single list of paths, and a pair of entries overlaps where a path of one equals a path of the other or lies under it by whole components (`rust/guard` holds `rust/guard/src/lib.rs`, not `rust/guardian`). It is asked against entries IN FLIGHT only (the task line: "the tasks in flight"). A held tree whose task the queue does not list has files nobody wrote down: it is named `not checked` and holds nothing back, since holding on it would idle the pool for every dispatch made outside the queue. `waits=alone` works both ways: an alone entry is passed over while any pool tree is held, and while one is in flight every READY entry is passed over.
  - **DEVIATION from T297's line: the overlap is named by `make builder-next` and `make builder-done`, not by `make builder-tree`** (label: deliberate deviation). The line says "make builder-tree compares the task's expected files"; the queue's commands compare them, and a handout made by hand (`make builder-tree` or `make builder-brief T=<a task picked by hand>`) names none (Found and left, T408).
  - **DEVIATION from T313's line: the command named is `make builder-brief`, not `make builder-tree T=<n>`** (label: deliberate deviation). The line predates 451 T334, which made `make builder-brief` the one command of a dispatch (it sizes the brief and takes the tree through `builder_tree`); a block naming `make builder-tree` would name a command whose output the brief guard then refuses to dispatch on.
  - **DECISION, the count is `L7R_BUILDERS`, default 3, a GUESS knob** (label: guess, a knob; `builder_queue::BUILDERS`). The line says "the count it keeps is the settled builder count". `docs/process-decisions.md`, "Two code builders at once", decides two and says the count is "to be re-measured" at three and four once the warm pool and the build slot are in; the session has run its warm pool trees rolling since 2026-11-26, the window the idle share above was measured over. The guard keeps whatever count is set and settles none: 3 is the pool as run, and a session holding the count lower exports `L7R_BUILDERS` or writes the escape's line.
  - **The escape STARTS its line, and the block now says so** (the closing half; label: tooling convention). The pattern is line-anchored as `BUILDER_BRIEF_OK`'s is, so the token after a bullet or in backticks is not taken; the build half's block said "on a line of your final message", which does not say that. Both wordings now say "start a line" ("Or start a line of your final message with: POOL_IDLE_OK: <why not, two words or more>"; "Start a line with: POOL_IDLE_OK: ..."), with a unit case and suite cases for a bulleted and for a backticked token. Every rendering passed `message-check`, observed 2026-11-27, method: one dispatch on `make guard-messages BUNDLE=1`'s 4 units, each PASS on fidelity and on brevity, recorded in `dev/guard-messages.tsv`.
  - **The live queue** (`specs/451-time-retro-and-efficiency/queue.txt`; `queue.md` keeps its prose under a paragraph that points at it): converted from `queue.md` by the build half with every KIND inferred, then made true by the closing half from the clone's `tasks.md`, pool registry and pool log for the group the session named - 43 entries, observed 2026-11-27, method: `l7r-gate queue 451` over a scratch copy of the clone's `tasks.md`, `tasks-done.md`, `builder-pool.json` and `builder-pool.log` with this file: 0 landed, 1 built, 4 in flight, 12 waiting, 26 READY, the next T275. T313 keeps ONE line for both halves after the round-2 fix, and that is still right: its tree was taken once, observed 2026-11-27, method: `grep T313` over the clone's `builder-pool.log` (one `take` line, 2026-11-27T01:35:27Z, and no `brief` or `done` line), and briefed before `ENTRY=` existed, so its one `make builder-done` will write a done line naming no entry, counted once - two lines would leave the closing half's READY after the carry. T416's line is removed, built here. `waits=` has no word for "a window of use must pass first": `GM` stands in for it on T401 and T354, each note saying so.
  - **Docs**: `docs/guards.md` (both tables), `scripts/container/builder-brief.md` (the queue's paragraph), `rust/guard/CLAUDE.md` (`pool_idle_hooks`, `shared::builder_queue`), `rust/gate/CLAUDE.md` (the task crate's `builder_queue.rs`), `docs/process-decisions.md` ("A free pool tree is not left idle ...", Decided, with the tree-idle figures and what reopens it), `dev/audits/pool-idle-queue.md` (kind `adopted`, read by `make audits`), `docs/make-targets.html` (regenerated by `make docs`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a line read field by field or refused by its number; each state computed; the overlap by crate and path prefix; the next entry; `alone` both ways | `builder_queue::tests` of `rust/guard/shared`, red on a stub module (item 9) | n/a: tooling | none | n/a |
| the queue listed, an entry appended or refused, the next entry named with what it passed over | `builder_queue::tests` of `rust/gate/crates/task`, red on a stub (item 9) | n/a: tooling | none | n/a |
| `make builder-done`'s step 1 is the queue's next entry | `the_next_dispatch_is_the_queue_s_next_entry` and the re-pinned `builder_done` tests, red on a stub (item 9) | n/a: tooling | none | n/a |
| a Stop over a free tree and a READY entry is blocked with the one command; each quiet case passes; the escape starts its line | `pool_idle_hooks::tests` and `tests/hooks/test-pool-idle-hooks.sh`, red with the holding branch removed (item 9) | n/a: tooling | none | n/a |
| an open performance task's entry first, of any queue at a Stop; an entry built when a done line names it, a line naming none counted | `an_open_performance_task_s_entry_is_offered_before_an_earlier_one`, `the_idle_rule_names_a_performance_entry_of_any_queue_first`, `a_done_line_names_the_entry_it_ends` of `rust/guard/shared`, red on file order and the count (item 9) | n/a: tooling | none | n/a |
| `make builder-brief ENTRY=` logged beside the take, inherited by a successor, written on the done line | `the_entry_a_brief_serves_is_on_the_log_and_on_its_done_line` of `rust/gate/crates/task`, red with no `brief` line (item 9) | n/a: tooling | none | n/a |

### T313 Approach (checklist part A)

1. **The goal, in the world.** A pool tree freed by a builder's end goes to the queue's next task without the session having to remember it: the queue is a file whose every state is computed, the builder's end names the next entry with its command, and a turn does not end over a free tree and a task that is ready for it.
2. **The constraints.** The pool's registry is 451 T285's (`shared::builder_pool`), read, not copied. A dispatch is `make builder-brief` (451 T334). A done commit and its ref are 451 T394's and T397's. A gate crate reads nothing of the guard's binary crate (451 T66), so what both read is in `l7r_shared`. A guard that can produce the compliant command produces it, and its escape states a reason of two words or more, recorded (the root CLAUDE.md, "What is enforced"). 451 T183's D10: a Stop hook blocks only for what the session must do before stopping - answered in the Approach's first DECISION.
3. **Where each comes from.** G: the GM's words of 2026-11-26 on T313's line, and of 2026-11-23 behind T183 (`request.md`). O: the tree-idle measurement of 2026-11-27. The constraints are earlier tasks' and are named with them above.
4. **Do they describe the world here?** Yes for the cause this task can reach: 46 of the 336 idle tree-minutes fell with the session stopped, its turn ended, and 170 in its own turn, where the order of a builder's end (451 T394) and a named next task shorten it, measured 2026-11-27 (`tree-idle.py`, each idle 10 seconds classed by what the session was doing). Whether the mechanism moves that idle share is not known until it has run over a like window (T401).
5. **The order.** After 451 T285 (the pool), T334 (`make builder-brief`) and T394 (`make builder-done`), all landed. Before T297's second half and T401, which wait on it in the queue, and before T408, T412, T415 and T418, which it leaves; T416 and T421 are built here.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/task rust/guard rust/guard/shared rust/gate rust/gate/crates/land"` and the guard's own suite in the builder's tree; the full gate with its coverage at the batch's landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, the build half, measured 2026-11-27 (`make rust-test CRATE=rust/guard/shared` against a stub module): 519 passed, 12 failed, the twelve `builder_queue` tests; measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/task` against a stub): 116 passed, 8 failed; measured 2026-11-27 (`bash tests/hooks/test-pool-idle-hooks.sh` with the guard's holding branch removed): 15 passed, 5 failed of its then 20 cases. The closing half, measured 2026-11-27 (`make builder-checks CRATE="rust/guard rust/gate/crates/task"` with the two new wordings asserted and the old ones still in the guard): the guard crate 554 passed, 2 failed; measured 2026-11-27 (`make builder-checks CRATE="rust/guard rust/guard/shared"` with `Verdict::Idle` answered quiet and `tasks-done.md` unread): the guard crate 553 passed, 3 failed (three of the four `pool_idle_hooks` tests), the shared crate 530 passed, 1 failed (`the_facts_are_read_from_the_clone`); measured 2026-11-27 (`bash tests/hooks/test-pool-idle-hooks.sh`): 17 passed, 9 failed with both stubs, and 24 passed, 2 failed with `tasks-done.md` alone unread (the two archived-box cases). After, measured 2026-11-27 (`make builder-checks` over the five crates, 54 s): the task crate 124 passed, 0 failed, the guard 556 passed, 0 failed, the shared crate 531 passed, 0 failed, the gate 8 passed, 0 failed, the land crate's last green result standing, lint and format clean on the five; measured 2026-11-27 (`bash tests/hooks/test-pool-idle-hooks.sh`): 28 passed, 0 failed; measured 2026-11-27 (`bash tests/hooks/test-make-only-hooks.sh`): 144 passed, 0 failed; measured 2026-11-27 (`make guard-messages`): 13 wordings, each reviewed or baselined and within its budget. THE ROUND-2 FIX, red first in its two DECISIONS above; after, measured 2026-11-27 (`make builder-checks CRATE="rust/gate/crates/task rust/guard rust/guard/shared"`): the task crate 125 passed, 0 failed, the guard 556 passed, 0 failed, the shared crate 534 passed, 0 failed, lint and format clean on the three; measured 2026-11-27 (`bash tests/hooks/test-pool-idle-hooks.sh`): 28 passed, 0 failed; the block's three renderings with `ENTRY=1` passed `message-check`, observed 2026-11-27, method: one dispatch on `make guard-messages BUNDLE=1`'s 3 units, each PASS on fidelity and brevity, recorded in `dev/guard-messages.tsv` (the tree's store refilled from the suite run under `L7R_MESSAGE_CORPUS`, T338's hand route); `make guard-messages`: 13 wordings, each reviewed or baselined and within its budget. Read for the batch gate's coverage, line by line, not run: one closure on a line of its own that no test reaches (the escape pattern's `unreachable!`, now on its builder's line as `builder_brief_hooks`' is), one arm no test of its crate rendered (`word`'s built entry, now asserted in the listing test), one assertion whose message stood on lines of its own (bound to a local). NOT run: coverage (the second tier's, by the GM's ruling of 2026-11-26), `make static`, `make hooks-test`, `make quick`; a real Stop of the coordinating session over the live pool - its first is after this task's carry.
10. **Before moving a constant.** n/a: no constant moves. `L7R_BUILDERS` (3), the audit entry's 15% idle and its 1 Stop in 5 escaped are new, each a GUESS knob no verdict depends on, moved on the first re-measurement's evidence (T401).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a defect of a map: no map, sheet or research claim changes. What a session sees differently: a builder's end names the next task and its command; `make queue` and `make builder-next` answer what `queue.md` was read for; and a turn's end over a free tree and a READY entry is refused once, with the command, until the entry is handed out or one line says why not.

**Found and left?**
- The second tier's gate is not proposed at the threshold: T313's line ends "the second tier's gate is proposed when the staged tasks reach the threshold with no carry in progress (trial 458 - a rolling pipeline never drains)", and nothing here prints it. Its visible effect: the session still decides by memory when to run `make land` over the built entries, the thing the line asks the tooling to say. Not fixed here: the threshold is trial 458's to settle (`specs/458-second-tier-threshold/spec.md`, Running), and a proposal printed at a number nobody has measured would be a second GUESS on top of the first. Filed as T415; lands before T22.
- A handout made by hand names no overlap (the first DEVIATION above). Its visible effect: `make builder-tree` or `make builder-brief T=<a task picked by hand>` hands a tree to a task whose queue entry overlaps a task in flight and says nothing, so the second cannot land until the first does - T297's own incident. Not fixed here: it is an edit of `builder_tree.rs`'s take, a third crate path of this task's brief, and the queue's own commands already name it. Filed as T408; lands before T22.
- `make queue` does not flag a `fix` entry whose task line `make builder-brief` reads as a mechanism: such an entry reads READY and the Stop block names a command that is refused (with its own escape, `SIZING_OK`). Its visible effect: observed 2026-11-27, method: each `fix` entry's task line of this queue held to `builder_brief::mechanism`'s rule by a script of the same rule - four of them (T406, T409, T369 on the words "make -C", T412 on a quoted phrase), each now saying so in its note. Not fixed here: it puts the brief's sizing rule into the queue's parser, a design of its own. Filed as T412; lands before T22.
- `make queue` and `make builder-next` with no `F=` stop at another feature's `queue.txt` of another form. Its visible effect: observed 2026-11-27, method: the clone's `specs/269-research-backfill/queue.txt` and `specs/280-modern-only-sweep/queue.txt` (page sessions' queues) sort before 451's and fail the parser, so the no-`F=` listing is an error where the guard (fixed above) goes on. Not fixed here: which files are builders' queues is a naming question for every caller of `queues()`. Filed as T418; lands before T22.
- The mechanism is not measured running: the audit entry holds the BEFORE figure only. Its visible effect: the audit entry's idle falsifier is unread and the guard's worth is unshown. Not fixed here: it needs an eight-hour window of the session using `make builder-done` and the queue, which no builder's tree can supply. Filed as T401; lands before T22.
- T297's second half (how a message sent to a builder in mid-work is delivered) is not built. Its visible effect: the builder brief still does not say how such a message arrives. Not fixed here: it is a measurement of its own, in the queue behind this task. Filed as T297; lands before T22.

Built here: T395 - the builders' queue in a form code reads
Built here: T416 - an entry is built when the done line names it (ENTRY= from make builder-next, logged by make builder-brief, written by make builder-done)
Built here: T421 - an open performance task the queue has no line for

**The landing.** Recommended: T313 is ticked with this section, and T395, T416 and T421 close as built here by the `Built here:` lines above (T395 is built here whole: `make builder-done`'s step 1 reads the queue; T416 whole: the named entry, the plan review's round-1 objection 2; T421 whole: the unlisted performance task named first by `make queue`, `make builder-next`, `make builder-done` and the Stop block, the round arbiter's ruling `ask:451-T313-plan-round3`); T297 stays open for its second half, its first half built here but for T408. T313's last clause lives in T415.

**Performance work?** yes: the builders' loop. It answers the measurement of 2026-11-27 (`dev/measurements/2026-11-27/tree-idle/results.md`): the three warm trees idle 336 of 1,440 tree-minutes (23%) over eight hours with the queue never short, measured 2026-11-27 (`tree-idle.py`). There is no after yet: the same table over a like window is T401's, read against the audit entry's 15% (a GUESS knob). Not an engine-speed task: docs/performance-checklist.md's engine questions do not apply.
<!-- plan-archive: T314 to T314 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T313 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T313 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T313's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T313's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T313 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T313 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T313 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T313's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T313's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T313 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T313 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T313 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T313's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T313's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T313 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T313 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T313 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T313's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T313's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T313 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T176 to T197 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T365 Approach (checklist part A)

1. **The goal, in the world.** The session knows why the guard crate's tests run slow under `/tmp`, who else pays the same cost, and which levers on it are worth building, before any is built.
2. **The constraints.** No source changed and nothing removed from `/tmp` by hand (the brief); a figure is the record's, with its date and method; every lever priced is filed (the brief, 451 T289).
3. **Where each comes from.** O: the task line's measurement of 2026-11-26 (T340's finding) and the record `dev/measurements/2026-11-26/tmp-clutter/t365-results.md`. G: the GM's words of 2026-11-20 in request.md, which count a measurement as performance work.
4. **Do they describe the world here?** Yes: the task line's gap came back as 5.34 s against 2.08 s medians, measured 2026-11-26 (`t365-bin-times.txt`, five runs each by `/usr/bin/time`), and its shim count accounts for it, measured 2026-11-26 (the shim, 9.97 s of listings against a 9.81 s difference on one thread).
5. **The order.** After T340, which found it; before T370 to T379, which it filed, and T373, T375 and T376, found beside it.
6. **The exits.** Green: the cause found and closed by arithmetic, the other payers counted, every lever priced and filed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One probe set aside: the first three timings were taken under a `TMPDIR` inside a session's scratchpad, where four guard tests fail, and were discarded (filed as T375, below).
8. **The budget.** One landing, of the record and this section.
9. **Done, measured.** The cause named and its arithmetic closed (9.97 s of listings for a 9.81 s difference), the live hooks, the leak pin, the hook suites and the gate's self-tests counted, and the seven levers of its section 4 priced and filed, measured 2026-11-26 (t365-results.md sections 1, 2 and 4).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here: a measurement builder changes no source. No map changes.

**Found and left?**
- A PreToolUse hook on an Edit took 342.2 ms median where one on a Bash call took 31.6, the same under either temp directory, measured 2026-11-26 (`t365-hook-times.txt`, 20 alternating runs); visible effect: every edit's wait. Not fixed here: it is not the temp directory, so which guard spends it is a measurement of its own. Filed as T373; lands before T302.
- Four `rust/guard` tests fail when `TMPDIR` is a directory under a session's scratchpad and pass under `/tmp`, measured 2026-11-26 (the guard test binary run under each, t365-results.md's closing section); visible effect: a red crate run wherever a tree's `TMPDIR` is so placed. Not fixed here: whether the tests pin their root or the guards misread a real clone under such a path is a decision past a measurement. Filed as T375; lands before T379.
- Something runs the land crate's whole test binary with `/tmp` as its temp directory, outside the leak pin, and it dies mid-run, leaving 29 `l7r-gate-ci-stop-handler-p<pid>-<seq>` directories written 12:46 to 14:07, measured 2026-11-26 (`t365-census-l7r.txt`, the census), with the visible effect of leftovers at `/tmp`'s top level and 14 to 16 ms a `TempDir` for each such run, measured 2026-11-26 (the loop of 300, t365-results.md section 1). Not fixed here: who runs it is not found from the logs. Filed as T376; lands before T371.

**Performance work?** yes: a measurement task, counted as performance work by the GM's words of 2026-11-20; it makes nothing faster itself

### T365 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T365 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T365's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T365's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T365 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T365 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T365 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T365's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T365's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T365 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T365 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T365 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T365's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T365's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T365 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T365 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T365 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T365's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T365's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T365 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T370 to T365 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T373 (a PreToolUse hook on an Edit took 342 ms where one on a Bash call took 32, found by T365, measured 2026-11-26 (`t365-hook-times.txt`, 20 alternating runs a call))

- **Approach**: a measurement; no source changed. What was asked (the task line): which guard spends the Edit hook's time, by `l7r-guard --only <guard>` on the same event, before any change. The record is `dev/measurements/2026-11-26/edit-hook/t373-results.md`, its scripts and tables beside it; every figure below is the record's, measured 2026-11-26 from 18:26 to 19:25 local at load 4.4 to 53 on 22 cores with other builders running, each figure the median / 90th centile ms of one hook call over 20 counted runs after a warm-up, the arms interleaved (`t373-time.py`), a row above load 20 marked LOADED (the record's head).
  - **The method.** A throwaway world under the scratchpad: a clone of the mirror, a clone of the real clone with its event logs, `checks-open.json` and caches copied in, a worktree of it standing in for a pool tree, the mirror's claim map copied and re-aimed, and the mirror's kept guard binary copied and reached through `L7R_GUARD_TARGET`, every call under `env -i` with only the named variables, measured 2026-11-26 (the record's "How it was measured"). Where a call writes was found under an `LD_PRELOAD` shim (`t373-shim.c`, `t373-probes.txt`), and a leak check found no line of a `t373-*` session in the real logs, claim map or guard log, measured 2026-11-26 (`t373-leak-check.txt`). Fidelity first: in the sandbox worktree the Edit hook came back at 372.3 / 413.1 ms LOADED, minimum 344.6, against T365's 342.2 / 362.0, measured 2026-11-26 (`t373-worktree.tsv`). The guards taken alone, less their extra process starts, sum to within 2% of the binary's own, measured 2026-11-26 (`t373-top3.txt`, 809 against 802 ms).
  - **Two guards, not one.** `event-log-hooks` spends 333.0 / 359.7 ms on every Edit (not a Write): its reversal tripwire reads the feature's whole event log, 41.0 MB and 156,753 lines, and JSON-parses every line, measured 2026-11-26 (`t373-guards.tsv`, the session in its dirty clone, load 5.4 to 16.9). About 265 to 290 ms of it is the parse of lines that cannot match, since the read alone is 46.6 ms and read and screened 67.6 ms, measured 2026-11-26 (`t373-levers.txt`, `t373-levers.rs`, load 18, LOADED). `clone-sync-hooks` spends another 480.1 / 508.0 ms on an Edit or Write in the session's clone itself, not in a pool worktree, because it reads the session's whole 274 MB transcript for the session's name before `dirty()` and then runs `git status --porcelain`, while a dirty clone never uses the name, measured 2026-11-26 (`t373-guards.tsv`, `t373-sizes2.tsv`). A clean clone adds 147 ms (627.3 against 480.1), the claim map's 2,871 files opened and the sessions directory listed 131 times over, measured 2026-11-26 (`t373-top3.txt`, the shim's opens). So the session's Edit in its clone cost 823.6 / 1146.0 ms and a builder's in a pool worktree 372 to 402 ms, growing 8.1 ms a MB of event log and 1.4 ms a MB of transcript, measured 2026-11-26 (`t373-guards.tsv`, `t373-worktree.tsv`, `t373-sizes2.tsv`).
  - **Found beside it**: while a plan review holds text, `record-edit-hooks` loads, snapshots and SAVES the 3.0 MB `checks-open.json` on every Bash call, 150.4 / 251.1 ms against 34.7 / 44.6 with no hold, measured 2026-11-26 (`t373-tools2.tsv`, `t373-nohold.tsv`), and 1,176 of the day's 4,202 Bash calls fell inside a `spec-fidelity` run, an UPPER BOUND on the hold's share, measured 2026-11-26 (`t373-holds.py`, `t373-holds.txt`).
  - **The day's cost is an ESTIMATE**: Edit and Write hooks 117 s, about 2.0 minutes, over 306 Edit and Write calls in a copy of the clone's event log taken at 18:26 local, the day not over, measured 2026-11-26 (`t373-events.py`, `t373-events.txt`). T365's 470 calls are its own day file's count, its own probe edits among them, and why the two differ was not determined, measured 2026-11-26 (`t365-events-counts.txt`). All hooks of the five tools timed came to about 604 s, 10 minutes of the day, measured 2026-11-26 (the record's "the other tools" table).
  - **The levers, each the record's section 3 with its filed task.**

    | lever | what it saves, by the record | its task | label |
    |---|---|---|---|
    | A. `reversal` screens each line for an Edit of the path before parsing it | 265 to 290 ms of 333 a call, about 60 s a day | T383, built and landed (T392 filed after it for the read that remains) | measured 2026-11-26 (t373-results.md section 3, `t373-levers.txt`) |
    | A2. the Edit lines kept in a side file beside the log | about 330 ms a call, 70 s a day, two files to keep in step | in T383, the option not taken first, now T392's to price | measured 2026-11-26 (t373-results.md section 3) |
    | B. clone-sync asks for the session's name only on the clean path | 383 ms of 480 on a dirty clone's Edit or Write, at most 18 s a day | T384 | measured 2026-11-26 (t373-results.md section 3, `t373-sizes2.tsv`) |
    | C. `titled` reads the transcript from its end | 383 ms on every caller of the session's name, 0.0 ms and one 64 KiB block against 755 ms forward | T385, built and landed | measured 2026-11-26 (t373-results.md section 3, `t373-levers.txt`, LOADED) |
    | D. clone-sync's clean path reads the sessions directory once | about 130 of the 147 ms a clean clone adds, at most 6 s a day | T386 | measured 2026-11-26 (t373-results.md section 3) |
    | E. the plan hold saves `checks-open.json` only where its snapshot changed, and prunes it | 100 to 115 ms of a Bash call's 150 under a hold, 135 s + 21 s a day, an upper bound | T387 | measured 2026-11-26 (t373-results.md section 3, `t373-holds.txt`) |
    | F. `git diff-index --quiet HEAD` before `git status --porcelain` | 52.1 ms against 110.9 a call, at most 2 s a day | DECLINED: under 3 s a day, noted in T384 | measured 2026-11-26 (t373-results.md section 3, `t373-git.txt`, LOADED) |
    | G. the Agent hooks (pair-hooks 88 ms, check-bundle-hooks 35, checks-hooks 98) | not priced: the cause was not read, about 60 s a day | T388, a measurement | measured 2026-11-26 (t373-results.md section 3, `t373-tools2.tsv`) |

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| no code changed: a measurement, its scripts and tables in `dev/measurements/2026-11-26/edit-hook/` | n/a: nothing fixed | n/a: tooling | none | n/a |

### T373 Approach (checklist part A)

1. **The goal, in the world.** The session knows which guards make an Edit's hook slow, by how much and why, and which levers on them are worth building, before any is built.
2. **The constraints.** No source changed; nothing written to the real event logs, claim map, guard log or plan-hold state (the sandbox and its leak check); `--only` run only for guards whose events and matcher take the tool; every lever priced is filed (the brief, 451 T289).
3. **Where each comes from.** O: T365's figure (`t365-hook-times.txt`) and the record `dev/measurements/2026-11-26/edit-hook/t373-results.md`. G: the GM's words of 2026-11-20 in request.md, which count a measurement as performance work.
4. **Do they describe the world here?** Yes: T365's case came back in the sandbox at 372.3 ms LOADED with a minimum of 344.6 against T365's 342.2, measured 2026-11-26 (`t373-worktree.tsv`, 20 interleaved runs).
5. **The order.** After T365, which found it; before T383 to T388, which it filed.
6. **The exits.** Green: the time split by guard and closed against the binary's own, each guard's cost read to its line of code, every lever priced and filed or declined. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Two first attempts were set aside, both kept in the record: without `.specify/feature.json` the event line went to a small `_unassigned.jsonl`, and with the sandbox clone misnamed the guard refused the edit as misrouted (`t373-try1-misnamed-clone.tsv`).
8. **The budget.** One landing, of the record and this section.
9. **Done, measured.** Two guards named and their sum within 2% of the binary's own, the Bash hold found beside them, eight levers priced - six filed, one kept inside T383 and one declined - measured 2026-11-26 (t373-results.md sections 1 and 3, `t373-top3.txt`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here: a measurement builder changes no source. No map changes.

**Found and left?**
- Every hook call spends 15 to 17 ms outside the guard binary, in `sh`, `env bash` and the launcher's staleness walk of `rust/guard/**` (`scripts/hooks/l7r-guard.sh`, `newer`), 34.7 against 17.5 ms for Bash and 23.8 against 8.7 for an Edit's PostToolUse, measured 2026-11-26 (`t373-tools2.tsv`, `t373-guards.tsv`), with the visible effect of about 166 s of the day's hook time over 10,400 calls, measured 2026-11-26 (`t373-events.txt`, the day's counts times 16 ms). Not fixed here: the record observed it and priced no lever, so which hop spends it is a measurement of its own. Filed as T439; lands before T302.
- The Bash call's slowness under a plan hold, above, is lever E. Not fixed here: a change to the hold's state, which must still restore held text. Filed as T387; lands before T302.

**Performance work?** yes: a measurement task, counted as performance work by the GM's words of 2026-11-20; it makes nothing faster itself


### T373 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T373 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T373's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T373's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T373 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T373 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T373 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T373's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T373's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T373 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T373 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T373 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T373's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T373's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T373 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T373 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T373 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T373's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T373's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T373 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T367 to T355 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T367 to T367 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T369 to T359 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T369 Approach (checklist part A)

1. **The goal, in the world.** A task started in two trees (a builder's pool tree, then the clone that carries its work) and unstarted in one reads, to every reader, as started in the other alone: its mark, its live start row and the hold on that tree's landings agree, and that tree can unstart it too.
2. **The constraints.** The task's line; one mark a task in its own tree (451 T254) and a bundle's one mark (451 T141); the start log's filter (451 T359-D9) and the static count's raw read (T359-D9b); the landing's `make task-start` of a carried task kept working (the brief); no guard message changed (the brief).
3. **Where each comes from.** O: T359's closing half's reading (the task's line); the real clone's start log (D1) and marks directory (D3), both read 2026-11-26. The GM's words name neither form; the choice is this builder's, from the brief.
4. **Do they describe the world here?** Yes: the defect was reproduced in the crate's tests on the old code (item 9). No real case was observed (the task's line: "no case observed"). The two-tree path is the common one (D1).
5. **The order.** After T359 (the unstart and the filter). No task waits on it.
6. **The exits.** Green: the first tier's checks on the three changed crates and the closing check's suite. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the readers were found by one search for `marks::` and `task-marks` over the tree, listed in the table above.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, observed 2026-11-26, method: `make rust-test CRATE=rust/gate/crates/task` with the two new tests on the code before the change: 122 passed, 2 failed. Both failed on the readers disagreeing: after the second tree's unstart, the marks named no tree and the log named the first tree. After, observed 2026-11-27, method: `make builder-checks CRATE="rust/guard/shared rust/gate/crates/task rust/gate/crates/land"`: green (shared 522 passed, task 124, land 155; lint and format clean). The tests that read the mark file at its old path were restated to find it with `marks::own_file`: four in the task crate and one in the land crate, observed 2026-11-27, method: `grep -rn task-marks rust`. `bash tests/hooks/test-closing-checks.sh`: 74 passed, 0 failed.
10. **Before moving a constant.** n/a: no constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** What the session sees differently: after a tree's `make task-unstart` of a task another tree also started, `make land`'s "was it started" and the push's hold no longer disagree with the marks, and the other tree can still run its own `make task-unstart` (before, it was refused "no start mark in any tree").

**Found and left?**

- A mark whose tree no longer exists (a pool tree dropped, a worktree removed) stays until its task lands: `make task-unstart` refuses it with a `make -C <tree>` that cannot run, and `make task-withdraw` refuses the task as started. Before T369, a start in the clone took such a mark over. Found by reading, no case observed. Not fixed here: which marks are stale (no tree, a tree the pool has released) is a rule of its own across the unstart, the withdrawal and the hold, outside this defect. Filed as T437; lands before T302.

**Performance work?** no - a defect.

### T369 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T369 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T369's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T369's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T369 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T369 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T369 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T369's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T369's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T369 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T369 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T369 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T369's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T369's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T369 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T369 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T369 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T369's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T369's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T369 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T383 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T384 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T386 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T387 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T388 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T139 to T393 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T392 to T383 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T392 to T392 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T325 to T301 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T403 (`make task-time` booked 27.6 of the second tier's blocking minutes over 2026-11-26T17:00Z to 2026-11-27T01:00Z to the session stopped waiting on the GM - its turns ended on a question to the GM between a task's carry and its landing - where every other window's waiting-on-the-GM minutes are the GM's row; the GM read the tier's figure as "a HUGE problem, either with our measurements or with our process", 2026-11-27, request.md; the measurement `dev/measurements/2026-11-27/tree-idle/results.md`)

- **Approach**: the booking already tells the session stopped waiting on the GM: `book.rs`'s `after_stop` names a main session's gap from its `Stop` to the GM's prompt `the GM` (or `the GM away`), and `is_gm` reads that category. But `segments` keyed that segment by `tiered`, which inside a batch's span (a task's carry to its landing) returns the batch's key, and the window's table folds every cell of a batch's key into the one second-tier category - so the GM's minutes there were the second tier's, and counted as working time too. Now `segments` keys a segment that is the GM's, where `tiered` gave a batch's key, to the session's own (`<feature>, -`): the GM's row gains it, the window's totals do not change. The second tier's note says its blocking is only the session's own work. Measured 2026-11-27, method: `make task-time`'s binary, kept before the change as a copy and built after it, run read-only on `/diagram/.clones/diagram-backlog`'s real logs (`--root`, `--since 2026-11-26T17:00:00Z --until 2026-11-27T01:00:00Z`, never `SINCE=last`):

| figure | before | after |
|---|---|---|
| the second tier's blocking (the window's table, and its section's line) | 146.9 | 119.3 |
| its section's `the GM` row's blocking | 27.6 | none |
| the window's `the GM` row's blocking | 43.6 | 71.2 |
| the header's waiting on the GM | 71.2 | 71.2 |
| the window's all (minutes, blocking) | 2670.9, 501.2 | 2670.9, 501.2 |
| the window's working blocking (all but the GM) | 457.7 | 430.0, now the header's own figure |

(The tier's 146.9 is today's figure for the window the measurement read 123.3 in: the logs gained lines since, and the GM's 27.6 is the same, measured 2026-11-27 (the reports above).) 451 T426's `slot-wait` on a scratch slot directory - 221.8 s, four waits of T355's builder in diagram-backlog-t270 from 2026-11-27T01:49Z - lies after the window, so none of it is in the second tier's rows, measured 2026-11-27 (every `slot-wait` Phase line of the clone's event logs summed by start); the tier's `waiting on a build slot` row is 6.1 minutes and 0.0 blocking, measured 2026-11-27 (the after report).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the GM's wait inside a batch's span booked to the GM's row | `tier_tests::the_session_waiting_on_the_gm_inside_a_batch_is_the_gm_s_row`, red on the old code (277 passed, 1 failed), green on the new (278 passed) | n/a: tooling | none | none |

### T403 Approach (checklist part A)

1. **The goal, in the world.** The second tier's blocking counts only the session's own work on a batch; the session's time stopped waiting on the GM is the GM's row in every window, inside a batch's span too.
2. **The constraints.** 451 T298's second tier (`book/tier.rs`'s doc); the GM's rows out of every other percentage's denominator (the GM 2026-11-25); the window's totals unchanged.
3. **Where each comes from.** G: the GM's words of 2026-11-27 in request.md; O: `dev/measurements/2026-11-27/tree-idle/results.md` and this section's re-measurement.
4. **Do they describe the world here?** Yes: the before report's second-tier section held a `the GM` row of 27.6 blocking minutes, and its window table's working blocking (457.7) disagreed with its header's (430.0) by the same 27.6, measured 2026-11-27 (make task-time's old binary on the clone's logs, the window pinned).
5. **The order.** After T298 and T394; independent of T426.
6. **The exits.** Green: the measure crate's tests and the re-measurement above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The fixture test red on the old code and green on the new (counts above); the real window's tier 146.9 to 119.3, the GM's row 43.6 to 71.2, all 501.2 unchanged (2026-11-27, method above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The report's second-tier figure, read by the GM as a process problem, held 27.6 minutes of his own wait, and the window's working blocking counted them as work, measured 2026-11-27 (make task-time's old binary on the clone's logs, the window pinned).

**Found and left?** none

**Performance work?** yes: a measurement task, counted as performance work by the GM's words of 2026-11-20; it makes nothing faster itself

### T403 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T403 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T403's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T403's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T403 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T403 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T403 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T403's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T403's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T403 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T403 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T403 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T403's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T403's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T403 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T403 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T403 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T403's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T403's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T403 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T399 to T308 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T409 to T307 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T409, T406 Approach (checklist part A)

1. **The goal, in the world.** While a tree's gate runs, a commit, an add or a record-writing make sent into it from any tree is held, and one sent from it into another tree - by `cd`, git's `-C` or make's own `-C` - passes.
2. **The constraints.** Feature 385 plan D13 (no write the gate would see while it runs), feature 375 FR-004 (a gate vouches for none of a tree that moved), T307 part 1's rule (a write in another, ungated tree passes); the refusal's text is not changed.
3. **Where each comes from.** O: T307 part 1's Found and left (`plan.md`, `### T307`), read 2026-11-26; GNU make 4.4.1's own reading of its options, measured 2026-11-26 as above.
4. **Do they describe the world here?** Yes: on the old code the walk placed `make -C sub x` where its shell stood and the guard let `git -C <the gated tree> commit` through from another tree, each shown by its new test failing (item 9).
5. **The order.** T409 then T406, one section; both before T307's tick; T430 and T405 stay open.
6. **The exits.** Green: `make builder-checks CRATE="rust/guard rust/guard/shared"` and the changed guards' suites in the builder's tree, the full gate at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, measured 2026-11-26 (`make rust-test`, each run's result line): T409's test on the old walk, `rust/guard/shared` 519 passed, 1 failed; T406's test on the old guard, `rust/guard` 554 passed, 1 failed. After, measured 2026-11-26 (`make builder-checks CRATE="rust/guard rust/guard/shared"`): `rust/guard` 555 passed, 0 failed, `rust/guard/shared` 520 passed, 0 failed, lint and format clean; `tests/hooks/test-gate-write-hooks.sh` 32 passed, 0 failed; the walk's readers' suites, run once after T409, measured 2026-11-26 (`bash tests/hooks/test-<guard>-hooks.sh`, each suite's last line): main-tree 104, gm-tree 24, make-only 144, static-runs 42, event-log 25, readme 87, builder-pool 17 passed, house-style passed, 0 failed in each.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome, not a difference: a gate voided by a commit sent into its tree from another, and a record-writing make aimed at another tree refused (or, for main-tree and static-runs, placed in the wrong tree).

**Found and left?**
- An Edit, a Write or a shell write into a gated tree from a session standing in another tree is not held (T406 extended only the commit, add and record-writing make rules). Visible effect: a gate voided; found by reading, no firing observed. Not fixed here: the brief held this bundle to those three kinds, and an Edit's rule asks the gated tree's own tree check, a widening with its own cases. Filed as T430; lands before T307.

**Performance work?** no - two gaps in a guard, a defect.

### T409 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T409 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T409's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T409's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T409 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T409 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T409 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T409's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T409's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T409 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T409 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T409 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T409's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T409's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T409 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T409 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T409 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T409's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T409's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T409 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T406 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T406 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T406's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T406's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T406 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T406 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T406 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T406's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T406's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T406 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T406 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T406 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T406's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T406's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T406 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T406 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T406 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T406's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T406's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T406 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T413 (the landing's first pass asks the push's unrelated-history and in-progress holds, and the ledger and batch cases of 2026-11-26/27 are pinned: a push refusal met only after the gate costs the gate's minutes)

- **Approach**: the questions T307 part 2's parity table left "not asked", built; the ledger and batch cases of 2026-11-26/27 given fixtures, the first built, the second pinned. The tests are `rust/gate/crates/land/src/land/cheap/tests/push_parity.rs`; the code `rust/gate/crates/land/src/land/parity.rs` (new), `cheap.rs` and `land.rs`; the test fake (`land/tests.rs`) answers `--holding` per directory and the ledger's listings in turn.
  - **Red first.** With the seven tests written and the code unchanged, 4 failed and 3 passed (observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/land`, 158 passed and 4 failed of 162): the unrelated history, the touched spec directory, the feature pointer and the ledger row after the claims wait each failed; the batch's changed block, the ready landing and the real ledger's measurement passed. With the code, 162 of 162 pass (observed 2026-11-27, method: `make builder-checks CRATE="rust/gate/crates/land"`).
  - **T413-D1, built: the unrelated history.** The first pass opens with the push's `refuse_unrelated_history` after its fetch - HEAD and origin/main both resolve and `git merge-base` finds none - and is then said ALONE, before the pass commits anything: every other answer reads a delta with no merge base, and the cure is a re-clone. It is a second copy of the shell's two git questions, not one function both call: the shell function also serves `sync_in`, which runs no Rust before it, and a function the shell could call would be a new gate command. Its words are the shell's but for the mirror, named by where it is rather than by the shell's `$MAIN`.
  - **T413-D2, built: the in-progress rule over every spec directory.** After `hold` (the landed feature, with its ready ruling), `others_in_progress` asks each other `specs/<dir>` the delta touches and the one `.specify/feature.json` names what the push asks it, through the same readers: `holding` (in process, `shared::speckit::holding_with`, the landing's tasks handed in as the push's `L7R_LAND_TICKS`; an error answer held, as the push's `|| echo fail-closed`), then `closed_by_status` (an error not closed), the pointer by `json-field`'s own function. Only the loop is a copy. Any other directory held is a refusal: the push's one exception is a delta of that feature's `specs/` directory alone, and a landing's tick commit touches the landed one.
  - **T413-D3, built: a ready landing asks no other feature.** Under `L7R_LAND_READY` the push's `--holding` answers nothing for ANY directory (`holding_with` returns early once every tick is ruled ready), so the first pass skips D2 where it ruled the landing ready, refusing nothing the push lets through. The push's exemption is itself a hole, filed below.
  - **T413-D4, built: the ledger asked again after the claims wait.** What the write does with each pass was measured through the real ledger first: a pass of the landing's own task is written whatever its reply (`see reply` where it has no transcript), and a pass traced to no task it lands is left owed, the one row `--refuse` then names (observed 2026-11-27, method: `the_landing_s_write_takes_its_own_pass_and_leaves_an_untraced_one_owed`, the real `reviews ledger-owed` on a scratch tree). So after the claims wait's write the landing asks the first pass's own refusal again (`ledger_refusal`, one function for both) and, where a row is still owed, stops before the ticks naming `make ledger-owed WRITE=`; it writes what it can first, as before.
  - **T413-D5, pinned: the batch's changed block.** A batch of T1 and T2 whose T2 section changed since its review is refused in the first pass for T2 alone, naming the block and `make plan-delta F=`: each task's tick check asks its own section (`held_for`), the scope the push asks once it is ticked. It held on the code before this task; the fixture pins it.
  - **The parity table, updated** (T307 part 2's, the rows this task moved; each other row as that table has it).

    | push check | after T307 part 2 | now |
    |---|---|---|
    | unrelated history | not asked | asked first, said alone (D1) |
    | the in-progress rule | the landed feature alone | every touched spec directory and the pointer, but under a ready ruling, as the push (D2, D3) |
    | the plan reviews' ledger rows written | written, the second write never refused | written, and refused before the ticks where a row is still owed (D4) |
    | `plan-gate.sh` in a batch | asked, unverified for a batch | pinned by a fixture (D5) |

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1 | `a_clone_whose_history_shares_no_commit_with_main_s_is_refused_before_anything_is_written` | n/a: tooling | none: tooling | the push refuses after the gate, as before |
| D2, D3 | `another_feature_in_progress_that_the_delta_touches_is_refused_unless_its_status_closes_it`, `the_feature_pointer_naming_a_feature_in_progress_is_refused`, `a_landing_ruled_ready_asks_no_other_feature_as_the_push_asks_none` | n/a: tooling | none: tooling | the push refuses after the gate, as before |
| D4 | `a_pass_the_landing_s_last_write_does_not_take_refuses_before_the_ticks` | n/a: tooling | none: tooling | `make ledger-owed WRITE=`, then land again |
| D5 | `a_batch_landing_whose_second_task_s_block_changed_since_its_review_is_refused_in_the_first_pass` | n/a: tooling | none: tooling | `make plan-delta F=`, as before |

### T413 Approach (checklist part A)

1. **The goal, in the world.** A landing is told before its gate every refusal its push would make, these two holds among them, and a pass made while the gate ran is named before the ticks.
2. **The constraints.** Feature 405 D23 (the first pass prints every refusal together), feature 133 (no feature in progress lands), feature 301 FR-019 (a clone on an unrelated history is refused), 451 T307 part 2 (the first pass asks the push's own checks).
3. **Where each comes from.** G: T307's line, talked through with the GM 2026-11-26, part (2): every check of the push also in the landing's first pass, proved by a fixture the first pass lets through today. O: the red-first run and the ledger measurement above.
4. **Do they describe the world here?** Yes: the push's two holds were read from `scripts/sync-with-main.sh` (`refuse_unrelated_history`, `push_cmd`'s in-progress loop) on 2026-11-27, and the readers each calls were followed to the Rust functions the first pass now calls.
5. **The order.** After T307 part 2; before T307's tick.
6. **The exits.** Green: the four red tests pass and the first-tier checks are green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks CRATE="rust/gate/crates/land"` green, 162 of 162; red first as recorded in the Approach.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome, not a difference: a landing refused by its push after its whole gate for a hold its first pass could have asked.

**Found and left?**
- A landing ruled ready beside the mark's task exempts every feature's hold at the push, not only the landed one's (`holding_with` returns nothing for any directory under `L7R_LAND_READY`). Visible effect: another feature's started task whose edits the delta carries reaches main beside a ready landing. Not fixed here: a change to the push's own rule, past this task's two jobs, and D3 mirrors it until then. Filed as T432; lands before T307.

**Performance work?** yes (a `[perf]` task: a landing refused after its gate costs the gate's minutes, dev/measurements/2026-11-27/tree-idle/results.md); not an engine-speed task, so the performance checklist's questions do not apply.

### T413 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T413 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T413's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T413's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T413 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T413 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T413 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T413's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T413's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T413 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T413 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T413 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T413's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T413's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T413 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T413 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T413 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T413's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T413's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T413 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T420 to T367 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T420 Approach (checklist part A)

1. **The goal, in the world.** The session knows what the build slots' waits after the small lane really were, what held the slots, and whether any change of the slots' count or lanes is worth building inside the memory budget.
2. **The constraints.** Read-only from the logs, but for the two dependency rebuilds, one at a time with no load generator (the brief); T347's memory budget; every lever priced is filed or declined with its number.
3. **Where each comes from.** O: T367's record (`dev/measurements/2026-11-27/prewarm-keys/results.md`), T355's `lint-memory/lint-wait-rows.txt`, T347's budget and sampler, and the record `dev/measurements/2026-11-27/slot-waits/results.md`. G: the GM's words of 2026-11-20 in request.md, which count a measurement as performance work.
4. **Do they describe the world here?** No: the premise did not hold, since 221.9 s of T367's waits were T355's scripted holds and no real wide wait reached 5 s, measured 2026-11-27 (`waits.py` over the event logs).
5. **The order.** After T347, T355 and T367, whose records it reads; before T425 and T426, which it filed.
6. **The exits.** Green: every `slot-wait` line of the window sorted real or synthetic, wide or lane, every wide slot-second's holder named, two dependency rebuilds measured and each lever priced against the budget. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One holder model set aside: with T355's scripted runs counted as holders it saw three holders at once for 155 s, without them never, measured 2026-11-27 (`waits.py`, both models), and they held no real slot.
8. **The budget.** One landing, of the record and this section.
9. **Done, measured.** 20 `slot-wait` lines sorted - 4 synthetic, 3 real wide, 13 real lane - six levers priced, one filed and five declined, measured 2026-11-27 (`waits.py`, `waits.txt`; the record's section 4).
10. **Before moving a constant.** n/a: `L7R_BUILD_SLOTS` and `L7R_BUILD_SLOTS_SMALL` are left as they are.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here: a measurement builder changes no source. No map changes.

**Found and left?**
- A `slot-wait` taken on a scratch slot directory is written to the event log like a real one, so `make task-time` booked 221.9 s of T355's scripted holds as waiting on a build slot and T367's record and this task's line read them as builds waiting after a dependency's edit, measured 2026-11-27 (`waits.py`, against `lint-memory/lint-wait-rows.txt`). Not fixed here: a change to the slot's event line and its readers. Filed as T426; lands before T380.

**Performance work?** yes: a measurement task, counted as performance work by the GM's words of 2026-11-20; it makes nothing faster itself


### T420 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T420 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T420's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T420's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T420 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T420 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T420 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T420's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T420's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T420 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T420 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T420 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T420's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T420's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T420 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T420 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T420 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T420's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T420's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T420 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T424 to T414 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T424 Approach (checklist part A)

1. **The goal, in the world.** The pre-warm test fails only where a pre-warm leaves a slot held, never on a copy of a let-go slot's file another test's child holds for a moment.
2. **The constraints.** `slot.rs`'s own word that a slot just let go may read held for a moment; the brief's method (451 T139, T314: the race made certain, never the machine loaded).
3. **Where each comes from.** O: the slowed scratch runs above, 2026-11-27; R: `slot.rs` lines 12-13, `tests/slot.rs` lines 125 and 320 (the same transient, met the same way).
4. **Do they describe the world here?** Yes: the slowed form failed the old check 3 of 3 on the `spare` half alone, measured 2026-11-27 (the scratch test of the Approach, run alone).
5. **The order.** After T367, T411 (carried in this tree); before their landing.
6. **The exits.** Green: the fixed check 3 of 3 on the slowed form, 30 of 30 alone. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** 3 of 3 red, then 3 of 3 green on the slowed form; 30 of 30 real runs; `make builder-checks CRATE="rust/gate/crates/rustc"` clean.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a reader of a map would see: a red batch gate on a correct pre-warm, so the check is fixed, not the code (constitution XIV).

**Found and left?** none.

**Performance work?** no - a flaky check.

### T424 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T424 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T424's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T424's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T424 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T424 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T424 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T424's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T424's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T424 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T424 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T424 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T424's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T424's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T424 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T424 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T424 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T424's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T424's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T424 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T419, T404 (bundle)

- **Approach**: two changes to `make carry` (`rust/gate/crates/land/src/land/carry.rs`) and the words that cause the first's stop. The session's hand version of job 1 (`resolve-heads.py`, copied to `dev/measurements/2026-11-27/carry-heads/`) was read as the specification by example.
  - **(a) A plan merged by HEADING** (`carry/sections.rs`, T419): each `### T<n>` heading line is a section of its own, keyed by the whole line (unique where a task id is not); T300's rules are applied per heading (a side's change taken, a removal kept where the other side left the section alone); a section only the builder has goes after the last section of its own task, else at the end; then each task's sections are put together where its first stands, ordered heading, Approach, performance checklist, then each `part <n>`'s, then `part B` ones. A heading of another kind (`Decisions`, `notes`) keeps its place after the section before it: older plans write those after their Approach (features 385, 405, 406). A section joined to the one it followed on the clone's side keeps its bytes; one in a new place gets the blank line a heading needs. The first build changed 9 plans that needed nothing, measured 2026-11-27 (the same survey as below): 3 reordered by ranking those headings as a task's heading (385, 405, 406), 6 by a blank line put between every two sections (426, 427, 430, 434, 451, 454). It stops where both sides changed one section, where both added one heading differently, where one removed what the other changed, where both changed the opening, where a side holds one heading twice, and - the stop the hand script lacked - where both sides replaced one base section with different headings (a stub filled on both sides), which the script would have kept as two main sections. "Two places" is no longer a stop.
  - **No tidy plan moves**, measured 2026-11-27 (`sections::merged(p, p, p)` over all 285 `specs/*/plan.md` by a scratch test since removed; `dev/measurements/2026-11-27/carry-heads/t419-noop.txt`): 281 come out byte-identical; the 4 that do not are plans the old merge stopped on - 3 hold a task's sections apart (417, 444, 449) and are put together, and 452 holds 16 headings twice and stops. The 451 plan at the replays' three sides: the two holding a part B apart (`72f7684524`, `cdac635559`) are put together, `a6bebcb623` comes out byte-identical.
  - **The two real carries replayed** (`dev/measurements/2026-11-27/carry-heads/t419-replay.sh`, in a scratch clone of the clone, the carry built from this tree): T355's commit `51dec6f1ba` onto `72f7684524`, the clone before the session moved T399's part B by hand (`c067fc1d27`; the commit's recorded parent `b991ec95f5~1` is that hand move, so the stop is reproduced one commit earlier), and T308's `1fb7ffff9b` onto its clone commit's parent `a6bebcb623`. Before (`t419-before.txt`): both exit 2, "the clone's side holds T399's sections in two places" and "the carried commit's parent holds T394's sections in two places", the stops of 2026-11-27. After (`t419-after.txt`): both carry and verify. Against the session's commits: T355's (`b991ec95f5`) differs by one blank line in `plan.md`, the carry's before `### T410`, where the hand left an archive comment against the heading; T308's (`3012655340`) `plan.md` holds the same lines but blank ones (`diff` with blank lines dropped: none) - the hand script rewrote every section to end in a blank line, 47 more than the clone's own text, which the carry keeps - and `request.md` one blank line more, T300's rule (c) as it was.
  - **(b) The cause** (`plan/approach.rs`): the owed block's words - `make arbiter-ruled`'s and the cohort's `approach owed:` line (`owe`) and `make tick`'s refusal (`refusal`) - now say to add it directly after the task's other sections, never at the plan's end; and `make decide` (`plan.rs`, through `approach::apart`) refuses a `part B` section of a task it decides whose preceding `### T<n>` heading names another task (a bundle's part B is its first task's), naming each and where it goes, beside the section's other findings. Only the tasks decided: a builder cannot move another task's section. Over the 451 plan the one part B (T399's) stands in place.
  - **(c) A done ref kept outside the clone** (`carry.rs`, `spent`, T404): refs are shared by every worktree, so a carry's verified end in a linked worktree deleted the ref of a done commit the clone still lacked. The ref is now deleted only where the carry ran in the clone's main worktree (`marks::main_top` of the tree's git common directory, compared by `marks::same_tree`); elsewhere the carry keeps it and says `; still waiting on its carry into <clone>, which this tree is not: <ref> kept`, at both ends that spend one (carried, and already in history). Not `builder_done`'s author-time-and-subject test: an empty pick leaves no such commit in HEAD, and its ref is spent in the clone all the same (T397's case, whose test passes unchanged).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a plan merged by heading | `a_plan_whose_tasks_sections_stand_apart_is_merged_by_heading_and_put_together` (exit 2 on the old code, the T308 stop), `a_tasks_sections_are_put_in_their_order_and_a_tidy_plan_is_left_as_it_is`, `a_long_heading_is_named_by_its_first_sixty_characters`, red on the old code; `sections_merged_takes_each_side_s_change_and_stops_on_a_choice`, `a_plan_section_both_sides_changed_stops` restated for the heading's words - 5 of 154 land tests red on the old code | n/a: tooling | none | none |
| the owed block's words and decide's refusal | `a_trigger_owes_a_block_stamped_after_it` (the two messages), `a_part_b_apart_from_its_tasks_sections_is_named` | n/a: tooling | none | none |
| a done ref kept outside the clone | `a_carry_outside_the_clone_keeps_the_done_ref_the_clone_still_waits_on`, red on the old code (1 of 155); `a_done_commit_is_carried_by_its_ref_after_its_tree_went_to_the_next_task` unchanged | n/a: tooling | none | none |

### T419, T404 Approach (checklist part A)

1. **The goal, in the world.** A carry never stops because a task's sections stand in two places on any side, and no carry outside the clone hides a done commit the clone still waits on.
2. **The constraints.** T300's: all of a pick's conflicts or none; the end verified; a choice between the sides never made for the session. Added: a tidy plan is never reordered by a carry.
3. **Where each comes from.** O: the two stopped carries of 2026-11-27, replayed; O: `resolve-heads.py`, the session's resolution; O: `builder_done.rs`'s carried test, read; G: the brief's words for T419 and T404, the session's.
4. **Do they describe the world here?** Yes: the real carries replayed and compared with the session's commits, and every plan in the repository merged against itself.
5. **The order.** After T300 (its rules restated per heading); before T400 and T423.
6. **The exits.** Green: the land and plan crates' tests and both replays carried. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One probe dropped: the first build changed 9 plans that needed nothing (above); an unknown heading now keeps its place, and a join the clone had keeps its bytes.
8. **The budget.** One landing.
9. **Done, measured.** Both stopped carries of 2026-11-27 carry untouched (2 of 2, where 0 did); 281 of 285 plans unchanged by a merge against themselves, the 4 others ones the old merge stopped on.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The session resolves no plan.md by hand for a part B written apart, and a builder's or scratch carry leaves `make builder-trees` listing the done commits the clone lacks.

**Found and left?**
- `specs/452-building-plan-followups/plan.md` holds 16 heading lines twice (the stubs of T001 to T008 with their Approach headings), so a carry whose plan conflicts there stops; observed 2026-11-27, method: the merge of every plan against itself above. Not fixed here: another feature's plan, which of each pair is kept is that feature's reading. Filed as T423; lands before T400.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop faster - a stopped carry is the session's turns while trees stand idle, `dev/measurements/2026-11-27/tree-idle/results.md`); no engine speed, so no checklist.

### T419 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T419 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T419's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T419's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T419 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T419 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T419 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T419's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T419's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T419 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T419 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T419 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T419's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T419's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T419 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T419 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T419 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T419's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T419's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T419 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T404 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T404 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T404's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T404's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T404 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T404 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T404 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T404's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T404's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T404 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T404 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T404 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T404's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T404's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T404 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T404 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T404 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T404's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T404's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T404 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T425 (found by T420, 2026-11-27: of the 13 real waits for the small lane from 00:20Z to 03:56Z, 87.4 s, a wide build slot stood free for 85.7 s, measured 2026-11-27 (the event logs' `slot-wait` and `slot-small` lines, `dev/measurements/2026-11-27/slot-waits/waits.py`))

- **Approach**: one change in the checks' tool, `l7r-rust` (`rust/gate/crates/rustc`, `rustc/slot.rs`). A build or lint pass told alone (T347, T355: `cargo_small` in `rustc.rs`, the only caller of `around_small`, which the binary key's test build, a red build's second asking and each lint pass take) that finds the lane held now takes a wide slot FREE at that instant, never a place in the wide queue. `take` becomes `take_or(first, also, ...)`: one wait loop, which at each look asks the lane (`first_free` of `small-<i>`) and then, only if the lane is held, the wide slots (`slot-<i>`), and takes the first free file of either. With the lane and both wide slots held it waits on both at once without spinning: no thread and no blocking lock, a `flock -n` start a slot file a look (three a look at the default widths) and the lane's poll (500 ms, a GUESS knob) of sleep between looks, on the lane's ceiling, notice and clock, so it ends at whichever frees first. The wide side is only an extra: where it cannot be asked (no wide slots, a `flock` that cannot start) it gives no slot of its own and the wait goes on in the lane, while a lane that cannot be asked still runs without at once, as before. A wait is one `slot-wait` line as before, and the build's `slot-small` line says which it took: code 0 the lane, 2 a wide slot (`OVERFLOW`, new), 1 none. No new step name, so no task-time category: the readers book `slot-small` to no category (`phase.rs`), and its wait stays booked as `waiting on a build slot` through `slot-wait`. The waiter's minute and ceiling lines name the holders of both sets. Memory: a build of the lane's class is 1.42 GiB at the most, measured 2026-11-26 (`dev/measurements/2026-11-26/small-build-memory/results.md`), inside a wide slot's 2.0 GiB of T347's paper budget (1.4 sessions + 2 x 2.0 wide + 1.6 lane room, a 7 GiB margin, GUESS knobs); the lane two wide was priced by T420 and left (1.4 + 4.0 + 2 x 1.42 = 8.2 > 7). `take` (one set) stays for the tests only (`#[cfg(test)]`), every call of the checks taking through `take_or`. `run_in` (T364) is untouched.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a held lane takes a free wide slot | `a_build_told_alone_that_finds_the_lane_held_takes_a_free_wide_slot_at_once` and `with_the_lane_and_both_wide_slots_held_it_waits_and_takes_whichever_frees_first` (`rustc/tests/overflow.rs`) red on the old code, 131 passed, 2 failed, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/rustc`: the first waited out its 2 s lane ceiling and ran without, the second waited the lane's while a wide slot freed), then green; `a_wait_on_the_lane_and_the_wide_slots_names_every_holder_and_ends_at_the_lane_s_ceiling` (green on both, a pin) and `a_wait_on_both_names_every_holder_of_each_and_the_lane_s_knob` (the lines' words, and a wide set that cannot be asked waiting on to the lane's ceiling); 134 passed in `make builder-checks` and in three `FRESH=1` repeats | n/a: tooling | none | none |

### T425 Approach (checklist part A)

1. **The goal, in the world.** A builder's test build or lint pass of one crate alone never waits for the small lane while a wide slot is free; it waits only where the lane and every wide slot are held, and then for whichever frees first.
2. **The constraints.** T347's memory budget (a lane-class build in a wide slot's room, never a second lane); T284's never a deadlock, never a refusal (one slot held, none waited for while held); the lane is still preferred, so a wide slot goes to a lane build only where the lane is held. T364's `run_in` untouched (the brief).
3. **Where each comes from.** O: T420's record (`dev/measurements/2026-11-27/slot-waits/results.md`, lever table: 85.7 of 87.4 s, about 570 s a day at the window's rate, a GUESS scaling). O: T347's memory figures (`dev/measurements/2026-11-26/small-build-memory/results.md`).
4. **Do they describe the world here?** Yes: the red tests reproduce the case on the old code - a held lane with a wide slot free waited the lane's whole ceiling, measured 2026-11-27 (`make rust-test`).
5. **The order.** After T347, T355 and T420; beside T364, which changes `run_in` and not the slot.
6. **The exits.** Green: the rustc crate's 134 tests and lint, measured 2026-11-27 (`make builder-checks CRATE=rust/gate/crates/rustc`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The two red fixtures green: a held lane with a wide slot free takes it with no wait (`slot-small 2`, no `slot-wait`), and with all three held a wide slot freed first is taken (`slot-wait 0`, `slot-small 2`), the lane freed first is taken (`slot-small 0`). In the world, `slot-small` lines of code 2 count the overflows; the saving expected is T420's 85.7 s of the window, about 570 s a day (a GUESS scaling), read again with `waits.py` over a later window.
10. **Before moving a constant.** n/a: no knob moves; `OVERFLOW` is a line code, not a tunable.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder's `slot-wait` seconds for the lane, where a wide slot was free, go to about none; `make task-time`'s `waiting on a build slot` shrinks by them.

**Found and left?** none.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop faster). Of 87.4 s of real lane waits in 3.61 h, 85.7 s had a wide slot free, measured 2026-11-27 (the event logs, `dev/measurements/2026-11-27/slot-waits/waits.py`), about 570 s a day at that rate (a GUESS scaling, x 6.65); those waits now end at once where a wide slot is free. No engine speed, so no checklist.


### T425 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T425 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T425's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T425's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T425 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T425 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T425 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T425's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T425's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T425 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T425 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T425 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T425's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T425's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T425 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T425 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T425 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T425's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T425's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T425 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T426 to T355 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T426 to T426 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T431 to T369 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T430 to T430 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T405 to T415 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T427, T428 Approach (checklist part A)

1. **The goal, in the world.** A builder in its wrap-up band can write nothing but its handoff and scratch under `/tmp`, by any route; and a session reading a resume refusal is told truly what the resumed builder may run.
2. **The constraints.** T427's and T428's lines; T417's band (`band.rs`, its section); the root `CLAUDE.md`'s guard rule (match invocations, not mentions: a quoted `>` passes); every changed guard message a message-check (451 T170, T338's hand route).
3. **Where each comes from.** O: T417's plan review's probe (the redirect), T417's builder (the stale line), both on the task lines; the walk's behavior read from `shared/src/tree.rs` (`writes_in`, `redirects`, `sanitize`).
4. **Do they describe the world here?** The unit tests and the suite's case 12 above, red with the check off, measured 2026-11-27.
5. **The order.** T427, then T428 (the same file, the message last so its check judged the final text).
6. **The exits.** Green: the tests above, `make builder-checks CRATE="rust/guard rust/guard/shared"` clean, the suite 102 of 102, `make guard-messages` clean. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** The suite's 102 cases and the two crates' tests green, measured 2026-11-27 (this tree's suite run and `make builder-checks`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** T427: a builder past the cap could write a source file through a redirect the band let through. T428: a session reading the resume refusal was told a resumed builder in its band could run nothing but its handoff.

**Found and left?**
- The shared walk misses a redirect spelled `>& FILE` or `>&FILE`: `REDIRECT`'s capture excludes `&` and `DUP_FD` strips only `>&<digit or ->`, so `tail -n 0 x >& rust/a.rs` writes a file no walk reader sees (main-tree, house style alike; the band now refuses any such `>&` whole, fixed here; observed 2026-11-27, method: reading `REDIRECT` and `DUP_FD` in `shared/src/tree.rs`, the one place every walk reader's redirects are found). Not fixed here: a change to the shared walk's redirect pattern reaches every guard that reads it, past this bundle's two jobs and its first-tier checks. Filed as T433; lands before T420.
- The shared walk reads no redirect of a `cd` or `pushd` segment: `walk_text` moves the shell and continues before `writes_in`, so `cd /t > /diagram/x.rs` truncates a file no walk reader sees (observed 2026-11-27, method: the band's probe above, then reading `walk_text`'s `cd` branch, the one place a segment's writes are skipped). The band refuses such a `cd` whole, fixed here. Not fixed here: a change to the shared walk's `cd` branch reaches every guard that reads it, past this bundle's two jobs and its first-tier checks. Filed as T436; lands before T420.

**Performance work?** no - a guard's gap and a message, defects.


### T427 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T427 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T427's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T427's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T427 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T427 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T427 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T427's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T427's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T427 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T427 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T427 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T427's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T427's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T427 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T427 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T427 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T427's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T427's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T427 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T428 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T428 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T428's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T428's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T428 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T428 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T428 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T428's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T428's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T428 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T428 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T428 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T428's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T428's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T428 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T428 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T428 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T428's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T428's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T428 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T230 to T239 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T436 to T427 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T437 to T369 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T438 to T369 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T364, T341 Approach (checklist part A)

1. **The goal, in the world.** A test run's phase ends when its binary exits, whatever the binary left behind, and the leak is said. A one-line edit of a guard crate starts its build in about 0.3 s, not 2 s, measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`).
2. **The constraints.** T101's leak pin is unchanged (`leak_checked` reads TMPDIR after the run, as before). Every byte a program writes before its exit is still read. A rebuilt tool never reads another binary's views.
3. **Where each comes from.** O: T340's measurement in T364's line (binary exit 2.00 to 2.04 s, pipe end 5.16 to 5.18 s, measured 2026-11-26 (T340, the binary by hand into a pipe)). O: T315's figures in T341's line. O: the step lines of 2026-11-27 (`checks-start/`). O: `l7r-gate.sh` line 166, read.
4. **Do they describe the world here?** Yes. Both were reproduced in this tree: the red test took 5.008 s on the old `run_in`, measured 2026-11-27 (`make rust-test`), and before the fix the step lines showed the views recomputed on every edited run.
5. **The order.** After T340. Before T363, whose failing half reads the same holders.
6. **The exits.** Green: the rustc crate's tests (130) and the after-runs. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The guess in T341's line (the kept key over the guard's sources and declared reads) was measured and is not the cost: the verdict key and the telling took 0.02 to 0.2 s, measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`).
8. **The budget.** One landing.
9. **Done, measured.** A held pipe costs at most `DRAIN` (250 ms, a GUESS knob) past the exit, where it cost the holder's whole life. An edited `rust/guard` run reaches its build at 0.30 to 0.33 s (load 9 to 10), where it took 6.95 to 7.66 s at load 45, measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`), and the full recompute it skips is 1.93 s at load 12, measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`).
10. **Before moving a constant.** `DRAIN` is new, a GUESS knob (above).
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder's `make rust-test` of a crate whose test leaves a process behind ends at the binary's exit and names the process. An edited guard crate's run re-reads only the files whose content moved.

**Found and left?**
- A real rebuild of `l7r-rust` (after an edit of `rust/guard/shared`, `core`, `tree` or `rustc`) still recomputes all 1,504 files' code views, 1.9 s at load 12 on top of the 2.0 s rebuild, measured 2026-11-27 (step lines), because the views are keyed by the whole binary; observed 2026-11-27, method: the step lines' first run after the fix's own rebuild. Not fixed here: keying the views by the code that computes them needs a test that holds that key to every function the views call, which is a mechanism of its own. Filed as T434; lands before T365.
- A green `cover` run does not show the `HELD` line: `cover_ran` rebuilds its result from the lines missed, so the tests' stderr is dropped (`rustc/cover.rs`, `run_one`); the cut still saves the time; observed 2026-11-27, method: `run_in`'s callers read (`side.rs`, `cover.rs`, `times.rs`, `cargo_in`), the other three keeping stderr into `answer`. Not fixed here: T363's failing half makes a held pipe a red crate through `leak_checked`, which the cover run also takes, and a red cover run shows its stderr. Filed as T363; lands before T365.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the checks faster). T364: a leaked process's hold on the pipe, 3.1 s in T340's case (measured 2026-11-26 (T340, the binary by hand into a pipe)), is cut to at most 250 ms (`DRAIN`, a GUESS knob). T341: the pre-build window of an edited guard crate went from 6.95 / 7.66 / 7.50 s (load 44.8 / 45.4 / 44.6) to 0.30 / 0.30 / 0.33 s (load 9.3 / 9.9 / 10.5), measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`), and the work removed, the 1,504-file views recompute, is 1.93 s at load 12, measured 2026-11-27 (step lines, `dev/measurements/2026-11-27/checks-start/`). No engine speed, so no checklist.

### T364 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T364 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T364's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T364's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T364 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T364 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T364 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T364's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T364's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T364 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T364 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T364 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T364's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T364's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T364 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T364 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T364 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T364's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T364's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T364 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T341 part B (2026-11-27T07:20Z)

Owed by red-gate@2026-11-27T06:33:54Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T07:20Z): the batch gate of feature 451's
staged tasks was red twice in a row, at 06:26Z-06:33Z the second time (2026-11-27, the landing's log). T341 is a task of that
batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's hook suites and coverage: `parts.sh.3` (14 FAILs, an empty exec path) and
   `context-cap-hooks.sh` (the T427 redirect cases) because the clone's guard binary had failed to link since about 05:47Z, and
   rustc's drain test's 2 s bound under a coverage build (observed 2026-11-27, method: the landing's log and the kept suite logs).
2. **A3 again.** The goal and the options stand as T341's section has them; the red is in a stale build and one test's bound,
   not in a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T341's change is untouched; the repair is the guard's rebuild and the drain test's bound
   (45792d53b7), with the link failure filed as T449.
6. **The one-sentence test.** "Why is T341 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more with the guard freshly linked and T449 in the batch (the
   arbiter's ruling).
8. **Every route measured?** The guard rebuilt and `context-cap-hooks.sh` passed alone against it (2026-11-27, run by hand in
   the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a repeat of these three failures is this finding again, a red
   anywhere else a new finding for its own task.

### T341 part B (2026-11-27T09:25Z)

Owed by red-gate@2026-11-27T09:06:32Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:25Z): the batch gate of feature 451's
staged tasks was red again at 09:06Z (2026-11-27, the landing's log), its causes new since the 06:33Z red. T341 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: the regex-scan check on two test fixtures in the rustc crate's
   `kept/code/tests/reach.rs` and a memchr byte search in `event_log_hooks/reversal.rs` it read as a regex scan, and coverage's
   lines no test reached in eight crates (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T341's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T341's change is untouched; the repair is the session's 5b2bf5b0d3 (fixtures renamed,
   the byte search through memmem's free function, assertion messages dropped, three tests added).
6. **The one-sentence test.** "Why is T341 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the eight crates is green after the repair (2026-11-27, run in the
   clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of the 09:06Z findings again, or a failure in the repair's own
   lines, is the fixes not converging; a red only in work carried since 09:06Z is new material.

### T341 part B (2026-11-27T09:45Z)

Owed by red-gate@2026-11-27T09:39:16Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:45Z): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T341 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T341's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T341's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T341 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

### T341 part B (2026-11-27T09:53Z)

Owed by red-gate@2026-11-27T09:39:13Z, ruled continue by the round arbiter (`arbiter.jsonl`, 2026-11-27T09:53Z, recorded again under the id the landing names; the 09:45Z sections answer the mis-keyed one): the batch gate of feature 451's
staged tasks was red again at 09:39Z (2026-11-27, the landing's log), three of its lines in the 09:06Z repair's own. T341 is a task of
that batch; the red was not in its change.

1. **What exactly is refusing?** The batch gate's static step: coverage's lines no test reached - three in the session's 09:06Z
   repair (a folded branch in `rustc/only.rs`, an environment closure in `task_add.rs`, a skip in `reversal.rs`), the rest in
   tasks carried since - and land-alone's test asserting a copy T442 removed (observed 2026-11-27, method: the landing's log).
2. **A3 again.** The goal and the options stand as T341's section has them; the red is in tests and two call shapes, not in
   a decision of this task.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: T341's change is untouched; the repair is the session's 7057dc718b (the red branch moved
   to the caller, the environment read named and tested, the skip written as a condition, the land test made current).
6. **The one-sentence test.** "Why is T341 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands (the arbiter's ruling).
8. **Every route measured?** `make builder-checks` over the six crates is green after the repair, and the crates' coverage
   was run before the gate (2026-11-27, in the clone); the rest is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; any of these three lines, or a line 7057dc718b wrote, failing again
   is a process fault; a red only in work carried since 09:39Z is new material.

<!-- plan-archive: T434 to T341 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T439 to T373 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T447 to T397 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T447 to T447 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T470 to T463 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T485 to T481 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T485 to T485 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T486 to T485 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T495 to T487 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T490 to T387 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T504 to T388 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T505 to T490 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T506 to T490 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T507 to T490 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T508 to T507 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T510 to T510 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T512 to T512 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T515 to T515 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T517 to T515 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T519 to T519 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T513 (T512-D5's finding: the main session's calls were booked by the next own event-log line, which named only the session's `make task-start` mark - 2,682 calls read back from 2026-11-27T04:30Z to no task, observed 2026-11-27, method: `make task-time SINCE=2026-11-27T04:30:00Z` before this task)

- **Approach**: the writer tags the main session's own line with the tasks its call names, and the report books each session call by its own tool calls, not by the next line in time (`rust/guard/shared/src/guards/event_log_hooks/fields.rs`, `rust/gate/crates/measure/src/measure/where_time/columns/spent.rs`, `task_time/turns.rs`, `task_time/beside.rs`, `task_time.rs`).
  - **T513-D1, what a call names.** One function, `event_log_hooks::session_names`, read by both the writer and the report. For a Bash call it is every `T=` value outside a heredoc (`T=T5`, `T=T5,T6`, `T="T5 T6"`), else each done ref the command names (`refs/l7r/done/451-T462`, which is how `make carry COMMIT=` is fed). For an Agent call it is the description's task ids, else the prompt's first line's (the `BUILDER-BRIEF` marker), else its `Blocks:` line's. Each task is named once, in order. A call naming several is booked to the first, as a bundle's builder is (T514 shows the bundle whole).
  - **T513-D2, the writer.** The main session's own `PreToolUse` and `PostToolUse` lines carry `names`, a new field. A builder's line carries none: a builder's `make plan-section T=<another>` reads another task's section for its own. `task` is unchanged. Widening it would move the line's filing, the re-numbering, the static-run count and the closing split.
  - **T513-D3, the reader.** A session call is booked to the first task its tool calls name. The names come from the call's own `PreToolUse` line by tool-use id (its `names`), else, for a line written before the field, from `session_names` over the transcript's call. The line's log gives the feature. The transcript reader now keeps each session call's tool calls across every row of its message id (`spent::Call`).
  - **T513-D4, a defect fixed in the old reader.** It booked a call to the next no-`by` line in time. Pool trees' check runs share the session's id with no `by`. Of the session's 1,278 calls in the window, the old rule booked 150 to a builder's `Phase` line, 10 to a subagent's start or stop line and 176 to the mark T312; it booked 151 to a task the line named, and left 791 unbooked before the carry filter, observed 2026-11-27, method: the session transcript's calls joined to the next no-`by` line of the 451, 461, 462 and `_unassigned` logs, a script (`t513/sim.py` in the shared scratchpad).
  - **T513-D5, a second defect fixed: the unbooked figure's window.** The 2,682 counted every session call of the read-back, which runs `BACK` hours before SINCE, and not only those of the window: the window holds 1,267 session calls, observed 2026-11-27, method: the transcript's message ids timestamped from 04:30Z counted. Unbooked calls are now counted from SINCE only. A call before SINCE is still booked to a landed task it names.
  - **T513-D6, what stays unbooked, and why.** It is printed by class: a reply with no tool call, tool calls naming no task (the session's own `grep`, `sed`, `git` reads), a task named with no own line to file it, and a call after its task's carry, which is the second tier's (T512-D5's rule, kept). No call inherits a task from the call before it. That would be a convention no record backs.
  - **T513-D7, before and after**, measured 2026-11-27 (`make task-time SINCE=2026-11-27T04:30:00Z UNTIL=2026-11-27T19:22:17Z`, read-only, the same window both times). Before: 2,682 calls booked to no task, their tokens 1,436,284.4k, measured 2026-11-27 (the command above, before this task). That figure includes the read-back before SINCE (D5). After: 919 of the window's calls booked to no task, their tokens 483,389.7k (cache read 481,720.5k). They are 258 replies, 594 tool calls naming no task, 0 named with no line, and 67 after their task's carry. With no UNTIL, the report to 19:41:13Z reads 930 (264, 599, 0, 67), measured 2026-11-27 (`make task-time SINCE=2026-11-27T04:30:00Z`).
| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the writer's `names` | `event_log_hooks::tests::named::a_session_call_names_the_tasks_its_command_or_dispatch_names`: with the field's write switched off, 0 passed and 1 failed (`left: None, right: Some(["T5"])`); 1 passed after, observed 2026-11-27, method: `make rust-test CRATE=rust/guard/shared ONLY="guards::event_log_hooks::tests::named"` | n/a, a log field | none | n/a |
| the reader: a call's own tool calls, the line's names before the transcript's, the window | `task_time::turns_tests::a_session_call_books_to_the_task_its_own_tool_calls_name`: with the line's names ignored, 1 failed (T5's calls `left: 1, right: 3`); with the window's start ignored, 1 failed (6 unbooked against 5); 1 passed after, observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/measure ONLY="measure::task_time::turns_tests"`. The size fixture's session call is now booked by its transcript's `make static T=T1` (`sized_tests`) | n/a | none | n/a |

### T513 Approach (checklist part A)

1. **The goal, in the world.** A reader of `make task-time` sees the orchestrating session's calls under the tasks they served, where the call itself names one. The rest is counted by why, inside the window.
2. **The constraints.** T512-D5's rule that a call after its task's carry is the second tier's. T512's "no new writer" covered T512 only; this task's brief asks for the writer. The GM's Goodhart caution: raw counts, no inferred booking.
3. **Where each comes from.** O: D4, D5 and D7. The brief: "tag the session's line with the task its command or dispatch names ... and read it back".
4. **Do they describe the world here?** Yes. The overnight window's session calls were read call by call against their lines (D4).
5. **The order.** After T512 and T522, which built the report this reads into. Beside T514, the same files.
6. **The exits.** Green: the tests above and D7's run. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The window's unbooked session calls fall from 2,682 to 919, each printed with its class (D7). The old rule booked at most 151 of the window's calls to a task their line named (D4).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The reader saw 2,682 unbooked calls, a figure past the window's own 1,267 calls, observed 2026-11-27, method: D5's. 336 of the calls it did book went to a builder's line, a subagent's line or the session's mark (D4). It now sees 919, each with its class.

**Found and left?**
- The old reader booked session calls to builders' `Phase` lines and to the mark (D4). Fixed here.
- The unbooked figure counted the read-back before SINCE (D5). Fixed here.

**Performance work?** yes: a measurement of where the time and tokens go, counted as performance work by the GM's words of 2026-11-20


### T514 (T512's finding: a bundle's second task read 0 turns, counts and tokens beside the commit it shares - T419 89 builder turns and T404 0, T465 24 unit-test runs and T474 0, observed 2026-11-27, method: `make task-time SINCE=2026-11-27T04:30:00Z` before this task)

- **Approach**: the bundle is shown as ONE figure, whole under each of its tasks and marked. Nothing is booked twice and nothing is split (`rust/gate/crates/measure/src/measure/task_time/beside.rs`, `task_time.rs`, `task_time/turns.rs`).
  - **T514-D1, what a bundle is.** A pool tree handed out for several tasks at once (`make builder-tree T=a,b`). It is read from the pool's log by `held::of`, the reading `held_for` already takes (`beside::bundles`). Each landed task of such a handout maps to every task of it under its own feature, itself among them. A task of two such handouts takes both handouts' tasks. A commit naming two tasks with no shared handout is not a bundle: its lines are shared, as before.
  - **T514-D2, why one figure, not booking to each.** The brief left the choice to the builder. The bundle's builder is filed under its brief's first task, and no record says which of its calls, runs or tokens served which task. Booking each to every member would count them once per member in each sum the report makes: the own path, which equals the builder minutes (T512-D4), and the window's tasks' side. Splitting them would invent a division. So each member's size row and its line beside its minutes read the bundle's unit-test runs, coverage runs, compiles, make runs, turns and tokens summed over its tasks. The row carries `(bundle T419 T404: its counts, turns and tokens the bundle's, whole)`. This is how the same table already shows a bundle's shared commit (T512-D1). The minutes, the grouped tables, the own path and each task's listed lines stay where they were booked.
  - **T514-D3, a task built inside another's tree.** T474 was filed and built by T465's builder, in a tree handed out for T465 alone. Its commit is `451 T465 T474:` (observed 2026-11-27, method: `builder-pool.log`'s handouts naming T465 or T474, and `git log --grep`). A landed task with no builder turns of its own that shares a commit joins that commit's tasks in the same way. Tasks sharing a commit that each had a builder stay apart (T365, T373, T420).
  - **T514-D4, before and after**, measured 2026-11-27 (`make task-time SINCE=2026-11-27T04:30:00Z`, read-only). Before: T404 read 0 unit-test runs, 0 compiles, 0 make runs, 0 turns and 0.0k tokens beside T419's 12, 29, 16, 89 builder turns and 15,246.8k cache read, measured 2026-11-27 (the command above, before this task). After: both rows read `12, 0.1 min each | 0 | 29 (29 of 1.0 s or more) | 16 | 89 | 0 | 3`, 16,012.1k cache read, each marked `(bundle T419 T404 ...)`. The 3 session turns are T513's. T474 reads T465's bundle the same way once D3 is built (its test, below). At one window end, 2026-11-27T19:22:17Z, the window's tasks' side moved by at most 0.1 minute in one cell (review 456.1 to 456.2, own-path builder thinking 1147.5 to 1147.4), measured 2026-11-27 (the same command with `UNTIL=2026-11-27T19:22:17Z`). That is lines written into the window after the first run. Every task's own-path line is identical, measured 2026-11-27 (the same command with `UNTIL=2026-11-27T19:22:17Z`, both runs' side rows and `Its own path` lines diffed).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a bundle's tasks, and a task built inside another's tree, read its counts, turns and tokens whole, marked | `task_time::turns_tests::a_bundles_tasks_each_read_the_bundles_counts_turns_and_tokens_whole`: with each row reading its own task alone, 63 passed and 1 failed; 64 passed after, observed 2026-11-27, method: `make rust-test CRATE=rust/gate/crates/measure ONLY="measure::task_time"`. The size fixture's T1, whose bundle commit names T9 with no builder, now carries the mark (`sized_tests`) | n/a, a report's text | none | n/a |

### T514 Approach (checklist part A)

1. **The goal, in the world.** A reader of a bundle's second task sees the work its builder did, marked as the bundle's, not zero.
2. **The constraints.** T512-D1's rule for a shared commit: whole under each task, marked, never split. T512-D4's own path equals the builder minutes. The GM's Goodhart caution: raw figures only.
3. **Where each comes from.** O: T512's finding, D3 and D4. The brief: "book to every task the marker names, or show the bundle as one row, your call, said with why".
4. **Do they describe the world here?** Yes: D4's run over the overnight window.
5. **The order.** After T513, whose session calls a bundle's row also sums.
6. **The exits.** Green: the test above and D4's run. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** T404's row reads its bundle's 89 builder turns, marked. The window's tasks' side and own-path totals are unchanged to 0.1 minute, measured 2026-11-27 (D4's run).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The reader saw T404 at 0 turns, 0 counts and 0 tokens beside a commit it shares with T419, measured 2026-11-27 (D4's before run). Now its row reads the bundle's figures, marked.

**Found and left?** none

**Performance work?** yes: a measurement of where the time and tokens go, counted as performance work by the GM's words of 2026-11-20


<!-- plan-archive: T520 to T515 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T523 to T520 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T528 to T522 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T529 to T522 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T531 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T531 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T532 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T532 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T535 to T364 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T536 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T536 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


### T537 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T537 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster, or measures where time goes: a measurement task counts, the GM 2026-11-20), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


