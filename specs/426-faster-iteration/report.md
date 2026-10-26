# Feature report - 426-faster-iteration

Written by `make feature-report F=426` from 668 events (2026-10-26T10:44 to 2026-10-26T13:09 UTC), 20 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 26 min | 60% |
| other tool | 20 min | 14% |
| waiting: subagent | 15 min | 10% |
| waiting: a background run | 8 min | 5% |
| quick test | 6 min | 4% |
| test file | 4 min | 3% |
| writing the spec | 3 min | 2% |
| waiting: spec-fidelity | 2 min | 1% |
| edit | 1 min | 1% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| spec-kit step | 0 min | 0% |

The session's own time above; its 41 subagent tool call(s) (of 292) are counted apart (0 by the subagent transcripts, 41 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 10 run(s), 23 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 7 min |
| make hooks-test | 6 min |
| make cohort | 4 min |
| make cover-changed | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 8 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 5, NOT-REVIEWABLE 1 |
| spec-fidelity-verify | 2 | FAITHFUL 1 |
| round-arbiter | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-426-faster-iteration-blocks-T10-5c8223aa | 2 |

## Process signals

- gates: red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 5 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1614 changed lines: cascade ratio 0.00
- tasks ticked: 9 of 11

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T02 | 1 h 05 min | 59 min | 7 min | 2 | 23, 35, 7 |
| T05 | 33 min | 11 min | 22 min | 1 | 11, 22 |
| T06 | 21 min | 0 min | 21 min | 0 | 21 |
| T10 | 8 min | 5 min | 3 min | 2 | 3, 2, 3 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T02 | 11:17-11:40 | spec-fidelity CLEAR | 72 | 23 | 0 | 0 | spec-fidelity x1 (1 min) |
| T02 | 11:40-12:15 | round-arbiter findings | 29 | 25 | 10 | 0 | round-arbiter x1 (1 min) |
| T02 | 12:15-12:22 | the tick or the last event | 4 | 4 | 3 | 0 | - |
| T05 | 12:24-12:35 | spec-fidelity CLEAR | 29 | 11 | 0 | 0 | spec-fidelity x1 (1 min) |
| T05 | 12:35-12:57 | the tick or the last event | 25 | 19 | 3 | 0 | - |
| T06 | 12:36-12:57 | the tick or the last event | 24 | 18 | 3 | 0 | - |
| T10 | 12:59-13:03 | spec-fidelity CLEAR | 8 | 1 | 2 | 0 | spec-fidelity x1 (3 min) |
| T10 | 13:03-13:04 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T10 | 13:04-13:07 | the tick or the last event | 1 | 1 | 3 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T02 | 11:17 | started (`make task-start`) | |
| T02 | 11:26 | `make cohort` (1 min) | |
| T02 | 11:40 | spec-fidelity returned CLEAR (1 min) | |
| T02 | 12:15 | part B written | |
| T02 | 12:15 | round-arbiter returned findings (1 min) | |
| T02 | 12:22 | ticked | |
| T05 | 12:24 | started (`make task-start`) | |
| T05 | 12:30 | `make cohort` (1 min) | |
| T05 | 12:30 | `make cohort` (0 min) | |
| T05 | 12:33 | `make cohort` (1 min) | |
| T05 | 12:35 | spec-fidelity returned CLEAR (1 min) | |
| T05 | 12:35 | `make cohort` (1 min) | |
| T05 | 12:57 | ticked | |
| T06 | 12:36 | started (`make task-start`) | |
| T06 | 12:57 | ticked | |
| T10 | 12:59 | started (`make task-start`) | |
| T10 | 13:03 | spec-fidelity returned CLEAR (3 min) | |
| T10 | 13:04 | spec-fidelity returned CLEAR (1 min) | |
| T10 | 13:07 | ticked | |

## What each check cost, per changed line (1614 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 8 | 21 min | 909k | 64.2k | 0.005 | 0.6k |
| spec-fidelity-verify | 1 | 1 min | 113k | 4.6k | 0.001 | 0.1k |

This report took 2.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
