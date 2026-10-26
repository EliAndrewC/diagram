# Feature report - 424-record-intro-maps-money

Written by `make feature-report F=424` from 89 events (2026-10-26T00:40 to 2026-10-26T01:27 UTC), 4 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| waiting: a background run | 32 min | 69% |
| other tool | 9 min | 19% |
| thinking | 5 min | 11% |
| test file | 0 min | 1% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |

The session's own time above; its 9 subagent tool call(s) (of 37) are counted apart (0 by the subagent transcripts, 9 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 3 run(s), 2 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make ledger-owed | 8 min |
| Bash | 1 min |
| make claims-bundle | 0 min |
| make claims-owed | 0 min |
| make record | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 2 | CLEAR 1, FAITHFUL 1 |
| impl-drift | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 1 over 35 changed lines: cascade ratio 0.03
- tasks ticked: 0 of 1

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 42 min (open) | 0 min | 42 min | 0 | 42 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 00:45-01:27 | the tick or the last event | 10 | 10 | 32 | 0 | impl-drift x1 (0 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 00:45 | started (`make task-start`) | |
| T01 | 01:18 | impl-drift returned findings (0 min) | |

## What each check cost, per changed line (35 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 2 min | 150k | 7.4k | 0.057 | 4.3k |
| impl-drift | 1 | 0 min | 19k | 0.3k | 0.029 | 0.5k |

This report took 2.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
