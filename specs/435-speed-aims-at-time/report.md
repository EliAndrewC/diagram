# Feature report - 435-speed-aims-at-time

Written by `make feature-report F=435` from 1107 events (2026-10-27T15:17 to 2026-10-27T19:25 UTC), 28 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 50 min | 68% |
| waiting: subagent | 39 min | 16% |
| other tool | 20 min | 8% |
| waiting: the GM | 8 min | 3% |
| test file | 3 min | 1% |
| waiting: a background run | 3 min | 1% |
| waiting: spec-fidelity | 2 min | 1% |
| quick test | 2 min | 1% |
| writing the spec | 1 min | 1% |
| waiting: escalation-check | 1 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| edit | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 160 subagent tool call(s) (of 441) are counted apart (0 by the subagent transcripts, 160 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 28 run(s), 45 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make claims-checked | 12 min |
| Bash | 6 min |
| make land | 6 min |
| make ledger-owed | 1 min |
| make cover-changed | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 12 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 7 |
| impl-drift | 5 | findings 5 |
| claims-triage | 4 | findings 2 |
| escalation-check | 3 | findings 3 |
| round-arbiter | 3 | findings 2 |
| general-purpose | 1 | clean 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| claims-triage | claims-triage | 4 |
| impl-drift | claims-owed | 4 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 7 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 5 over 1109 changed lines: cascade ratio 0.00
- tasks ticked: 6 of 9

## Tripwires (FR-010) - what fired, or would have

- 18:36 round:impl-drift|claims-owed@3
- 18:39 round:impl-drift|claims-owed@4

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 41 min | 12 min | 30 min | 1 | 12, 30 |
| T02 | 10 min | 7 min | 4 min | 1 | 7, 4 |
| T06 | 29 min | 1 min | 28 min | 1 | 1, 28 |
| T08 | 21 min | 16 min | 5 min | 2 | 1, 15, 5 |
| T04 | 22 min | 0 min | 22 min | 0 | 22 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 15:46-15:58 | round-arbiter findings | 10 | 11 | 0 | 0 | impl-drift x1, round-arbiter x1 (1 min) |
| T01 | 15:58-16:28 | the tick or the last event | 6 | 24 | 6 | 0 | - |
| T02 | 17:32-17:38 | spec-fidelity CLEAR | 31 | 5 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T02 | 17:38-17:42 | the tick or the last event | 1 | 1 | 3 | 0 | - |
| T06 | 17:52-17:53 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T06 | 17:53-18:21 | the tick or the last event | 38 | 18 | 10 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T08 | 18:24-18:24 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T08 | 18:24-18:39 | spec-fidelity CLEAR | 24 | 11 | 4 | 0 | claims-triage x2, impl-drift x2, spec-fidelity x1 (2 min) |
| T08 | 18:39-18:45 | the tick or the last event | 4 | 2 | 3 | 0 | - |
| T04 | 18:47-19:09 | the tick or the last event | 14 | 17 | 5 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 15:46 | started (`make task-start`) | |
| T01 | 15:56 | impl-drift returned findings (0 min) | |
| T01 | 15:58 | round-arbiter returned findings (1 min) | |
| T01 | 16:28 | ticked | |
| T02 | 17:32 | started (`make task-start`) | |
| T02 | 17:33 | claims-triage returned findings (1 min) | |
| T02 | 17:34 | impl-drift returned findings (1 min) | |
| T02 | 17:38 | spec-fidelity returned CLEAR (1 min) | |
| T02 | 17:42 | ticked | |
| T06 | 17:52 | started (`make task-start`) | |
| T06 | 17:53 | spec-fidelity returned CLEAR (1 min) | |
| T06 | 18:18 | claims-triage returned (0 min) | |
| T06 | 18:19 | impl-drift returned findings (1 min) | |
| T06 | 18:21 | ticked | |
| T08 | 18:24 | started (`make task-start`) | |
| T08 | 18:24 | spec-fidelity returned CLEAR (1 min) | |
| T08 | 18:35 | claims-triage returned (0 min) | |
| T08 | 18:37 | impl-drift returned findings (1 min) | |
| T08 | 18:39 | claims-triage returned findings (0 min) | |
| T08 | 18:39 | spec-fidelity returned CLEAR (1 min) | |
| T08 | 18:40 | impl-drift returned findings (1 min) | |
| T08 | 18:45 | ticked | |
| T04 | 18:47 | started (`make task-start`) | |
| T04 | 19:09 | ticked | |

## What each check cost, per changed line (1109 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 9 | 16 min | 1020k | 58.6k | 0.008 | 0.9k |
| impl-drift | 5 | 3 min | 468k | 18.6k | 0.005 | 0.4k |
| escalation-check | 3 | 2 min | 279k | 10.7k | 0.003 | 0.3k |
| spec-fidelity-verify | 3 | 5 min | 202k | 13.6k | 0.003 | 0.2k |

This report took 1.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
