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
exit 3 with its ticks standing, is a landing whatever its code) and plan re-rounds (a task's `spec-fidelity` and
`spec-fidelity-verify` dispatches after its first). `feature-report` reads the same columns through the same functions (one place:
`where_time.rs`'s new `columns` module), keeping its existing `UNTIL=`.

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

<!-- plan-archive: T12 to T12 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T13 to T13 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
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
### T33 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T33 Approach (checklist part A)

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

**Performance work?** <no - or yes (a `[perf]` task, 451 FR-013: it makes the engine, the checks, the gate, the landings or the builders' loop faster), and for an engine-speed task its answers to docs/performance-checklist.md below (`make task-add ... PERF=1` writes them)>


<!-- plan-archive: T34 to T14 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T34 to T34 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T36 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T36 Approach (checklist part A)

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


<!-- plan-archive: T37 to T18 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T37 to T37 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T38 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T38 Approach (checklist part A)

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

### T38 Performance checklist (docs/performance-checklist.md - prompts, never a gate; time is the goal, calls the measure)

1. **Where does the time go?** <the stage and the loop: its counted operations, `make work-budget` (a hamlet stage) or `make budget-sheets` (a Mode A stage)>
2. **Removes work, or only moves it?** <fewer candidates, a screen, a kept result, an index, an early stop, a better algorithm,
   a loop into C - or an inlining, a merge, a builtin written out: never the goal, only where the time evidence shows a gain>
3. **What do you expect it to save, and why?** <a share of the stage's profiled time>
4. **How does the work grow with the settlement?** <the growth exponent between sizes, and whether this bends it>
5. **What did the before and after show, and under what conditions?** <the counted operations before and after, and any wall
   time with the host's load - evidence, not a pass>
6. **Did any map move, and does it still keep the research?** <`make maps-moved`, the cohort>


<!-- plan-archive: T39 to T32 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T39 to T39 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T40 to T21 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T40 to T40 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
### T41 (T34's reading of `scripts/gates/l7r-gate.sh`: the launcher rebuilds `l7r-gate` when `rust/guard` changes and the gate links the guard, so one builder's uncompiling guard edit fails every other builder's gate command in a shared clone - read, not measured, until this task)

- **Approach**: measured first, then one change to the launcher's build-failure path; no gate crate changed.
  - **The measurement.** A scratch clone of the clone at d6d242ec5b in `/tmp`, its own target (a copy of the clone's `tool/` profile), every launcher arm built, then `fn t41_broken( {` appended to `rust/guard/src/shared.rs`.
    `l7r-gate.sh --version`, `make decide F=451 T=T41`, `make format FILE=...`, `make speckit-todo`, `l7r-gate.sh rust lint` and `l7r-gate.sh mode-a` each failed, exit 1 (make's 2), in 0.1-0.2 s, measured 2026-11-20 (each run timed by `date +%s.%N` in the scratch clone).
    A type error in the same file failed the same way in 0.48 s, measured 2026-11-20 (the same method).
    `browser`, `embed` and `hamlet` ran: none of them depends on `l7r_guard`, measured 2026-11-20 (`cargo tree -p <pkg> -e normal`, which finds the guard under `l7r_gate`, `l7r_gate_rustc` and `l7r_mode_a` alone).
    `L7R_GATE_STALE_OK=1` ran the old binary, as T129 means it to (the Makefile's parse-time goals line).
    Every failure printed cargo's report, `--> guard/src/shared.rs:36:18` (relative to `rust/`), and then `l7r-gate: the build failed - fix what cargo names above`: an order to edit the neighbor's file.
    A broken `rust/gate/crates/owed/src/lib.rs` (T43's crate) fails `l7r-gate` the same way in 2.7 s, and `rust lint`, whose `l7r-rust` does not link `owed`, ran clippy for 130 s to a red, measured 2026-11-20 (the same method).
    A guard edit that compiles cost the next `l7r-gate` call 2.6 s of rebuild, measured 2026-11-20 (the same method), so the compiling side is not this task's cost.
  - **The fix: the refusal names the file and what to do, and nothing falls back.** On a failed build the launcher keeps cargo's report and adds two lines: each file cargo points at, once, from the tree's root (`rust/guard/src/shared.rs`; an absolute path kept), and `yours? fix what cargo names above. Not yours? another builder in this tree is mid-edit: leave it alone and re-run once it compiles`, with the `git status` that shows the uncommitted edits. A failure naming no file keeps the old line. It holds for any uncompiling source, the guard's or a gate crate's.
  - **Why not the last good binary (the rule).** A command may run on a binary older than the tree only if it renders no verdict and writes no record a later gate or push trusts, because the old binary is behind every source newer than it - the caller's own compiling gate-crate edits too - and the gate links the guard's shared code into nearly every command (`shared::speckit`, `regex`, `log`, `checks`, `guards::house_style_hooks`, 28 modules, measured 2026-11-20 (`grep -o 'l7r_guard::...'` over `rust/gate` and `rust/mode_a`)).
    `make decide` lints a plan section and records a deferral escape that `make plan-delta` reads, so it fails the rule; so do `task-start` (its hold), every `check`, `rust lint|test|cover|dead`, `rust format --check`, `speckit-todo --check|--holding|--closed-by-status` (the push's route), `mode-a` and `hamlet` (the generation cache's engine identity).
    What passes it - `rust format` writing, a bare `speckit-todo` listing, `coord lines` - was 787 of the week's 12,700 make targets, 6%, measured 2026-11-20 (`.git/tool-usage.jsonl`, `kind: target`, 2026-11-13 to 20).
    A fallback for that 6% leaves `make decide` (449 runs) and `rust-test` (2,414 runs) failing, measured 2026-11-20 (the same log and window), and adds a path where an old binary runs, so it is not built.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the refusal names the uncompiling files and what to do | `tests/hooks/test-l7r-gate.1.sh`, "a neighbor's uncompiling file": red on the unfixed launcher (2 FAIL lines: the named files, the advice), green after, measured 2026-11-20 (the shard run in the scratch clone) | n/a: no engine code | none: no engine code | n/a |

### T41 Approach (checklist part A)

1. **The goal, in the world.** A builder whose gate command fails because another builder's file does not compile is told which file and that it is not theirs to fix, and no gate verdict comes from a binary older than the code it judges.
2. **The constraints.** FR-013 (a `[perf]` task makes the builders' loop faster); the launcher fails closed (feature 449 T061); `L7R_GATE_PRINT_FRESH` names no stale binary (T205); the ground rule from the dispatch: a gate check over a changed guard uses the new code.
3. **Where each comes from.** R: tasks.md T41 and the launcher's header; O: the scratch-clone runs above.
4. **Do they describe the world here?** Yes: the failure reproduced on the real launcher with real cargo, measured 2026-11-20 (the scratch clone, a broken `shared.rs`, then a broken `owed/src/lib.rs`).
5. **The order.** After T40 (independent of T43, which edits `rust/gate/crates/owed` and not the launcher).
6. **The exits.** Green: the shard's new cases pass and the real `make decide` against a broken guard prints the two lines. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one failure path, read whole.
8. **The budget.** One landing.
9. **Done, measured.** `make decide F=451 T=T41` against the scratch clone's broken guard: exit 2 in 0.23 s with `rust/guard/src/shared.rs does not compile, so l7r-gate is not built ...` and the advice line, measured 2026-11-20 (the scratch clone, fixed launcher); the shard green, measured 2026-11-20 (`tests/hooks/test-l7r-gate.1.sh` in the scratch clone).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** A builder reading the refusal sees the neighbor's file named and is told to leave it alone, where before it was told to fix it; no map, finding or check changes.

**Found and left?** none.

**Performance work?** yes (a `[perf]` task, 451 FR-013: the builders' loop - a builder no longer edits, reverts or debugs a neighbor's file on the launcher's word); not an engine-speed task, so no performance checklist.

### T42 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T42 Approach (checklist part A)

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


### T43 (T40's finding: every owed computation read the record's pages at the merge base whole, 1,951 blobs by one `git cat-file --batch` for a one-page delta, 0.63-1.13 s of each 1.4-1.6 s computation, measured 2026-11-20 (T40's `git` shim))

- **Approach**: one change in the `owed` crate's `Delta::fetch` (`rust/gate/crates/owed/src/record/delta.rs`), which every base read of the record, translation and pop-up families goes through; no caller changed but a doc comment (`owed.rs`'s `prefetch`).
  - **The rule.** A name `rev` lists that the working tree holds unchanged is read from the tree as the same bytes; every other name still goes to `cat-file`. Unchanged means: no line of the computation's cached `git diff --name-status --no-renames rev -- WATCHED` names it (the diff `changed_sources` already asks, so the common path pays no new diff), `git ls-files -v -- LISTED` does not flag it (assume-unchanged or skip-worktree, whose diff is silent whatever the file holds; one new `git` call, 6 ms on the real clone, measured 2026-11-20 (the shim below)), it is a plain file (not a link, not absent as a sparse checkout leaves it) and holds no carriage return (an end-of-line conversion could make its blob differ). It is decoded as `cat_blobs` decodes a blob (`from_utf8_lossy`, no newline conversion), so `Delta::texts(rev, names)` gives what `cat_blobs(rev:names)` gives, string for string, and every owed unit downstream is the same.
  - **Holds for any revision**, so `--between`'s two reads shrink too wherever the tree matches either side.
  - **Rejected: keying the base read by the merge base and reusing it.** It would keep state between computations, which `delta.rs` rules out (each computation's reads are its own), and still pay one full read per merge base; the tree's copies cost a file read each.
  - **Red first, on a cost counter.** `Delta::blobs_asked` counts the objects handed to `cat-file`. `a_one_page_delta_asks_git_for_that_page_alone` (one page reworded on the owed fixture, every family) asked 11 before the fix and asserts 1: `left: 11, right: 1`, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed` with the counter and the test, before the change to `fetch`); green after. `a_file_read_from_the_tree_is_the_blob_git_would_give` holds `texts` equal to `cat_blobs` over every listed file in each state - edited, deleted, staged then reverted, skip-worktree and absent, a link, a carriage return, untracked, assume-unchanged and edited - and red with the `ls-files -v` guard taken out (the assumed file read as `edited`), measured 2026-11-20 (the same target).
  - **Failing closed** (the session's ruling on this section's found-and-left, 2026-11-20). A `git diff` that fails printed nothing, which read as "nothing changed": every listed page would read from the tree, edits and all, and the record family owe nothing where before it compared whole pages. Now the cached diff, and `ls-files -v`, carry git's error where it failed (`ran`), and where either failed nothing is called unchanged and every name goes to `cat-file`, as before T43; no new `git` call on the success path. `a_diff_git_cannot_run_reads_every_base_file_from_git` corrupts the fixture's index (which fails the diff and `ls-files -v` alike while `cat-file` still reads the base) over an edited page and holds `texts` equal to `cat_blobs` and every name asked: red before the change (`texts` gave the tree's `A long way apart.` where the blob holds `A short way apart.`, log `/tmp/t43/red-diff-fails.log`), green after (84 passed), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). On the real record, the reword's state with the scratch clone's index corrupted, the HEAD build and this one owe the same 5 units (`record-owed --unanswered --slugs`, sorted, identical) of the 11 the state owes with its index whole, measured 2026-11-20 (`/tmp/t43/scripts/corrupt.sh`): the six missing, the next bullet's. A failed `ls-files -v` alone (the diff good) rides the same rule and is not tested by itself: no state was found that fails one and not the other.
  - **A failed diff refused, not read as "nothing changed"** (the session's second ruling, 2026-11-20). `Delta::changed`, the narrow diff before it alike, read a failed `git diff` as an empty delta, so the pop-up family (`modals.rs`'s `changed_pages`), the write-ups' (`owed.rs`'s `changed_sources`) and entry-drift's start (`entry_drift_owed`) owed nothing for a moved page: on the reword's state with the index corrupted, the six modal-research units of `sheet/parley-mats` and `sheet/parley-room` (accuracy, references, gaps) went unowed. Now `changed` returns git's error and every owed computation reading it refuses with it: `cannot tell what changed: git diff failed: <git's stderr>; repair the index, e.g. git -C <tree> reset -q` - never owing everything, which a corrupt index would turn into a flood. A tree with NO repository at all is nothing to judge, as before T43: where the diff fails and `git rev-parse --git-dir` fails too (asked only after a failed diff, so the common path pays nothing), `changed` is empty, and `others` (`ls-files --others`) still reads a failure as no untracked files - the command-line tests pin it (`modals::tests::the_command_line`, `triage::tests::the_command_line_s_refusals`, red when `others` refused, measured 2026-11-20) and `land`'s `replay_owing::tests::the_counts_are_the_python_s` runs the triage in a bare directory (red at the T41 and T43 landing's `make static` when `changed` refused there, the session's report 2026-11-20); a repository whose diff fails (a corrupt index) is refused by `changed`, which every family asks first wherever there is a base. `a_tree_with_no_repository_has_nothing_changed` holds the first: red before the split (`left: Err("cannot tell what changed: git diff failed: warning: Limiting comparison with pathspecs is only supported if both paths are directories. ...")`, `right: Ok("")`, log `/tmp/t43/red-norepo.log`), green after, measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). `a_diff_git_cannot_run_is_refused_not_read_as_nothing_changed` owes modal units on the edited fixture with its index whole, then corrupts it and holds the refusal: red before the change (`called Result::unwrap_err() on an Ok value: ["quote-check:0094#k", "record-format:0094"]`, the modal units gone, log `/tmp/t43/red-refused.log`), green after (85 passed), measured 2026-11-20 (`make rust-test CRATE=rust/gate/crates/owed`). On the real record, the reword's state with the scratch clone's index corrupted: `record-owed` and `modal-owed` refuse, exit 1, `cannot tell what changed: git diff failed: fatal: .git/index: index file smaller than expected; repair the index, e.g. git -C /tmp/t43/w reset -q`; with the index whole this build owes the HEAD build's 11 units, identical, measured 2026-11-20 (`/tmp/t43/refused.real`, `/tmp/t43/whole.after`).
  - **The counter on the real record.** A `git` shim first on PATH teeing `cat-file`'s input, one computation (`record record-owed`, every family) on a full scratch clone of HEAD d6d242ec5b with one sentence of `0094-rooms-for-a-parley-across-a-border.html` reworded: before 2,249 objects (1,951 by `Delta`'s base read - 1,654 question pages and the 297 pop-up files - then the same 297 pop-up files by entry-drift's own reader, 1 page by entry-drift's moved anchors), after 299 (1, 297, 1), 16 and 17 `git` calls, measured 2026-11-20 (the shim).
  - **The computation alone.** The same clone and delta, the HEAD build and this build run directly (not through the launcher T41 edits), before, after, after, before, five times, `RECORD_CHECKS_DIR` an empty store: before 3.89 (the first, cold), 2.78, 2.14, 2.21, 2.25, 2.20, 2.45, 1.90, 2.20 and 1.80 s of wall (median 2.21 s), 2.94-6.13 user CPU-seconds, after 1.82, 1.58, 1.18, 1.20, 1.45, 1.23, 1.31, 1.25, 1.31 and 1.38 s (median 1.31 s), 2.54-3.67 user CPU-seconds, load 4.1-4.8, measured 2026-11-20 (`/usr/bin/time` around each, `/tmp/t43/scripts/time.sh`). So about 0.9 s off each computation, the size of T40's `cat-file` share, measured 2026-11-20 (the medians above).
  - **The owed output, the same.** Eight real commits that touched the record, its notes, the write-ups or the pop-ups (76221da67f, 13407d397c, 085847d541, 3cb07dd2ba, 94f514f15f, a650df3cb7, 7ec3bb6396, ed88a709e2), each put in the scratch clone as its parent checked out with origin/main at the parent and the commit's tree restored over the working tree (its delta uncommitted, its new files untracked), and the reword above: `record-owed`, `modal-owed`, `modal-owed --ids` (every pop-up's fingerprints), `translation-owed` and `modal-triage bundle`, and `record-owed --between <parent> <commit>`, each by both builds on an empty store - 53 listing pairs (nine states by five verbs, and eight `--between`) and three triage bundles: every listing and exit identical but the three triage outputs, which differ only in the `--out` path each side printed, and the bundles identical file for file (`diff -r`, checked on 13407d397c), measured 2026-11-20 (`/tmp/t43/scripts/diff.sh`). The record units' fingerprints, which the listing does not print: on five of those states each build answered the units it listed into an empty store (the entry-gate suite's `answer_all`; 11, 18, 4, 114 and 26 listed, 0, 1, 2, 21 and 0 left unanswered even by the answering build, the script not answering every kind), and the other build then left as many unanswered, measured 2026-11-20 (`/tmp/t43/scripts/fp.sh`); and line by line on four of them (the reword, 76221da67f, 085847d541, 13407d397c), each build answering and both listing what was left, sorted: the lists identical, all eight (0, 1, 2 and 21 lines), with this section's fail-closed build, measured 2026-11-20 (`/tmp/t43/scripts/fp.sh`, log `/tmp/t43/fp-lists.log`). The leftovers' fingerprints are held by `a_file_read_from_the_tree_is_the_blob_git_would_give` (the base text each fingerprint is taken of, equal to `cat-file`'s) and, for the pop-ups, by `modal-owed --ids` above.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| unchanged base files read from the working tree | n/a - no map | n/a | none | n/a |
| a failed `git diff` or `ls-files -v` reads every base file from git | n/a - no map | n/a | none | n/a |
| a failed `git diff` refused with git's error, not owed as nothing changed | n/a - no map | n/a | none | n/a |

### T43 Approach (checklist part A)

1. **The goal, in the world.** Each owed computation asks git at the base only for what the delta names, so every gate run, push, landing and the entry-gate suite's chain is faster; no map changes and the owed units come out the same.
2. **The constraints.** FR-010, FR-013; the task line's hold (the owed units the same, red first on a cost counter); `delta.rs`'s rule that nothing is kept between computations; only the `owed` crate and this section edited (T41 works on `scripts/gates/l7r-gate.sh`).
3. **Where each comes from.** O: T40's shim figures (1,951 blobs, 0.63-1.13 s, measured 2026-11-20 (T40's `git` shim)), and this task's counter, shim and timings; the task line for the hold.
4. **Do they describe the world here?** Measured on a full scratch clone of HEAD with the real record (1,654 question pages and 297 pop-up files at the base), by a `git` shim and `/usr/bin/time`, and on eight real commits from history, measured 2026-11-20 (the approach's methods).
5. **The order.** After T40 (its finding); before T22 (as filed); beside T41 (different files).
6. **The exits.** Green: the one-page delta's base read at 1 object, the computation faster on the same delta, the owed output identical on real commits. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The counter's test red then green; the shim's object count on the real record before and after; the computation alone, the two builds alternated on the same delta, the load noted; the differential and the fingerprint cross-check above.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a reader of a map sees; no check's verdict changes (every listing identical on the real commits). Not a defect: a speed change; the fail-closed rule restores what a failed diff owed before T43, and a failed diff now refuses where it owed nothing, each red first on its own test.

**Found and left?**
- A failed `git diff` (a corrupt index fails it) printed nothing, so every listed page read from the tree, edits and all, and the record family would owe nothing where before T43 it compared whole pages: fixed here (failing closed, the approach's bullet above, the session's ruling 2026-11-20); no state short of a corrupt index was found that fails it.
- With a failed `git diff`, `Delta::changed` (the narrow diff before it alike) read the delta as empty, so the pop-up family owed nothing for a moved page: on the reword's state with the index corrupted, the six modal-research units of `sheet/parley-mats` and `sheet/parley-room` (accuracy, references, gaps) went unowed by the HEAD build, measured 2026-11-20 (`/tmp/t43/scripts/corrupt.sh` against the same state whole): fixed here (the approach's refusal bullet, the session's second ruling 2026-11-20).
- Entry-drift's report reads every pop-up file at the base by its own reader (`entry.rs`'s `read_at`, a `RevReader` with its own `cat-file`), 297 objects in 0.025 s of each computation, measured 2026-11-20 (the shim). Not a defect: no wrong outcome, a cost, and not filed: about 2% of the computation, measured 2026-11-20 (the shim against the timings above).

**Performance work?** yes - a `[perf]` task (451 FR-013: every gate run's owed computation). Its answers:

1. **Where does the time go?** Into one `cat-file --batch` of 1,951 base blobs, 0.63-1.13 s of each 1.4-1.6 s computation, the rest the binary's own work, measured 2026-11-20 (T40's `git` shim).
2. **Removes work, or only moves it?** Removes it: 1,950 fewer blobs inflated a computation on a one-page delta; the tree's copies cost a file read each, from the page cache.
3. **What do you expect it to save, and why?** Most of the `cat-file` share, 0.6-1.1 s a computation (a GUESS from T40's shim figures before measuring).
4. **How does the work grow with the settlement?** n/a - no settlement; with the record, the base read now grows with the delta, not with the record's pages.
5. **What did the before and after show, and under what conditions?** On a one-sentence delta, median 2.21 s before and 1.31 s after of wall, user CPU 2.94-6.13 against 2.54-3.67 s, ten alternated pairs at load 4.1-4.8, measured 2026-11-20 (`/usr/bin/time`); the base objects asked 2,249 before and 299 after, measured 2026-11-20 (the shim).
6. **Did any map move, and does it still keep the research?** No map.
