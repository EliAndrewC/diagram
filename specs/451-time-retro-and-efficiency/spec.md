# Feature Specification: Where the time goes, and the six cheap fixes

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=451-time-retro-and-efficiency`)

**Created**: 2026-11-19

**Status**: Draft

**Approved**: the GM, 2026-11-19, "All 6 of your proposed improvements sound good so please do all of that, along with your 4 proposed ideas for filling ion what's missing from gathering this kind of data.  And let's make sure all of the enforcement is real enforcement and not just instructions."

**Affects**: tooling

**Input**: the GM's request in `request.md`; the 2026-11-19 retrospective of feature 449's last 14 hours

## Why

The GM asked where a working day's time goes - per task, and overall on tooling, tests and recompiling - and whether the retrospective
could be cheap and historical. The 2026-11-19 retrospective of 828 wall-clock minutes of feature 449 (measured 2026-11-19 (the session's
and its subagents' transcripts, the gate's run records, the landing logs)) found builder agents' model turns 55% of the wall clock,
test runs 19%, review agents 9%, landings 2%, guards at most about 3%; and six cheap fixes worth, by its estimates, 110 to 190 minutes of
that window. It had to be assembled by hand: `make where-time` booked 678 of its 845 minutes as "waiting on work" and every gate and
test column 0 (measured 2026-11-19 (`make where-time F=449 SINCE=2026-11-19T14:00:00Z`)), because the guard's event log (`.git/l7r-events/<feature>.jsonl`), which records every tool call with its duration,
agent and make target, classes 206 of 208 tool-minutes as "other tool" (measured 2026-11-19 (the `ms` of the log's PostToolUse lines since 14:00Z, summed by `cat`)) and keeps no end for a background run, no phase inside a make
run and no token cost of an agent.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A retrospective is one command (Priority: P1)

The GM asks where a day's time went. The session runs one `make where-time F=<feature> SINCE=<time> UNTIL=<time>` and reads off,
per task and in total, the time spent on tests, compiling, the gate, landings, reviews, background runs and the model, with the wall
clock on the critical path apart from the summed agent-minutes, and the rework (refused landings, plan re-rounds).

**Why this priority**: it is what the GM asked for, and every later efficiency question is answered from it.

**Independent Test**: on a fixture event log holding one task's tool calls, background runs, make phases and agent stops, the report's
columns equal the fixture's known sums.

**Acceptance Scenarios**:

1. **Given** a window in which `make static`, `make rust-test` and `make hooks-test` ran, **When** the report runs, **Then** their time
   is under tests, not "other tool".
2. **Given** a `make land` started in the background, **When** the report runs, **Then** its span is booked to land from its start to
   its completion notice, and the wait it caused is booked to it.
3. **Given** a `make static` run whose coverage build took 40 s of its 60 s, **When** the report runs, **Then** compile shows 40 s and
   tests 20 s for that run.
4. **Given** agents that stopped in the window, **When** the report runs, **Then** each agent's minutes and token cost appear under
   its task.

---

### User Story 2 - A builder's context stays small (Priority: P1)

A builder agent on a long task reaches the context size at which its model calls slow (measured 2026-11-19 (3,280 builder calls by
context size): 10 s per 1,000 output tokens under 200k tokens, 23 s over 700k). Its next tool call is refused, naming the handoff:
write a handoff file of what is done and what is left, and stop; the main session dispatches a fresh agent with it. A SendMessage that
would resume an agent already past the size is refused the same way.

**Why this priority**: the largest saving the retrospective found, 44 to 95 minutes of a 14-hour window, on the critical path - an estimate from a correlation (measured 2026-11-19 (the per-1,000-output-token rates by context size applied to the calls' own output tokens, at the 200-400k rate for calls over 400k and at the under-200k rate for calls over 200k)).

**Independent Test**: a subagent tool call whose transcript reports a context past the threshold is refused with the handoff named; one
under it passes; a SendMessage to an agent past it is refused.

**Acceptance Scenarios**:

1. **Given** a subagent whose last model call's context is past the threshold, **When** it makes a tool call other than writing its
   handoff file, **Then** the call is refused naming the handoff file's path and the next step.
2. **Given** the same agent writing its handoff file, **Then** the write passes.
3. **Given** the main session resuming such an agent by SendMessage, **Then** it is refused naming a fresh dispatch with the handoff.

---

### User Story 3 - The full static check is not the edit loop (Priority: P2)

A builder runs `make static` a third time in one task since the last landing. It is refused, naming the crate-scoped checks that answer
the same question for the crate being edited, and an escape with a reason.

**Why this priority**: 124 runs at about 35 s in the window (measured 2026-11-19 (the subagent transcripts' Bash spans)), the second
largest saving, 26 to 52 minutes (measured 2026-11-19 (the runs capped at two a task, 34 against 124, at each run's own measured time: 52 minutes, or 26 if half the extra runs were needed)).

**Independent Test**: a third `make static` in one task is refused with the crate-scoped checks named; the first two pass; a run
after a landing starts the count again; the escape with a reason passes and is recorded.

**Acceptance Scenarios**:

1. **Given** two `make static` runs in a task since its landing, **When** a third is asked, **Then** it is refused naming the
   crate-scoped checks.
2. **Given** the escape with a reason of two words or more, **Then** the run proceeds and the escape is recorded.

---

### User Story 4 - A long run is one the session can track (Priority: P2)

A make target or cargo run started with `&`, `nohup`, `setsid` or `disown` inside a Bash call is refused, naming the Bash tool's
background form, whose completion wakes the session. The main session's own wait loops poll every 60 s, not 480 s.

**Why this priority**: the only stretches with nothing running were an agent's untracked run (14.9 minutes) and a long poll (2.9
minutes) (measured 2026-11-19 (the transcripts' idle spans)).

**Independent Test**: `( make static > log ) &` in a Bash call is refused with the background form named; `make static` in a
background Bash call passes; a long-running make in the foreground passes.

---

### User Story 5 - A deferral is never left unordered (Priority: P3)

A plan section's "Found and left?" item that defers a defect names its filed task and its order ("lands before ..."), or `make decide`
refuses the section, naming the form.

**Why this priority**: two of the seven first-round plan-review blocks in the window were deferrals with no order (measured 2026-11-19
(the spec-fidelity verdicts)), each a review round of several minutes.

**Independent Test**: a section whose found-and-left item names a defect with no task id is refused; one naming `T123, which lands
before T124` passes; `none` passes.

---

### User Story 6 - The slow hook suites and the small landing frictions (Priority: P3)

`make hooks-test`'s three slowest suites are split so that none of the shards takes more than about 20 s, so the run's wall time is not
held by one suite. `make land T="T1,T2"` is read as `T="T1 T2"`. `make task-add` runs the spec lint on the line it writes and refuses
the line (leaving nothing written) where it cites another feature's requirement without naming the feature.

**Why this priority**: about 13 minutes in the window together (measured 2026-11-19 (the hook suites' timings; the refused landings)).

**Independent Test**: each shard's measured time; a comma-separated `T=` lands both tasks; a task-add line citing a bare `FR-019` of
another feature is refused.

### Edge Cases

- A builder past the context threshold mid-edit: it may still write its handoff file, and nothing else.
- A task with no landing yet: the static count runs from the task's start.
- A background run whose completion notice never arrives (the session ended): the report books it as open from its start, not as a
  zero-length run.
- An event log line with an unknown make target: booked to "other", never dropped.
- The escape for a refusal: every refusal here has one, a reason of two words or more, recorded, as the project's guards do.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The event log classes each Bash call that runs a make target by its target into tests, compile, gate, land, review,
  docs or other, by one table the readers share.
- **FR-002**: A background run's end is logged from its completion notice, with its span; a wait between turns is booked to the
  background run that was in flight.
- **FR-003**: The Rust checks append their build, test and cover seconds per crate, and `make land` its phases' seconds (the cheap
  refusals, the gate, the claims round, the push), as event lines.
- **FR-004**: An agent's stop line carries its token cost (input, cached input, output) and its task where its dispatch names one.
- **FR-005**: `make where-time` and `make feature-report` read FR-001 to FR-004's lines into columns for tests, compile, gate, land,
  review, background run and model; report the wall clock on the critical path apart from the summed agent-minutes; count the rework
  (refused landings, plan re-rounds, agents nudged); and `make where-time` takes `UNTIL=`.
- **FR-006**: A guard refuses a subagent's tool call once its context is past a threshold, but for writing its handoff file, naming
  the file and the next step; and refuses a SendMessage resuming an agent past the threshold, naming a fresh dispatch. The threshold is a
  knob, GUESS: 400k tokens.
  Past it the builder calls ran 14.8 s per 1,000 output tokens, 11.9 s below (observed 2026-11-19, method: the 3,280 builder calls bucketed by context size).
- **FR-007**: A guard refuses a third `make static` in one task since its last landing, naming the crate-scoped checks for the crates
  the task's delta changes.
- **FR-008**: A guard refuses a make target or cargo run put in the background inside a Bash call (`&`, `nohup`, `setsid`, `disown`),
  naming the Bash tool's background form; the main session's waits poll at 60 s.
- **FR-009**: `make decide` refuses a plan section whose found-and-left item defers a defect without its filed task id and its order.
- **FR-010**: The three slowest hook suites are split so each shard takes about 20 s or less.
- **FR-011**: `make land` reads commas in `T=` as spaces; `make task-add` refuses, before writing, a line that cites another feature's
  requirement without naming the feature.
- **FR-012**: Every refusal of FR-006 to FR-009 and FR-011 has a red-first test proving it fires (the check deleted, the test red), an
  escape of a reason of two words or more that is recorded, and a message naming the compliant command (the project's guard rules).

### Key Entities

- **Event line**: one JSON line of the event log - a tool call's start or end, a background run's end, a make phase's seconds, an
  agent's stop with its cost - with its time, session, agent and task.
- **Category table**: the one map from a make target to its bucket, shared by the log's writer and its readers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a window of real work, `make where-time F= SINCE= UNTIL=` books under a tenth of the wall clock as unexplained
  waiting (a target, GUESS).
  Today it books 678 of 845 minutes so (observed 2026-11-19, method: `make where-time F=449 SINCE=2026-11-19T14:00:00Z`).
- **SC-002**: The 2026-11-19 retrospective's per-task table and totals can be reproduced from the event log by that one command, within
  a tolerance of 10% on each bucket (a target, GUESS), for work done after this feature lands.
- **SC-003**: Each of the six fixes' refusals fires on its red fixture and passes its compliant case (FR-012).
- **SC-004**: No hook-suite shard takes more than about 20 s (measured the same way the suites' timings are now).
- **SC-005**: In the first full day after landing, `make static` runs per task fall to at most two but for recorded escapes, and no
  agent's context passes the threshold but for a recorded escape.

## Assumptions

- The thresholds (400k tokens; the third static run; 20 s a shard; the 60 s poll) are GUESS knobs from one day's measurement, retuned
  from the new data (`make tunables`).
- The Claude Code hook payloads carry what the guards need: a subagent's transcript path (for its context size) and the background
  run's completion notice; where one does not, the plan says what it reads instead.
- Out of scope: changing what any check or review judges, and any map.
