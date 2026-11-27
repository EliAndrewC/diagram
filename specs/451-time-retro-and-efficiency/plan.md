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
<!-- plan-archive: T104 to T99 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T104 to T104 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

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


<!-- plan-archive: T391 to T393 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

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

<!-- plan-archive: T143 to T312 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T312 to T309 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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


<!-- plan-archive: T151 to T249 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->

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
<!-- plan-archive: T159 to T154 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T159 to T159 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

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


<!-- plan-archive: T164 to T289 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T164 to T164 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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
<!-- plan-archive: T227 to T227 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T239 to T433 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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


<!-- plan-archive: T232 to T232 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T233 to T233 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->

<!-- plan-archive: T433 to T427 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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

<!-- plan-archive: T246 to T246 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T248 to T227 moved to plan-done.md, 2026-11-25 (feature 375 FR-044) -->
<!-- plan-archive: T250 to T233 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T250 to T250 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T260 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T260 Approach (checklist part A)

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


<!-- plan-archive: T261 to T84 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T261 to T261 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T261 to T84 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T261 to T261 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T263 to T263 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T264 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T264 Approach (checklist part A)

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


<!-- plan-archive: T265 to T250 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T265 to T265 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T266 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T266 Approach (checklist part A)

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


<!-- plan-archive: T267 to T267 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T268 to T263 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T268 to T268 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T269 to T258 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T269 to T269 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T273 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T273 Approach (checklist part A)

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


<!-- plan-archive: T274 to T274 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T275 to T267 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T275 to T275 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T276 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T276 Approach (checklist part A)

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


### T277 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T277 Approach (checklist part A)

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


### T278 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T278 Approach (checklist part A)

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


### T279 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T279 Approach (checklist part A)

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


### T280 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T280 Approach (checklist part A)

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


<!-- plan-archive: T281 to T285 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T281 to T281 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T283 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T283 Approach (checklist part A)

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


<!-- plan-archive: T284 to T284 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T286 to T286 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T286 to T286 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T287 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T287 Approach (checklist part A)

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


<!-- plan-archive: T288 to T369 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T288 to T288 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T290 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T290 Approach (checklist part A)

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


### T291 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T291 Approach (checklist part A)

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


<!-- plan-archive: T292 to T262 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T292 to T292 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T293 to T293 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T294 to T292 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T294 to T294 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T300 (the session resolved about fifteen stopped carries by hand on 2026-11-26, its turns at a carry builder-idle time; PART 1 of the task's carry part, the spec files - the task stays open for the generated and one-line files and for its registry tables)

- **Approach**: `make carry` resolves by rule the three spec-file conflicts the session resolved by script that day (`resolve3.py`, kept at `/home/agent/.claude/jobs/c6fd72d1/tmp/`, read as the specification by example). Measured 2026-11-26 by REPLAY (`dev/measurements/2026-11-26/carry-replay/`: `t300-replay.sh` redoes each builder commit's pick onto the parent of the clone's commit of it in a scratch clone and compares the carry's tree with the session's commit; `t300-pin.py` is the box check): of the clone's 68 commits since 2026-11-26 opening `451 T`, 54 pair with a builder's commit (same author time and subject), 30 of those conflict under a plain `git cherry-pick`; the carry before this task carried 16 of the 30 (`t300-before.txt`) and now carries 24 (`t300-job1.txt`), 16 identical to the session's commit and 8 differing only where the hand resolution was wrong (below). The 6 still stopping are this task's second job (4: `docs/make-targets.html`, the one-line and adjacent-block conflicts of T274, T285, T334 and T336's carries) and T399's (2: a `.jsonl`).
  - **(a) `plan.md` by section** (`rust/gate/crates/land/src/land/carry/sections.rs`): merged from its three whole sides, never from hunks - the clone's order kept, a section only one side changed taken from that side, one the builder removed dropped, one the clone removed left out, the builder's new ones appended; it stops where both sides changed one section, where a side removed what the other changed, where both changed the text before the first section, or where a side holds one task's sections in two places. `resolve3.py` was silent on two of those (a section the builder changed that the clone no longer has was never emitted; one the builder removed that the clone changed was dropped): both are stops here. This replaces the hunk rule of T289 for a plan (its test, two trees' filed stubs, passes unchanged).
  - **(b) `tasks.md`** (`carry/boxes.rs`): the carry's own merge already kept a box with its line (T289's by-block rule; its diff3 hunks held whole blocks in all 30 replays). The seven lost research lines were the HAND's: git's conflict block ended between a box and the line under it and the script kept both sides of the block. What the hand lost then persisted - git merges the clone's bare box cleanly - so the rule added is the pin itself: after the merge a bare open box that either side holds with lines under it takes them back, the clone's first, in the tasks.md the carry resolved and in one git merged cleanly beside a conflict. In the replay, measured 2026-11-26 (`t300-pin.py` over each carried tree), no carried tasks.md ends with a bare box either side had lines under (`pin-lost=[]` on all 24), where 11 of the session's 30 commits did.
  - **Tried and dropped**: merging a tasks.md with a box and its lines joined as one line, so no hunk could split them. It stopped three carries the line merge resolves (T251, T293, T334: "a hunk both sides changed"); recorded in `boxes.rs`'s header so it is not tried again.
  - **(c) `request.md`**: a hunk both sides only added `## ` sections to keeps both, the clone's first, one blank line between; one heading over different words stops.
  - **The last line** names each file resolved with its rule (`; resolved <path> (by section), <path> (both sides' list lines)`, also `both sides' dated sections`, `the record's merge`, `a bare box's lines restored`), where it said `both sides kept in <paths>`.
  - **The 8 differences from the session's commits, each the hand's fault**, measured 2026-11-26 (`git diff --stat` of the carry's tree against the session's commit, `t300-job1.txt`): `tasks.md` one line more in 7 (1b687e3c1f, 1ceb830054, d217a39fad, ca16aed82a, 83326f83a3, 148fa78bdf, 1783cf6eed: the research line the hand lost, restored by hand later in 39801a6844); `request.md` one blank line more in 2 (83326f83a3, 1783cf6eed: the hand left a `## ` heading on the line after the section before it); `plan.md` one blank line fewer in 2 (e8e9ab809a, d217a39fad: two blank lines before a section where the plan has one everywhere else).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a plan merged by section | `a_plan_is_merged_by_section_the_builders_filled_stub_taken_and_the_clones_withdrawn_stub_left_out`, `a_plan_section_both_sides_changed_stops`, red on the old code; `sections_merged_takes_each_side_s_change_and_stops_on_a_choice` | n/a: tooling | none | none |
| a bare box's lines restored | `every_open_box_keeps_the_line_under_it_that_either_side_had`, red on the old code; `a_tasks_git_merged_cleanly_beside_a_conflict_keeps_its_boxes_lines_too`, `a_bare_open_box_takes_back_the_lines_a_side_holds_under_it` | n/a: tooling | none | none |
| a request's dated sections kept both | `a_request_both_sides_added_a_dated_section_to_keeps_both`, `a_request_section_both_sides_wrote_differently_stops_and_one_both_hold_is_not_doubled`, red on the old code; `keep_both_takes_whole_request_sections_both_sides_added` | n/a: tooling | none | none |

### T300 Approach (checklist part A)

1. **The goal, in the world.** A builder's commit reaches the clone by `make carry` without the session's hand: the spec files every parallel carry conflicts in are resolved by rule, and what the rule cannot decide stops with the files named, as before.
2. **The constraints.** The carry resolves all of a pick's conflicts or none; it ends verified (nothing in progress, unmerged or staged, the non-spec files in HEAD); a choice between the sides is never made for the session; an open box keeps the line under it.
3. **Where each comes from.** O: the replay of 2026-11-26's carries (30 conflicted, 14 stopping before); O: `resolve3.py`, what a correct resolution was; G: the brief's words for T300's carry part, the session's.
4. **Do they describe the world here?** Yes: measured by replaying every paired carry of the day, not by reading the scripts alone - the replay is what showed the lost lines were the hand's and not the carry's.
5. **The order.** Before the second job (the generated and one-line files), which adds rules beside these; before T399 and T400.
6. **The exits.** Green: the land crate's tests and the replay's count. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** One probe dropped (the joined merge, above); the red fixtures took three shapes before git itself conflicted on them - the real conflict's shape (the clone withdrawing the plan's last stub) is the one kept.
8. **The budget.** One landing.
9. **Done, measured.** 24 of the 30 conflicted carries of 2026-11-26 carried untouched where 16 were, none ending with a bare box.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The session at a stopped carry resolves nothing by hand for a plan.md, a tasks.md or a request.md; a builder waits that much less for its tree's release.

**Found and left?**
- A carry still stops on a line-per-record file both sides appended to or pruned (`dev/claims-triage-skips.jsonl`, `dev/gm-attribution-baseline.jsonl`; 2 of the 30 replayed carries), resolved by hand. Not fixed here: a third file class with its own rule, outside the brief's cases. Filed as T399; lands before T400.
- A pick git merges wholly cleanly is committed before the box check runs, so a bare box the builder's tree has lines for stays bare there (0 of the 30 replays; the step beside a conflict caught the 1 that would have). Not fixed here: it needs the pick made without committing, a change to the carry's whole flow. Filed as T400; lands before T392.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the landings and the builders' loop faster - the session's turns at a stopped carry are builder-idle time, `dev/measurements/2026-11-27/tree-idle/results.md`); no engine speed, so no checklist.

### T300 part 2 (the six carries of 2026-11-26 that still stopped after part 1 - four on the generated target page, a registry row or help line both sides added words to and two blocks added at one place, two on a `.jsonl`; PART 2 of the task's carry part - the task stays open for its registry tables)

- **Approach**: four rules of `make carry` for files outside a feature's spec directory, each announced in the carry's last line with its rule's name; part 1's rules are unchanged. Measured 2026-11-26 by the same REPLAY as part 1 (`dev/measurements/2026-11-26/carry-replay/t300-replay.sh`, the output `t300-job2.txt`): of the 30 conflicting carries, 30 now carry untouched where 24 did after part 1, 17 identical to the session's commit where 16 were. Anything the rules do not cover stops as before, nothing resolved, the files named; the carry still ends verified.
  - **(d) `docs/make-targets.html` is regenerated, never merged** (`carry.rs`, `resolve_all`): it is left out of the merge, and once every other conflict is written and staged the page is written by `make docs`' own code in process (`l7r_gate_cohort::make_docs::write`; the land crate already depends on cohort) from the Makefile as the pick and the other rules left it, then staged; `(regenerated)`. A stop in another file leaves the page untouched (all or none, as before). The one case that is not all-or-none: the regeneration itself failing (no Makefile, an unreadable one) after the other files are staged - the carry then exits 2 with the pick standing and says so, with the three commands that finish it. In the replay the regenerated page is byte-identical to the session's in all four carries (T274, T285, T334, T336).
  - **(e) a prose hunk is merged by words** (`carry/words.rs`; `(by words)`): for a diff3 hunk with base lines, each side is cut into words - **a word is a maximal run of non-whitespace characters, and each run of whitespace between two words, line ends included, is a token of its own** (the session's hand scripts' `\S+|\s+`) - and each side's changes against the base (`l7r_gate_core::difflib::opcodes`, Python's SequenceMatcher without junk, the hand scripts' measure) are applied together in base order. It never chooses: a change that reaches into the other side's stops (`both sides changed the same words: ...`); the same change made by both is made once (the hand scripts would have stopped or doubled it); two insertions at one point are both kept, the clone's first; changes that touch without overlapping are both made, which is diff3's own rule at the grain of a word. It never touches code: every line of the hunk, on all three sides, is a prose line of its file's kind - any line of a `.md`; a Makefile line opening `#` or a target's line holding ` ## `, whose text before the `##` (the target and its prerequisites) must be the same on every side; a `.rs` line that is wholly a comment - else it stops (`a line that is not prose: ...`), and the result is held to the same test. That last test is a guard no fixture reaches (I found no input where each side passes and the result does not); it is one line, executed on every merge.
  - **The mixed hunk is the same rule, and it held**: one side adding whole lines BESIDE a line the other reworded (measured 2026-11-26 (the diff3 hunks of the replayed picks): `scripts/container/builder-brief.md` in T334's carry: ours 3 lines, base 1, theirs 1; a reflowed `//!` paragraph of `rust/gate/crates/task/src/builder_tree.rs` in T336's, 5 lines beside 4 added) is merged by the same words rule over the whole hunk, the added lines being an insertion of words. Tried as the handoff said - before any Rust, by the hand scripts' token merge over each whole hunk, then by the built rule in the replay - and both files came out byte-identical to the session's commits b1d4a453fe and f5007f94d3. T285's two-row hunk (`task` and `land` rows of `rust/gate/CLAUDE.md`) is the whole-hunk rule too, not line by line: identical to 7af8a39d52.
  - **(f) two added blocks are kept both** (`carry/added.rs`; `(both sides' added blocks)`, or `(by words and both sides' added blocks)` where a file has a hunk of each kind): for a hunk with NO base lines. In a Makefile: each side holds a target's line, neither opens on a recipe's tab-indented line, and no target is added by both (that stops: `both sides added the target ...`) - ours, exactly one blank line, theirs, a trailing blank line kept where a side had one; identical to the session's Makefile in T334's carry. In a `.md`: list lines with their continuation lines, by part 1's own block rule for a tasks.md (`both`, unchanged) - a bullet both hold whole is not doubled, one bullet with different lines under it stops. In a `.rs`, two blocks added at one place stop: their order can matter and no replayed carry needed it.
  - **(g) a `.jsonl` by record - T399, built here** (`carry/records.rs`; `(both sides' records)`): from its three whole sides, the base's records neither side removed, in the base's order, then the clone's appended records, then the builder's. A side that changed a record in place or added one anywhere but the end stops. EACH appended record is kept, an identical line too: I read the skip log's writer (`rust/gate/crates/claims/src/claims/commands.rs`, one appended line a skipped triage, dated by day) - two identical lines are two events, and the file held 49 such lines on 2026-11-26.
  - **The end's check** (`missing`): a non-spec file a rule resolved is held whatever its text - a page regenerated to what the clone already had, or records the clone already held, is neither "moved by the carry" nor "at the commit's content", and exited 1 (the handoff's trap; `a_page_regenerated_to_the_clones_own_text_is_still_verified`, red first).
  - **The six newly passing carries against the session's commits**, measured 2026-11-26 (`git diff --stat` of the carry's tree against the session's commit, `t300-job2.txt`): T285 (7af8a39d52) identical. T274 (f40606920e), T334 (b1d4a453fe), T336 (f5007f94d3): every non-spec file identical; `tasks.md` one line more in each (the research line the hand lost, part 1's rule (b)); T336's `plan.md` holds the same lines with the builder's two new stubs (T361, T362) after the clone's last section where the hand put them among them, and two blank lines fewer (part 1's rule (a)). T298 (240c7d89f9): `dev/claims-triage-skips.jsonl` one record more, measured 2026-11-26 (`wc -l` of the carry's file and the session's) at 108 lines where the session kept 107 - the clone had appended the record twice and the builder once, and the hand kept the clone's side and lost the builder's event; `plan.md` one blank line fewer, `tasks.md` one line more, as part 1. T250 batch 8 (e3922827ac): `dev/gm-attribution-baseline.jsonl` 5 records where the session kept 42 - the hand kept the clone's side and so kept the 37 records the builder had pruned; the session pruned them later by hand in 72fdac1313, and the carry's file is byte-identical to that commit's.
  - **Still stopping**: none of the 30. What stops by rule, with no replayed case: a conflict in code or in a file with no rule (`a file the carry has no rule for`), words both sides changed, a help line whose target a side changed, two blocks added at one place of a `.rs`, a record changed in place.
  - **How the section was added**: a second section for one task, `### T300 part 2`, directly under part 1's so the task's sections stay in one place (part 1's rule (a) stops a plan that holds one task's sections in two).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the generated page regenerated | `the_generated_page_is_regenerated_from_the_merged_makefile_never_merged`, `a_page_regenerated_to_the_clones_own_text_is_still_verified`, red on the old code; `a_page_that_cannot_be_regenerated_and_a_file_with_no_rule_stop_with_the_pick_standing` | n/a: tooling | none | none |
| a prose hunk merged by words | `prose_lines_both_sides_added_words_to_are_merged_by_words`, `lines_one_side_added_beside_a_line_the_other_reworded_are_merged_by_words_and_a_list_takes_both_bullets`, `words_both_sides_changed_stop_and_nothing_is_resolved`, red on the old code; `words_are_merged_only_in_prose_and_never_by_choosing`, `a_files_kind_is_read_from_its_name` | n/a: tooling | none | none |
| two added blocks kept both | the page's and the mixed hunk's tests above (a Makefile's blocks, a list's bullets), red on the old code; `added_blocks_are_kept_both_only_where_the_files_kind_says_what_a_block_is` | n/a: tooling | none | none |
| a `.jsonl` by record (T399) | `a_line_per_record_file_keeps_both_sides_appended_records_and_drops_what_either_pruned`, red on the old code; `a_record_changed_in_place_or_added_inside_the_file_stops` | n/a: tooling | none | none |

### T300 part 2 Approach (checklist part A)

1. **The goal, in the world.** A builder's commit reaches the clone by `make carry` without the session's hand in the files every tooling task meets another in: the generated page, a registry row, a help line, a new target's block, a record log.
2. **The constraints.** Part 1's: all of a pick's conflicts or none; the end verified; a choice between the sides never made for the session. Added: code is never merged by words; the generated page is never merged at all.
3. **Where each comes from.** O: the replay of 2026-11-26's 30 conflicting carries; O: the session's hand scripts `resolve334.py` and `resolve336.py` and its commits, what a correct resolution was; G: the brief's words for T300's carry part, the session's; O: the skip log's writer, read for rule (g).
4. **Do they describe the world here?** Yes: every rule was run on the real carries and compared byte for byte with what the session committed, and each difference traced to the hand (above).
5. **The order.** After part 1 (in the tree); before the task's registry-table part, which makes rule (e) fire less often but not never; before T400.
6. **The exits.** Green: the land crate's tests and the replay's count. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one design (a whole-hunk word merge) was prototyped on the five real hunks before it was built and held on all five; the two fixtures corrected while building were mine (an expected stop that is a clean merge by words, and a code file the base already held).
8. **The budget.** One landing.
9. **Done, measured.** 30 of the 30 conflicted carries of 2026-11-26 carried untouched where 24 were, each newly passing one's non-spec files identical to the session's commit or differing where the hand lost a record.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The session at a stopped carry resolves nothing by hand in a generated page, a registry row, a help line, a new target's block or a record log; a builder waits that much less for its tree's release.

**Found and left?** none - T399, which part 1 filed and left, is built here as rule (g); T400 stays open as part 1 left it.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the landings and the builders' loop faster - the session's turns at a stopped carry are builder-idle time, `dev/measurements/2026-11-27/tree-idle/results.md`); no engine speed, so no checklist.


### T301 (the host's scan of 2026-11-26: one cargo target directory holds 20 to 31 hashes of one crate, and the GM asking that day why a builder's repeated test runs could not reuse more of their compilation; PART 1 of the task's four, the measurement of why - the task stays open for parts 2 to 4)

- **Approach**: a measurement, no code changed. This is PART 1 of T301 (why the hashes); its parts 2 (what to evict), 3 (the scratch sweep's patterns) and 4 (the loose profraw files) are later builders'. Scripts kept in `dev/measurements/2026-11-26/cargo-hashes/` (`fingerprints.py`, `eras.py`, `gate-call.sh`); every read of the session clone's cache was read-only, every build was in the pool tree `diagram-backlog-t271`'s own target directory.
  - **The verdict.** No setting flips between the gate's cargo calls and forces a crate to be rebuilt: each call run again with nothing changed is all `Fresh`, before and after every other step. The hashes are NOT source history either - a source edit rebuilds in place under the same hash. They are (a) the build CONFIGURATIONS that live side by side by design (a test build against clippy's check, a crate's own features on and off), (b) those multiplied by every past value of the profile (CONFIG history: `debug = "line-tables-only"` became `debug = 0` on 2026-11-25, 451 T246), and (c) siblings that differ only in a DEPENDENCY's hash, which come from which features a dependency gets from the packages one call selects, and from past edits of a manifest's dependency list. (c) is real compile time and is filed (T325); (a) and (b) cost disk only.
  - **A hash is not a source state**, measured 2026-11-26 (`gate-call.sh`: the gate's `cargo test --no-run --message-format=json` with `-v` for `--quiet`, from the tree's root into the tree's target): `rust/gate/crates/registry/src/lib.rs` touched twice and rebuilt twice, `.fingerprint/l7r_gate_registry-*` 9 directories before and 9 after; `rust/gate/crates/core/src/lib.rs` touched and all 28 gate manifests rebuilt, the workspace's fingerprint directories 214 before and 214 after. Cargo's `-<hash>` is its metadata hash - package, features, profile, mode, the dependencies' hashes, the compiler - and a path crate's source content is not in it.
  - **How the gate invokes cargo** (read 2026-11-26: `rust/gate/crates/rustc/src/rustc.rs`, `rustc/kept.rs`, `rustc/side.rs`, `rustc/cover.rs`, `rustc/times.rs`, `scripts/gates/l7r-gate.sh`, `scripts/hooks/l7r-guard.sh`, the Makefile). Every call runs from the tree's root, so `.cargo/config.toml`'s rustflags are the same for all. `<cache>` is `~/.cache/l7r-cargo-target/<tree's name>`.

    | call | target directory | profile and mode | packages selected | features |
    |---|---|---|---|---|
    | the test build: `cargo test --no-run --message-format=json --quiet` (`kept.rs` `binary_key`; `rustc.rs` `test_args`; `times.rs`) | `<cache>/debug` | dev and test, build | ONE manifest a call | default; `--all-features` for `test-counters`; every feature but `counters` for `test-no-counters` |
    | the doctests: `cargo test --doc --quiet` (`side.rs`) | `<cache>/debug` | dev and test, build | one manifest | as the test build |
    | lint: `cargo clippy --quiet --all-targets`, then the same with `--all-features` | `<cache>/debug` | dev and test, CHECK | one manifest | default, then all |
    | the counting run: `cargo run --quiet [--features F] --bin B` with `HAMLET_DEV` | `<cache>/debug` | dev, build, no dev-dependencies | one manifest | as asked |
    | the engine: `cargo run --release --quiet` (`rustc.rs` `hamlet`; the Makefile's `HAMLET_RUN`) | `<cache>/release` | release | one manifest | as asked |
    | coverage: `cargo test --no-run --lib --quiet --message-format=json-render-diagnostics -p <each OWED crate of the family>` (`cover.rs` `build`) | `<cache>/cover-<family>/target/debug` | dev and test, build, under `cargo llvm-cov show-env`'s environment with the coverage flags moved to a `RUSTC_WORKSPACE_WRAPPER` | the owed crates, a set that changes run to run | default |
    | the tools: `cargo build --profile tool --quiet -p <one of l7r_gate, l7r_gate_rustc, l7r_browser, l7r_embed, l7r_mode_a, l7r_phases>` (`l7r-gate.sh`, flag variables cleared; a failed link once more with `CARGO_INCREMENTAL=0`) and `-p l7r_guard` (`l7r-guard.sh`) | `<cache>/tool` | tool (incremental release) | one package of seven | default |

    So `debug/` is shared by five kinds of call in two modes and three feature forms, each selecting one manifest; `tool/` by seven package selections; a family's coverage directory by one call whose `-p` set varies.
  - **What cargo fingerprints that does NOT vary**, measured 2026-11-26 (every `.fingerprint/*/*.json` of the session clone's `diagram-backlog/debug`, `cover-gate/target/debug` and `tool`: 1,514, 528 and 697 files): one `rustc` value, one `rustflags` value and one `compile_kind` in each. No RUSTFLAGS, toolchain or target difference made any of the hashes.
  - **Three crates, hash by hash**, measured 2026-11-26 (`fingerprints.py` over the session clone's cache: each fingerprint's unit, `features`, `profile` and dependency hashes, and its mode read from `deps/` - an `.rlib` a build, an `.rmeta` alone a check, a bare name a test executable).
    - `debug`, `l7r_mode_a`, 29 directories: four units (the library 9, its test 7, the binary 6, its test 7). Per unit: build against check, times `counters` off and on, times two profile values (by their dates, before and after 451 T246's `debug = 0` of 2026-11-25: the one profile edit in `git log` of `rust/Cargo.toml` in the cache's life; the hash itself does not say which setting moved). 16 of the 29 carry the old profile; 12 are the live mode-and-feature configurations; 1 is a sibling by a dependency's features (`l7r_gate_core`, `registry` and `research` vary 6 ways where the outside crates vary 4).
    - `cover-gate`, `l7r_gate_measure`, 23 directories: the library 12, its test 11, ONE mode and ONE feature set throughout. 16 carry the old profile. Within one profile value every hash differs from the next only in its dependencies' hashes - `l7r_gate_trials` and `l7r_gate_cohort` under it, and under those `l7r_gate_owed` (15 hashes, `testkit` off and on) and `l7r_gate_registry` (12, off and on).
    - `debug`, `l7r_gate_core`, 24 directories (the library 17, its test 7): check against build, `testkit` off and on, three profile values (the two above and one seen only on 2026-11-22 from 01:27 to 02:06 - not identified; the night of 451 T142, when a session exported `CARGO_INCREMENTAL=0`, which is its own profile hash), and `l7r_shared` under it with `test-env` off and on.
  - **Counted over every workspace crate**, measured 2026-11-26 (`eras.py`: a fingerprint whose profile value no build in the day-old `diagram-backlog-t271` cache produced for that unit is counted as config history - an upper bound, since that tree has built no test of the guard, `mode_a` or `phases` and no counting form, so their live hashes are counted as history too; sizes are the `deps/` files of that hash). This split is a COUNT, not an eviction list: part 2 must derive what no live configuration can produce from the configurations themselves, since evicting a live one costs its build again. The incremental caches, the host's 90 GB, follow the same explanation: `incremental/` holds one directory a workspace fingerprint directory (153 and 153 in `diagram-backlog-t271/debug` before these runs, 214 and 214 after, 72 and 72 in its `cover-gate`, measured 2026-11-26 by `ls`), under a hash of its own, so its bytes are not attributed to a row here.

    | target directory | workspace fingerprint directories | config history (a profile value no build at HEAD made) | current profile: distinct unit, mode and own features | current profile: siblings by a dependency's hash only | explained by source content | explained by a flag, toolchain or environment flip | label |
    |---|---|---|---|---|---|---|---|
    | `diagram-backlog/debug` | 681 | 520 (5.8 of 6.0 GB of `deps/`) | 131 | 30 | 0 | 0 | measured 2026-11-26 (`eras.py`) |
    | `diagram-backlog/cover-gate` | 448 | 320 (12.8 of 14.0 GB) | 61 | 67 | 0 | 0 | measured 2026-11-26 (`eras.py`) |
    | `diagram-backlog-land/debug` | 410 | 378 (1.1 of 1.2 GB) | 30 | 2 | 0 | 0 | measured 2026-11-26 (`eras.py`) |
    | `diagram-backlog-t271/debug` (a day old, after this measurement's builds; the reference) | 214 | 0 | 178 | 36 | 0 | 0 | measured 2026-11-26 (`eras.py`) |

    `tool/` was counted more coarsely: `diagram-backlog/tool` 282 directories for 41 units and 80 distinct (unit, features, profile), `diagram-backlog-t271/tool` 47 for 39.
  - **The dependency-feature axis, shown without compiling**, measured 2026-11-26 (`cargo tree --offline -e normal,dev -f '{p} [{f}]'` over `rust/Cargo.toml`): `-p l7r_gate_claims` resolves `l7r_gate_owed []`, `l7r_gate_research []`, `l7r_gate_registry []`; adding `-p l7r_gate_bundle` makes it `owed [testkit]`, `research [testkit]`; adding `-p l7r_gate_owed` instead makes it `registry [testkit]`; adding `-p l7r_gate_semantic`, `archive [testkit]`, `research [testkit]`; `-p l7r_gate_core` alone resolves `core []` where every other gate crate's tests resolve `core [testkit]`. Five gate crates carry a `testkit` feature a dev-dependency turns on (`core`, `research`, `registry`, `owed`, `archive`; `l7r_shared`'s `test-env` is the guard's), so a crate below them is built once for each combination the selected packages ask for.
  - **The reproduction in the pool tree**, measured 2026-11-26 (`gate-call.sh` in `/diagram/.clones/diagram-backlog-t271`, load average 6 to 18 of 22 cores; the replica held to the gate - after `l7r-gate.sh rust test --crate rust/gate/crates/measure` and `rust lint` of it, the hand calls found 12 of 12 packages `Fresh`).
    - The test build of `owed` twice, nothing changed: the second 0.4 s, 0 rustc runs, 5 of 5 `Fresh`, measured 2026-11-26 (`gate-call.sh`).
    - `registry/src/lib.rs` touched, then each step: the test build of `registry` (3.9 s, 2 rustc runs), of `owed` (1.2 s, 3), lint of `registry` plain (0.7 s, 2) and with all features (0.7 s, 2), lint of `owed` plain (1.5 s, 2) and with all features (1.4 s, 2), measured 2026-11-26 (`gate-call.sh`); then the test build of `registry`, of `owed` and the lint of `registry` again: 0.1 s, 0.1 s, 0.2 s, 0 rustc runs, all `Fresh`, measured 2026-11-26 (`gate-call.sh`). One edit of `registry` compiled its library four times - a build with `testkit` off (its own tests), a build with it on (under `owed`'s tests), a check off, a check on - and nothing twice in one configuration.
    - Every `Dirty` reason cargo gave, verbatim: "the file `gate/crates/registry/src/lib.rs` has changed", "the dependency l7r_gate_registry was rebuilt", "the dependency l7r_gate_core was rebuilt", "the dependency l7r_gate_owed was rebuilt", "the dependency l7r_gate_claims was rebuilt", "the file `gate/crates/measure/src/lib.rs` has changed". None names a flag, a feature, a profile or an environment variable.
    - `core/src/lib.rs` touched, then the 28 gate manifests' test builds in turn: 75 rustc runs for 58 distinct targets, so 17 (23%) were a library compiled again in another configuration - `l7r_gate_owed` 4 times, `bundle`, `archive` and `registry` 3, `claims`, `arbiter`, `research`, `core`, `semantic`, `uncited`, `trials` and `record` twice, measured 2026-11-26 (`gate-call.sh`); 34.5 s in all, measured 2026-11-26 (`gate-call.sh`) (a touch changes no content, so rustc's incremental cache answers most of it: a floor, not an edit's cost).
    - A real one-line edit of `rust/gate/crates/measure/src/lib.rs` (a constant appended, then removed): 2.4 s and 2.0 s, 2 rustc runs each (the library and its test), and unchanged 0.1 s, measured 2026-11-26 (`gate-call.sh`).
    - A configuration this tree had never built compiles from nothing with NO `Dirty` line: the first test build of `owed` here took 20.0 s for 3 rustc runs, and bringing all 28 gate manifests' test builds up took 246 s and 67 rustc runs, of which 9 were `Dirty` and 58 first builds (`measure` 19.5 s, `reviews` 21.5 s, `record` 21.9 s, `arbiter` 19.6 s), measured 2026-11-26 (`gate-call.sh`). The tree had been handed out WARM, and was: for the lint and the coverage builds its earlier tasks ran. Of the five workspace crates with the most hashes in its `debug/` before these runs, one (`l7r_shared`) had a plain test executable; the likely reason, not measured, is that until the two-tier trial of 2026-11-26 a builder's tests ran inside the coverage build, whose green keeps the plain tests' too.
  - **What this says to the GM's question** (a builder's test runs of about 19 s each, as the brief relays it), every figure measured 2026-11-26 (`gate-call.sh`, the bullets above): a run that changes one crate compiles that crate's library and test, 2 to 4 s for a large gate crate at this load, a run that changes nothing compiles nothing (0.1 to 0.4 s of cargo), and about 19 s is what the FIRST plain test build of a large gate crate costs in a tree that has not built it, or it is the tests' own run time, which no compile cache holds: `dev/measurements/2026-11-26/build-levers/m9-results.md` has the guard family's test run with nothing to compile at 14.6 s and at 23.8 s after a touch of its root library, a band about 19 s sits in. `make task-time` splits a run's `build` from its `test` (451 T05) and says which.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| no code changed: a measurement, its scripts in `dev/measurements/2026-11-26/cargo-hashes/` | n/a: nothing fixed | n/a: tooling | none | n/a |

### T301 Approach (checklist part A)

1. **The goal, in the world.** The session knows why a target directory holds 20 to 31 hashes of one crate, and whether any of the gate's builds is repeated needlessly, before any cache is swept.
2. **The constraints.** The GM's rule that disk work begins later and that time saved outranks disk (the task line's restatement of 2026-11-26): nothing deleted, the session clone's cache read only. 451 T278 (the variant sweep) and T301's part 2 read this record.
3. **Where each comes from.** G: the task line and the GM's question of 2026-11-26 about a builder's repeated test runs, as the coordinating session's brief relays it. O: the host's report `~/.claude/disk-report-from-host-2026-11-26.txt` and the measurements above.
4. **Do they describe the world here?** Yes: the host's counts were found again from inside (`l7r_gate_pool` 31 and `l7r_mode_a` 29 fingerprint directories in `diagram-backlog/debug`, `l7r_gate_measure` 23 in `cover-gate`), measured 2026-11-26 (`fingerprints.py`).
5. **The order.** Before T301's part 2 (what to evict) and before T278; T325, filed here, before either sweep is tuned, since it changes how many hashes are live.
6. **The exits.** Green: each crate's hashes explained field by field, and the pool tree's re-runs all `Fresh`, measured 2026-11-26 (`fingerprints.py`, `gate-call.sh`). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing, of this section, the three scripts and T325's line; the task is not ticked.
9. **Done, measured.** 0 of 1,539 workspace fingerprint directories in three target directories explained by source content or by a flag flip, at most 1,218 by config history, the rest by live configurations and dependency-feature siblings, and every unchanged re-run 0 rustc runs, measured 2026-11-26 (`eras.py`, `gate-call.sh`, above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here: no call rebuilds what it built, so there is no flipping setting to fix. The one cost found - a library compiled 2 to 4 times, once a feature combination - is a design choice between two forms that each need measuring, filed as T325. No map changes.

**Found and left?**
- A crate below a `testkit` crate is compiled once for each feature combination the selected packages ask for: 17 of 75 rustc runs after a touch of `core` across the 28 gate test builds, measured 2026-11-26 (`gate-call.sh`), and in the coverage build a `-p` set never asked before must compile its downstream crates instrumented from nothing - inferred from the fingerprints and `cargo tree`, no coverage build was run to time it (67 of `diagram-backlog/cover-gate`'s 128 current-profile hashes differ from another only in a dependency's hash); visible effect: seconds of every test and coverage build below `core`, `research`, `registry`, `owed` or `archive`, and the sibling hashes the sweeps then keep. `rust/Cargo.toml`'s "ONE FEATURE SET FOR EVERY GATE CRATE" comment says testing one crate never rebuilds what another built with other features, which holds for outside crates only. Not fixed here: the fix is a choice between naming the whole family in every test and coverage build and compiling the test helpers always, each to be measured, and it changes `kept.rs`, `side.rs` and `cover.rs` - a builder of its own by the sizing rule. Filed as T325; lands before T278.

- A pool tree handed out WARM compiles from nothing each configuration its earlier tasks never built: 58 first builds, 246 s for all 28 gate manifests' plain test builds in `diagram-backlog-t271`, measured 2026-11-26 (`gate-call.sh`). Not a defect and not filed: nothing is built twice, the cost is paid once a tree and a crate, and the builds are kept, and it is recorded here because it is one reading of the test runs the GM asked about.

**Performance work?** yes for part 1: a measurement task, counted as performance work for ordering by the GM's words of
2026-11-20 (it makes nothing faster itself; what it found to make faster is T325's, a `[perf]` task). Parts 2 to 4 are disk work,
which by the GM's words of 2026-11-26 in `request.md` ("the disk work and the principle behind it") begins after the talk on
parallelizing and is ordered by time saved, never by disk freed.


### T302 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T302 Approach (checklist part A)

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


<!-- plan-archive: T303 to T281 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T303 to T303 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T304 to T281 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T304 to T304 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T306 to T295 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T306 to T306 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T307 (part 1 of the task, the gate and the clone's other writers: on 2026-11-26 07:51 UTC the session, standing in the clone while its gate ran, was refused the commit of a builder's worktree, `cd /diagram/.clones/diagram-backlog-t265 && ... git add -u; ... git commit` (observed 2026-11-26, method: `make guard-log GUARD=gate-write SINCE=2026-11-26 FULL=1`, 3 firings: this one, a Write of a handoff under `.git` at 01:22, and that Write's escape at 01:22))

- **Approach**: this section is ONE PART of T307, its part (1); the task is not ticked from this landing.
  - **T307's remainder, not built here and still open on the task's box**: part (2), every check of the push asked in the landing's first pass with the table of the push's checks against the first pass's, and the way out for a task built inside another task's reviewed section; part (3) is the session's and the GM's. Part (2) was not started: the builder's brief ordered part (1) first and the two did not fit one builder.
  - **D1, part (1a), built: a commit is held only where it runs in the gated tree.** The cause as read in `rust/guard/src/guards/gate_write_hooks.rs`: the guard finds the gated tree from where its own process stands (`decide`, `top_of`), then refused a command whose text held `git commit` or `git add` (the pattern `GIT_WRITE`) or a record-writing make (`MAKE_WRITE`) whenever the gated tree showed a change the gate sees - never asking where that command ran. The rule built, `stands_here`: each such command is placed by the walk the guard's shell-write rule already uses (`shared::tree::walk_judged`: the command's `cd`s and git's `-C`), and it is held where one stands in the gated tree, where the walk cannot say where one stands (a `cd "$VAR"`), and where the pattern matches and the walk places none (a quoted `git commit`), each as before. The refusal's text is unchanged, so no message-check is owed.
  - **D2, a defect fixed in passing: a file under the gated tree's `.git` is no file of the tree.** The 01:22 firing refused a Write of `.git/l7r-handoffs/T254-<agent>.md`, a builder's handoff at its context cap; the gate's snapshot (`git diff --name-only HEAD`) never holds a path under `.git`, and the shell-write rule already let one through. The Edit and Write rule now does too.
  - **D3, part (1b), measured and NOT built.** How the gate decides the tree moved (read 2026-11-26, `rust/gate/crates/measure/src/preflight.rs`): at its start `tree()` records HEAD and the content hash of every TRACKED file that differs from HEAD (an untracked file is never held); at its end `seen_moves` compares, reads a HEAD move as the paths its diff names, and excuses a path only by `plainly_unseen`: the same bytes, one of 4 named records (`RECORDS`), one of 5 files of the active feature (`FEATURE_RECORDS`, `tasks.md` among them, `plan.md` not), or a new landing-cohort log. So `make task-add` voids a gate by its plan.md stub alone, a measurement record by its commit (the HEAD move), and `research/source-attempts.jsonl` by any appended line. What the landing's up-front check reads (`land/writers.rs`, `foreign`): every line of `git status --porcelain` after its own escape records are committed, untracked files too; it is asked in the first pass and again before the ticks, and a clone dirty when the landing STARTS is not refused but sent to land alone in the landing worktree (`land/alone.rs`, `alone_owed`) - so the refusal of 2026-11-27 for the fetch log was the log appended between those two readings, seconds apart. What the green gate is to the push (`rust/gate/crates/tree/src/stamp.rs`): a hash of the files of four areas (the engine paths, the hook scripts and their suites with the Makefile, the page assets, the browser's), which the push compares with the content it sends; a landing begun again on content a stamp covers runs no gate (`land/long_runs.rs`). The options, by what keeps FR-004's purpose (a gate must not vouch for content it did not check):

    | option | what it changes | FR-004 | cost, and why it is not a fix |
    |---|---|---|---|
    | (A) a moved path outside every stamp area is unseen by the tree check | `plainly_unseen` asks the stamp's areas | kept only if every gate phase that reads a file outside the areas is asked again at the push; `spec-lint`, the record build and the research pointers are (the push-checks table), the tests' own reads of `dev/` and `specs/` are not inventoried | an inventory of each phase's reads first; and the write, cleared at the gate, is still refused before the ticks (`writer_refusal`), swept into the tick's `git add -- <feature dir>` or refused by the push's dirty-tree line unless committed - so the landing must also commit it, which changes what `make land` commits and pushes |
    | (B) the landing commits the append-only logs as its own records (the fetch log, as it commits `dev/bypass-log`) before `alone_owed` and in `foreign` | `land/alone.rs`, `land/writers.rs`, `RECORDS` | kept for the log (its one reader outside tests, `check research-pointers`, is asked again at the push) | a research agent's log lines pushed by a landing that did not write them: it changes what `make land` pushes |
    | (C) every landing gated in the landing worktree at its commit, the clone free to write | `make land` always takes `land-alone.sh`'s route | kept whole: the gate reads only the commit it lands | each landing pays the worktree's route (its seeding and the tip taken back); it changes where every landing runs |

    Chosen: none built. Each option that lets the incident's writes go on changes what a landing commits or pushes, which the brief ruled out of a fix; (A) alone would move the refusal from the gate to the pre-tick check. Filed as T405 with this table.

  - **The tests.** `guards::gate_write_hooks::tests::a_commit_in_another_tree_is_not_held` (4 commands let through, 9 held, the handoff Write let through and a tree file's Write held) and 4 cases of `tests/hooks/test-gate-write-hooks.sh`, counted in the test's text, observed 2026-11-26, method: read from the two files after the last edit. Red-first, 2026-11-26: on the old code the guard crate gave 552 passed, 1 failed (the new test, at its first let-through command); after, 553 passed, 0 failed; the suite 30 passed, 0 failed.

### T307 Approach (checklist part A)

1. **The goal, in the world.** While the clone's gate runs, the session commits a finished builder's worktree and a builder writes its handoff without a refusal; a commit, an add or a record-writing make in the gated tree is still held.
2. **The constraints.** Feature 385 plan D13 (no write the gate would see while it runs) and feature 375 FR-004 (a gate vouches for none of a tree that moved) both stand; the refusal's text is not changed.
3. **Where each comes from.** G: T307's line in tasks.md, talked through with the GM 2026-11-26, whose part (1) asks that only writes to the tree being gated be held. O: the guard log's firings of 2026-11-26 01:22 and 07:51.
4. **Do they describe the world here?** Yes: `make guard-log GUARD=gate-write SINCE=2026-11-26 FULL=1`, read 2026-11-26, shows both commands and the session's tree for each.
5. **The order.** Before T307's tick; T405, T406 and T409 follow it and land before that tick.
6. **The exits.** Green: the new test and the suite's new cases pass and the first-tier checks are green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The guard crate's 553 tests and the suite's 30 cases pass, measured 2026-11-26 (`make builder-checks CRATE="rust/guard rust/gate/crates/land"` and `bash tests/hooks/test-gate-write-hooks.sh`); on the old code the new test fails.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome, not a difference: a commit that moves nothing the gate compares was refused, costing the session a wait or an escape for each builder finished during a gate.

**Found and left?**
- The tree check voids a gate for writes it never read, and the landing's up-front check refuses for a log appended mid-pass (D3). Visible effect: a whole gate run again, or a landing attempt lost. Not fixed here: each option changes what a landing commits or pushes, so it is larger than a fix. Filed as T405; lands before T307.
- A commit sent INTO the gated tree from a session standing in another tree is not held (the guard asks only of the tree its own process stands in). Visible effect: a gate voided; found by reading, no firing observed. Not fixed here: it needs the guard to ask of every tree a command writes, a new rule with its own suite. Filed as T406; lands before T307.
- A make's own `-C` is not read by the walk, so `make -C <another tree> tick` is held as the gated tree's while its gate runs. Visible effect: a false refusal of a record-writing make aimed at another tree; found by reading and pinned by one held case of the new test, no firing observed. Not fixed here: the walk (`rust/guard/shared/src/tree.rs`) is shared with the main-tree, gm-tree, make-only and house-style guards, so reading make's `-C` there moves their placements and owes their suites, a change of its own (observed 2026-11-26, method: read from the walk's make branch, which pushes one write where the shell stands). Filed as T409; lands before T307.

**Performance work?** yes (a `[perf]` task: it removes a wait from the landings and the builders' loop); not an engine-speed task, so the performance checklist's questions do not apply.


### T307 part 2 (the landing's first pass asks the push's own checks, and a task built inside another task's section closes with it: a push check met only after the gate costs the gate's minutes, and five filed tasks built inside other tasks' reviewed sections had no way out)

- **Approach**: this section is ONE PART of T307, its part (2); the task is not ticked from this landing, and part (1)'s section above is unchanged.
  - **T307's remainder, not built here and still open on the task's box**: part (3), one gate run for several finished and carried tasks.
  - **D1, built (by the first builder of this part, closed here): the first pass asks the push's own table.** `make land`'s first pass (`rust/gate/crates/land/src/land/cheap.rs`, `push_refusal`) calls `l7r-gate push-checks <root> --every`, the push's table run without stopping at its first refusal (`rust/gate/crates/cohort/src/push.rs`, `run_every`), told `L7R_LAND_TICKS` and `SPECIFY_FEATURE` as the push is told them, its refusal one entry of the first pass's list. Skipped: the gate's own stamp rows, which the gate writes and the landing's second pass reads, and the ledger's row, which the first pass asks in its own form naming the landing's tasks; the closing row too under a `CLOSE_OK` that states a reason, as the push skips it. One call of the same table, so a row added to the push is asked here by construction. `entry-gate.sh` joins the three gates the first pass already ran.
  - **D2, built: the closing check with the first pass.** `tick::checks` (`rust/gate/crates/task/src/tick.rs`, `close_owed`) asks the closing check where the tasks the landing would tick are every open box of the feature, its reasons joined to the last task's refusal in the tick's own words; a tooling fix the landing carries (451 T182) is no reason there.
  - **D3, a defect fixed in passing: every refusing row said whole.** The first builder showed the call's output as one tail of its last 1200 characters, as a gate's refusal is shown; with several rows refusing the earliest rows' lines were cut, the very list `--every` exists to give. `every_row_said` keeps each `sync-with-main:` line whole and cuts only the rows' own output before them, to its last 600 characters (a CONVENTION, the length of a gate's shown refusal in the same pass).
  - **D4, the first pass's closing row logs a firing.** The push's closing row writes a `closing-owes` line to the guard log when it refuses; asked by the first pass it writes one too. Kept: it records a real refusal of the push's check, and the record is what `make guard-log` counts; a landing refused there says so once, before its gate.
  - **D5, built: a task built inside another task's section.** The host's section names it on a line of its own, `Built here: T<n> - <what>` (or as a list item), read by `rust/gate/crates/plan/src/plan/inside.rs` (`built_inside`: the host found in plan.md, or in plan-done.md where its tick archived it before this task's, its verdict read as the archive reads one, `task_current` or `section_clear`). The tick of T<n> (`rust/gate/crates/task/src/tick/refusal.rs`) asks the plan gate of the HOST in its place and no Approach block of its own, and refuses, every reason together and in the first pass as at the tick: its own section filled in (a decision of its own, which its landing would remove), the host's section without a current CLEAR verdict (no escape: the host's review is the only one its work gets), or the host neither in this landing nor ticked. Accepted, the tick appends ` built inside T<host>` to its box, removes its unfilled stub (`plan::template::without_stub`, moved there from `make task-withdraw` as the one stub test) and writes a `TaskBuiltInside` line to the feature's event log. `make land` now hands the tick its landing's tasks as the first pass handed `tick::checks` them, so `T="B A"` ticks B with its host open in the same landing. `make task-withdraw` keeps refusing carried code.
  - **D6, built: `make decide` holds the line.** Its lint gains `BuiltHere` (`lint.rs`, `inside::decide_findings`): each `Built here:` line must name an OPEN box whose plan section is its unfilled stub or none, or - the section decided again after - a box already ticked built inside a task the section decides; a task the section itself decides, one no box files, a filled section and a box ticked another way are each a finding. So the host's plan review sees the line and rules on it.
  - **D7, built: the removed stub owes nothing.** `status::scope_of` reads a box ending ` built inside T<n>` (`inside::built_inside_box`, the one rule of the form, anchored at the line's end so a title saying the words is none) as it reads a withdrawn box: its removed block owes no review where it was a block of the unfilled stub, and a filled block removed beside such a box is still owed (T359-D15b). The push's reading at HEAD (`task::push_held`) asks the same `scope_of`.
  - **The parity table: each check of the push (`scripts/sync-with-main.sh` push_cmd, in its order) and whether the first pass asks it.** The table's figures, where a cell states one, are labeled in the line after it.

    | push check | before this part | now |
    |---|---|---|
    | `land --unfinished` | asked, alone, before the first pass | unchanged |
    | the dirty-tree line | asked (`writers.rs`; a dirty clone lands alone) | unchanged |
    | unrelated history | not asked | not asked: filed as T413 |
    | the plan reviews' ledger rows written | written (`write_ledger`) | unchanged |
    | the in-progress rule | asked for the landed feature alone (`ready.rs`) | the other touched spec directories and the feature pointer not asked: filed as T413 |
    | `review-gate.sh`, `plan-gate.sh` | asked | unchanged |
    | `push-checks`, every row of its table | the ledger's row asked in its own form, and the make-targets page regenerated; no other row | one `--every` call asks every row but the gate's stamp rows, which cannot precede the gate, and the ledger's, asked in the landing's form |
    | the closing row | asked only at the last tick, after the gate | asked in `tick::checks` as if ticked |
    | `entry-gate.sh` | not asked | asked |
    | `claims-gate.sh` | asked, deferred to the wait where a round is in flight | unchanged |
    | `cohort-gate.sh` (gated route) | the second pass rolls the cohort where it would refuse (`long_runs.rs`) | unchanged: its record is the second pass's |
    | `make work-budget-review` | asked in the second pass before the gate on an engine delta | unchanged |
    | `make gated-check` (gated route) | cannot precede: its condition is the green gate | unchanged; its other conditions (the `ci` crate) not read here |

    The table's counts: the push's table holds 26 rows (observed 2026-11-27, method: `scripts/gates/l7r-gate.sh push-checks --list | wc -l`), of which the first pass asks all but 3 (observed 2026-11-27, method: `AFTER_GATE` and `OWN_FORM` in `cheap.rs`, pinned by its test against the same `--list`).
  - **What the call costs.** One run on this pool tree with this part's delta took 14.27 s wall and refused one row, the audit register's, owed an entry for the new landing refusal (measured 2026-11-27 (`/usr/bin/time scripts/gates/l7r-gate.sh push-checks "$PWD" --every --skip "gate-stamp selftest" --skip gate-stamp --skip ledger-owed`)). With the entry written, a second run took 7.01 s and refused nothing (measured 2026-11-27 (the same command, run again)). The push asks the same table after the gate anyway, its stamped rows kept; the entry is `dev/audits/landing-first-pass-push-table.md`.
  - **Not verified here, and filed.** A ledger row owed for a check dispatched after the landing's last write (the second `write_ledger` after the claims wait writes and never refuses), and the plan gate's "block(s) changed since their review" in a batch landing, have no fixture yet; each is in T413. `LEDGER_ROWS_OK` is honored by the push and not by the first pass's own ledger refusal, which is stricter up front, as before this part.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| D1-D4, the first pass | n/a: no map step | n/a: tooling | none: tooling | `make land` as before, the push refusing after the gate |
| D5-D7, a task built inside another | n/a: no map step | n/a: tooling | none: tooling | `make task-withdraw` refuses as before; the task waits for a section of its own |

### T307 part 2 Approach (checklist part A)

1. **The goal, in the world.** A landing is told before its gate every refusal its push would make, and a filed task whose work was built inside another task's reviewed section is closed by that task's landing, its box saying where.
2. **The constraints.** Feature 405 D23 (the first pass prints every refusal together), feature 243 (a plan's decisions reviewed before its tasks are ticked: the host's review stands for the absorbed task's, never none), 451 T359-D15b (a box's form alone exempts nothing).
3. **Where each comes from.** G: T307's line in tasks.md, talked through with the GM 2026-11-26, part (2): every check of the push also in the landing's first pass, proved by a fixture the first pass lets through today. O: the five tasks built inside other sections named in this part's brief; the tree-idle measurement of 2026-11-27.
4. **Do they describe the world here?** Yes: the push's table was read from `scripts/sync-with-main.sh` and `push-checks --list` on 2026-11-27, and the five tasks' boxes and sections were read from tasks.md, plan.md and plan-done.md on 2026-11-27.
5. **The order.** After part (1); before part (3) and T307's tick; T413 lands before T307's tick.
6. **The exits.** Green: the new tests pass, each failing on the code without its mechanism, and the first-tier checks are green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** `make builder-checks` over the land, task, plan and cohort crates green; red first, measured 2026-11-27 (`make rust-test` with each mechanism disabled and its tests kept): the plan crate's decide test, the plan crate's withdrawn-scope test and the task crate's built-inside test each fail.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A wrong outcome, not a difference: a landing refused after its whole gate for a check its first pass could have asked, and a finished task that no command could close.

**Found and left?**
- The unrelated-history refusal, the in-progress rule over every touched spec directory, and fixtures for the ledger-row and changed-block cases above are not yet asked by the first pass. Visible effect: a landing refused after its gate on them. Not fixed here: each is its own reading of the push's shell and its own fixture, past this part's two jobs. Filed as T413; lands before T307.

**Performance work?** yes (a `[perf]` task: a landing refused after its gate costs the gate's minutes, dev/measurements/2026-11-27/tree-idle/results.md); not an engine-speed task, so the performance checklist's questions do not apply.

### T308 (the plan review's later rounds, one part of the task: of feature 451's 135 plan review rounds from 2026-11-24 to 26, 56 were not the first for their task, 169 minutes of the 373 (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts))

- **Approach**: this section is ONE PART of T308, its ALSO on the plan review's rounds; the task is not ticked from this landing.
  - **T308's remainder, not built here and still open on the task's box**: the two tiers built into the tooling (the builder's brief block of `scripts/container/builder-brief.md`, whose STOP POINT still names `make closing-checks`; the batch gate; the trial's measurement against round one) and the changed crate's coverage run tried beside the review.
  - **The measurement, whole before any rule.** Each later round was classed from the round before it - its NOT LEGITIMATE rulings or its reply, and the section's diff between the two rounds. The record, with every round's row, is `dev/measurements/2026-11-26/plan-review-rounds/t308-results.md`.

    | class | what the round was owed for | rounds | minutes |
    |---|---|---|---|
    | (a) | a found-and-left item with no filed task id | 4 | 11.0 |
    | (b) | NOT-REVIEWABLE: an unlabeled figure, or the GM's words missing from request.md | 8 | 40.6 |
    | (c) | the section edited after its CLEAR | 16 | 31.5 |
    | (d) | a real objection to a decision | 26 | 78.6 |
    | (e) | the round before unrecorded: the section edited while it was reviewed | 2 | 7.4 |

    The table's label: observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts.
  - **What the classes hold.** In (b) the GM's words were missing in 6 rounds and a figure alone was unlabeled in 2, and the unreviewable rounds before them took another 20.6 minutes (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). In (c) a real change accounts for 9 rounds, the filed ids written in for 2, a touch-up that changed no decision for 3, a caveat the review asked for for 1 and results restated for 1 (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). An id nobody had filed is the root of 8 rounds counted every way: the 4 of (a), 2 of (d) where it blocked beside a real objection, and the 2 of (c) (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). T285's fifth round was first classed (d) and is (a): the round before it blocked on one item left with no filed id, and its cure was the filing; the table, the record and `scripts/container/builder-brief.md`'s count moved with it.
  - **What today's decide already refuses: none of them.** Replayed, HEAD's `make decide` passes the section before each of the 8 (b) rounds, and refuses 16 of 124 sections on the deferral form alone, an artifact of the scratch tree's tasks.md or a section dispatched under `DEFER_FORM_OK` (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-replay.py`, HEAD's `plan decide` over each section in a scratch tree).
  - **T308-D1, built: the GM's words on the task's own line are in request.md, or decide refuses.** A plan review reads request.md and never tasks.md, so words relayed onto the task line and nowhere else come back NOT-REVIEWABLE. `lint/task_line.rs` reads each quoted span that follows "the GM" on the box line of each task `make decide` names, in single or double quotes, and refuses one that request.md does not hold, naming the heading form to append it under. Its two constants are GUESS knobs: a span shorter than `MIN_WORDS` = 4 is a term in quotes, and a single quote opens within `REACH` = 80 characters. It catches 3 of the 6 rounds (T243, T245, T285); the other 3 cited him by reference, which no script follows (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). Replayed as built over the first-round sections of the 77 tasks reviewed, against request.md as committed before each task's first round, it refuses 11: 6 whose first review itself said his words were missing (those three, T246, T298 and T316), 3 whose words stood uncommitted in the builder's own request.md, which the replay could not see and a builder's `make decide` would have, and 2 false refusals, T241 and T235, where the line quotes words request.md does not hold and the review raised nothing about them (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-d1replay.py`, `l7r-gate plan decide` over each section in a scratch tree, read beside each round-1 reply). The 2 are accepted: the refusal's second remedy, correcting the task line, cures each in one edit, against a round of minutes for each of the 6. It is judged at `make decide` only: `make plan-delta` reads blocks, and two blocks of one task would report it twice.
  - **T308-D2, built: two figure forms the lint did not read.** A count's numeral takes a `k`, `K` or `M` suffix (T235's `about 70k tokens`) and a rounded figure with a unit is a figure (T259's `20-odd minutes`). A rule's threshold reads the same numeral, so `past 300k tokens` stays the limit it was and not a count. Each flags its one sentence and no other in the 124 reviewed sections (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-figures.py` over the reviewed sections).
  - **T308-D3, built: decide says which later edits void the verdict.** On a section owed a review, `make decide` ends with the rule as the code has it: until the reviewed section is committed, any edit of it voids the verdict and owes another round, an edit outside the section alone being kept; once it is committed the verdict is kept across whitespace, re-wrapping, case, punctuation and a typo-scale respelling (`sections::typo_only`, unchanged); and an edit while the review runs gets its record refused. It refuses nothing. The first half is what a builder meets, since a builder's tree never commits: `record_task` keeps the section's digest and no text, and the earlier text a typo is told from is read from plan.md's committed versions only, which `status::tests::a_task_verdict_survives_a_typo_only_once_its_reviewed_section_is_committed` pins as today's behavior. The notice first said the typo-scale edits were kept, which that test showed false for an uncommitted section; the notice was made true and the tolerance left to its own task (Found and left, below). Of the 135 rounds 8 had their record refused for an edit while the review ran (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts).
  - **T308-D4, NOT built: a digest over the decisions rather than the section.** None of the 132 task sections reviewed holds a `**D<n> - ` line or a Decisions block, so there is no machine-readable decision to take a digest over (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). The census looked for those two forms only: a section that labels its decisions another way, as this one does (`**T308-D<n>, built:`), has no line it counts, and no two sections share such a form. Of the 132 sections read, the 124 the replay could rebuild at their reviewed digest are the ones T308-D2 and T308-D5 were replayed over. At most 5 of the 16 (c) rounds changed no decision, 6.1 minutes (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). A rule that kept a verdict across a prose edit could keep it across a decision, which is the promise the plan gate makes; the test asked for (a changed decision line voids the verdict) cannot be written where no line is a decision line. What would reopen it: sections that mark their decisions.
  - **T308-D5, NOT built: "N of M" read as a count.** It flags 47 unlabeled sentences in 26 of the 124 sections, and the reviews objected to 1 of them (observed 2026-11-26, method: `dev/measurements/2026-11-26/plan-review-rounds/t308-figures.py` over the reviewed sections). The other unlabeled figures the reviews named ("589 s" beside a GUESS in its sentence, "load median 42", "six more profiles") are judgment, not a pattern.
  - **T308-D6, built: the T55 order notice names the first tier to a builder.** `static_runs_hooks/order.rs` told a first-tier builder at every `make decide` to start `make closing-checks`, which its brief forbids. A caller with an `agent_id` is now told `make builder-checks CRATE="<the crates you changed>"` first and the closing run as the other tier's, and a `builder-checks` it started since its last code edit silences the notice as a `closing-checks` does. The main session, which builds under no tier, is told what it was. The notice stays a notice. Its wording is the one `message-check` asked for (two feature references cut), and the hook suite now renders it, which it did not: with no suite case `make guard-messages` could not see the new wording to owe it a review.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the task line's GM words (T308-D1) | `lint::tests::the_gms_words_on_a_task_line_are_in_the_request_or_refused`, `tests::the_decide_commands_and_the_guard_that_waits_for_them` | n/a: tooling | none | n/a |
| the two figure forms and the threshold's numeral (T308-D2) | `lint::tests::a_suffixed_count_and_a_rounded_unit_figure_need_a_label` | n/a: tooling | none | n/a |
| decide's notice (T308-D3) | `tests::the_decide_commands_and_the_guard_that_waits_for_them`, `status::tests::a_task_verdict_survives_a_typo_only_once_its_reviewed_section_is_committed` | n/a: tooling | none | n/a |
| the order notice (T308-D6) | `order::tests::a_builder_checks_run_started_since_a_builders_last_code_edit_silences_it`, `order::tests::a_decide_after_a_code_edit_with_no_closing_checks_started_since_is_told_the_order`, `tests/hooks/test-static-runs-hooks.sh` case 8 | n/a: tooling | none | n/a |

### T308 Approach (checklist part A)

1. **The goal, in the world.** A plan review is dispatched once: what a script can see is refused at `make decide` in seconds, and a builder knows before it dispatches which edits will cost it another round.
2. **The constraints.** FR-013 (performance work first); feature 375's decision preflight and its promise that a decision cannot change under a kept verdict; feature 239's figures contract; the two-tier trial of `docs/process-decisions.md`, "Two tiers of checking"; no check refuses good work (constitution XIV), so each new refusal is replayed over the reviewed sections first.
3. **Where each comes from.** G: the GM's words of 2026-11-26 on T308's line, now in request.md under "2026-11-26: two tiers of checking, and the plan review's later rounds (451 T308)"; the ALSO on the plan review's rounds is the coordinating session's build of them, as that section says. O: the measurement above and `dev/measurements/2026-11-26/split-reproduction/m16-results.md`.
4. **Do they describe the world here?** Yes: the later rounds were counted and classed from the reviews' own transcripts, and each candidate rule was replayed over the sections those reviews read, as the Approach above states with its labels.
5. **The order.** After T289 (a builder files what it finds); before T308's remainder and before T302.
6. **The exits.** Green: the new tests green, red with the rules off, and `make builder-checks` green on both crates. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: each rule was written from the sentences that drew a NOT-REVIEWABLE return and then replayed over every reviewed section; "N of M" failed that replay and was dropped.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, observed 2026-11-26, method: the three decide rules switched off in place and `make rust-test CRATE=rust/gate/crates/plan` run, `190 passed; 3 failed`, the three tests of the table, then the order notice's tests before its change under `make rust-test CRATE=rust/guard`, `538 passed; 2 failed`, its two. Then the threshold's assertions, added before its numeral took the suffix, observed 2026-11-26, method: `make rust-test CRATE=rust/gate/crates/plan`, `193 passed; 1 failed`, the figure test at `A builder past 300k tokens hands off.` After, observed 2026-11-26, method: `make builder-checks CRATE="rust/gate/crates/plan rust/guard"`, green with `194 passed` and `540 passed`, and `bash tests/hooks/test-static-runs-hooks.sh`, `40 passed, 0 failed`. Not seen red: the figure test's second assertion (the rounded figure), since the test stops at its first; the test of the verdict across a typo, which pins what the code does today and was written to learn it; and the hook suite's two new cases, whose rule the crate's own tests were red for.
10. **Before moving a constant.** n/a: `MIN_WORDS` and `REACH` are new GUESS knobs, no claim's.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. The checks it changes: `make decide` passed a section whose review then returned NOT-REVIEWABLE, a check passing what its own next step refuses; and the order notice told a builder to start a run its brief forbids.

**Found and left?**
- Three of the six rounds owed for the GM's words cited him by reference to a record the bundle does not hold, which T308-D1 cannot see; the review still returns NOT-REVIEWABLE there, a round spent. Not fixed here: it needs the bundle to carry the task's line or a rule over references, a design of its own. Filed as T333; lands before T302.
- A CLEAR does not survive a typo-scale edit of a section not yet committed (T308-D3), so in a builder's tree a comma owes a round where a committed section would keep its verdict. Not fixed here: it changes what `record_task` keeps and what `History::section` reads, the plan gate's own promise, a build with its own red-first test, and this part's brief was to make the notice true by its smallest change. Filed as T337; lands before T302.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop faster); not an engine-speed task, so the performance checklist's engine items do not apply.

### T308 part 2 (the remainder: after a day of the two-tier trial, parts of the tooling still spoke the one-tier language - the closing half's brief block, the builder brief's rules file, the order notice in the session clone and the plan template's performance prompt - each of which cost a round or a correction on 2026-11-26/27; and the trial's own record, so the task's box can close)

- **Approach**: this section is the REST of T308, after its plan-review part above; with it the task's box can be ticked. It changes words the tooling prints and one notice's rule, adds one refusal at `make decide` (T410, built here), and records what the trial has measured and what it has not. The remainder line of the part above also named the changed crate's coverage run tried beside the review: the GM's ruling the same night retires it - a builder runs no coverage, coverage is the second tier's (request.md, "2026-11-26: a builder runs no coverage (451 T308)"; `docs/process-decisions.md`, "Two tiers of checking", the paragraph REVERSED the same night) - so it is not built and not owed.
  - **T308-D7, built: the closing half's block is the first tier, like every kind.** `make builder-brief KIND=closing-half` printed a STOP POINT asking for real coverage of the changed crates and a CHECKS line naming `make crate-checks` with coverage (`rust/gate/crates/task/src/builder_brief.rs`), the amendment the GM reversed. Every kind that changes source now prints one CHECKS line: `make builder-checks CRATE=...` and a changed guard's own suite, no closing-checks, static, hooks-test or coverage run, with the one exception stated in it - a brief whose JOB is the coverage repair of a red batch gate runs `make crate-checks` on the crates it names. The mechanism refusal's hint for the closing half says the owed tests where it said coverage. The block keeps its bound: the longest block the command can print for this feature's real paths (a closing half of a two-task bundle, three jobs, the load line, three crates) is 1,793 characters against the 2,000 `agent-prefix-hooks` refuses a repeat of (measured 2026-11-27 (the block's format strings filled with those values and counted in a scratch script)), and the crate's test holds every printed block under 2,000.
  - **T308-D8, built: the rules file says the same.** `scripts/container/builder-brief.md`: THE FOUR KINDS no longer tells the closing half to run coverage, and the TWO TIERS item states that a builder runs no coverage, why (the GM's ruling), the one exception, and that in the session clone the check of a repair is the batch gate. The incidents stay. No sentence of the file tells a builder to run `make closing-checks`, `make static` or a coverage run (observed 2026-11-27, method: `grep -n "closing-checks\|coverage\|make static\|crate-checks"` over the file, each hit read - the prohibition, the withdrawn amendment's incident, the exception and the assertion-message incident).
  - **T308-D9, built: the order notice names the batch landing in the session clone.** `rust/guard/src/guards/static_runs_hooks/order.rs` told the coordinating session at `make decide`, after a one-line repair of a red batch gate, to start `make closing-checks T=<task>`: the full rigor a second time in the clone, where the batch gate is the check. The notice tells a builder from the main session by the call's `agent_id` (the part above). For the main session it now reads two more things from the same event log: (i) a landing RUNNING - a `make land` it started since the edit (its call line with its result line) with no landing `end` line after it - and it then says nothing; (ii) work STAGED - a `make carry` it ran since the last landing that went out - and it then names `make land F=<feature> T="<the staged tasks>" NOTE="<what lands>"` with `run_in_background: true` in place of the closing run. With nothing staged the main session is told the closing run as before, and a builder's wording is unchanged. The staged tasks are a placeholder on purpose: a carry's log line is filed under the session's own task, not the carried one. Read from the log, so two known misses, both on the quiet side of a notice that refuses nothing: a carry that stopped on a conflict counts as staged (the landing named then refuses in its own words), and a landing killed before its `end` line keeps the notice silent until the next landing ends. The changed wording had its message-check: the hook suite renders it (case 8's new lines), its rendering was put in the tree's store by the hand route T338's line gives, and `message-check` returned PASS on FIDELITY and BREVITY for key 211d059bf7eb596a, 356 characters against a budget of 900 (measured 2026-11-27 (`make guard-messages BUNDLE=1`, the unit's own header)), recorded in `dev/guard-messages.tsv`. `docs/guards.md`'s row for the guard says the new rule.
  - **T308-D10, built: the performance prompt names FR-013's measurement clause, and decide refuses the no - T410, covered here.** `rust/gate/crates/plan/src/plan/template.rs`: the prompt's definition of a `[perf]` task now ends "or measures where time goes: a measurement task counts, the GM 2026-11-20" (FR-013's second sentence; his words are in request.md under the heading of 2026-11-20 on measurement work). `lint/perf_line.rs`, judged at `make decide` only: a line that opens `**Performance work?**` (after an indent or a list dash), whose answer's first word is `no` and which holds the word `measurement`, is refused, the refusal printing the sentence to write and saying to tag the box `[perf]`. The template's own unfilled prompt opens `<no` and is no answer; `none`, `not` and a `yes` naming a measurement pass. The cost of the rule's plainness: a task that truly is not performance work and writes the word in its no is refused, and the refusal says the way out (say it without that word). A stub is matched byte for byte (`make task-withdraw`, the plan gate's withdrawn-stub rule), so `stubs()` now also yields the two forms as they were written before this change: the plans of features 449, 451 and 452 hold 151 unfilled prompts in the old wording (observed 2026-11-27, method: `grep -c "Performance work?\*\* <no - or yes"` over each `specs/*/plan.md` once T410's own stub was filled, the three non-zero counts summed), which a changed template alone would have orphaned. Replayed over the plans as committed the rule refuses none of the 193 Performance lines of those three plans (observed 2026-11-27, method: `dev/measurements/2026-11-27/two-tier-trial/perf-line-replay.py` over the three plan.md files): the sections that answered no of a measurement were corrected in their reviews' later rounds, which is the round this refusal saves.
  - **T308-D11, the trial's record, from what is already measured** (the readings are kept in `dev/measurements/2026-11-27/two-tier-trial/`; nothing was run again but two reports over the event log):
    - Tasks through: 33 tasks landed under two tiers from the trial's first `make builder-checks` at 2026-11-26T17:10Z to 2026-11-27T03:08Z, in 16 landings that went out of 33 attempts (observed 2026-11-27, method: `dev/measurements/2026-11-27/two-tier-trial/landings.py` over the 451 event log's `Phase` lines of `make land`, its output `landings-to-2026-11-27T0308.txt`).
    - Builder minutes a task: 28 tasks landed in the window 2026-11-26T17:00Z to 2026-11-27T01:00Z with 825.0 builder minutes between them (observed 2026-11-27, method: `make task-time SINCE=2026-11-26T17:00:00Z UNTIL=2026-11-27T01:00:00Z`, its table of landed tasks, kept as `task-time-2026-11-26T17-to-2026-11-27T01.txt`, the builder-minutes column summed). The eight tasks one builder closed in under twenty minutes took 7.9 to 19.9 builder minutes each (observed 2026-11-27, method: the same table, the rows with one builder and under twenty builder minutes). Under one tier the closing checks alone were a median 28.8 minutes of a small task's builder clock, 63% of it (measured 2026-11-26 (`dev/measurements/2026-11-26/task-route/m11-results.md`, its decomposition over the 8 small tasks)). The two are not like for like - round one's eight tasks were chosen as small, the window's eight are the ones that came out short - so this says the closing checks' share is gone from a builder's clock, not by how much a task shortened.
    - Batch gates red: of the 33 attempts, 17 did not go out - 10 red at the gate and 7 refused before a gate ran (observed 2026-11-27, method: `dev/measurements/2026-11-27/two-tier-trial/landings.py`, a `gate` step with a non-zero code against an attempt with no `gate` step). The red gate runs took 34.6 minutes of gate time together, the green ones 51.5 (measured 2026-11-27 (`dev/measurements/2026-11-27/two-tier-trial/landings.py`, each `gate` step's span summed)). By cause, as the record already tells it and not tallied gate by gate here: lines no test reached (4 of the first 9 batch gates, `docs/process-decisions.md`; the two in a row of 2026-11-27T01:42Z and 01:50Z, this plan's `### T394 part B`), what only integration shows (a field one task added that another's test did not set, a recipe a hook suite the first tier does not run refuses, a test that fails only beside other crates' tests: the same decision record), one test that failed by the clock (commit 4f244987ac, a task id matched against a timestamp for one hour), and attempts the cheap pass refused on the session's own omissions.
    - What a red batch cost, and who repaired it: a red gate delays the landing on main and takes a repair and a second gate, 5 to 15 minutes each for the first four (measured 2026-11-26 (`docs/process-decisions.md`, "Two tiers of checking", the amendment's paragraph)); the repairs were the coordinating session's by hand or a small fresh agent's, and no builder was kept or called back for one. The second tier as a whole took 258.2 machine minutes of the eight-hour window and 146.9 blocking minutes (measured 2026-11-27 (`make task-time` over the window, its category table)), where the report expects near none. The three warm pool trees stood idle 23% of that window, 105 of their 336 idle tree-minutes while a landing ran and 170 in the session's own turns (measured 2026-11-27 (`dev/measurements/2026-11-27/tree-idle/results.md`)): the cost of the second tier fell on builders through the ORDER the session worked a builder's end in, which T394 changed (dispatch before carry).
    - What the trial has NOT shown: (i) whether the threshold for running the second tier (at the drain, a ceiling of about six tasks or ninety minutes, GUESS knobs) is right, or a gate on a snapshot is better - trial feature 458 holds that, not to be read before 2026-11-28; (ii) whether T394's order brought the trees' idle share down - 451 T401 is that re-measurement; (iii) tasks landed a wall hour against round one, which no record here states like for like; (iv) the cost of each red gate's repair in the session's turns and tokens, gate by gate, and so whether repairs after a gate hold builders back by more than a coverage step would cost them - the one thing the GM's ruling says would reopen a builder's coverage run; (v) the falsifier's third arm, a defect reaching main that a builder's closing checks would have caught: none is recorded, and none was looked for by a method.
  - **T308-D12, a RECOMMENDATION, the GM's to confirm at the talk: T308's box closes with the two tiers adopted as the trial stands.** The tooling now speaks two tiers in every place this task found (D7 to D10 and the part above), and that is what the task's box asked to be built. The verdict on the arrangement itself - the threshold, the snapshot gate, the idle share after T394 - stays open with feature 458 and T401 and is not decided by this section. Against the trial's falsifier as measured so far: builder minutes a task are down by the closing checks' share, and no defect on main is recorded; gate failures were frequent (10 red of 26 gate runs to 03:08Z (observed 2026-11-27, method: `dev/measurements/2026-11-27/two-tier-trial/landings.py`)) and what they cost against the closing checks they replaced is item (iv) above, not shown. If the GM does not confirm, the box stays open and nothing built here is undone by that.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the closing half's block (T308-D7) | `builder_brief::tests::each_kind_s_block_opens_with_its_marker_and_stays_short`, red on the old code; `a_brief_is_sized_before_any_tree_is_taken`'s pin of the refusal's hint | n/a: tooling | none | none |
| the order notice in the session clone (T308-D9) | `order::tests::the_main_session_with_a_batch_staged_is_told_the_landing_and_nothing_while_one_runs`, red on the old code; `tests/hooks/test-static-runs-hooks.sh` case 8's two new lines | n/a: tooling | none | none |
| the performance prompt and decide's refusal (T308-D10, T410) | `lint::tests::a_performance_line_answering_no_of_a_measurement_is_refused_at_decide` and `template::tests::a_stub_s_blocks_are_the_template_s_with_the_id_filled`, each red on the old code | n/a: tooling | none | none |

### T308 part 2 Approach (checklist part A)

1. **The goal, in the world.** Every word the tooling prints to a builder or to the coordinating session about checks agrees with the two tiers: a builder runs tests, lint and format in its tree and no coverage; the session, in its clone with a batch staged, runs the batch gate once; and a section that measures where time goes is not sent to a review answering no to performance work.
2. **The constraints.** The GM's two tiers and his ruling that a builder runs no coverage (request.md); FR-013 with its measurement clause; the block under the 2,000 characters `agent-prefix-hooks` holds a repeated prompt to; a notice stays a notice (T55's replay priced a refusal there and declined it); a stub is matched byte for byte, so no filed stub may be orphaned; no check refuses good work (constitution XIV).
3. **Where each comes from.** G: the GM's words of 2026-11-26 in request.md under "2026-11-26: two tiers of checking, and the plan review's later rounds (451 T308)" and "2026-11-26: a builder runs no coverage (451 T308)", and of 2026-11-20 on measurement work; O: the brief of this builder, the session's account of where each one-tier wording cost a round or a correction; O: T410's line (the five blocked plan reviews); O: the event log and `make task-time`, for the trial's record.
4. **Do they describe the world here?** Yes: each wording was read in the code that prints it before it was changed, and the trial's figures are read from the event log and the reports named beside each, none from memory or from the brief.
5. **The order.** After the part above and after T394 (the order of a builder's end); before T302. T410 lands with it. The trial's verdict is feature 458's, after 2026-11-28.
6. **The exits.** Green: the changed crates' tests and `make builder-checks` green, the hook suite green, the changed message reviewed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one design each. For the notice, reading git for commits ahead of main was weighed against reading the log and left: the module reads the log alone and its tests are pure.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, each on the old code with the new tests, observed 2026-11-27, method: `make rust-test CRATE=<crate>` with the source file put back to HEAD's and the new test kept, then restored - the order notice `552 passed; 1 failed` in `rust/guard`, then `553 passed; 0 failed`; the block `119 passed; 1 failed` in `rust/gate/crates/task`, then `120 passed; 0 failed`; the prompt and the refusal `196 passed; 2 failed` in `rust/gate/crates/plan` (the lint at HEAD's with the new module only declared, the template's new constant set to the old wording), then `198 passed; 0 failed`. The hook suite `static-runs-hooks: 42 passed, 0 failed` (observed 2026-11-27, method: `bash tests/hooks/test-static-runs-hooks.sh` in the tree, its last line).
10. **Before moving a constant.** n/a: no constant moves; the notice and the refusal add no knob.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. What a reader of the tooling sees differently: a closing-half builder is no longer told to run coverage the GM ruled out; the session at `make decide` in its clone is told the landing that is the check, or nothing while it runs, where it was told to start a second full run; a section answering no to performance work of a measurement is refused in seconds where a plan review blocked a round on it.

**Found and left?** none - T410 is built here (T308-D10) and closes with this landing; what the trial has not shown is held by feature 458 and T401, both open before this section, and is no defect of this code.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop and the landings faster - a coverage run off the closing half's path, a second full check run off the session's, a plan review round saved - and its second job records where the trial's time went, FR-013's measurement clause); not an engine-speed task, so the performance checklist's engine items do not apply.


<!-- plan-archive: T309 to T272 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T310 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T310 Approach (checklist part A)

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


<!-- plan-archive: T311 to T305 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T311 to T311 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T143 to T143 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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

### T315 (the GM, 2026-11-26, on 451 T305's repeated slow test runs: why more of a builder's test run could not be cached, T301 part 1 having answered the compile side and T316 having timed one run of `rust/gate/crates/land` on a heavily loaded machine)

- **Approach**: a measurement, no code changed. Scripts and raw results are kept in `dev/measurements/2026-11-26/test-run-split/` (`gate-run.sh`, `edit-probe.sh`, `edit-split.sh`, `body-edit.sh`, `ps-sample.py`, `run.py`, `count-shim.c`, `shares.py`, `phase-history.py`, `slot-waits.py`, `git-fixture-bench.py`; `slowest-tests.txt`, the `.jsonl` and `.txt` results). Everything ran in the pool tree `diagram-backlog-t269`, one run at a time, on 22 cores (observed 2026-11-26, method: `nproc`) beside two other builders; each row carries its load. `strace` and `perf` are refused in the container, so file calls were counted by an `LD_PRELOAD` shim (`count-shim.c`) and processes by sampling `/proc` (`ps-sample.py`).
  - **The verdict.** The slow runs the GM asked about were BUILD, not tests, and beside other builders a build's seconds are now mostly a queue. T305's own runs, in this tree, are in the event log: five `make rust-test` runs of `reviews` whose builds took 24.4, 5.6, 8.0, 5.4 and 7.9 s and whose tests 1.1 to 2.8 s, the third beside `land`'s build of 8.7 s and its tests of 11.4 s, observed 2026-11-26, method: the `Phase` lines of `.git/l7r-events/451-time-retro-and-efficiency.jsonl` naming `diagram-backlog-t269` between the tree's take and release for T305 in `.git/builder-pool.log`, 17:13 to 17:37 UTC. This task's first run in the tree, after its handout, was the same shape: 27.6 s of wall, 7.5 s build, 1.6 s tests and 18.5 s before the first phase line, the checks' own tools rebuilding after the commits the handout brought (T316's subject), measured 2026-11-26 (`make rust-test CRATE=rust/gate/crates/land FRESH=1` timed, its `Phase` lines read, load 11). A real edit - a statement at the head of a function body, in one file and in three files of `reviews` - compiled in 2.3, 3.2, 3.9 and 4.0 s at load 25 to 28, after WAITING 57.3, 18.2, 2.5 and 34.9 s for one of the machine's two build slots behind other builders' compiles, measured 2026-11-26 (`body-edit.sh`: the `build` line less the `slot-wait` line inside it), and the slot landed that afternoon (451 T284), T305's runs carrying no such line. Filed as T347. Alone, no gate crate's edit-and-test run takes the 19 s the task's line gives for T305's (observed 2026-11-26, method: T315's line in `tasks.md`, the coordinating session's figure): a one-line edit of `land`, `reviews`, `measure`, `plan` or `task` rebuilds in 0.8 to 2.1 s and its tests run in 0.8 to 1.9 s, measured 2026-11-26 (`edit-probe.sh`, `gate-run.sh`, load 3 to 12). Runs of that length were the same work on a loaded machine and first builds after other landings: the recorded test phases of `land` on 2026-11-25/26 were 4.2 s at the median and 18.3 s at the 90th centile of 57, measured 2026-11-26 (`phase-history.py`), against 1.6 to 1.7 s alone, and T316's 10.7 s of tests was taken at load 248, measured 2026-11-26 (T316's plan section). The suites are already parallel and their time is processes and files, not waiting - except in the two guard crates, where three things that are not the tests' work cost 5 to 7 s of every run and are filed (T339, T340, T341), measured 2026-11-26 (`gate-run.sh`, `run.py`, `ps-sample.py`). No lever on where the tests write, how they make a repository, the linker or the thread count is worth a task.
  - **The split, crate by crate, alone.** A FRESH gate run three times each with nothing changed (`gate-run.sh`: `make rust-test CRATE= FRESH=1`, the `build` and `test` `Phase` lines and the wall); the one-line edit is a constant appended to the crate's `lib.rs`, then taken out, through the same command (`edit-probe.sh`); the linker's seconds are the life of the `cc` process that runs rust-lld, sampled (`edit-split.sh`); the binary's own run is the test executable run as the gate runs it (the crate's directory, cargo's variables, a `TMPDIR` of its own) three times (`run.py`), its processor time `user + sys` of the process and its children.

    | crate | lines of Rust | tests | build, nothing changed | build after a one-line edit | of it the linker | the gate's `test` phase | the binary's own run | its processor time | processor time over wall | label |
    |---|---|---|---|---|---|---|---|---|---|---|
    | `rust/gate/crates/land` | 8,753 | 128 | 0.07-0.09 s | 0.8-1.1 s | 0.20-0.25 s | 1.65-1.70 s | 1.43-1.54 s | 21 s | 14 | measured 2026-11-26 (`gate-run.sh`, `edit-probe.sh`, `edit-split.sh`, `run.py`; load 3-7) |
    | `rust/gate/crates/reviews` | 20,974 | 209 | 0.08-0.09 s | 1.3-1.4 s | 0.15 s | 1.45-1.54 s | 1.19-1.44 s | 18 s | 13-15 | measured 2026-11-26 (the same; load 5-9) |
    | `rust/gate/crates/measure` | 27,694 | 241 | 0.08-0.09 s | 1.9-2.1 s | 0.25 s | 0.75-0.80 s | 0.43-0.62 s (a first run 1.73 s) | 6.2 s | 10-14 | measured 2026-11-26 (the same; load 4-11) |
    | `rust/gate/crates/plan` | 11,648 | 191 | 0.08 s | 0.9-1.0 s | 0.10 s | 0.77-0.83 s | 0.61-0.63 s (one run 1.14 s) | 3.8 s | 6 | measured 2026-11-26 (the same; load 4-10) |
    | `rust/gate/crates/task` | 8,186 | 99 | 0.07-0.08 s | 0.75-0.8 s | 0.15-0.20 s | 1.83-1.90 s | 1.61-1.62 s | 10.4 s | 6.4 | measured 2026-11-26 (the same; load 4-10) |
    | `rust/guard` | 45,763 | 539 | 0.09-0.11 s | 2.4-2.8 s | 0.16-0.20 s | 5.3-6.2 s | 2.05-2.07 s | 18.5 s | 9 | measured 2026-11-26 (the same; load 5-12) |
    | `rust/guard/shared` | 43,362 | 505 | 0.08-0.09 s | 2.5-2.9 s | 0.10-0.15 s | 8.8-8.9 s | 8.36-8.38 s | 15.3 s | 1.8 | measured 2026-11-26 (the same; load 4-12) |

    With the test executable deleted and no source changed the build took 0.74 s (`task`) to 2.5 s (`rust/guard/shared`), within 0.45 s of the one-line edit's in every crate, measured 2026-11-26 (`edit-probe.sh`, its `probe-link` rows): a small edit's rebuild is rustc starting, reading its incremental cache and writing the binary again, not compiling the edit, and the link proper is a tenth of it. A run whose edit leaves the test binary's bytes as they were (an unused constant's value) builds and runs no test: the kept result is keyed on the binary, measured 2026-11-26 (`edit-split.sh`, its `e2` rows: a `build` line of 0.8 to 2.6 s and no `test` line).
  - **A builder's whole command after a one-line edit**, without `FRESH` as a builder runs it, measured 2026-11-26 (`edit-split.sh`, its `e1` rows, load 3-6): `reviews` 3.0 s (0.3 s before the build, 1.3 s build, 1.3 s tests), `plan` 2.0 s (0.3, 1.0, 0.7), `rust/guard` 11.9 s (2.3, 3.9, 5.5), `rust/guard/shared` 15.8 s (4.2, 2.7, 8.7). `FRESH=1` adds a REASON check through the whole `l7r-gate` tool, which is rebuilt first where any gate source moved: 1.1 to 2.8 s more before the build after an edit of a gate crate, measured 2026-11-26 (`edit-probe.sh` with `gate-run.sh`'s `before` figure, 1.4 to 3.1 s against 0.3 s) - the escape's cost, not a builder's run's.
  - **What the recorded runs took**, measured 2026-11-26 (`phase-history.py` over the clone's `.git/l7r-events/*.jsonl`: every `build` and `test` `Phase` line of 2026-11-25/26 that names one crate and passed, a line under 0.5 s being a build found fresh and is left out of the centiles):

    | crate | step | lines | not found fresh | median | 90th centile | longest | label |
    |---|---|---|---|---|---|---|---|
    | `rust/gate/crates/land` | build | 71 | 58 | 3.3 s | 18.3 s | 63.4 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/land` | test | 57 | 57 | 4.2 s | 18.3 s | 79.4 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/reviews` | build | 37 | 30 | 6.1 s | 20.5 s | 101.2 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/reviews` | test | 27 | 27 | 1.5 s | 2.5 s | 6.5 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/measure` | build | 100 | 91 | 15.1 s | 23.8 s | 76.1 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/measure` | test | 62 | 62 | 0.7 s | 1.4 s | 4.5 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/plan` | build | 48 | 39 | 5.9 s | 19.3 s | 76.5 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/plan` | test | 40 | 40 | 0.8 s | 2.8 s | 19.4 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/task` | build | 50 | 41 | 2.7 s | 13.0 s | 48.2 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/gate/crates/task` | test | 39 | 39 | 1.8 s | 6.5 s | 31.9 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/guard` | build | 104 | 94 | 14.9 s | 59.0 s | 178.7 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/guard` | test | 83 | 83 | 5.5 s | 7.4 s | 45.5 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/guard/shared` | build | 86 | 78 | 15.9 s | 50.5 s | 132.4 s | measured 2026-11-26 (`phase-history.py`) |
    | `rust/guard/shared` | test | 64 | 64 | 8.9 s | 12.2 s | 24.8 s | measured 2026-11-26 (`phase-history.py`) |

    The test medians are the alone figures above except `land`'s (4.2 s against 1.7 s), measured 2026-11-26 (`phase-history.py`, `gate-run.sh`); the build medians are 3 to 8 times a one-line edit's alone. The log does not say which builds were a builder's own edit and which the first build after others' landings (T316's subject) or a build beside two others', so the gap is not split here; T301 part 1 measured a first build of a large gate crate at about 20 s, measured 2026-11-26 (T301 part 1's section, `gate-call.sh`).
  - **The ten slowest tests of each crate** are listed whole in `dev/measurements/2026-11-26/test-run-split/slowest-tests.txt` (libtest's own per-test seconds, the suite running whole on its 22 threads, so each is a time beside its neighbors and not alone), measured 2026-11-26 (`run.py --report`). What they do, read in their sources 2026-11-26:
    - `land` (the ten 0.83 to 1.48 s, 10.9 s of the 27.0 s the tests sum to): all `land::alone::tests`, each a pair of throwaway clones with an origin, driven through the real `scripts/land-alone.sh` and shell lines of git add, commit and push, measured 2026-11-26 (`run.py --report`).
    - `reviews` (0.55 to 1.27 s, 6.7 of 27.1 s): `reviews::owed` and `reviews::prereq::scoped` tests, each a throwaway repository with several commits read back through `git rev-parse`, `diff`, `log`, `ls-tree` and `merge-base`, measured 2026-11-26 (`run.py --report`).
    - `measure` (0.20 to 0.36 s, 2.5 of 9.3 s): the command-line tests of `feature_report`, `maps_moved`, `work_budget_review` and `fix_yield`, each a throwaway repository and several git reads, measured 2026-11-26 (`run.py --report`).
    - `plan` (0.11 to 0.47 s, 1.7 of 5.7 s): the slowest is in memory (`the_label_search_is_linear_in_its_sentence`, a 240,000-word sentence), as are the two megabyte-plan tests, measured 2026-11-26 (`run.py --report`); the rest make a repository.
    - `task` (0.31 to 1.45 s, 6.2 of 15.7 s): `task_add::tests::two_filings_at_once_keep_both_boxes_and_both_sections` runs two filings on threads against a `make quick` stand-in that sleeps 0.3 s, measured 2026-11-26 (`run.py --report`); the rest are repositories with worktrees and pushes.
    - `rust/guard` (0.38 to 1.91 s, 7.9 of 25.9 s): `context_cap_hooks`' transcript test writes and reads transcripts of hundreds of thousands of bytes, `no_poll_hooks`' frozen corpora and the case tables are in memory over recorded commands, and the two `scratch_sweep_hooks::disk` tests at 1.04 s each build fixture cache directories, measured 2026-11-26 (`run.py --report`).
    - `rust/guard/shared` (0.44 to 8.06 s, 17.8 of 27.3 s): `guards::set_down_hooks::tests::stalls::the_idle_check_looks_again_until_its_budget` WAITS 8.06 s of real seconds and is the suite's whole wall, measured 2026-11-26 (`run.py --report`); `house_style_hooks`' `a_spelling_past_a_million_steps_is_corrected` is 3.42 s of processor time over a text of 1.35 million characters, measured 2026-11-26 (`run.py --report`); two idle tests wait 1.01 s each, measured 2026-11-26 (`run.py --report`). Filed as T339.
  - **How much of a run is tests that start git or another program** (the brief's part 2). A test is counted as starting git where it fails with a `git` first on `PATH` that exits 127, and as starting any program where it fails with `PATH=/nonexistent`; its seconds are the good run's. A lower bound: a test that starts a program by its full path, or does not check what it started, passes both.

    | crate | tests | the tests' seconds, summed | start git | start any program | start none | label |
    |---|---|---|---|---|---|---|
    | `land` | 128 | 27.0 s | 110 tests, 26.8 s (99%) | 113, 26.9 s (100%) | 15, 0.1 s | measured 2026-11-26 (`shares.py`) |
    | `reviews` | 209 | 27.1 s | 138, 26.8 s (99%) | 139, 26.8 s (99%) | 70, 0.4 s (1%) | measured 2026-11-26 (`shares.py`) |
    | `measure` | 241 | 9.3 s | 73, 8.4 s (90%) | 80, 8.7 s (93%) | 161, 0.7 s (7%) | measured 2026-11-26 (`shares.py`) |
    | `plan` | 191 | 5.7 s | 79, 4.2 s (73%) | 79, 4.2 s (73%) | 112, 1.5 s (27%) | measured 2026-11-26 (`shares.py`) |
    | `task` | 99 | 15.7 s | 75, 14.0 s (89%) | 77, 14.0 s (89%) | 22, 1.7 s (11%) | measured 2026-11-26 (`shares.py`) |
    | `rust/guard` | 539 | 25.9 s | 126, 9.6 s (37%) | 207, 16.3 s (63%) | 332, 9.6 s (37%) | measured 2026-11-26 (`shares.py`) |
    | `rust/guard/shared` | 505 | 27.3 s | 117, 16.2 s (59%) | 134, 16.5 s (60%) | 371, 10.8 s (40%) | measured 2026-11-26 (`shares.py`) |

    So the gate crates' test time is git almost wholly, and what it costs is processes: in `land`, 13 of the 21 s of processor time are the kernel's (`sys`), measured 2026-11-26 (`run.py`).
  - **What a run writes** (the brief's part 2, and the figures feature 460 asks for first). The gate gives each crate's run its own `TMPDIR`, `/tmp/l7r-rust-tests-<crate>-...` (`rust/gate/crates/rustc/src/rustc.rs`, `leak_checked`), and every `TempDir` and the shared `l7r-test-scratch` directory root there (`rust/guard/shared/src/tempdir.rs`: `std::env::temp_dir()`), so the tests' files are under that one directory, on the container's own disk. One run of each binary with the counting shim, a wrapper logging every `git`, and the directory walked as it ran (`run.py --count --gitlog --sample`; the wrapper's own process and file a git call are taken out of the counts below). The peak is a SAMPLED peak, a lower bound; the bytes dirtied are `write_bytes` of `/proc/<pid>/io`, which counts a file deleted before it reaches the disk too.

    | crate | processes started | of them git | `git init` | files created | directories made | files removed | directories removed | `fsync`, `fdatasync`, `sync_file_range` | peak in the `TMPDIR` | bytes dirtied | label |
    |---|---|---|---|---|---|---|---|---|---|---|---|
    | `land` | 4,177 | 2,533 | 55 | 14,220 | 8,980 | 14,519 | 8,309 | 0 | 8.1-8.4 MB in 1,937-2,022 files and 1,577-1,584 directories (three samplings) | 43 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `reviews` | 5,567 | 4,366 | 180 | 11,868 | 8,848 | 11,575 | 6,108 | 0 | 5.5 MB, 1,298 files, 1,185 directories | 40 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `measure` | 1,631 | 1,195 | 81 | 6,799 | 4,774 | 6,877 | 3,550 | 5 | 4.9 MB, 1,165 files, 1,006 directories | 22 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `plan` | 638 | 634 | 84 | 3,855 | 1,832 | 3,565 | 1,596 | 2 | 3.5 MB, 521 files, 316 directories | 16 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `task` | 2,569 | 1,577 | under 8 (not among its twelve commonest git words) | 8,180 | 6,677 | 9,406 | 5,814 | 0 | 5.4 MB, 1,154 files, 1,233 directories | 21 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `rust/guard` | 2,883 | 1,244 | 111 | 11,777 | 9,563 | 8,243 | 6,263 | 0 | 23.3 MB, 1,522 files, 690 directories | 65 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |
    | `rust/guard/shared` | 1,381 | 953 | 145 | 6,849 | 5,262 | 5,973 | 3,597 | 0 | 19.5-19.7 MB, 650-694 files | 41 MB | measured 2026-11-26 (`run.py`, `count-shim.c`) |

    The seven sampled peaks sum to 71 MB, were all seven suites to run at one moment, measured 2026-11-26 (`run.py --sample --count`); one copy of the `land` suite holds 8.4 MB, measured 2026-11-26 (`run.py --sample --count`). The tests' git runs with no `core.fsync` setting (none in the container's git configuration, read 2026-11-26 by `git config --get-regexp`), and seven runs made 7 sync calls between them: the writes are directory churn (about 63,500 files created and 45,900 directories made over the seven suites), not syncs, so no git sync setting would change them, measured 2026-11-26 (`run.py --sample --count`).
  - **The levers, each priced.**

    | lever | what was measured | seconds a run | verdict | label |
    |---|---|---|---|---|
    | the tests' `TMPDIR` on `/dev/shm` | it fits by size (`land`'s peak 8.2 MB and `rust/guard`'s 23.3 MB of 62.5 MB, nothing else in it) and FAILS by its mount: `/dev/shm` is `noexec`, and 72 of `land`'s 128 tests and 22 of `rust/guard`'s 539 fail there, 70 of `land`'s 72 with `Permission denied` on a script they write and run, measured 2026-11-26 (`run.py --tmp-parent`, `git-fixture-bench.py`); no other memory-backed directory in the container is writable and executable and a mount is refused, so the whole suite could not be timed on one. In its place: a repository made, one file committed and the repository removed, 60 at a time, three rounds, on each - 12.3 + 1.1 ms on `/tmp` against 10.2 + 0.4 ms on `/dev/shm` | not timed on a whole suite, and ESTIMATED instead: a repository's making and removing is a fifth faster there (10.6 against 13.4 ms), so at most about 0.3 s of `land`'s 1.5 s, were its whole run that work, measured 2026-11-26 (`git-fixture-bench.py`) | NO task for time. For feature 460's question the size is: 8.4 MB a copy of `land`, 71 MB for the seven suites at once, so 128 MB holds them with room, and the directory must be mounted with `exec` | measured 2026-11-26 (`run.py --tmp-parent`, `git-fixture-bench.py`; load 3-6) |
    | `git init` with an empty template | end to end: `GIT_TEMPLATE_DIR` an empty directory for a whole `land` run (it reached git: 914 fewer files created, 13,306 against 14,220) - 2.4 to 3.7 s with it against 2.1 to 6.6 s without, four and three runs taken in turn while the load rose from 4 to 16: not shown to differ, measured 2026-11-26 (`run.py --env`, `git-fixture-bench.py`). Per repository 0.9 ms (4.2 against 3.3 ms) | 0.05 to 0.16 s of PROCESSOR time a run (55 to 180 inits), under 0.02 s of wall on 22 threads | NO task | measured 2026-11-26 (`run.py --env`, `git-fixture-bench.py`) |
    | a shared fixture repository copied per test | a committed repository (27 files, 15 directories) copied in process 2.5 ms, by `cp -r` 3.5 ms, against 12.3 ms made by `git init`, `add` and `commit` | about 10 ms of processor time a repository: 0.5 s (`land`, 55) to 1.8 s (`reviews`, 180) of processor time a run, 0.04 to 0.13 s of wall at the measured 14 processors in use, measured 2026-11-26 (`git-fixture-bench.py`). An estimate: the tests' repositories differ and most of their git calls come after the first commit (`land`: 2,533 git processes for 55 inits) | NO task | measured 2026-11-26 (`git-fixture-bench.py`; load 3) |
    | the tests' thread count | the suite is already parallel: libtest's default is a thread a core, 22, and the gate passes none (`run_built`, `test_args`). `land` at 1, 4, 8, 22 and 44 threads: 16.5, 4.5, 2.2-3.1, 1.4-1.9 and 2.0 s, measured 2026-11-26 (`run.py --threads`); `reviews` 20.3, 14.0, 3.0-5.6, 1.2-3.4, 5.2; `rust/guard` 23.6, 6.6, 2.3-2.7, 2.1, 2.3; `rust/guard/shared` 24.9, 10.7, 8.7-8.8, 8.5, 9.1 (one or two runs each, at load 17 to 29 as other builders worked) | nothing to gain: 44 threads no faster than 22 | NO task | measured 2026-11-26 (`run.py --threads`) |
    | only the tests a change reaches | the checks' tool takes a crate and nothing narrower (`rust/gate/crates/rustc/src/rustc.rs`, `parse`: `--crate` and `--check` alone). `land` filtered to one module by hand: `land::phase` (18 tests) 0.16-0.18 s of wall and 1.2 s of processor time, `land::unfinished` (7) 0.2-0.8 s and 0.8-1.4 s, `land::alone::tests::takeback` (4 of the ten slowest) 1.1-3.4 s, against 1.4-1.5 s and 21 s whole (load 15-17) | alone at most 1.3 s a run of `land`, less for the others, measured 2026-11-26 (`run.py -- <filter>`); on a loaded machine its processor time, a twentieth, is what counts, and that is not measured | a task whose first step is that measurement: T342 | measured 2026-11-26 (`run.py -- <filter>`) |
    | a faster linker | the link is already rust-lld (`.cargo/config.toml`, 449 T96) and lives 0.10 to 0.25 s of a 0.8 to 2.9 s rebuild | under 0.25 s were it free | NO task | measured 2026-11-26 (`edit-split.sh`, `ps-sample.py`) |
    | a check-only pass before the test build | not run: T301 part 1 measured a check of an edited gate crate at 0.7 s beside its test build of 1.2 to 3.9 s, measured 2026-11-26 (T301 part 1's section, `gate-call.sh`); a check first adds its seconds to every run that compiles and saves the difference only on one that does not | none on a run that compiles | NO task | cited: T301 part 1, measured 2026-11-26 (`gate-call.sh`) |
    | a smaller crate | the one-line rebuild follows the crate's size, 0.75 s at 8,186 lines to 2.9 s at 43,362 (the table above) | about 1 s a run for halving the largest gate crate, `measure` | NO task: a split costs every caller's imports for a second | measured 2026-11-26 (`edit-probe.sh`) |
    | the shared guard crate's waiting test | the suite run without `the_idle_check_looks_again_until_its_budget`: 3.6, 5.4 and 4.6 s, measured 2026-11-26 (`run.py -- --skip`); without it and the spelling test: 2.4, 2.1 and 2.5 s, measured 2026-11-26 (`run.py -- --skip`); whole: 8.4 s (load 15-18 for the first two, 4-9 for the whole) | about 5 s, and the second test's 3.4 s is then the suite's floor, which may not shorten (its text is as long as the old limit's firing needs) | T339 | measured 2026-11-26 (`run.py -- --skip`) |
    | the guard crate's orphaned processes | the binary run by hand into a pipe exited at 2.03 s and the pipe closed at 5.16 s, nine or more `sleep 5` processes of parent 1 alive between, measured 2026-11-26 (`gate-run.sh`, `run.py`); under the gate the binary stands as a zombie through 14 samples of 0.2 s, measured 2026-11-26 (`gate-run.sh`, `run.py`); the gate's `test` phase 5.3-6.2 s against the binary's 2.05-2.07 s | 3.2 s | T340 | measured 2026-11-26 (`gate-run.sh`, `run.py`, a process listing during each) |
    | the tool's 2.0 s before an edited guard crate's build | `l7r-rust` alone on one thread from 0.36 s to 2.33 s of the command, between its `git ls-files` and its first cargo call, measured 2026-11-26 (`ps-sample.py`, `edit-split.sh`); 0.3 s for an edited gate crate, and where in the tool is not measured (the kept result's key over the guard's sources is a guess) | 2.0 s (`rust/guard`), 2.2 s (`rust/guard/shared`, beside 2.0 s of the tool's own rebuild, which builds from that crate) | T341 | measured 2026-11-26 (`ps-sample.py`, `edit-split.sh`) |

  - **What this says to the GM's question.** The build is cached as far as it can be (T301 part 1) and a one-line edit's rebuild is 1 to 3 s, measured 2026-11-26 (the tables above); the tests' own run is not cacheable and is 1 to 2 s for a gate crate alone, measured 2026-11-26 (the tables above). T305's runs were builds of 5 to 24 s with tests of 1 to 3 s beside them: a real edit's rebuild is 2 to 4 s of compiling, longer beside other builders, 24 s the first time after a handout (T316 now warms it), and since T284 it also waits for a build slot, the largest single cost measured here (T347), measured 2026-11-26 (the verdict's figures, above). Where a test phase itself ran long (`land`'s 11.4 s in T305's third run), it is that crate's 21 s of processor time - 4,177 processes, 2,533 of them git - sharing 22 cores with other builders' compiles: the tests' run is all processes, so it stretches with the load where a cached build does not, measured 2026-11-26 (the tables above). What shortens it is fewer processes in a run (T342, a builder running the tests its change reaches) and fewer compiles beside it; nothing about where the tests write or how they make a repository does.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| no code changed: a measurement, its scripts and results in `dev/measurements/2026-11-26/test-run-split/` | n/a: nothing fixed | n/a: tooling | none | n/a |

### T315 Approach (checklist part A)

1. **The goal, in the world.** The session knows where a builder's test run of the crates builders change most spends its seconds, and which levers on it are worth building, before any is built.
2. **The constraints.** No load generator and no copies of a suite run together (the brief, after the host's freeze of 2026-11-26, feature 460); one run at a time in the pool tree; nothing T301 part 1 or T316 measured is measured again.
3. **Where each comes from.** G: the GM's question of 2026-11-26 about T305's repeated test runs, as the task line and the brief relay it. O: T301 part 1's and T316's plan sections, `dev/measurements/2026-11-26/build-levers/m9-results.md`, and the measurements above.
4. **Do they describe the world here?** The length the task's line gives for T305's runs was not found again alone: `land`'s whole edit-and-test command is under 5 s at load 3 to 7, and the recorded runs reach 18.3 s at their 90th centile, measured 2026-11-26 (`phase-history.py`).
5. **The order.** After T301 part 1 and T316, whose figures it starts from. T339, T340, T341, T342, T344 and T347, filed here, are independent of each other; T342's first step is a measurement.
6. **The exits.** Green: each of the seven crates' runs split into build, link and tests, its writes counted, and each lever priced by a measurement or cited, measured 2026-11-26 (the scripts above). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing, of this section, the scripts and results, the six filed tasks' lines and feature 460's one pointer line.
9. **Done, measured.** Seven crates' runs split and counted, eleven levers priced, six tasks filed, measured 2026-11-26 (the tables above).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing is fixed here. The three costs found in the guard crates are test and tool code a measurement builder was not briefed to change, each with its own red-first proof to write. No map changes.

**Found and left?**
- One test of `rust/guard/shared` waits 8.06 s of real seconds and is the suite's whole 8.4 s of wall, measured 2026-11-26 (`run.py --report`); visible effect: about 5 s of every test run of that crate, 64 recorded on 2026-11-25/26, measured 2026-11-26 (`phase-history.py`). Not fixed here: the test's waits are the guard's own knobs and the fix is a clock the test steps, a change with its own proof. Filed as T339; lands before T302.
- Tests of `rust/guard` leave `sleep 5` processes that hold the test binary's output pipe open after it exits, measured 2026-11-26 (the binary run into a pipe: exit at 2.03 s, the pipe closed at 5.16 s); visible effect: 3.2 s of every test run of that crate, 83 recorded on 2026-11-25/26, measured 2026-11-26 (`phase-history.py`), and processes left running after a suite ends. Not fixed here: which tests start them is not found, and the pin belongs with the fix. Filed as T340; lands before T302.
- The checks' tool spends 2.0 s on one thread before the build of an edited guard crate where a gate crate's takes 0.3 s, measured 2026-11-26 (`ps-sample.py`, `edit-split.sh`); visible effect: 2 s of every test run of an edited `rust/guard` or `rust/guard/shared`, measured 2026-11-26 (`ps-sample.py`, `edit-split.sh`). Not fixed here: where in the tool it is spent is not measured (`perf` and `strace` are refused in the container). Filed as T341; lands before T302.
- The checks' tool cannot run a part of a crate's tests, so a builder's every run of `land` starts 4,177 processes for 21 s of processor time, measured 2026-11-26 (`run.py --count`); visible effect: the 4.2 s median and 18.3 s 90th centile of that crate's recorded test phases beside other builders, measured 2026-11-26 (`phase-history.py`), against 1.7 s alone. Not fixed here: what it saves on a loaded machine must be measured first, and it is a new option of a command. Filed as T342; lands before T302.
- A builder's test build waits for one of the machine's two build slots behind other builders' compiles: 57.3, 18.2, 2.5 and 34.9 s of waiting for compiles of 2.3 to 4.0 s in four runs at load 25 to 28, measured 2026-11-26 (`body-edit.sh`, the `slot-wait` and `build` `Phase` lines), and twelve such waits of 0.5 to 57.3 s in the day's event log, observed 2026-11-26, method: every `slot-wait` `Phase` line of `.git/l7r-events/*.jsonl` listed (`slot-waits.py`); visible effect: a builder's edit-and-test run of a gate crate takes 9 to 64 s where its work is 4 to 7 s, measured 2026-11-26 (`body-edit.sh`, the wall of each run). Not fixed here: the slot is 451 T284's memory guard and its count a knob to retune from a measurement of what a one-crate build needs. Filed as T347; lands before T302.
- All 179 `Phase` lines of this task's runs in the pool tree `diagram-backlog-t269` carry task `T285`, as every `Phase` line of the tree has since 14:00 UTC through its handouts to T284, T305, T104, T316 and T315 (`.git/builder-pool.log`), observed 2026-11-26, method: the `Phase` lines of `.git/l7r-events/451-time-retro-and-efficiency.jsonl` naming that tree from 20:07 UTC on, counted by their `task` field; visible effect: `make task-time` books those tasks' build and test seconds to T285. Not fixed here: the handout and the event line's task are `builder-tree`'s and the log's code, outside a measurement. Filed as T344; lands before T302.
- `/dev/shm` in the container is `noexec` and 62.5 MB, so the suites cannot run there as it is (72 of `land`'s 128 tests fail), measured 2026-11-26 (`run.py --tmp-parent /dev/shm/t315`). Not a defect and not filed: nothing uses it, and it is the measurement feature 460 asked for, to which that spec now points.
- A `land` test run after a gate source edit rebuilt the whole `l7r-gate` tool inside its `test` phase (3.1 s of a 4.7 s phase, once), because a test runs the tree's own wrapper, observed 2026-11-26, method: `ps-sample.py` over one run after `rust/guard/shared/src/lib.rs` had been edited and put back. Not a defect and not filed: the tool is rebuilt once an edit by whichever command next needs it, so the seconds move and are not added; tests that read the machine's live state are 451 T312's and T143's.

**Performance work?** yes: a measurement task, counted as performance work for scheduling and coming first (the GM, 2026-11-20: "I would also like for this kind of measurement task to be counted as a performance task for the purpose of scheduling and coming first"); it changes no code and is no engine-speed task, so docs/performance-checklist.md's questions have nothing to answer here. What it found to make faster is T339's, T340's, T341's, T342's and T347's, each a `[perf]` task.


<!-- plan-archive: T316 to T316 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T317 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T317 Approach (checklist part A)

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


### T318 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T318 Approach (checklist part A)

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


### T326 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T326 Approach (checklist part A)

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


### T327 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T327 Approach (checklist part A)

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


### T329 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T329 Approach (checklist part A)

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


### T330 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T330 Approach (checklist part A)

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


<!-- plan-archive: T332 to T344 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T332 to T344 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T320 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T320 Approach (checklist part A)

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


### T321 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T321 Approach (checklist part A)

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


### T325 (found by 451 T301 part 1, measured 2026-11-26: after a touch of `rust/gate/crates/core`, the 28 gate manifests' test builds ran rustc 75 times for 58 targets, 17 of them a library compiled again under another feature set, `dev/measurements/2026-11-26/cargo-hashes/gate-call.sh`)

- **Approach**: every crate's `[dev-dependencies]` names the test-only feature on every crate of its build that has one, itself included, so cargo resolves ONE feature set for a library whichever crate a call selects; no word of a test or coverage call changes, and the lint gains one pass for the crates that name themselves (D6). Built in 19 manifests under `rust/` (41 lines, observed 2026-11-26, method: `git diff --stat -- rust` and the pin's red list), pinned by a test over the real tree, `rust/gate/crates/checks/src/checks/guard_deps/feature_sets.rs`, with the lint's third pass in `rust/gate/crates/rustc/src/rustc.rs`; `rust/Cargo.toml`'s ONE FEATURE SET comment restated as the task's line asks; `rust/Cargo.lock`, which is tracked, gains the workspace's own new edges and no outside crate. The record: `dev/measurements/2026-11-26/feature-unify/results.md`.
  - **The cause, as measured.** The gate builds tests one manifest a call and coverage with `-p` for the owed crates, and cargo unifies features over what one call selects. `testkit` of `core`, `research`, `registry`, `owed` and `archive` was on only where the selected crate's `[dev-dependencies]` named it: over the 34 workspace crates' test builds, 6 crates resolved with more than one feature set and 41 root-and-crate pairs were short of the fullest, measured 2026-11-26 (`featsets.sh`: `cargo tree --offline -e normal,dev` a manifest, no compile).
  - **T325-D1, the route is the manifests.** Measured, not chosen, each asked of cargo 1.87.0 on 2026-11-26 (`results.md`, "The routes not taken"): a feature named on the test call is refused for a crate reached only through another (`error: the package 'l7r_gate_measure' does not contain this feature: l7r_gate_owed/testkit`), and 20 of the 41 pairs are such; workspace feature unification is `-Z` only (`warning: ignoring resolver.feature-unification without -Zfeature-unification`). The task line's two candidates are both declined: the helpers always compiled would put the tests' seams into the tools, which the brief rules out (`owed`'s `entry_lines` would read a scratch record's `entry-lines.json` in place of the real report); the whole family named in every call would make a builder's check of one crate build all 28 crates' tests (observed 2026-11-26, method: `rust/gate/Cargo.toml` and `ls rust/gate/crates`).
  - **T325-D2, a crate that is the root names itself** (`l7r_gate_core = { path = ".", features = ["testkit"] }`, and so `research`, `registry`, `owed`, `archive` and `l7r_shared`). CONVENTION (cargo's own form for a test-only feature of the crate under test): without it `core`'s own test build, and a coverage build selecting `core` alone, compile it without the feature every other call compiles it with.
  - **T325-D3, the rule is what cargo resolves, and the fix it prints is the direct line.** CONVENTION: the pin reads each manifest's `[features]`, `[dependencies]` and `[dev-dependencies]` as resolver 2 does for the forms the workspace writes (a path dependency on one line), computes each crate's features in the test build of every root, and names each root short of the fullest set with the line to add. Its red list on the old manifests is cargo's own: 41 pairs, `research` 15, `registry` 12, `owed` 9, `archive` 3, `core` 1, `l7r_shared` 1, counted 2026-11-26 both ways (`red-problems.txt`; `featsets.sh`). It cannot see a feature named on a command line (`counters`) and does not judge one.
  - **T325-D4, `l7r_shared`'s `test-env` stays apart: one set in the guard's family, not across the workspace.** DELIBERATE: the feature makes `env` read a test thread's own map, and `rust/guard/shared/Cargo.toml` says a gate crate's tests read the process's environment; turning it on for the 31 other crates that build on it would change what their tests read (observed 2026-11-26, method: `featsets.sh`'s roots). The pin holds `rust/guard` and `rust/guard/shared` to it (`APART`); the library is still built twice in a tree that tests both families, which costs one compile of `l7r_shared` an edit of it and is not a repeat a touch of a gate crate makes.
  - **T325-D5, the pin is a test in `checks`, not a new command.** CONVENTION (the precedent of `checks/documents/`): `checks` declares `reads = ["."]`, so its tests run again whenever a manifest moves, and the failure prints every line to add.
  - **T325-D6, the lint gains a third pass for a crate that names itself** (`rustc.rs`, `check`'s `lint` arm and `names_itself`). Measured, then built: `cargo clippy --all-targets` reads `[dev-dependencies]`, so with D2 both of the lint's passes had the root crate's test-only feature on, and its lines compiled only with the feature off - what the tools run - were linted by nothing. Shown with a seed, observed 2026-11-26, method: `if name.len() == 0` (clippy's `len_zero`) put into `core/src/build.rs`'s testkit-off `env`, to which `l7r-gate.sh rust lint --crate rust/gate/crates/core` answered `lint clean on 1 crate(s)`. The third pass is `cargo clippy --quiet --lib`, which reads no dev-dependency, run only for a crate whose `[dev-dependencies]` hold a `path = "."` line: with it the same lint seeded as `name.len() < 1` (another spelling, since the first seed's green was a kept result) fails the crate, exit 1, observed 2026-11-26, method: the same command through the rebuilt tool, the seed then removed. The lines it is for, observed 2026-11-26, method: `grep -rn 'feature = "testkit"\|feature = "test-env"\|feature = "counters"' rust --include=*.rs` and its `not(` hits read: `core/src/record/bundle.rs` 10 and 14, `core/src/build.rs` 92, `owed/src/record/owed.rs` 254, `rust/guard/shared/src/env.rs` 15 and `rust/guard/shared/src/checks/handle.rs` 82; `archive/src/lib.rs` 36 is feature-ON code, and every `counters`-off line (`phases`, `mode_a`, `pool`) is read by the plain pass as before, no dev-dependency naming `counters`. Its cost over the six crates that name themselves, after a touch of `core` and `l7r_shared`: 7 check compiles and 12.8 s, beside the two passes' 14 and 23.9 s, load 10 to 14, measured 2026-11-26 (`lint-pass.sh`); all six lint clean through the three passes, observed 2026-11-26, method: `L7R_RUST_FRESH=1 l7r-gate.sh rust lint` over the six, exit 0. Declined: moving the lines out from under the cfg, which would compile the tests' seams into the tools.
  - **The small lane and the healed link** (T347, T336): no test build's words changed, so `kept/alone.rs`'s key holds the same words; the key also holds the workspace's manifests, the lockfile and each crate's own `Cargo.toml`, so every crate's first build after this lands is told wide once, as any manifest edit makes it. `stepped` and `stale::built` are not edited.
  - **Measured, before and after**, all 2026-11-26 in the pool tree `diagram-backlog-b1`, one run at a time, another builder on the machine (`results.md`; `family.sh`, `rust-test.sh`, `phases.py`):

    | what | before | after |
    |---|---|---|
    | after a touch of `core`, the 28 test builds: rustc runs / targets / repeats | 75 / 58 / 17 | 58 / 58 / 0, both measured 2026-11-26 (`family.sh`) |
    | that pass, wall | 42.6 s, load 12.8 to 10.0 | 40.0 s, load 12.8 to 7.8, both measured 2026-11-26 (`family.sh`) |
    | a constant appended to `core/src/lib.rs`, the checks' test step over the 28: wall | 171.1 s, load 50.5 to 26.4 | 51.6 s, load 23.1 to 17.6, both measured 2026-11-26 (`rust-test.sh`) |
    | that run's `build` lines less its build-slot waits | 99.3 s (152.7 s less 53.4 s) | 42.5 s (no wait), both measured 2026-11-26 (`phases.py` over the run's `Phase` lines) |

    The touch pass is the like-for-like one and moved 2.6 s, measured 2026-11-26 (`family.sh`): a touch changes no content and rustc's incremental cache answers a repeat quickly, the floor T301 part 1 named. The appended-constant runs are one sample each under different load; their difference is an upper bound, not a figure to repeat as the saving. The count is exact: 17 of 75 compiles (23%) were repeats and none of 58 is, measured 2026-11-26 (`family.sh`).
  - **The coverage build** is reached by the same lines and was not compiled (a builder runs no coverage): `cargo tree` with `-p claims`, `-p claims -p bundle`, `-p claims -p owed`, `-p claims -p semantic`, `-p core` alone and all 28 together each resolve the five crates `[testkit]`, measured 2026-11-26 (`results.md`, "The coverage build"), where T301 part 1 found the set changing with the selection.
  - **A production build compiles what it did**: `cargo tree --offline -e features,no-dev -p <package>` for the seven packages the launchers build, captured before the first edit and after the last, identical by `diff -r`, and none names `testkit` or `test-env`, measured 2026-11-26 (`results.md`).
  - **What a test now runs differently.** `owed`'s `entry_lines` is the one place `testkit` changes what runs: eight crates (`gate`, `checks`, `ci`, `claims`, `land`, `measure`, `task`, `trials`) built `owed` without it and now get the seam - the use its own doc comment names ("this crate's tests, and those of the crates above it through the `testkit` feature") - observed 2026-11-26, method: `featsets.sh` before the edits and the pin's red list. All 28 gate crates' tests ran after the change and passed, observed 2026-11-26, method: `rust-test.sh`'s settle run, 28 `test` lines, exit 0.
  - **What only the landing's gate can show**: the coverage verdicts of the 34 crates and lint over all of them, observed 2026-11-26, method: `featsets.sh`'s roots; here 9 crates were linted and `mode_a`'s tests run (`make rust-test CRATE=rust/mode_a`: 362 passed), its manifest having gained one line, `research` with `testkit`, which adds a public module.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a library gets one feature set in every crate's test build | red first 2026-11-26 (item 9); pinned by `every_test_build_under_rust_compiles_a_library_with_one_feature_set` | n/a: tooling | none | n/a |
| a root short of a feature is told the line to add, itself by `path = "."` | pinned by `a_root_that_gets_fewer_features_is_told_its_line` (new code, not run red) | n/a: tooling | none | n/a |
| `test-env` is held in the guard's family alone | pinned by `a_feature_held_apart_is_one_set_in_its_own_family_alone` (new code, not run red) | n/a: tooling | none | n/a |
| a crate that names itself is linted a third time, no dev-dependency read | red first 2026-11-26 (item 9); pinned by `a_crate_that_names_itself_is_linted_a_third_time_with_no_dev_dependency_read` | n/a: tooling | none | n/a |

### T325 Approach (checklist part A)

1. **The goal, in the world.** A gate crate's library is compiled once for an edit, whichever crate's tests or coverage are asked next: the same features for it in every test build and in the coverage build, and the tools built as before.
2. **The constraints.** T325's line in `tasks.md`: measure, then build the cheaper route, and restate `rust/Cargo.toml`'s comment. The coordinating session's brief: nothing a production build compiles in may change; T347's small lane and T336's healed link keep working; red-first where a test can pin it; the re-measurement T301 part 1's way, one run at a time, no load generator.
3. **Where each comes from.** G: none - T325's line holds no words of the GM; the question behind T301 is his of 2026-11-26, as T301's section relays it. O: T301 part 1's section and the measurements of the Approach.
4. **Do they describe the world here?** Yes: T301 part 1's 75 runs for 58 targets were found again in this tree before any edit, measured 2026-11-26 (`family.sh`, the run after the tree's pre-warm ended).
5. **The order.** After T301 part 1 (the finding), T336 and T347 (whose calls it leaves alone). Before T301's part 2 and T278, as T301's section says: it changes how many hashes are live. T389 was filed here for the lint's lost reach before the plan review ruled it this task's to mend; D6 mends it, and nothing of T389 is left to do.
6. **The exits.** Green: the pin test green and the touch pass at 58 runs for 58 targets, measured 2026-11-26 (`family.sh`), then the landing's gate. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, observed 2026-11-26, method: `make rust-test CRATE=rust/gate/crates/checks`'s result line with the test file added and the manifests as they were: 198 passed, 1 failed (`every_test_build_under_rust_compiles_a_library_with_one_feature_set`, naming 41 lines); with the manifests edited, 199 passed. The module's other two tests exercise code the old tree does not have and were not run red (observed 2026-11-26, method: the module read). THE LINT'S PASS, observed 2026-11-26, method: `make rust-test CRATE=rust/gate/crates/rustc`'s result line with `names_itself` and the test added and the lint arm as it was: 116 passed, 1 failed (`a_crate_that_names_itself_is_linted_a_third_time_with_no_dev_dependency_read`, two passes where three were asked); with the arm changed, 117 passed. After: `featsets.sh` shows 1 crate with more than one feature set (`l7r_shared`, D4) where it showed 6, and the touch pass 58 rustc runs for 58 targets, measured 2026-11-26 (`family.sh`).
10. **Before moving a constant.** n/a: no constant moves.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Not a defect of a map: no map changes. The wrong outcome it answers: 17 of 75 compiles after a touch of `core` were a library built a second, third or fourth time, measured 2026-11-26 (`family.sh`).

**Found and left?**
- With a crate naming itself in `[dev-dependencies]`, both lint passes had its test-only feature on and its feature-off lines went unlinted (D6); visible effect: a seeded `len_zero` in `core/src/build.rs` passed the lint. `fixed here` (the third pass; observed 2026-11-26, method: the `grep` D6 names, every `not(` hit of the three features read). T389, filed for it before the review, has nothing left to do and is the session's to withdraw.
- The tree's pre-warm compiled beside the first "before" pass with the same words and three manifests found their build done (72 rustc runs for 54 targets), observed 2026-11-26, method: `ps` (`l7r-rust prewarm`, started 18:41) and the pass run again after it ended. Not a defect and not filed: it is the pre-warm doing its job; a measurement of a tree's builds waits for it to end, as `results.md` says.
- Three comments of `rust/Cargo.toml` (its lines on the roxmltree, geo and resvg pins) say `rust/Cargo.lock` is not tracked, and `git ls-files rust/Cargo.lock` names it, observed 2026-11-26, method: that command and `grep -n "not tracked" rust/Cargo.toml`. Not a defect and not filed: a comment's wording with no outcome wrong - the pins hold either way - and outside this task's lines of the file.
- `l7r_shared` is still built under two feature sets in a tree that tests both the guard and the gate (D4). Not a defect and not filed: the two sets read the environment differently on purpose.

**Performance work?** yes - a `[perf]` task of the checks and the builders' loop: after a touch of `core`, the 28 gate manifests' test builds ran rustc 75 times for 58 targets before and 58 times for 58 after (17 repeats to none), 42.6 s and 40.0 s at load 13, and after a one-line edit of `core` the checks' test step over the 28 took 171.1 s at load 50 before and 51.6 s at load 23 after, one sample each, measured 2026-11-26 (`dev/measurements/2026-11-26/feature-unify/results.md`). Not an engine-speed task: the checklist below is answered for the checks, and no map is drawn.

### T325 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** In compiles of one library under several feature sets: 17 of the 75 rustc runs after a touch of `core`, `owed` 4 times, `archive`, `bundle` and `registry` 3, measured 2026-11-26 (`family.sh`).
2. **Removes work, or only moves it?** Removes it: the 17 repeated compiles are not made. It adds the lint's third pass for six crates, 7 check compiles and 12.8 s after a touch of `core` and `l7r_shared`, measured 2026-11-26 (`lint-pass.sh`). It adds a one-time rebuild in each tree, 53 rustc runs and 200.1 s for the 28 test builds at load 15, measured 2026-11-26 (`family.sh`, the warm pass).
3. **What do you expect it to save, and why?** A fifth of the compiles after an edit of a crate many build on; in seconds, between the 2.6 s of the touch pass (incremental cache answering) and the 56.8 s between the two appended-constant runs' compile spans, which also holds their load difference, measured 2026-11-26 (`results.md`). GUESS until `make task-time` is read for a day after the landing.
4. **How does the work grow with the settlement?** n/a: no map is drawn. The repeats grew with the number of crates above a testkit crate; there are none now.
5. **What did the before and after show, and under what conditions?** 75 runs for 58 targets before, 58 for 58 after, load 12.8 at the start of both; the appended-constant runs 171.1 s at load 50.5 to 26.4 and 51.6 s at load 23.1 to 17.6, measured 2026-11-26 (`results.md`) - evidence, with the loads beside it, not a pass.
6. **Did any map move, and does it still keep the research?** No map is drawn by the checks; none moved.


### T319 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T319 Approach (checklist part A)

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


<!-- plan-archive: T324 to T289 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T324 to T345 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T328 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T328 Approach (checklist part A)

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


### T331 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T331 Approach (checklist part A)

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


### T334 (the coordinating session's own briefs of 2026-11-26 broke the sizing rules of `scripts/container/builder-brief.md` five times with nothing refusing - T285, T298, T316 and T308 each reached the 300k cap, T315 ended at 308k - and carried no STOP POINT line; the GM asked that day whether the instructions were in the right place)

- **Approach**: the standing part of a builder's brief is printed by a command that sizes the brief first, and a guard holds a builder's dispatch to the block's first line. Built in two halves: the build half wrote the command, the guard and their tests and ended at a handoff; this closing half made the one change the coordinating session ruled (T334-D7), reached every line with a test, took the message checks and wrote this section.
  - **What is built.** `make builder-brief T=<task(s)> KIND=fix|measurement|build-half|closing-half [F=] [JOBS=] [MEASURES=] [CRATE=] [BLOCKS=] [LOAD=1]` (`rust/gate/crates/task/src/builder_brief.rs`) refuses an oversized brief from its caller's own words, then takes the task's tree from the pool by `builder_tree::run` in process and prints the block: the marker line `BUILDER-BRIEF <feature> <task> KIND= JOBS= TREE=`, `Blocks:`, the tree and its exports, the kind's STOP POINT, the checks of its tier, the filing and report lines, and where asked the order-and-stop sentence and the "runs ALONE" line. `builder-brief-hooks` (`rust/guard/src/guards/builder_brief_hooks.rs`, PreToolUse on Agent) refuses a builder's dispatch with no marker line, with a marker of an unknown kind or of more jobs than `JOBS_MAX`, with a marker whose tree the pool does not hold for its task, or a `KIND=measurement` brief with a job line that orders a source edit; each refusal prints the command that makes the brief. The marker's one format is `rust/guard/shared/src/builder_brief.rs`, written by the command and read by the guard. `scripts/container/builder-brief.md` lost its pasted block and keeps what a prompt cannot show: each rule with its incident.
  - **T334-D1, built, a DEVIATION from the task's line: the kinds are `fix|measurement|build-half|closing-half`.** The line wrote `fix|measurement|mechanism-build|closing`. Label: CONVENTION (a naming of the tooling; no research claim). Reason: the coordinating session's dispatch brief for the build, written after the line, named the kinds this way, and `build-half` and `closing-half` are the words `builder-brief.md` already used for the two builders of a mechanism.
  - **T334-D2, built, a DEVIATION from the task's line: an unsplit mechanism is refused by the COMMAND, not by the PreToolUse check.** The line lists "a mechanism not split into its build and closing halves" among the check's refusals. Label: CONVENTION (where a rule of the tooling lives). Reason: whether a task is a mechanism is read from its line in `tasks.md`, which the command reads once, before a tree is taken (`mechanism()`: one of the phrases "a new command", "a new guard", "a guard refuses", "a PreToolUse check", or a `make <target>` with a hyphen that the clone's Makefile does not define); the guard would read `tasks.md` on every Agent call to make a second copy of a check the command has already made, and a builder cannot be dispatched with a marker except by running the command. `KIND=fix` on such a line is refused with the two commands to run; `SIZING_OK="<reason>"` passes this one refusal for a line that names a guard or command the task only repairs, logged by the Makefile's `LOGESCAPE`. The guard still refuses a marker of more than `JOBS_MAX` jobs, which only a hand-edited marker can carry.
  - **T334-D3, built: a builder's dispatch is known by the pool's registry, not by a name's shape.** An `Agent` call of type none, `general-purpose` or `claude` whose prompt names a path some clone's pool registry holds (ended at a character that is no part of a name), or carries a marker line. A defined agent, `Explore` and `Plan` are never one, and a prompt opening `Run the claims round` is exempt as `context_cap_hooks/split.rs` reads it. Label: CONVENTION. Reason: a check agent is told the builder's tree to read it, and a guard that fires on correct work teaches a session to bypass it.
  - **T334-D4, built: the marker and the escape count only on a LINE OF THEIR OWN.** T334's own build brief named both in a sentence; replayed, it is refused for no marker and takes no escape. A reason that starts `<` (the refusal's placeholder pasted back) is no reason. Label: CONVENTION. The shared `escape_or_refuse` was not used: it reads a token anywhere in a command, and a prompt is prose.
  - **T334-D5, built: the escape `BUILDER_BRIEF_OK: <reason of two words or more>` is checked after "is this a builder's dispatch" and before every refusal**, so a dispatch that is no builder's records nothing and every escape taken is logged. Label: CONVENTION.
  - **T334-D6, built, a DEVIATION from the dispatch brief: `KIND=measurement` REQUIRES `MEASURES`.** The brief wrote it optional. Label: CONVENTION. Reason: left optional, the bound never fires on a caller who did not think to count, which is T315's case.
  - **T334-D7, built on the coordinating session's ruling of 2026-11-26: a BUNDLE is briefed as one builder.** The build half refused more than one task in `T=`; the ruling: `make builder-brief T=a,b` is allowed where `make builder-tree T=a,b` allows it - one builder, one tree, the marker naming both - because T299 and T282 were built as one bundle that day and an escape on every bundle would spend the audit's falsifier. Label: CONVENTION. As built: the tasks are joined by commas in the marker (a space would end the marker's task word), each task's line is read and a mechanism among them still refuses `KIND=fix`, the handoff is `<a>-<b>-build.md`, scratch files take the first task's prefix, and the guard holds the tree to every task the marker names. The pool hands a bundle the tree that ONE of its tasks already holds; the command refuses that case, naming the brief for what holds the tree and the brief for the other task, since the guard would refuse the block made on it.
  - **T334-D8, built: every sizing refusal runs before the pool's handout**, so a refused brief holds no tree (asserted in `a_brief_is_sized_before_any_tree_is_taken`). Label: CONVENTION.
  - **T334-D9, built: `MEASURES_MAX` is 6 and `JOBS_MAX` is 3, both GUESS knobs.** `JOBS_MAX` is the sizing rule's own limit, set where the measured hand-off rate steps up (`builder-brief.md`, "Why"). `MEASURES_MAX` is a GUESS: T315's brief counted as one job, timed seven crates and priced eight levers and ended at 308k of context (observed 2026-11-26, method: T315's builder report and its record `dev/measurements/2026-11-26/test-run-split/`); no brief was ever sized by this count, so the bound sits under the smaller of the two and is a knob to move on the first measurement builders it sizes. Both are in `dev/audits/builder-brief-command.md`'s `covers:` lines.
  - **T334-D10, built NARROW, and said to be: the measurement rule reads a line opening `Job <n>`, `Part <n>` or `Step <n>` that holds `fix`, `fixes`, `implement`, `patch`, `build it` or `red-first`.** The task's line says "a KIND=measurement brief that names a source edit"; a guard that read every sentence for an edit would refuse correct measurement briefs. Label: GUESS (the word list and the three openings). What it misses and its one false-positive form are at the head of the guard's file and under Found and left.
  - **T334-D11, built: the block is under 2,000 characters and carries no rule text.** `agent-prefix-hooks` refuses a prompt that repeats 2,000 characters of an earlier dispatch of its type, and every builder is one type, so the block names `builder-brief.md` instead of quoting it (pinned in `each_kind_s_block_opens_with_its_marker_and_stays_short`). Every kind's block holds a line opening `STOP POINT (`, which `split.rs` knows a code builder by. Label: CONVENTION.
  - **T334-D12, built: the build half's handoff is `<git common dir>/l7r-handoffs/<task>-build.md`**; a closing half asked for before it exists gets a note on stderr, not a refusal. Label: CONVENTION.
  - **The replay.** The table's label: observed 2026-11-26, method: `dev/measurements/2026-11-26/builder-brief-replay/t334-replay.py` - every Agent call of the coordinating session's transcript dated 2026-11-26 UTC piped through the built guard by `tests/hooks/builder-brief-hooks.sh`, on a fixture pool of the trees the prompts name, all free.

    | verdict | dispatches | which |
    |---|---|---|
    | refused, no marker | 56 | every one a builder's dispatch into a pool tree, T334's own build brief among them |
    | refused, any other rule | 0 | none carried a marker |
    | passed, defined agents | 36 | the checks |
    | passed, ad-hoc, no pool tree named | 17 | measuring agents, and builders that worked in the clone itself |
    | passed, the claims round | 1 | exempt by its opening words |
    | no builder's dispatch, refused | 0 | the escape was needed for none |

    The record, with the second table - the five oversized briefs given a truthful caller - is `dev/measurements/2026-11-26/builder-brief-replay/t334-results.md`. Beyond "no marker", the command's sizing takes T285 (a mechanism as one fix), T298 (`JOBS=4`) and T315 (`MEASURES=7`) from the caller's own words, and neither T316 nor T308 (observed 2026-11-26, method: the command run on a scratch fixture repository holding the real `tasks.md`, `L7R_BUILDER_POOL=0`, and `t334-replay2.py` for the guard's rule). The detectors were not tuned until they fired. The `tree-not-held` rule was not replayed: the pool's holders of each moment of that day are not recoverable.
  - **The guard's messages.** Its refusals were judged by `message-check` from the suite's rendering, copied into this tree's store by hand as 451 T338's line describes: the no-marker text and the too-many-jobs text each failed BREVITY once (a rationale and a hand-off rate, cut) and passed reworded; the other refusals passed as written. Every builder-brief wording has its PASS in `dev/guard-messages.tsv`.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the command's sizing, before any tree (T334-D2, D6, D8, D9) | `builder_brief::tests::a_brief_is_sized_before_any_tree_is_taken` | n/a: tooling | none | n/a |
| each kind's block, its marker, its length and its STOP POINT line (T334-D11, D12) | `builder_brief::tests::each_kind_s_block_opens_with_its_marker_and_stays_short` | n/a: tooling | none | n/a |
| the mechanism test and the task's line | `builder_brief::tests::a_task_s_line_names_a_new_mechanism_by_a_phrase_or_an_unknown_target`, `builder_brief::tests::a_feature_is_found_by_its_number_and_an_archived_task_by_its_line` | n/a: tooling | none | n/a |
| a bundle (T334-D7) | `builder_brief::tests::a_bundle_is_briefed_as_one_builder_on_the_tree_held_for_it`, `builder_brief_hooks::tests::a_marker_is_held_to_its_kind_its_jobs_and_the_pool` | n/a: tooling | none | n/a |
| the marker's one format | `l7r_shared::builder_brief::tests::a_marker_round_trips_and_a_mention_is_none` | n/a: tooling | none | n/a |
| the guard (T334-D3, D4, D5, D10) | `builder_brief_hooks::tests`, `tests/hooks/test-builder-brief-hooks.sh` | n/a: tooling | none | n/a |

### T334 Approach (checklist part A)

1. **The goal, in the world.** A builder's brief is sized before it is written and opens with a block the tooling printed; a brief that breaks the sizing rules, or a builder sent into a pool tree without the block, is refused with the command to run.
2. **The constraints.** The sizing rules of `scripts/container/builder-brief.md` (one task or one bundle, at most three jobs, a mechanism as two builders, a measurement sized by what it measures); the pool of 451 T285 (a tree comes from `make builder-tree` alone); `agent-prefix-hooks`' block of 2,000 repeated characters; `split.rs`' STOP POINT line; a guard that fires on correct work teaches a session to bypass every guard (root `CLAUDE.md`, "What is enforced").
3. **Where each comes from.** G: the GM's words of 2026-11-26 on T334's line, in request.md under "2026-11-26: a builder is dispatched through the tooling (451 T334)"; what to build from them is the coordinating session's, as that section says. O: the replay above; `dev/measurements/2026-11-25/talk-measures/` for the three-job limit.
4. **Do they describe the world here?** Yes for the dispatches replayed: the guard refuses every builder's dispatch of the day and no other. Not wholly for the sizing: it rests on the caller's own count of jobs and things measured, and misses two of the five briefs it was built for (Found and left).
5. **The order.** After T285 (the pool) and T289 (a builder files what it finds); before T352, T353, T354 and T360, and before T302.
6. **The exits.** Green: the changed crates' tests, lint, format and coverage clean, the guard's suite and its two neighbors green. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: the mechanism test and the measurement rule were written from the day's briefs and then replayed over all of them once; what they missed is reported, not tuned away.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, observed 2026-11-26, method: `bash tests/hooks/test-builder-brief-hooks.sh` with the guard's `decide` returning at its prefilter, `14 passed, 13 failed`; restored, `27 passed, 0 failed`. Not seen red: the command's tests and the marker's test, new code with no older behavior to fail on. After, observed 2026-11-26, method: `make crate-checks CRATE="rust/guard rust/guard/shared rust/gate/crates/task rust/gate"`, green - tests (guard `548 passed`, shared `506 passed`, task `104 passed`, gate `8 passed`), lint, format and `cover clean on 4 crate(s)`, 110 s of wall time; `bash tests/hooks/test-builder-pool-hooks.sh`, `17 passed, 0 failed`, and `bash tests/hooks/test-agent-model-hooks.sh`, `40 passed, 0 failed`. To see it by hand: `make builder-brief T=T334 F=451 KIND=build-half` prints the block; `make builder-brief T=T334 F=451 KIND=fix` is refused with two commands.
10. **Before moving a constant.** n/a: `MEASURES_MAX` and `JOBS_MAX` are GUESS knobs, no claim's.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** No map changes. The check it adds: a builder's dispatch that broke the brief's sizing rules, or carried no standing block, went out with nothing refusing.

**Found and left?**
- A build half that reaches the context cap cannot write the handoff its closing half is told to read: the cap's one exit lets through only a file named `<task>-<agent_id>.md`, so the closing half's block names a file that does not exist and the command only notes it on stderr. Not fixed here: it changes `context_cap_hooks.rs`' exit, another guard's rule with its own red-first test. Filed as T352; lands before T302.
- A builder briefed to work in the session clone itself, naming no pool tree, passes the guard with no marker and no sizing: 17 ad-hoc dispatches of the replay's day named none, some of them builders (observed 2026-11-26, method: `dev/measurements/2026-11-26/builder-brief-replay/t334-replay.py`). Not fixed here: which of them edit source is unmeasured, and a rule that read "names the clone and orders an edit" from prose would refuse readers. Filed as T353; lands before T302.
- A measurement and a build briefed as two jobs - T316's and T308's shape - is caught by nothing reliable: the command passes both, and the guard's measurement rule fires on T308's brief only by a word of its measurement line and not on T316's numbered list (observed 2026-11-26, method: `dev/measurements/2026-11-26/builder-brief-replay/t334-replay2.py`). Not fixed here: whether `JOBS` over 1 on a measurement is refused outright is a decision to take from a week of briefs the command made, not from five. Filed as T354; lands before T302.
- A builder sent from a Workflow script's `agent()` call is not seen: the guard matches the Agent tool, and `workflow_hooks.rs` holds a Workflow to the model rule alone. Not fixed here: no builder was sent that way on the replay's day, and it needs `workflow_hooks.rs` to put a workflow's `agent()` call through this guard's verdict, that guard's change with its own test. Filed as T360; lands before T302.

**Performance work?** yes, by FR-013's own test (the GM 2026-11-20: "can we in general priotitize performance improvements going forward?"): it makes the builders' loop faster, since each brief the command refuses is a builder that would have reached the context cap and handed off, a fresh builder's re-reading each time (`builder-brief.md`, its paragraph on why builders stop where they do). Its line carries no `[perf]` tag; that tag is the coordinating session's to add. Not an engine-speed task, so the performance checklist's engine items do not apply.

### T333 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T333 Approach (checklist part A)

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


### T337 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T337 Approach (checklist part A)

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


### T338 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T338 Approach (checklist part A)

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

### T335 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T335 Approach (checklist part A)

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


<!-- plan-archive: T336 to T299 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T336 to T336 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

### T343 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T343 Approach (checklist part A)

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

### T346, T382 (bundle) (a carry booked to the task that took the tree in its last second, and a builder's lines outside every span in no span: on 2026-11-26 the carry from diagram-backlog-t271 that ended 19:40:54Z read as T308's where T301 held the tree, and 60 agents' 4,149 own lines in the logs since 2026-11-21 were in no span, measured 2026-11-26 (Python passes over the pool log and every log's start, stop and by lines))

- **Approach**: the carry's holder is read at its run's start, and an agent's own lines outside every span of it open a span of their own.
  - **T346, the cause.** `tiers::carries` (`rust/gate/crates/measure/src/measure/task_time/tiers.rs`) took the pool log's last take of the carry's tree at or before the run's END. The run of 2026-11-26 was one command, `make carry`, `make builder-tree-release` and `make builder-tree` together, from 19:40:49.7Z to 19:40:54.5Z, and the pool log holds T301's release and T308's take at 19:40:54Z, so the last take before the end was T308's, measured 2026-11-26 (the run's two lines in the 451 log and `.git/builder-pool.log`'s lines for the tree).
  - **T346, the rule.** The holder is the last take at or before the run's START: what the carry brought into the clone is what the tree held when the command began, whatever the same command or the next handout did to the tree after. A tree nobody held when the run began is no task's carry, as before for a tree with no take at all. The carry's time in the report is still its run's end, which `batches` compares with the landing's.
  - **T346, the live view.** `make task-progress` reads the same function (`progress.rs`, `landings`), so its staged list and each block's "carried into the clone" line follow; its `retask` already read a `Phase` line's holder at the phase's start.
  - **T382, the cause.** `columns::flight` (`rust/gate/crates/measure/src/measure/where_time/columns/flight.rs`) opened a span only at a `SubagentStart` line, so a builder's own lines after a stop with no start line logged were in no span: the builder-minutes column and "Working at once" left that time out while its turns and runs were booked from the lines.
  - **T382, the population.** Read from the 451 log alone the task line's figures stand: 64 agents, 1,981 own lines. Read as the commands read them - an agent's start and stop lines and its own lines from every feature's log - 60 of the 3,050 agents with own lines since 2026-11-21 had such lines, 4,149 of 143,674 own lines, in 242 spans of 557.5 min under the rule below: 45.4 min on 2026-11-21, 277.9 on 11-22, 232.2 on 11-23 and 2.0 on 11-24, none since, measured 2026-11-26 (a Python pass over every log's start, stop and by lines, the rule's spans summed by day). All 60 are `general-purpose` agents with a start line earlier, every one of the 242 spans ends at a stop line, and no two own lines inside one are 4 min apart, so no span runs across a time the builder stood stopped, measured 2026-11-26 (the same pass, each span's end and its longest gap between own lines listed).
  - **T382, the rule.** An own line of an agent outside every span of it opens a span, from that line to the agent's next stop, else to its last own line before its next start or the window's end - `span_end` itself, so the span ends as a started one does. A line alone, with no later line or stop of the agent, holds no time and opens none. An agent with no start line takes its kind from its first stop that names one (so a review agent whose start is in no log read is not counted a builder), else `?`. Each such span is in flight for a wait as a started one is (`Flight::book`). This is T345's reading from the other side: a builder's stop to its next own line is the builder stopped, and its last own line to a later start is too.
  - **T382, why the span starts at the first own line, not at the stop.** The stop to the next line is the time T345 books as `builders: stopped, waiting to be resumed`; a span from the stop would count it as work twice over.
  - **Two tests pinned the old reading and are restated.** `a_resumed_builder_is_booked_in_every_span_and_stopped_between_them`: the fixture's third run, 03:00 to 03:30 with no start line, is now a span - the builder's minutes 109 s where they were 79, the session's wait from 02:40 the builder stopped to 03:00 and its reply to 03:30, measured 2026-11-26 (the test's asserted figures, old and restated). `the_columns_book_make_runs_compile_and_until` (`make where-time`): a `Stop` written before `inflight` books the wait's last 7 min to the agent whose lines ran through it, where no run held them, measured 2026-11-26 (the test's asserted row, old and restated).
  - **The re-measurement, read-only**, on the clone's real logs, the old build's binary kept as a copy and both run back to back: `l7r-gate measure task-time --root /diagram/.clones/diagram-backlog --since 2026-11-26T17:00:00Z --until 2026-11-27T01:00:00Z`, measured 2026-11-26 (the two reports, `t346-before.md` and `t346-after.md` in the session's scratchpad; no `SINCE=last`, the GM's marker untouched). The window was still open when both ran (00:36Z and 00:37Z of its last hour), so a row that moved between them by the log's growth is not counted a change here: `plan review: agents` 132.4 to 134.5 min, the reviews then running, as it had grown from 129.7 between two runs of the OLD binary eight minutes apart, measured 2026-11-26 (the row in the old binary's two reports and the new one's).
  - **The pinned window, the builder-minutes column.** 742.5 min before and 742.5 after, 31 builders over the 23 landed tasks both times, no row changed, measured 2026-11-26 (the fourth column of each report's "The landed tasks" table, summed). No agent of this window has an own line outside its spans: the last such line in any log is of 2026-11-24, measured 2026-11-26 (the Python pass above, its spans by day). The one span the rule opened in this run lies outside the window, at the first line the report reads back to (2026-11-24T17:00:06Z, 1.1 min, an agent whose start is before that line), measured 2026-11-26 (a build that printed each span the rule opened, the print removed after).
  - **The pinned window, the carries booked to each task.** 27 carries by main sessions ended in the window, each booked to one holder both times; one changed, the task line's own: the carry from diagram-backlog-t271, 19:40:49Z to 19:40:54Z, T308's before and T301's after, so T308's count falls from 1 to 0 and T301's rises from 0 to 1 and the other 23 holders' counts stand, measured 2026-11-26 (a Python pass over the logs' `make carry` runs, their commands' `FROM=` in the session's transcript and the pool log, the holder read at each run's end and at its start). Neither task landed in the window, so no row of the report's landed table moved. The live view shows it (`l7r-gate measure task-progress --root /diagram/.clones/diagram-backlog --at 2026-11-26T19:45:00Z`, old binary and new): the staged list's line `451 T308: carried 19:40:54, 4.1 min ago` reads `451 T301: carried 19:40:54, 4.1 min ago` after, and T308's block no longer holds a `carried into the clone 19:40:54, 4.1 min ago` line, with no other line of the view changed, measured 2026-11-26 (the two outputs' diff).
  - **A settled window where the rule's spans are**, since the pinned one holds none: `--since 2026-11-22T00:00:00Z --until 2026-11-23T00:00:00Z`, the same two binaries, measured 2026-11-26 (`t346-w2-before.md` and `t346-w2-after.md` in the session's scratchpad). The 96 landed tasks' builder minutes sum to 2743.6 where they summed to 2482.0, 95 builders both times, 24 rows changed, measured 2026-11-26 (the fourth column of each report's "The landed tasks" table, summed). The eight that moved most:

    | task | builders | builder minutes before | after | blocking before | after |
    |---|---|---|---|---|---|
    | 449-rust-codebase T197 | 2 | 17.8 | 131.5 | 141.8 | 141.8 |
    | 451-time-retro-and-efficiency T110 | 2 | 71.8 | 105.4 | 104.5 | 104.5 |
    | 449-rust-codebase T261 | 5 | 98.3 | 113.0 | 247.0 | 247.0 |
    | 449-rust-codebase T263 | 1 | 13.6 | 28.1 | 31.8 | 31.8 |
    | 449-rust-codebase T273 | 1 | 7.6 | 19.0 | 21.2 | 21.2 |
    | 451-time-retro-and-efficiency T89 | 2 | 89.5 | 99.7 | 103.0 | 103.0 |
    | 449-rust-codebase T247 | 3 | 51.8 | 61.2 | 91.1 | 101.9 |
    | 449-rust-codebase T235 | 1 | 19.9 | 28.2 | 23.0 | 23.0 |

    The window's minutes stand at 8737.4 (a builder's turns and runs were always booked from its lines); its blocking rose from 3539.9 to 3550.8, the sessions' waits that fell on a builder inside a span it now has; "Working at once" reads none 129.5, one 162.1, two 204.0, three or more 944.4 where it read 129.9, 173.3, 264.3 and 872.5, measured 2026-11-26 (the two reports' opening lines and "The window, every category" tables).
  - **What the open tasks still distort in these figures.** T332 and T344 (a pool tree's Phase lines carrying an old task): each task's compile, test and hook-suite phase minutes and blocking. T393 (a bundle's carry is no task's): the "its own table ends at" cell of a task landed from a bundle, and the task its carry's run is keyed to.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a carry's holder read at its run's start | `a_carry_is_the_task_s_that_held_the_tree_when_it_began`, red on the old code | n/a: tooling | none | n/a |
| an agent's own lines outside every span a span | `own_lines_outside_every_span_are_a_span`, red on the old code | n/a: tooling | none | n/a |
| the booking and `make where-time` read the new span | `a_resumed_builder_is_booked_in_every_span_and_stopped_between_them` and `the_columns_book_make_runs_compile_and_until`, restated | n/a: tooling | none | n/a |

### T346, T382 Approach (checklist part A)

1. **The goal, in the world.** `make task-time` and `make task-progress` book a carry to the task whose work it carried, and a builder's minutes hold every stretch its own lines show it working, with or without a start line.
2. **The constraints.** The task lines of T346 and T382; T324 and T345's reading of a resumed builder (`plan-done.md`, "T324, T345 (bundle)"): a stop to the next own line is the builder stopped; `span_end`'s rule for a span no stop ends (451 T243).
3. **Where each comes from.** O: the task lines' measurements of 2026-11-26. G: the GM's words of 2026-11-20 on measurement work, in `request.md`, which count this as performance work.
4. **Do they describe the world here?** Yes: the old build's live view at 19:45Z lists T308 as carried 19:40:54, and the old build's report of 2026-11-22 reads 2482.0 builder minutes where the lines give 2743.6, measured 2026-11-26 (the reports named above).
5. **The order.** T346 then T382, one section; T332, T344 and T393 stay open and separate.
6. **The exits.** Green: `make builder-checks CRATE="rust/gate/crates/measure"` in the builder's tree, the full gate at the landing. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** RED FIRST, measured 2026-11-26 (`make rust-test CRATE=rust/gate/crates/measure`, each run's result line). T346's test on the old `carries`: 268 passed, 1 failed; with the rule, 269 passed. T382's test on the old `flight`: 269 passed, 1 failed; with the rule and the two pinned tests not yet restated, 268 passed, 2 failed; after, 270 passed, 0 failed, lint and format clean (`make builder-checks`).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The finding: the reports the GM reads to decide how the work is run named the wrong task for a carry (T308 for T301's, 2026-11-26) and left a builder's working time out of its minutes (557.5 min over 2026-11-21 to 11-24), measured 2026-11-26 (the passes named above). No map changes.

**Found and left?**

- A bundle's carry is no task's in `make task-time`: the pool log's detail for a bundle is `451 T324,T345`, `tiers::batches` splits it on whitespace alone, and the landed table reads "its landing's start (no carry found)" for T324, T345, T370 and T372 in the pinned window, measured 2026-11-26 (the after report's landed table and a grep of `.git/builder-pool.log`). Not fixed here: which task a bundle's carry run books its minutes to is a rule to choose, a third job past this bundle's two. Filed as T393; lands before T380.

**Performance work?** yes: a measurement task, counted as performance work by the GM's words of 2026-11-20; it makes nothing faster itself


### T348 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T348 Approach (checklist part A)

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


### T349 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T349 Approach (checklist part A)

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


### T350 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T350 Approach (checklist part A)

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

<!-- plan-archive: T339 to T315 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->
<!-- plan-archive: T340 to T315 moved to plan-done.md, 2026-11-26 (feature 375 FR-044) -->

<!-- plan-archive: T342 to T315 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T351 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T351 Approach (checklist part A)

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


<!-- plan-archive: T355 to T347 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T355 to T355 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T357 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T357 Approach (checklist part A)

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


<!-- plan-archive: T359 to T358 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T359 to T359 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T353 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T353 Approach (checklist part A)

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


### T354 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T354 Approach (checklist part A)

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


### T360 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T360 Approach (checklist part A)

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

### T361 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T361 Approach (checklist part A)

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


### T362 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T362 Approach (checklist part A)

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


### T363 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T363 Approach (checklist part A)

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


<!-- plan-archive: T365 to T340 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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
### T371 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T371 Approach (checklist part A)

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

### T371 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


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

### T374 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T374 Approach (checklist part A)

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


### T375 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T375 Approach (checklist part A)

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


### T376 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T376 Approach (checklist part A)

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


### T377 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T377 Approach (checklist part A)

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

### T377 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


### T378 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T378 Approach (checklist part A)

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

### T378 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


### T379 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T379 Approach (checklist part A)

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

### T379 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>

<!-- plan-archive: T367 to T355 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T367 to T367 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T368 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T368 Approach (checklist part A)

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


### T380 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T380 Approach (checklist part A)

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
### T384 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T384 Approach (checklist part A)

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


### T386 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T386 Approach (checklist part A)

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


### T387 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T387 Approach (checklist part A)

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


### T388 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T388 Approach (checklist part A)

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



### T390 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T390 Approach (checklist part A)

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


<!-- plan-archive: T139 to T393 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

<!-- plan-archive: T392 to T383 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T392 to T392 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T399 (2 of the 30 conflicting carries of 2026-11-26 stopped on a line-per-record file both sides appended to or pruned, each resolved by hand and each hand resolution losing something; built with T300's part 2 as its rule (g))

- **Approach**: built in T300's part 2, in the same code and the same landing: `### T300 part 2`, rule (g), holds the rule, why an identical appended record is kept, and the two real carries compared with the session's commits (`rust/gate/crates/land/src/land/carry/records.rs`; measured 2026-11-26 by the replay, `dev/measurements/2026-11-26/carry-replay/t300-job2.txt`: both carry, T298's skip log with the builder's record the hand lost, T250 batch 8's baseline byte-identical to the session's later hand prune 72fdac1313). `merge=union`, the task line's other option, was not taken: it cannot drop a record one side pruned, which is the baseline's whole case.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a `.jsonl` by record | `a_line_per_record_file_keeps_both_sides_appended_records_and_drops_what_either_pruned`, red on the old code; `a_record_changed_in_place_or_added_inside_the_file_stops` | n/a: tooling | none | none |

### T399 Approach (checklist part A)

1. **The goal, in the world.** A carry whose only conflict is a record log both trees appended to or pruned is carried without a hand, and loses no record.
2. **The constraints.** T300's: all of a pick's conflicts or none; the end verified; never a choice between the sides - a record changed in place stops.
3. **Where each comes from.** O: the replay's two carries; O: the skip log's writer (`rust/gate/crates/claims/src/claims/commands.rs`); G: the brief's words for rule (g), the session's.
4. **Do they describe the world here?** Yes: both real carries replayed and compared with the session's commits.
5. **The order.** With T300's part 2; before T400.
6. **The exits.** Green: the land crate's tests and the replay's count. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing, T300 part 2's.
9. **Done, measured.** Both carries pass in the replay (30 of 30 with T300's part 2).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The session resolves no `.jsonl` conflict by hand at a carry, and the builder's appended or pruned records are not lost as both hand resolutions lost them.

**Found and left?** none

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the landings and the builders' loop faster - the session's turns at a stopped carry are builder-idle time, `dev/measurements/2026-11-27/tree-idle/results.md`); no engine speed, so no checklist.

### T399 part B (2026-11-27T01:51Z)

Owed by red-gate@2026-11-27T01:50:26Z, ruled continue by the round arbiter (`arbiter.jsonl`): the batch gate of 451 T394, T391
and T399 (with T300's carry part) was red twice in a row, at 01:42Z and 01:50Z (2026-11-27, the landing's log), each time on
lines no test reached. Line 143 of `words.rs` came in with T300's second part, which this task was built beside.

1. **What exactly is refusing?** The batch gate's coverage: `land/carry/sections.rs` line 55 and `task/builder_done.rs` line 327
   at the first run (a fixer's tests cleared them; observed 2026-11-27, method: the landing's log), `land/carry/words.rs` line 143 at the second - the closure of
   `ok_or_else` on a guard its builder documented as one no fixture can reach.
2. **A3 again.** The goal and the options stand as the section has them; the red is in tests and one error's form, not in a
   decision.
3. **A4 again.** The section's figures are unchanged by it.
4. **Moving something earlier for something later?** No. Under the two tiers a builder runs no coverage (the GM, 2026-11-26,
   `docs/process-decisions.md`, "Two tiers of checking": a few coverage failures fixed later are the accepted cost).
5. **Tuning or changing?** Changing one line's form: the error said eagerly with `ok_or`, the same behavior, no test weakened.
6. **The one-sentence test.** "Why is T399 owed this?" - it is a task of the batch whose gate was red twice.
7. **The next step is a measurement.** The batch gate run once more on the batch as it stands with the one-line repair, nothing
   else carried in before it (the arbiter's ruling).
8. **Every route measured?** The repair is first-tier green in the clone (2026-11-27, `make builder-checks` on the land crate);
   coverage is the gate's to say.
9. **After a ruling:** continue, recorded in `arbiter.jsonl`; a red on the load-sensitive hook-suite case alone (451 T139) is
   re-run as that suite, not counted a third red; a new unreached line is fixed the same way and asked again.

### T400 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T400 Approach (checklist part A)

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


### T396 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T396 Approach (checklist part A)

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


<!-- plan-archive: T397 to T397 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T398 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T398 Approach (checklist part A)

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


### T401 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T401 Approach (checklist part A)

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

### T410 (five plan reviews of 2026-11-26/27 blocked a round on a section answering no to performance work of a measurement - T315, T274, T301 and two the session headed off by brief - against FR-013's measurement clause; built with T308's part 2 as its T308-D10)

- **Approach**: built in T308's part 2, in the same code and the same landing: `### T308 part 2`, T308-D10, holds the template's new wording, the refusal at `make decide` (`rust/gate/crates/plan/src/plan/lint/perf_line.rs`), why the old stubs are still matched, and the replay over the committed plans.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the performance prompt and decide's refusal | `lint::tests::a_performance_line_answering_no_of_a_measurement_is_refused_at_decide` and `template::tests::a_stub_s_blocks_are_the_template_s_with_the_id_filled`, each red on the old code | n/a: tooling | none | none |

### T410 Approach (checklist part A)

1. **The goal, in the world.** A section for a task that measures where time goes answers yes to performance work before any review reads it.
2. **The constraints.** FR-013's measurement clause; a stub matched byte for byte is not orphaned; no check refuses good work (constitution XIV), so the refusal prints the sentence to write and the way out.
3. **Where each comes from.** G: the GM's words of 2026-11-20 on measurement work, in request.md; O: this task's line, the five blocked reviews.
4. **Do they describe the world here?** Yes: the prompt's old wording was read in `template.rs`, and the rule was replayed over the committed plans (T308's part 2).
5. **The order.** With T308's part 2; before T302.
6. **The exits.** Green: the plan crate's tests. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing, T308 part 2's.
9. **Done, measured.** The plan crate's tests of the prompt and the refusal red on the old code and green on the new, as item 9 of T308's part 2 records with its counts and method.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A section answering no to performance work of a measurement is refused at `make decide`, where a plan review blocked a round on it; `make task-add` writes the prompt with the clause named.

**Found and left?** none

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop faster, a plan review round saved); not an engine-speed task, so the performance checklist's engine items do not apply.

### T407 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T407 Approach (checklist part A)

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


### T405 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T405 Approach (checklist part A)

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


### T409, T406 (bundle) (two gaps in the gate-write guard and the walk it reads, found by 451 T307 by reading, no firing observed: the walk read no `make -C`, so `make -C <another tree> tick` was placed where its shell stood, and the guard asked only whether a gate ran in the tree its own process stood in, so `git -C <the gated clone> commit` sent from a pool tree passed while the clone's gate ran (observed 2026-11-26, method: read from `rust/guard/shared/src/tree.rs`'s make branch and `gate_write_hooks.rs`'s `decide` and `running`))

- **Approach**: the walk places a make where its own directory options put it, and the guard judges a commit, an add or a record-writing make against every tree where a gate runs.
  - **T409, the rule built.** `rust/guard/shared/src/tree/make_dir.rs` (`make_place`, called from `writes_in`'s make branch in `tree.rs`): a make's place is where its shell stands, moved by each directory option in turn, each relative to the one before and an absolute one afresh; "named" once an absolute one frees it from the shell's place, and a directory the walk cannot read is judged by what it knows of it, as git's `-C` is (451 T79's one rule, through `path_write`). The forms are GNU make 4.4.1's, measured 2026-11-26 on a scratch Makefile echoing `$(CURDIR)` (`t409-make` in the builders' scratchpad, 15 forms then 5 more): `-C D`, `-CD`, `--directory=D`, `--directory D`, `--di=D` (an unambiguous prefix: no other long option opens `di`, read from `make --help`), `-C a -C b` is `a/b`, `x -C a` (after a goal), `-sC a` and `-sCa` (in a cluster), none past `--`; `-f -C a` reads `-C` as the makefile; `-j -C a` is `a` and `-j4C a` refuses (an optional value takes only what is joined to it). The option lists that take a value are `make --help`'s: short `C E f I o W` required, `j l O` optional, and ten long ones beside `--directory`.
  - **T409, the walk's other readers, and what moves for each** (read 2026-11-26, method: `grep -rln "tree::walk\|walk_judged\|tree::judge"` over `rust/`, each make reader read):
    - `main_tree_hooks` (through `tree::judge`): `make -C <the mirror> X` sent from a clone is now `named-main` and refused, where it passed; `make -C <a clone> X` sent from the mirror now writes no mirror and passes, where it was rewritten into the clone. No command of the Makefile or `scripts/` runs `make -C` (observed 2026-11-26, method: `grep -rn "make -C\|make --directory"` over both), so no command of the project's own is moved. Pinned in `tree/tests/make_dir.rs`.
    - `gm_tree_hooks`: `make -C <gm-assistant's tree> X` is now a write in gm-assistant's main tree and refused; it passed from any other place.
    - `static_runs_hooks::run_tree` read the `-C` itself and joined it onto the make's place; with the walk placing the make there it would join it twice (`cd w && make -C rust/a static` to `w/rust/a/rust/a`), so its own read is removed and the walk's place taken as is.
    - `gate_write_hooks`: `make -C <another tree> accept` passes from the gated tree (the case `a_commit_in_another_tree_is_not_held` held, T307's section naming it owed here), and `cd <another tree> && make -C <the gated tree> tick` is held.
    - `house_style_hooks`, `make_only_hooks`, `event_log_hooks` (`writes` on a Bash line), `readme_hooks`, `builder_pool_hooks` and the bench read a make target's place as where the make runs; each now reads its `-C` place. Their suites pass unchanged.
  - **T406, the rule built.** `gated` in `rust/guard/src/guards/gate_write_hooks.rs` replaces `running` and `runs_here`: one pass over `/proc` finds every work tree where a `make done` runs (the program and the target matched as before, the tree the work tree of the process's cwd; a directory in no work tree, or a cwd that cannot be read, runs no gate). Each gated tree is judged in turn (`Gate`): a commit, an add or a record-writing make the walk places in it is held. The fail-closed cases T307 kept - a place the walk cannot read (`cd "$VAR"`) and a pattern's match with no command placed (`echo 'a; git commit'`) - hold in the tree the hook's process stands in alone; in another gated tree only a positive placement holds, or a quoted `git commit` would be refused wherever any session's gate ran. A command with no `cwd` in its event stands in the hook process's tree, as before. T307's rule stands: a write in another, ungated tree passes. The refusal's text is unchanged, so no message-check is owed.
  - **T406, kept to the brief's three kinds.** An Edit, a Write and a shell write are still judged in the hook process's tree alone: the same gap for them is filed as T430, pinned by the new test's let-through Write.
  - **The tests.** `tree::tests::make_dir::a_make_runs_where_its_own_directory_options_say` (16 forms placed in `sub`, 2 composed, 4 that read no directory, 2 with the shell's place unknown, 1 unreadable, 2 main-tree verdicts); `guards::gate_write_hooks::tests::a_commit_sent_into_a_gated_tree_from_another_is_held` (5 commands held from a pool tree, 5 let through, a Write let through, and the gated tree's commit into the pool tree let through); `a_commit_in_another_tree_is_not_held` now 5 let through and 9 held; `nothing_is_refused_with_no_gate_running_here` gains a gate whose cwd cannot be read; 2 new cases of `tests/hooks/test-gate-write-hooks.sh` (from another tree, `git -C <the gated tree> commit` and `make -C <the gated tree> tick` refused), counted in the files' text, observed 2026-11-26, method: read from the files after the last edit.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| T409, the walk reads a make's own `-C` | `a_make_runs_where_its_own_directory_options_say`, red on the old code | n/a: tooling | none: tooling | the walk's make branch as before |
| T406, a commit held in every gated tree | `a_commit_sent_into_a_gated_tree_from_another_is_held`, red on the old code | n/a: tooling | none: tooling | `GATE_WRITE_OK` with a reason |

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

### T423 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T423 Approach (checklist part A)

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
### T431 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T431 Approach (checklist part A)

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


### T430 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T430 Approach (checklist part A)

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

<!-- plan-archive: T408 to T297 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T408 to T408 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T412 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T412 Approach (checklist part A)

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


### T415 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T415 Approach (checklist part A)

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



### T418 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T418 Approach (checklist part A)

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



### T432 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T432 Approach (checklist part A)

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

<!-- plan-archive: T427 to T417 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
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
### T439 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T439 Approach (checklist part A)

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


<!-- plan-archive: T440 to T312 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T441 to T275 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T441 to T441 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T442 to T275 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T442 to T442 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T444 to T143 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T444 to T444 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T447 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T447 Approach (checklist part A)

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

<!-- plan-archive: T450 to T397 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T450 to T450 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T448 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T448 Approach (checklist part A)

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


### T451 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T451 Approach (checklist part A)

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

<!-- plan-archive: T453 to T306 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T453 to T453 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->

### T452 (found by T449's reading of the night's bad rlib: `scripts/hooks/l7r-guard.sh` cut its own build with `timeout` (SIGTERM at `L7R_GUARD_BUILD_SECS`, 45 s), the cut T336 measured breaking the next link 16 of 31 times on `rust/guard` (`dev/measurements/2026-11-26/prewarm-link/`), observed 2026-11-27, method: the evidence of T449 (1) and the wrapper's `build` read)

- **Approach**: past its limit the guard build is LEFT TO FINISH, not cut (`scripts/hooks/l7r-guard.sh`, `build` and the new `detached_build`).
  - **The call** takes `guard.lock` on fd 9 as before (`flock -n`, or `-w` under the cold seam of 451 T286), checks `stale` under it, truncates `build.log`, and starts the build as `setsid bash <the wrapper>` with `L7R_GUARD_DETACHED=<its limit>`. The build gets stdin from `/dev/null` and its stdout and stderr appended to `build.log`, and it inherits fd 9 and so the lock. The call then closes its own copy and waits on the lock (`flock -w`) for what is left of its limit. If the build ends inside the limit, the result is the same as today's. Past the limit the call writes `l7r-guard: the build passed this call's <n> s limit; it carries on detached (pid <p>), and the next call after it ends runs what it built (feature 451 T452)` to `build.log` and runs the last good binary, as it did, or fails open where none was ever built, as it did. A second call while the build runs finds the lock held and runs what is there, as before.
  - **The detached build** is the old body, unchanged in what it decides (the linker check, the build, the heal of T449, the self-check and copy, `guard.failed`). It runs in a session of its own (`setsid`), so neither a hook's process group being killed nor the session ending takes it down. It first closes every inherited descriptor but its stdio, fd 9 and bash's 255, so a harness pipe or a caller's lock is not held to its end. It runs cargo, the heal's `rm` and the self-check with `9>&-`, so a lingering grandchild cannot pin `guard.lock`. Each result (`l7r-guard.good`, `guard.failed`, `guard.healed`) is stamped with the build's START time (`guard.started`, `touch -r`): a source edited while the build ran is newer than what it built, and the next call builds again. Without that stamp, the session's edits made during a detached build would be read as built (the plan review of the approach, the advisor's point). A build that ran past its call's limit says so at its end: `l7r-guard: the build took <n> s, past the hook's <m> s limit; it finished detached (feature 451 T452)`. This is the record of an overrun that T449 (1) found missing.
  - **The one cut left is a ceiling for a hung build**, `L7R_GUARD_DETACHED_SECS`: 600 s, a GUESS knob, taken from case 7's figure for a real build given room on a loaded machine. It is never under the call's own limit, so `make builder-tree`'s 1800 s (a GUESS knob, `L7R_BUILDER_GUARD_SECS` in `rust/gate/crates/task/src/builder_tree.rs`) and hooks-test's 600 s (a GUESS knob, T449's) keep their bounds. The heal of T449 waits for cargo's `tool/.cargo-lock` and rebuilds within what is left of the ceiling, not the hook's 45 s (a GUESS knob, `L7R_GUARD_BUILD_SECS`). Detached, a gate build holding the profile is waited out instead of leaving the heal to the next call.
  - **Print-fresh** (`L7R_GUARD_PRINT_FRESH=1`): a call whose own build it left running past the limit says `its build did not finish inside the <n> s limit; run again and it carries on`, the line it said before, instead of waiting a second limit on its own build's lock.
  - DECISION (rendering; the brief's "the hook returns within the limit"): the call waits on the lock with `flock -w`, not `wait $!`, because bash's `wait` takes no timeout and a polling loop costs a fork a tick. The cost, measured 2026-11-27 (`dev/measurements/2026-11-27/guard-detached-build/wall-fast.tsv`, the stub cargo building at once, 10 runs each, load 12 to 14): a call whose build finishes inside its limit took 160.5 ms median against 152.5 ms on HEAD's wrapper, +8 ms for the second bash start and the `flock` process. That happens only on the first call after a guard source changes. That call's real build, even T95's incremental one (its figure in the wrapper's header), is far longer than the added fork. Accepted (the builder's choice); the brief's "a hook never waits longer than today" holds at the limit, which is the bound that matters.
  - **Measured, the stub cargo sleeping 3 s past a 1 s limit with a good binary standing, 10 runs each, 2026-11-27, load 9.5 to 10.4** (`dev/measurements/2026-11-27/guard-detached-build/wall.sh`, `wall-before.tsv`, `wall-after.tsv`). Before (HEAD's wrapper): the call's wall was 1.034 s median (1.031 to 1.124 s), and the next call ran the slow build's binary 0 of 10 times, measured 2026-11-27 (`wall-before.tsv`). Each next call built again, because the first build was cut. After: the wall was 1.027 s median (1.026 to 1.032 s), and the next call ran the slow build's binary 10 of 10 times, with no build of its own, measured 2026-11-27 (`wall-after.tsv`).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the build left to finish detached, the call bounded at its limit | `tests/hooks/test-l7r-guard.sh` cases 0, 6f and 6g. Red on HEAD's wrapper: 94 passed, 14 failed (measured 2026-11-27, the suite run with HEAD's `l7r-guard.sh` copied into its fixture tree). Green: 108 passed, 0 failed (measured 2026-11-27, the suite run). The cases cover: the call back at its limit; the build finishing and the next call running it with no second build; cargo's late output and the overrun in `build.log`; the build in a session other than the hook's; a second call mid-build neither waiting nor building; the healed rebuild finishing detached; cargo's lock released after the call, waited out and healed (this one also pins the descriptor closing: on a copy of the wrapper with the loop deleted, the detached build waited on the test's lock it had inherited, 98 passed and 10 failed, measured 2026-11-27, the suite run on that copy); the ceiling never under the call's limit | n/a: tooling | none | `make arbiter-ask` |
| results stamped at the build's start | case 6g's two mid-build edits: a copy of the wrapper without the `touch -r` stamps failed them, 106 passed and 2 failed (measured 2026-11-27, the suite run on that copy) | n/a: tooling | none | `make arbiter-ask` |

### T452 Approach (checklist part A)

1. **The goal, in the world.** A guard build that outlasts a hook's limit is no longer cut mid-write, so it cannot leave the stale rlib that broke the link on 2026-11-27. It finishes on its own, and the next hook call runs the guards it built. No hook waits past its limit.
2. **The constraints.** Feature 449 T004: the call is bounded inside the hook entry's timeout and never waits on another call's build. Feature 449 D7: only a build that links and self-checks replaces the good binary. 451 T286: the cold seam's bound. 451 T449: the heal, once a source change. The settings check (case 8) still reads the first `L7R_GUARD_BUILD_SECS:-45`.
3. **Where each comes from.** O: T336's 16 of 31 cut builds breaking the next link (`dev/measurements/2026-11-26/prewarm-link/`). O: T449 (1)'s reading of the night's mtimes. O: the walls above. R: T452's line and the brief's.
4. **Do they describe the world here?** Yes for the mechanism: the stub cargo's build ran in its own session id, and the walls were measured on this machine at load 9.5 to 14, measured 2026-11-27 (the suite run and `wall.sh`). The real-crate case 7 ran green through the new wrapper, measured 2026-11-27 (the suite run). Whether a detached build removes the night's broken link is inferred from T336's measurement of the cut, not observed on a second night.
5. **The order.** After T449, which heals the effect; this task removes its likely cause. It lands before T365 (T449's filing).
6. **The exits.** Green: the suite green and the walls above. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None. The wrapper's other callers were read for their limits, each a GUESS knob: `make hooks-test`'s print-fresh at 600 s, `make builder-tree`'s at 1800 s, the disk floor's cold seam at 600 s. Each keeps its bound, since the ceiling is never under it.
8. **The budget.** One landing.
9. **Done, measured.** The next call ran the slow build's binary 10 of 10 times against 0 of 10, at the same call wall (1.027 against 1.034 s median), measured 2026-11-27 (`wall.sh`). The suite went from 94 passed, 14 failed to 108 passed, 0 failed.
10. **Before moving a constant.** n/a. No limit moves. The new ceiling `L7R_GUARD_DETACHED_SECS` (600 s, a GUESS knob) is case 7's existing figure.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A guard edit made under load no longer leaves every hook on an old binary behind a cut build's broken link (49 minutes, observed 2026-11-27, method: T449's repair of the clone). It also no longer costs every later call a rebuild until one fits inside the 45 s limit (a GUESS knob, `L7R_GUARD_BUILD_SECS`).

**Found and left?** none.

**Performance work?** yes (a `[perf]` task, 451 FR-013: it makes the builders' loop and the gate faster - a cut build was rebuilt by every next call, and its broken link cost a batch gate's 8 minutes and a hand repair, observed 2026-11-27, method: T449's repair of the clone). Not an engine-speed task: no checklist answers owed.


### T462 (the round arbiter's process-fault on `round:spec-fidelity|plan:451-time-retro-and-efficiency#T448@3`, 2026-11-27T08:00Z: a blank task stub counted plan-review rounds)

- **Approach**: a task section whose every own block is still a block of the `make task-add` template byte for byte (`plan::template::stub_block`, the one stub test) is UNWRITTEN (`plan::status::unwritten`; a bundle's heading is no stub, and one block written makes the whole section written). Three places read it. (1) `make plan-delta`'s keys drop an unwritten section's blocks (`status::written_only`, in `plan.rs`'s `plan_delta`, after the BLOCKED keys are merged in, since T448's stub kept riding because a BLOCKED bundle verdict named it), so the bundle, its `blocks-<tasks>` name and the round the review-round guard counts from that name all leave it out; the feature-wide judgment (`judge_held` with no scope) drops it too, so `plan owed` and `plan-delta` agree, while a scoped judgment keeps its tasks' stubs owed - the tick of the stub's own task still owes it (and the approach gate refuses its `<...>` answers anyway). (2) The guard's round counter (`review_round_hooks::plan_rounds`) stops at a review row that names the task's stub first heading, `### <task> (<why: ...>)`, as it stops at a CLEAR: a stub-era round is no round of the section, so a section filled after riding in bundles counts from zero. The title is one copy, `l7r_shared::plan_text::STUB_TITLE`, pinned to the template by `template.rs`'s test. (3) The arbiter's accept or process-fault on a plan round records no verdict for a named task whose section is unwritten (`record::split_unwritten`; `Accepted.unwritten`), and `make arbiter-ruled` says `no verdict recorded - <task>'s section is still the make task-add template ... owes its first plan review once written`. Measured 2026-11-27 on `specs/451-time-retro-and-efficiency/plan-review.json` (a script over `block_reviews`, the guard's own count rule): T446, T447, T448, T450 and T452-T455 count 0 trailing rounds, T451 counts 1 - a stub-era round that, on the old counter, would have made its first real BLOCKED round its second and tripped the cap a round early.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| plan-delta and the whole-plan judgment drop an unwritten section | `tests/stub.rs` `a_blank_stub_rides_in_no_bundle_until_its_text_differs`, `a_stub_beside_a_written_block_of_its_own_is_written_...` | new | none (no engine code) | `make arbiter-ask` |
| the round counter stops at a stub-era row | guard test `a_blank_stub_s_rounds_count_nothing_and_its_written_section_counts_from_zero` | new | none | `make arbiter-ask` |
| no verdict recorded for an unwritten section | `tests/stub.rs` `a_process_fault_on_a_stub_s_round_records_no_verdict_...`, arbiter `a_process_fault_on_an_unwritten_section_s_round_records_no_verdict` | new | none | `make arbiter-ask` |

### T462 Approach (checklist part A)

1. **The goal, in the world.** A blank stub holds no other task's plan review: it rides in no `make plan-delta` bundle, counts no round, and gets no verdict, and when it is written its first review is owed and counted from one.
2. **The constraints.** The round arbiter's `tooling_fix` on T448 (arbiter.jsonl, 2026-11-27T08:00:04Z) and T462's line; FR-043 (a changed block is owed its review); feature 385 T16 and 451 T92 (an accept or process-fault stands as the named task's verdict); 451 T359's one stub test; no guard message changes.
3. **Where each comes from.** R: the ruling's `why`, `what` and `tooling_fix`; O: the trailing-round count above; O: T448's four rows in `block_reviews` (indexes 450-453, three BLOCKED on other tasks' points, and the arbiter's CLEAR row 459), measured 2026-11-27 (a script over the record's `block_reviews`).
4. **Do they describe the world here?** Yes: T448's rows name `### T448 (<why: ...>)` and `### T448 Approach (checklist part A)` beside the tasks whose points blocked them, read 2026-11-27 from the record.
5. **The order.** Before the next `make plan-delta F=451` dispatch (the ruling's own order); no other task waits on it.
6. **The exits.** Green: the five tests above red on the old code (plan crate: 3 failed, 204 passed; guard: 1 failed, 573 passed, the stop disabled) and green now, with `make builder-checks` clean on the four crates and the review-round guard's suite (91 passed), measured 2026-11-27 (`make rust-test` and `tests/hooks/test-review-round-hooks.sh`, their summary lines). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one stub test (`stub_block`), reused; the guard reads one shared constant.
8. **The budget.** One landing.
9. **Done, measured.** The tests above; on the real plan, `make plan-delta F=451` no longer lists a stub's blocks.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** The tripwire refused correct work: every plan-delta dispatch of feature 451 was held behind T448's four empty rounds.

T462-D1 - **A process-fault on a WRITTEN section still records its verdict** (the brief's second exit: why "no verdict" cannot be the rule for every process-fault). The plan round counter stops at a CLEAR row, and the arbiter's CLEAR row is the only thing that restarts a written section's count; without it, a process-faulted written section re-trips at the same round on its next dispatch, since only a `continue` lifts the cap. An unwritten section needs no reset, because its stub-era rows count nothing under (2), so it gets no verdict. Either way a filled section owes its own first review: block verdicts are keyed by digest and the task verdict by its section's digest, so filled text is owed even where an older record holds the stub CLEAR, as T448's does today (pinned by the second half of `a_process_fault_on_a_stub_s_round_records_no_verdict_and_the_filled_section_owes_its_review`). Accepted limitation (the builder's choice, 2026-11-27): a section whose first heading keeps the template's `(<why: ...>)` while its body is written counts no rounds until the heading changes - a lenience in the reviewer's favor, since the decide lint already refuses a `<...>` placeholder. The other choice priced, a row's text digest, was not taken: rows carry keys only.

**Found and left?** none - T448's stub CLEAR verdicts, already in plan-review.json, are left: they change no outcome (its filled text is owed by digest, and an unfilled tick is refused by the approach gate's placeholder check), so no defect.

**Performance work?** yes (a `[perf]` task, 451 FR-013: a held plan-delta dispatch is every builder's waiting - this unblocks the builders' loop).

<!-- plan-archive: T458 to T443 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T458 to T458 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T459 to T443 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T459 to T459 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T465 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T465 Approach (checklist part A)

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

### T463 (found by 451 T455, dev/measurements/2026-11-27/land-test-time/results.md sections 1 and 4: six green land test runs of 61 to 102 s, 58 to 93 s over same-time controls, not reproduced in 70 runs, measured 2026-11-27 - the next one is to be caught alive)

- **Approach**: a test program run past a bound has its live state recorded once, beside its `test` Phase line, for any crate. `rust/gate/crates/rustc/src/rustc/alive.rs` (new): `Bound::of(world, manifest)` reads the bound - `AFTER`, 30 s, a GUESS knob (why beside it: the land crate's green runs took 1.9 to 12.3 s and its slow ones 61 to 102 s, measured 2026-11-27 (T455's record, sections 1 and 4)), moved by `L7R_RUST_ALIVE_MS` through the tree's own reader - and places the record in the event-log directory's `alive/` (as the sampler's `samples/`), named `<epoch>-<crate>-<pid>.txt`. `Bound::watch(pid, program)` starts a thread on `recv_timeout(bound)` beside the run's blocking `child.wait()`; the run ends the watch by dropping the sender, so a run inside its bound joins a thread that has already returned: nothing is signalled, polled or waited on for the record. Past the bound the thread writes, once, `record(/proc, pid)`: a head line (program, bound, load), then the program and every process under it (root first, by depth) with pid, parent, age, state, wait channel, cwd, command line (300 characters), `SigIgn`/`SigCgt` (T455's one lead is a TERM that may not land), and each thread's name, state and wait channel. libtest names each test's thread after its test, and the kernel cuts that name to 15 characters (`land::stop::tes` at best). The stat line is read after its name's last `)`, and the record is cut at `CAP`, 64 KiB, a GUESS knob, at a character's edge with a line saying so. The paths watched: a built binary run directly (`side.rs`'s `run_built`, the first record of a crate's binaries) and a crate's `cargo test` (`tested`, from `stepped` and `check`), which records cargo's whole tree with the test binary under it; doctests and builds are not watched. The Phase line takes `"alive": "<path>"` only where a record was written (`phase::wrote_alive`; `wrote` passes none). The program runs moved with this change from `rustc.rs` to `rustc/run.rs` (`Ran`, `run_in`, the new `run_seen`, the cargo calls, the new `cargo_seen` and `tested`, `leak_checked`), because the change took `rustc.rs` to 1,033 lines, past the 1,000-line bar, measured 2026-11-27 (`make quick`'s file-scale check); it is now 838 lines, with 210 in `run.rs`. Red first, measured 2026-11-27 (`make rust-test CRATE=rust/gate/crates/rustc ONLY=rustc::tests::alive` on the old code, the World unchanged): 2 failed, 1 passed of 3 - the built binary and the `cargo test` past a 100 ms bound named no record; the third, a run inside its bound recording nothing, held already. Green, measured 2026-11-27 (`make builder-checks CRATE=rust/gate/crates/rustc`): 152 passed, lint and format clean. The tests (`rustc/tests/alive.rs`): a stand-in binary, and a fake cargo, each start `sleep 46.3` and stay until a record appears (at most about 10 s, a test's own GUESS cap, never a fixed sleep). The record must hold that child's args, the run's cwd, `SigIgn=` and a thread line, and must be named on the crate's `test` line, one file. A run inside the 30 s bound (`AFTER`, the GUESS knob) writes no field and no directory. A fake `/proc` covers a name holding `) `, a process gone mid-read, a stat line with no name, an unrelated process left out, a root already gone, and the cap's cut inside a two-byte character.
  - **The lead read** (`rust/gate/crates/land/src/land/stop/tests.rs`, `a_running_landing_is_sent_term`): no spawn-and-signal race can make the TERM miss. `Command::spawn` returns only once `sleep` has been exec'd, and std resets the child's signal mask, observed 2026-11-27, method: the code read at HEAD and std's spawn path. The one way it misses is a TERM the test process was started ignoring: `SIG_IGN` passes through fork and exec, and the guard's handler keeps an inherited ignore (`tempdir/signals.rs`'s `listen`). No land test sets TERM to ignored in process: only `stop::stopped(15)` does, and no test calls it with 15, observed 2026-11-27, method: grep of the land crate and the shared tempdir code. Under `bash -c "trap '' TERM; exec <the land test binary> --exact ..."` the test is green at 30.02 s against 0.03 s plain, but `term_stops_every_held_group_and_exits_143` goes red at 10.14 s against 0.10 s, measured 2026-11-27 (one run each, `diagram-backlog-b1`'s built binary `l7r_gate_land-35df8d33ecfe35d2`). So an ignored TERM makes the binary red, not one of the six green slow runs. The test can wait 30 s, measured 2026-11-27 (the timing above), but that is not shown as their cause. The record's `SigIgn` line settles it on the next catch.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a test run past its bound recorded alive and named on its Phase line (`rustc/alive.rs`, `rustc/run.rs`, `side.rs`, `phase.rs`), red first 2 of 3, measured 2026-11-27 | n/a: tooling, no map drawn | n/a: tooling | none | n/a |

### T463 Approach (checklist part A)

1. **The goal, in the world.** The next slow green land test run, or a slow run of any crate's tests, leaves a record of which processes and test threads were alive, and on what they waited. The run is no slower for it.
2. **The constraints.** T463's line; the brief's scope (never kill or slow the run, any crate, bounded in size, the land crate unchanged); 451 FR-013 (performance work); constitution X clause 13 (the 1,000-line bar, met by the `run.rs` split); the two tiers (first-tier checks only).
3. **Where each comes from.** G: the GM's words of 2026-11-20 counting work that measures where time goes as performance work. O: T455's record, sections 1 to 4, measured 2026-11-27; this task's red-first run and the lead's two timings, measured 2026-11-27.
4. **Do they describe the world here?** Yes, measured 2026-11-27: the tests run the real `answer` path, both ways a test program runs (a built binary and a `cargo test`), and read the real `/proc` of a stand-in with a live child; the lead was timed on the land crate's own built test binary.
5. **The order.** After T455, which filed it; before T469, the land test's bounded wait, so the next slow run is caught before the lead's fix changes what it would show; before T470, the per-test times.
6. **The exits.** Green: the crate's tests, lint and format clean with the red-first tests passing; the next slow run's Phase line names its record. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** Seventy runs did not reproduce the slow ones, measured 2026-11-27 (T455's record, section 4), so this builds an instrument rather than running the tests more.
8. **The budget.** One landing.
9. **Done, measured.** The red-first tests fail 2 of 3 on the old code and pass on the new, and the crate passes 152 tests with lint and format clean, measured 2026-11-27 (`make rust-test ONLY=` then `make builder-checks`).
10. **Before moving a constant.** n/a: `AFTER` (30 s) and `CAP` (64 KiB) are new GUESS knobs, each with its why beside it.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing: tooling, no map changes; no defect is fixed here (the lead's test is filed, not changed).

**Found and left?**
- `land::stop::tests::a_running_landing_is_sent_term` waits unbounded on the `sleep 30` it TERMs. Started with TERM ignored, it is green at 30.02 s against 0.03 s, measured 2026-11-27 (the lead read above), so a TERM that misses costs a silent 30 s rather than a red test. Not fixed here: the brief keeps the land crate unchanged, and the record should name the next slow run's cause first. Filed as T469; lands before T435.
- T463's line also asks for libtest's per-test times (`--report-time --format json` under `RUSTC_BOOTSTRAP=1`), and whether those words move cargo's fingerprint of the test build (a rebuild every run) is unmeasured. Not fixed here: not ordered by the brief, and it needs that measurement first. Filed as T470; lands before T435.

**Performance work?** yes: a `[perf]` task (451 FR-013): it measures where the gate's test time goes, which counts as performance work under the GM's words of 2026-11-20. It is not engine speed, so the performance checklist does not apply.


<!-- plan-archive: T466 to T464 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
<!-- plan-archive: T466 to T466 moved to plan-done.md, 2026-11-27 (feature 375 FR-044) -->
### T467 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T467 Approach (checklist part A)

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


### T468 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T468 Approach (checklist part A)

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


### T472 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T472 Approach (checklist part A)

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


### T477 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T477 Approach (checklist part A)

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


### T469 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T469 Approach (checklist part A)

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


### T470 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T470 Approach (checklist part A)

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



### T473 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T473 Approach (checklist part A)

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

