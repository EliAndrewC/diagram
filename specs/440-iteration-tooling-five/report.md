# Feature report - 440-iteration-tooling-five

Written by `make feature-report F=440` from 261 events (2026-10-27T22:48 to 2026-10-27T23:24 UTC), 9 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 19 min | 53% |
| other tool | 9 min | 26% |
| waiting: spec-fidelity | 4 min | 12% |
| waiting: spec-fidelity-verify | 2 min | 6% |
| quick test | 1 min | 2% |
| waiting: round-arbiter | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 43 subagent tool call(s) (of 118) are counted apart (0 by the subagent transcripts, 43 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 17 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make perf-ab | 1 min |
| make ledger-owed | 0 min |
| make plan-delta | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 2 |
| impl-drift | 1 | findings 1 |
| round-arbiter | 1 | findings 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 1 over 360 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 1

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 6 min (open) | 1 min | 5 min | 1 | 1, 5 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 23:18-23:19 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T01 | 23:19-23:24 | the tick or the last event | 3 | 5 | 0 | 0 | impl-drift x1 (0 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 23:18 | started (`make task-start`) | |
| T01 | 23:19 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 23:24 | impl-drift returned findings (0 min) | |

## What each check cost, per changed line (360 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 12 min | 938k | 39.2k | 0.011 | 2.6k |
| spec-fidelity-verify | 1 | 4 min | 279k | 9.2k | 0.003 | 0.8k |
| impl-drift | 1 | 0 min | 19k | 0.2k | 0.003 | 0.1k |

This report took 1.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
