# Research: what the two guards have actually cost

Every number in `spec.md` comes from here. Two sources, both already in the repository or on the
box, neither of them an estimate:

- **`dev/run-log/`** - one JSON file per `make done` / `ci-*` invocation, with `target`, `scope`,
  `seconds`, `result` and `commit`. It exists precisely so that *"a target that quietly gets slower
  shows up in the history rather than in someone's memory"*.
- **This project's Claude Code transcripts**, `~/.claude/projects/-diagram/*.jsonl`, 29 files,
  715 MB, 2026-08-24 to 2026-08-30. Every tool call and every hook refusal is in them. The replay
  script is [`measure/replay.py`](measure/replay.py) in this directory; it is the only way the
  questions below could be answered, because **no guard records when it fires** - which is itself
  finding R6.

## R1 - what the expensive-measurement guard has cost and saved

Method: `measure/replay.py budgets`, which walks every transcript in order and runs the same state
machine `scripts/measure-hooks.sh` runs (count `make test-full` / `done FULL=1`; reset on an edit to
`l7r/**.py` outside `tests/`, on `git commit`, on `MEASURE_OK`; block and reset when the count passes
the budget).

| budget | blocked | ran | sessions affected |
|---|---|---|---|
| 3 | 17 | 112 | 2 |
| 2 (today) | 30 | 99 | 3 |
| **1 (this feature)** | **56** | **73** | **7** |

Real firings recorded in the transcripts: **9** (the replay counts more because it also replays
sessions that predate the guard, which landed 2026-08-28).

What happened in the very next Bash call after each of the 9: **4 escaped with `MEASURE_OK`**, 1 went
straight back to a make target, 4 went and did something else. So the guard plausibly changed the
session's behavior 4 times in 9, and the other 5 firings bought a round trip and no saving.

**The ruling is the GM's** (`request.md`), taken with that number in front of it. What makes it pay
is FR-002: a reminder on the first run costs zero round trips, so the cheapest place to change
behavior is before the block, not at it. If the escape rate on the tighter budget stays above about
half once FR-006's log can measure it, the budget is the thing to revisit, and `MEASURE_BUDGET`
exists so that is a one-line change.

## R2 - a block costs a round trip; a reminder costs nothing

The GM states the mechanism in the request: *"bouncing back a command forces another pass through
the LLM engine, which also takes time"*. This repository's own transcript profile (2026-07-20,
re-confirmed 2026-07-25) puts **78% of wall time in model turn latency, not tool execution**, and
`CLAUDE.md` derives its whole batching doctrine from it.

So the arithmetic for any guard is: a firing spends one round trip and saves the run it prevented,
multiplied by how often it actually prevents one. A reminder rides in output the session is already
reading, spends nothing, and needs no deterrence rate to be worth having. That is why FR-002 exists
and why it is emitted once per streak rather than on every run.

## R3 - the quick+done block is overridden more often than it is obeyed

Method: `measure/replay.py blocks`, which finds every tool result carrying a guard's refusal text and
reads the next Bash command in the same transcript.

37 firings of the "quick and done in ONE command" block:

| what the session did next | count |
|---|---|
| escaped with `GATE_OK` in the very next call | **23** |
| ran a make target (the guard's intent) | 5 |
| something unrelated | 8 |
| nothing | 1 |

So 62% of firings were escaped in the very next call, at a cost of one round trip each, to prevent
between 4.1 s (a warm `quick`) and 25.3 s (a cold one) of duplicated work.

**The doctrine this triggers is already written down** in `CLAUDE.md`: *"a guard that fires on
correct work teaches a session to bypass every guard"*, and the escape becoming routine is the exact
symptom it names. The answer is the GM's: combine, do not reject.

## R4 - what `make quick` could hand to `make done` (the declined stamp)

Measured in a fresh clone at main's tip, 2026-08-30:

| phase | cost |
|---|---|
| `make lint` | 1.03 s |
| `make format` | 0.11 s |
| `make typecheck` | 0.65 s |
| `make quick`, warm (testmon, nothing changed) | 4.13 s |
| `make quick`, cold (no testmon database) | 25.33 s |
| `make done`, green, median of the last 25 recorded runs | 137 s |

`quick`'s pytest run and `done`'s are not the same run and the results are not transferable:
`done` runs the whole tree under coverage; `quick` runs a testmon-selected subset with `--no-cov`,
ignoring `tests/gate`, `tests/full`, `tests/tier_town`, `tests/tier_city` and (when fresh)
`tests/tooling`. The Makefile already records what happens if you deselect from a traced run - *"a
deselected test takes its coverage with it"* - measured on 2026-08-24, when deselecting two files
dropped a module from 100% to 52% on code nothing had changed.

### The alternative that would make the GM's proposal work literally, priced

The decline above is only honest if the other road is priced too: make `quick` PRODUCE coverage
data, so the subset it ran genuinely transfers and `done` can deselect it.

- **Measured anchor** (one file, `tests/settlement/test_houses.py`): `make test-file` 3.07 s
  (8 workers, `--no-cov`) against `make cov-file` 4.08 s (coverage, and serial - so the comparison is
  conflated and this is an upper bound on the tracing cost rather than a clean reading of it). What
  it establishes is the direction and the order of magnitude: tracing is a tens-of-percent tax on the
  loop whose whole value is that it answers in about four seconds.
- **The structural half, which decides it regardless of the number**: what `done` could deselect is
  exactly the set testmon SELECTED, and that set is small BY CONSTRUCTION - it is why `quick` costs
  4.1 s while `done`'s test phase costs tens of seconds. `done` would still run the whole remaining
  tree under coverage and would additionally have to combine two coverage datasets produced by
  different processes with different worker counts, which this Makefile already records as the slow
  half of a traced run ("xdist's coverage combine is the slow half" - the reason `cov-file` is
  serial). The transferable prize is the small part; the machinery to transfer it lands on the large
  part.
- **Ruling**: rejected. It makes the fast loop slow, which is the reason `quick` exists, to transfer
  the smallest share of the gate.

**DECLINED, with its price** (the project's rule for recording an accepted limitation and the
alternatives that were rejected): a cross-process stamp letting `done` skip `lint`/`format`/
`typecheck` after a green `quick`. It would save **1.8 s of a 137 s gate**, 1.3%. Against that it
adds a second content key that would have to cover `tests/` and every configuration file the three
phases read - the existing engine key deliberately does not - and the failure mode of getting that
key wrong is silent: a gate phase skipped that should have run. Not worth 1.8 s. FR-003 removes the
duplication for the single-command form outright, which is the larger half anyway.

## R5 - the quoted durations were wrong, and the class of defect is stale hardcoding

`dev/run-log/`, green `make done` runs only, by day:

| day | n | median | min | max |
|---|---|---|---|---|
| 2026-08-24 | 8 | 316 s | 279 | 412 |
| 2026-08-25 | 16 | 301 s | 294 | 338 |
| 2026-08-26 | 20 | 44 s | 33 | 337 |
| 2026-08-27 | 22 | 35 s | 32 | 138 |
| 2026-08-28 | 50 | 68 s | 16 | 1470 |
| 2026-08-29 | 59 | 111 s | 10 | 324 |

The guard message says "~70 s with scope locked". `dev/switches.json` records the scope as
**unlocked since 2026-08-27T23:50Z**, so for three days the message has described a configuration
nobody was in, quoting a number 2x below what the gate was costing. Nothing detected this, because
the number is a string in a shell script and the truth is a directory of JSON.

Hence FR-005: derive it, or do not state it.

**Second-order finding, left as a note rather than acted on here**: the gate's median cost has risen
from 35 s (2026-08-27) to 111 s (2026-08-29). Part is the scope unlock, which is deliberate. Whether
the rest is deliberate is a question for a session that owns the gate's cost, and it is recorded here
so that the next such session starts from the number rather than from an impression. It is out of
this feature's scope (`spec.md`, "OUT of scope").

## R6 - no guard records when it fires

The question the GM asked this session - *"should we make it so we start blocking at 2 in a row"* -
could only be answered by replaying 715 MB of transcripts, because none of the twelve guards writes
anything when it refuses a command. `docs/review-ledger.md` exists so that *"is it pulling its
weight"* is a total rather than an impression for the review subagents; the guards have no
equivalent.

The raw grep also shows why the replay had to be careful: a naive count of the string
`pair-hooks.sh` across the transcripts returns 277, of which only **13** are firings - the rest are
file listings, settings dumps and this kind of audit quoting the name. A guard log makes the count
exact and free.

FR-006 is that log, in the form `dev/run-log/README.md` already argues for: one file per entry,
because *"an append-only shared log conflicts on EVERY concurrent push"*. It covers the TWO guards
this feature touches and no others: `batching-hooks.sh` firing 119 times is a finding to put to the
GM as its own question, not a reason to edit ten guards and their ten companion tests inside a
feature about two of them (`spec-fidelity`, round 1).

**Sources:** this repository's own `dev/run-log/`, `dev/switches.json` and Claude Code transcripts;
no external source is cited because no claim here is about the world outside this repository.

## R7 - a question for the GM: the gate rolls a map before it lints

Found while planning this feature, measured, and NOT acted on here - `spec-fidelity` ruled it
unrequested in round 2, and it is right: the GM's request is about what a guard does when it fires,
not about what `make done` runs in what order.

`make done` runs `reference` - **29 s measured** - before `lint`, `format` and `typecheck`, which
cost **1.8 s together**. So a lint error is reported 29 seconds after it could have been. The run log
records **7 gate runs that failed on lint, format or typecheck**, each of which paid the roll first.

Reversing the order (static phases, then `reference`, then the rest) does not weaken the doctrine
that the reference settlement gates everything expensive: the phases moved ahead of it are cheaper
than it by a factor of 16, and everything expensive still stands behind it.

It wants a one-line ruling. If the GM says yes it is a Makefile reorder plus a test, in minutes.

**Sources:** `dev/run-log/`, and the timings measured in this clone on 2026-08-30.
