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
### T31 (found by T15's corpus replay, 2026-11-20: main-tree refused `python3 -c "data = open('$SP/x.html','rb').read() ..."` - a read - as a write where the shell stands, with no escape, the same before and after T15's shared-reader fix; observed 2026-11-20, method: T15's replay of the main-tree refusals corpus)

- **Approach**: the cause is feature 204's D5, `rust/guard/src/shared/tree.rs` `writes_in` reading every `python3 -c` as a write where the
  shell stands. D5 (feature 204 spec): *"`python3 -c` remains a write. It was a false positive on read-only diagnostics, but its cost is
  now zero: from the clone it is allowed; from main it is moved. Narrowing the write list would reopen the false-allow direction for no
  saving."* Its "zero cost" fails where the clone cannot be resolved: the move becomes the refusal `clone-unresolved`. And a read moved
  to the clone is still a model-visible rewrite. Refusing a read is a wrong outcome (constitution XIV; the session's ruling,
  2026-11-20), so D5 is NARROWED here: a `-c` program that a denylist of known writers judges read-only is not a write, unless the
  same command also runs a Python program from stdin.
  - `shared/tree/py_c.rs` (new): `reads(body, quote, dir)` judges a program a read only when no known writer appears in it (a
    DENYLIST of calls and modules: `write`, `remove`, `shutil`, `subprocess`, `.dump(`, `save*(`, `getattr(`, `urlretrieve`, ...;
    `replace(` only with `os`/`Path` in the program); every `open(` is in a read mode (no `*`/`**` argument, no non-literal mode);
    no command substitution, and no shell expansion outside a Python literal (a `#` comment's quotes opening none), in a
    double-quoted body; no relative import; and no import that the directory it runs in could answer (the tree's own code, which
    can write anything), with any import a write where the directory is unknown. Anything else stays D5's write.
  - `tree.rs`: `sanitize` carries each `-c` program out beside the text, `__py_c_<n>__` standing in its place, so the program's own
    `;`, `(` and `|` do not split the walk. `writes_in` finds the `-c` past the interpreter's flags (`python3 -I -c`, `-Ic`,
    `-W x -c`) and a minor version (`python3.12`), and keeps a read program in the walk as a target MARKED `how = "read"`. `judge`'s
    write tests and its re-judge (`lands_in_main`) skip that mark, so house style still sees where the command lands, as before.
    `walk` marks no `-c` a read where any segment of the command runs Python from stdin (`python3 -`, `python3 <<BODY`,
    `python3 < p.py`, `| python3`; `python_stdin`): the walk judges no stdin program, and D5's write of the `-c` beside it was what
    refused the heredoc writers parse#72 and window#61. The heredoc itself gets no target, and a `-c` program's own stdin is data.
  - `gm_tree_hooks.rs` `offending` skips the mark too, so a read standing in gm-assistant's tree is no longer refused.
  - red first, the tests before the code, each in `/tmp/t31/`, all `make rust-test CRATE=rust/guard`, 2026-11-20:
    - the read refused: 673 passed, 1 failed (`red-first.log`);
    - the classifier's gaps: 15 of 18 new write cases judged reads (`red3.log`);
    - gm-tree refusing a read: 676 passed, 1 failed (`gmred.log`);
    - the stdin rule and the comment: 674 passed, 3 failed (`red4.log`) - window#61's shape allowed by main-tree with no clone,
      the walk's stdin cases marked `read`, `# don't\n$CODE` judged a read; parse#72 and window#61 themselves allowed by the
      stage-1 binary's replay (`after1.nobody.main-tree-hooks.tsv`) and refused by the final one (`after3`);
    - green: 677 of 677 (`green4.log`); 678 of 678 once the walk's Python cases became their own test, for its length
      (`final-test.log`).
  - replays (the four corpora, 1,134 rows, measured 2026-11-20 (`/tmp/t31/scripts/replay.sh`); before = HEAD's binary, after =
    the final one; SID `t` resolves a clone, `nobody` resolves none):
    - house-style, gm-tree, make-only alone (`t`), gm-tree alone (`nobody`): 0 moved, 0 outputs changed each, measured 2026-11-20 (`replay.sh`, `cmp.sh`);
    - main-tree alone, measured 2026-11-20 (`replay.sh`, `cmp.sh`), `nobody`: 80 refused -> allowed; `t`: 79 rewrote -> allowed and window#308 refused -> allowed; 0 other
      outputs changed;
    - all guards, measured 2026-11-20 (`replay.sh`, `cmp.sh`), `t`: 79 rewrote -> allowed and window#308 refused -> allowed; `nobody`: 80 refused -> allowed; a second `t` run
      0 differences (no noise);
    - against the stage-1 binary (no stdin rule), measured 2026-11-20 (`cmp.sh` after1 vs after3): exactly 5 moved back - parse#72, window#61 (heredoc writers), main-tree#147,
      window#339, window#361 (heredoc reads beside a `-c` read) - the same 5 an independent scan of the 85 stage-1 moves for a
      stdin Python program predicted. Under all guards window#61 stays refused by guard-file-hooks and its output is back to
      HEAD's.
    - the final source rebuilt and all eight runs replayed again, measured 2026-11-20 (`cmp.sh` against the previous build's):
      0 verdicts and 0 outputs changed.
  - fixture: `tests/hooks/fixtures/main-tree-refusals-2026-09.json` relabeled, measured 2026-11-20 (its verdicts against the
    main-tree replay, `t`), 57 rows rewrote -> allowed (expected 167 allowed, 6
    rewrote), exactly the replay's main-tree# moves; main-tree#147 stays rewrote.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| a `python3 -c` read is no write (main-tree, gm-tree) | n/a - no map | n/a | none | n/a |

### T31 Approach (checklist part A)

1. **The goal, in the world.** No map changes. A builder's read-only `python3 -c` diagnostic standing in the mirror or in
   gm-assistant's tree runs as typed: it is neither refused nor rewritten. Every write is still moved or refused as before.
2. **The constraints.** T31's line (measure on the corpora, fix the refusal of correct work, red first); feature 204 D5, quoted above
   and narrowed here (a read judged by a denylist of known writers is no write, unless the command also runs a stdin program); D6
   (unknown resolves toward main) untouched; the guards that read a walk's targets (house style, gm-tree, the bench) see the same
   targets; 100% line coverage of the guard crate.
3. **Where each comes from.** G: the session's ruling, 2026-11-20 - refusing a read is a wrong outcome (constitution XIV), so
   narrowing D5 is right, and the stdin rule's cost (3 reads refused again) is within D5's scope as the session set it. R: feature
   204 spec D5 and D6. O: the replays above, measured 2026-11-20.
4. **Do they describe the world here?** Measured on the four corpora by replay, and each moved row hand-read as a WHOLE command,
   not its `-c` program alone: every head of every segment listed (`/tmp/t31/scripts/heads.py`) and each one that is not a known
   read judged. That read found the two heredoc writers (parse#72, window#61) the `-c` write had been covering, measured 2026-11-20 (`heads.py`
   and a hand-read). The `curl -o`
   writes the walk does not judge were measured 2026-11-20 (a hand-read of the moved rows) at 0 rows to cover: their targets
   (main-tree#112, #122; window#416 has none) are absolute scratch paths outside the mirror. The script runs were measured
   2026-11-20 (the same hand-read) at 4 rows left under the walk's standing policy that a script run is no write (`python3 x.py`
   pinned empty), not shown to write nothing: main-tree#103 runs a scratch script, window#60, #62 and #308 run the mirror's own
   test suites and hooks, and in each the `-c` write was the only thing that moved or refused it, so each now runs as typed.
5. **The order.** After T15 (its replay found this); beside T33 (the guard-file guard, a different file).
6. **The exits.** Green: the red tests green; the replays; `make rust-test CRATE=rust/guard` and the crate's lint, format and cover;
   `make quick`; `make static` (once); `make hooks-test`. Red: what failed recorded and the task set down, a claim that it cannot be
   done ruled through `make arbiter-ask`.
7. **The search smell.** Every reader of a walk's targets was found: `judge` (`named`/`shell`, and the re-judge), `explain`
   (`named` only), `Verdict::context` (logs `how`), `gm_tree_hooks::offending`, `house_style_hooks::lands_outside` (paths only) and
   `suite_tools/bench.rs` (paths only); no script or test reads the logged `how`. Read 2026-11-20 (`grep '\.targets\|\.how'` over
   `rust/guard/src`, `grep '"how"'` over `scripts/ tests/ Makefile`).
8. **The budget.** One landing.
9. **Done, measured.** The read refused with no clone is allowed (`red-first.log` -> `green4.log`); 80 corpus rows refused with no
   clone and 79 rewritten with one now run as typed, every move accounted above; 0 moves on the other guards alone; the heredoc
   writers parse#72 and window#61 refused as before.
10. **Before moving a constant.** n/a - no constant.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing on a map. The fix is not a restatement: refusing a read is the wrong outcome (constitution XIV), so
    D5's claim *"python3 -c remains a write"* is narrowed in the code, the session ruling it. A builder sees its read run where it
    was refused (`clone-unresolved`) or rewritten into the clone. The narrowing stops where the walk stops seeing: a command that
    also runs a Python program from stdin keeps its `-c` a write, because the walk judges no stdin program and D5's write was the
    only thing refusing such a heredoc's writes in the mirror (parse#72, window#61); its cost is 3 heredoc reads refused or
    rewritten again (main-tree#147, window#339, window#361), as before T31.

**Found and left?**
- The stdin rule keeps three real reads refused or rewritten: main-tree#147, window#339 and window#361 (each runs a `-c` read beside
  a stdin Python program that only reads), observed 2026-11-20, method: the replays of item 9, the rows that moved back against the
  earlier build, each hand-read. Not fixed here: telling those programs' bodies from a writer's needs the stdin reader T31 does not
  build, and lifting the rule without it lets parse#72's and window#61's writes through. Filed as T42 (which retires the rule once
  stdin bodies are judged); lands before T22.
- A Python heredoc (or other stdin program) that writes, standing in the mirror, is judged by no one: measured 2026-11-20
  (`heredoc_writers.py` over the replays), in the four corpora 331 rows
  run a stdin Python program whose body holds a known writer standing in the mirror; main-tree with no clone resolvable allows 301
  of them before and after T31 and refuses 30 (28 for another write in the command, parse#72 and window#61 by T31's
  stdin rule); of the 301, 85 have no `cd` in the command and 42 of those name a
  relative path. Not fixed here: judging a heredoc body is a new reader with its own replay and moves, past T31's `-c` scope, and
  T31's stdin rule keeps every row it refused before refused. Filed as T42; lands before T22. observed 2026-11-20, method: every
  corpus row's heredocs after a `python3` scanned for a known writer (`/tmp/t31/scripts/heredoc_writers.py`) against the before and
  after main-tree replays.

**Performance work?** yes - a `[perf]` task in FR-013's sense (the builders' loop): each refused or rewritten read cost a model
round trip; the corpora hold 80 such refusals and 79 such rewrites. Not filed with `PERF=1`: no engine stage's counted operations
or time.


<!-- plan-archive: T32 to T14 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
<!-- plan-archive: T32 to T32 moved to plan-done.md, 2026-11-20 (feature 375 FR-044) -->
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
### T40 (T21's finding: `make hooks-test`'s full-run wall is entry-gate's suite plus 2-3 s, measured 2026-11-20 (T21's full runs), its case-4 chain of record gates the last thing running)

- **Approach**: measured first, then two cuts in `tests/hooks/test-entry-gate.sh` alone; no gate command's code changed.
  - **Where the chain's time goes.** Case 4 (`case_answers`) is one clone and six computations of the tree's owed units, one after
    another: the listing `answer_all` reads, its three `--answer` calls (quote-check, record-format, modal-research), and two gates.
    Alone, the clone took 1.66-1.70 s (0.79 user, 0.87 sys) and each computation 1.40-1.64 s of wall and 2.4-3.4 CPU-seconds, the first on a
    fresh clone 2.1 s, measured 2026-11-20 (`/usr/bin/time` and `EPOCHREALTIME` around each, a scratch clone of HEAD with case 3's reword, load 0.6-14).
    Of a computation, 0.63-1.13 s is one `git cat-file --batch` of 1,951 base blobs (the record's pages at the merge base, read whole for a one-page
    delta), the rest the binary's own work, measured 2026-11-20 (a `git` shim first on PATH timing each call and teeing `cat-file`'s input).
    A gate run is one `entry-gate.sh`, three launcher and binary pairs (`push-gate skip` 0.30 s, its unscoped `git diff --name-only HEAD`
    0.24 s of it, `record-owed --unanswered`, `log guard`) and 23 git processes, measured 2026-11-20 (`bash -x` with `EPOCHREALTIME` in PS4, the shim).
    What repeats: the owed units, computed six times on states that differ by one sentence, each reading the same 1,951 base blobs again,
    and a checkout of all 28,472 tracked files when the gate reads the record's pages and the pop-ups' files.
    Under a full run's load the same steps stretch: the clone 6.7-17.5 s, `answer_all` 28.5-32.0 s, a gate 12.6-21.1 s, measured
    2026-11-20 (the suite's steps timed by a `tick` line in an instrumented copy, run alone at load 22-43, the host loaded by other builders' replays and builds).
    No profiler reaches the binary here (`perf` opens no event and `strace` cannot attach in this container, observed 2026-11-20), so the binary's
    own share is read from the git calls' gaps.
  - **Cut 1, the answers side by side.** The three `--answer` calls write different units' records (one file a unit in the answers'
    store; the dispatch state they touch is taken under its lock), so `answer_all` starts them together and waits: the chain's six computations
    in series become four. This moves work, it removes none.
  - **Cut 2, a sparse clone.** `fixture` clones with `--no-checkout` and checks out `research/questions`, `research/sources` and
    `l7r/diagram/interactive` (cone mode, so the top-level files too), 8,499 of the 28,472 tracked files: 0.59-0.61 s against 1.61-1.67 s alone, measured
    2026-11-20 (`/usr/bin/time`, four alternated pairs of a full and a sparse clone of the clone, load 2.6-2.8), and a smaller index for every gate's `git diff` and `git status`. Held to the full clone's behavior: both clones driven through the
    eight states the suite drives (clean, comment, reword, `ENTRY_DRIFT_OK`, answered, stale, `RECORD_CHECKS_OK`, restored), the gate's output and
    exit code and `record-owed`'s listings diffed, identical, 175 lines each, measured 2026-11-20 (a script driving both). Case 7 counts the bypass
    records under `dev/bypass-log/`, absent from the sparse clone, so its `find` now says nothing when the folder is not there; the count is
    still the before and after of one gate.
  - **Rejected, measured.** A single-pack shallow clone (`--depth 1`): 6.96 s and 14.3 CPU-seconds to make, and a computation on it 1.45 s
    against 1.44 s on the plain clone, measured 2026-11-20 (`/usr/bin/time`, the same delta) - the base reads cost the same in one pack or 38.
    A fixture shared by the two cases: each edits its own page in place and the clone is under a second, so a copy saves nothing a sparse
    clone does not.
  - **Kept the same.** Every case, every assertion, the cases' order and the two parts; still red where its behavior breaks: with
    `entry-gate.sh` asking `record-owed` without `--unanswered` (answers ignored), the new suite fails `answered units ship` (12 passed,
    1 failed), measured 2026-11-20 (a scratch clone with that one-line change and the new suite).
  - **The wall.** Two scratch clones of HEAD c71c168ebe, `after` carrying the new suite, `make hooks-test HOOKS_ALL=1` alternated, HOOKS_JOBS 8,
    `L7R_MODEL_CACHE` set (a clone has no model cache of its own).
    Before 43.8 and 44.0 s, entry-gate's suite 39.7 and 41.9 s, measured 2026-11-20 (`EPOCHREALTIME` around make, each run's "ran" line, load 19.7 and 16.0 at their starts).
    After 44.4 and 44.2 s, entry-gate's suite 32.4 and 34.2 s, measured 2026-11-20 (the same method, load 16.8 and 15.1 at their starts, `after` dirty in the suite and `before` clean).
    A third pair, 52.2 s and 72.5 s, overlapped another builder's replays and is dropped, measured 2026-11-20 (the same method).
    So the suite fell about 7.5 s and the wall did not move, sync-with-main's suite the longest at 33.7 and 35.7 s and the wall ending 8-11 s after it, measured 2026-11-20 (the same runs).
  - **The equal-dirt pair** settles that confound: both scratch suites carry the same inert `tick` lines, run before, after, after,
    before, `/usr/bin/time` around make, each suite's end read from its `.git/hooks-test/<suite>.s` mtime against make's start.
    Before 41.3 s and 491 CPU-seconds at load 17.1, entry-gate's suite 39.2 s ending at 40.3 s, measured 2026-11-20 (`/tmp/t40/s2/run.sh`).
    Before again 62.3 s and 729 CPU-seconds at load 20.4, the suite 59.1 s ending at 61.0 s, measured 2026-11-20 (the same script).
    After 37.0 s and 461 CPU-seconds at load 12.0, the suite 27.7 s ending at 28.8 s, sync-with-main 27.3 s ending at 28.4 s, the last suite ending at 35.6 s, measured 2026-11-20 (the same script).
    After again 55.0 s and 634 CPU-seconds at load 14.2, sync-with-main 39.0 s ending at 40.0 s, the suite 36.5 s ending at 37.5 s, the last suite ending at 52.6 s, measured 2026-11-20 (the same script).
    So the chain no longer sets the full run's wall: before, the wall was the suite's end plus 1 s, and after, the short suites dealt last end 7-15 s past it, the wall the run's whole work over its eight jobs, measured 2026-11-20 (the four runs above).
    The walls' 4.3 and 7.3 s are not read as a saving, the loads differing by 3-5 between the pair's runs, measured 2026-11-20 (the same runs).
  - **The incremental run, the common case** (the session's ruling: keep the cuts if the suite is measurably faster alone and in an
    incremental run that reruns it). Each run appends a comment line to `scripts/gates/entry-gate.sh` in its scratch clone and runs
    `make hooks-test`, which reruns entry-gate's suite, l7r-gate's three shards and sync-with-main's, alternated before, after, after,
    before, twice.
    Before 29.4, 24.5, 24.2 and 23.5 s, entry-gate's suite 27.6, 23.0, 22.7 and 22.0 s, measured 2026-11-20 (the same script, load 9.9-20.1).
    After 23.5, 21.5, 20.9 and 21.3 s, the suite 21.8, 20.0, 19.4 and 19.8 s, measured 2026-11-20 (the same script and loads).
    The wall is the suite's end plus 0.4-0.5 s in every run, so here the suite still sets it, and each back-to-back pair fell 2.2-5.9 s, about 3 s at the lower loads, measured 2026-11-20 (the eight runs).
    CPU-seconds did not fall, 158-182 before and 171-190 after, system time down about 3 s and user time up about 12 s, measured 2026-11-20 (`/usr/bin/time`).
  - **Alone.** The old and new suites alternated (old, new, new, old, twice).
    Old 13.3, 15.1, 15.5 and 16.9 s, new 10.5, 11.7, 12.3 and 11.4 s, CPU-seconds 41.7-48.7 against 44.0-47.6, measured 2026-11-20 (`/usr/bin/time` around `/tmp/t40/run1.sh`, load 4.5-6.8).
    One part at a time, old 22.4 and 24.9 s, case 4 12.1 and 13.3 s, the rest 9.5 and 10.8 s, measured 2026-11-20 (`PARTS_MAX=1`, alternated, each case's first and last `tick`, load 2.6-3.3).
    New 17.7 and 17.4 s, case 4 9.6 and 9.3 s, the rest 7.8 and 7.8 s, so `WEIGHT` is now 9 and 8, measured 2026-11-20 (the same method).
    The landed suite passes 13 of 13 at `PARTS_MAX=1` in 16.6 s and at `PARTS_MAX=2` in 9.5 s, measured 2026-11-20 (`tests/hooks/test-entry-gate.sh` run alone).
    So the cuts save about 3.7 s of wall alone and about 3 s in an incremental run, and no CPU, measured 2026-11-20 (the figures above).
    The sparse clone's system time saved is spent again as user time, likely the three computations sharing the cores (a GUESS, unmeasured: no profiler here).

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|
| the answers side by side, a sparse clone | n/a - no map | n/a | none | n/a |

### T40 Approach (checklist part A)

1. **The goal, in the world.** A faster `make hooks-test`: the suite measurably faster alone and in an incremental run that reruns it, the
   common case (the session's ruling, 2026-11-20, once the full run's wall proved set by other suites); no map changes.
2. **The constraints.** FR-010, FR-013; the suite checks what it checked (every case and assertion, each red when its behavior breaks); only
   the suite and this section edited (T31 works in `rust/guard`).
3. **Where each comes from.** G: improvement 5 (the GM 2026-11-19, a faster `make hooks-test`); O: T21's full-run figures and this task's step timings.
4. **Do they describe the world here?** Measured on scratch clones of HEAD, the git calls by a shim, the suite's steps by an instrumented copy, the wall back to back.
5. **The order.** After T21 (its finding); beside T31 (different files).
6. **The exits.** Green: the suite faster alone and in an incremental run that reruns it, the suite green at `PARTS_MAX` 1 and 2 and red on a broken gate. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** The suite alone, old and new alternated; an incremental `make hooks-test` after an edit to `entry-gate.sh` and a
   full `HOOKS_ALL=1` run, on two scratch clones of HEAD equally dirty, alternated, wall and CPU-seconds by `/usr/bin/time`, each suite's end, the load noted.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.
12. **Before any fix.** Nothing a reader of a map sees; no check's verdict changes (the gate's output identical at every state). Not a defect: a speed change.

**Found and left?**
- Every computation of the owed units reads the record's pages at the merge base whole, 1,951 blobs by `git cat-file`, though a page the
  delta does not touch reads the same in the working tree: 0.63-1.13 s of each 1.4-1.6 s computation, measured 2026-11-20 (the shim's
  `cat-file` timing). Not fixed here: a change to the `owed` crate's `Delta::fetch`, outside this task's files, and it cuts every gate
  run, the push's too, not this suite alone. Filed as T43; lands before T22.
- `push-gate skip`'s `git diff --name-only HEAD` walks the whole index, 0.24 s a gate run on the full clone, observed 2026-11-20 (the shim).
  Not a defect: no wrong outcome, a cost, and not filed: a real gate pays it once a push, and this suite's sparse clone already
  shrinks the index it walks.

**Performance work?** yes - a `[perf]` task (451 FR-013: the guard suites' wall). Its answers:

1. **Where does the time go?** Into six computations of the owed units in series and a full checkout (the approach's figures).
2. **Removes work, or only moves it?** The sparse clone removes work (about 20,000 fewer files checked out and indexed per case); the answers
   side by side only move it, three computations at once where they ran in turn.
3. **What do you expect it to save, and why?** About two computations and most of a clone off the chain, 3-4 s alone and more under a full run's
   load, where each step stretched 4-10x (a GUESS from the step timings).
4. **How does the work grow with the settlement?** n/a - no settlement; with the record it grows as its pages do.
5. **What did the before and after show, and under what conditions?** The approach's figures.
   Alone 13.3-16.9 s before and 10.5-12.3 s after, measured 2026-11-20 (load 4.5-6.8).
   An incremental run after an edit to `entry-gate.sh` 23.5-29.4 s before and 20.9-23.5 s after, each pair 2.2-5.9 s faster, CPU-seconds unchanged or higher, measured 2026-11-20 (load 9.9-20.1).
   In a full run the suite fell 7.5-12 s but stopped setting the wall, now the run's whole work over eight jobs, 41.3 and 62.3 s before against 37.0 and 55.0 s after, measured 2026-11-20 (the equal-dirt pair, loads 12-20).
6. **Did any map move, and does it still keep the research?** No map.

### T41 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T41 Approach (checklist part A)

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


### T43 (<why: the finding or measurement that files it>)

- **Approach**: <what changes, where, and how it was measured - each figure dated with its method>.

| step | alone off: fixed and pinned | fresh block vs HEAD | pool manifests moved | the last resort |
|---|---|---|---|---|

### T43 Approach (checklist part A)

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

