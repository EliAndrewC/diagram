# Feature report - 434-placement-call-counts

Written by `make feature-report F=434` from 425 events (2026-10-27T13:00 to 2026-10-27T14:23 UTC), 11 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 40 min | 49% |
| thinking | 35 min | 42% |
| waiting: subagent | 4 min | 5% |
| waiting: a background run | 1 min | 1% |
| quick test | 1 min | 1% |
| writing the spec | 1 min | 1% |
| dispatching: spec review | 0 min | 0% |
| edit | 0 min | 0% |
| waiting: round-arbiter | 0 min | 0% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |

The session's own time above; its 50 subagent tool call(s) (of 175) are counted apart (0 by the subagent transcripts, 50 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 11 run(s), 26 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make land | 23 min |
| Bash | 8 min |
| make ledger-owed | 5 min |
| make phase-calls | 2 min |
| make placement-stages | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 11 | CHANGES REQUIRED 1, CLEAR 2, NOT-REVIEWABLE 1 |
| round-arbiter | 3 | findings 2 |
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
- check dispatches 1 over 569 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 3

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 33 min (open) | 25 min | 8 min | 2 | 19, 6, 8 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 13:49-14:08 | round-arbiter findings | 19 | 19 | 0 | 0 | impl-drift x1, round-arbiter x1 (1 min) |
| T01 | 14:08-14:15 | round-arbiter findings | 5 | 6 | 0 | 0 | round-arbiter x1 (1 min) |
| T01 | 14:15-14:23 | the tick or the last event | 6 | 8 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 13:49 | started (`make task-start`) | |
| T01 | 14:08 | impl-drift returned findings (0 min) | |
| T01 | 14:08 | round-arbiter returned findings (1 min) | |
| T01 | 14:15 | part B written | |
| T01 | 14:15 | round-arbiter returned findings (1 min) | |

## What each check cost, per changed line (569 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 16 min | 1148k | 35.5k | 0.007 | 2.0k |
| spec-fidelity-verify | 3 | 7 min | 327k | 19.2k | 0.005 | 0.6k |
| impl-drift | 1 | 0 min | 21k | 0.3k | 0.002 | 0.0k |

This report took 1.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
