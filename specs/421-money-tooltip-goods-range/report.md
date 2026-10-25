# Feature report - 421-money-tooltip-goods-range

Written by `make feature-report F=421` from 109 events (2026-10-25T13:41 to 2026-10-25T15:21 UTC), 6 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 30 min | 89% |
| waiting: subagent | 10 min | 10% |
| other tool | 0 min | 0% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 14 subagent tool call(s) (of 41) are counted apart (0 by the subagent transcripts, 14 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 3 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make record | 1 min |
| Bash | 0 min |
| make ledger-owed | 0 min |
| make task-start | 0 min |
| make decide | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 31 changed lines: cascade ratio 0.00
- tasks ticked: 1 of 2

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 2 h 29 min | 1 min | 2 h 29 min | 1 | 1, 149 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 13:44-13:44 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (0 min) |
| T01 | 13:44-16:13 | the tick or the last event | 9 | 87 | 9 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 13:44 | started (`make task-start`) | |
| T01 | 13:44 | spec-fidelity returned CLEAR (0 min) | |
| T01 | 16:13 | ticked | |

## What each check cost, per changed line (31 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 2 min | 251k | 11.4k | 0.097 | 8.1k |
| spec-fidelity-verify | 1 | 1 min | 44k | 2.9k | 0.032 | 1.4k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
