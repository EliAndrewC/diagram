# Feature report - 427-call-volume-refactors

Written by `make feature-report F=427` from 2525 events (2026-10-26T12:19 to 2026-10-28T04:18 UTC), 43 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 28 h 25 min | - |
| thinking | 3 h 23 min | 43% |
| other tool | 1 h 41 min | 21% |
| waiting: a background run | 1 h 12 min | 15% |
| waiting: subagent | 40 min | 8% |
| test file | 24 min | 5% |
| waiting: the GM | 22 min | 5% |
| writing the spec | 6 min | 1% |
| waiting: impl-drift | 2 min | 0% |
| waiting: spec-fidelity | 1 min | 0% |
| edit | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| quick test | 0 min | 0% |
| waiting: round-arbiter | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| gate | 0 min | 0% |
| waiting: escalation-check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

The session's own time above; its 213 subagent tool call(s) (of 1057) are counted apart (0 by the subagent transcripts, 213 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 59 run(s), 1 h 30 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 39 min |
| make land | 9 min |
| make land-tooling | 9 min |
| make task-start | 6 min |
| make perf-fanout | 6 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 25 | BLOCKED 6, CHANGES REQUIRED 1, CLEAR 7, NOT-REVIEWABLE 1 |
| impl-drift | 19 | findings 19 |
| claims-triage | 8 | findings 4 |
| round-arbiter | 5 | CLEAR 1, findings 3 |
| spec-fidelity-verify | 3 | CHANGES REQUIRED 4, FAITHFUL 5, NOT-REVIEWABLE 1 |
| escalation-check | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-owed | 16 |
| claims-triage | claims-triage | 8 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 10 recorded in commits, 6 returned
- reversals (A -> B -> A): 0
- check dispatches 19 over 2323 changed lines: cascade ratio 0.01
- tasks ticked: 11 of 13

## Tripwires (FR-010) - what fired, or would have

- 19:32 round:impl-drift|claims-owed@3
- 19:37 round:impl-drift|claims-owed@4
- 19:38 round:impl-drift|claims-owed@5
- 19:47 round:impl-drift|claims-owed@6
- 20:27 round:impl-drift|claims-owed@7
- 20:29 round:impl-drift|claims-owed@8
- 20:32 round:impl-drift|claims-owed@9
- 20:33 round:impl-drift|claims-owed@10
- 21:00 round:impl-drift|claims-owed@11
- 21:02 round:impl-drift|claims-owed@12
- 22:02 round:impl-drift|claims-owed@13
- 22:10 round:impl-drift|claims-owed@14
- 22:13 round:impl-drift|claims-owed@15
- 22:43 round:impl-drift|claims-owed@16

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 22 min | 14 min | 8 min | 2 | 12, 1, 8 |
| T02 | 9 min | 0 min | 9 min | 0 | 9 |
| T04 | 16 min | 0 min | 16 min | 0 | 16 |
| T05 | 34 min | 19 min | 15 min | 1 | 19, 15 |
| T06 | 17 min | 16 min | 1 min | 5 | 1, 6, 4, 3, 2, 1 |
| T07 | 48 min | 32 min | 16 min | 2 | 31, 1, 16 |
| T12 | 36 min | 5 min | 31 min | 1 | 5, 31 |
| T08 | 52 min | 44 min | 8 min | 1 | 44, 8 |
| T09 | 26 min | 0 min | 26 min | 0 | 26 |
| T11 | 4 min (open) | 0 min | 4 min | 0 | 4 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 16:43-16:55 | spec-fidelity-verify FAITHFUL | 36 | 10 | 2 | 0 | spec-fidelity-verify x1 (2 min) |
| T01 | 16:55-16:57 | spec-fidelity-verify FAITHFUL | 5 | 1 | 0 | 0 | spec-fidelity-verify x1 (1 min) |
| T01 | 16:57-17:05 | the tick or the last event | 1 | 1 | 7 | 0 | - |
| T02 | 17:19-17:28 | the tick or the last event | 11 | 6 | 3 | 0 | - |
| T04 | 18:49-19:05 | the tick or the last event | 25 | 13 | 3 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T05 | 19:10-19:29 | round-arbiter | 50 | 19 | 0 | 0 | escalation-check x1, round-arbiter x1 (1 min) |
| T05 | 19:29-19:44 | the tick or the last event | 55 | 8 | 7 | 0 | claims-triage x3, impl-drift x4 (4 min) |
| T06 | 19:47-19:47 | spec-fidelity CLEAR | 3 | 0 | 0 | 0 | spec-fidelity x1 (0 min) |
| T06 | 19:47-19:53 | spec-fidelity BLOCKED | 17 | 5 | 1 | 0 | impl-drift x1, spec-fidelity x1 (3 min) |
| T06 | 19:53-19:57 | spec-fidelity BLOCKED | 5 | 4 | 0 | 0 | spec-fidelity x1 (4 min) |
| T06 | 19:57-20:01 | spec-fidelity BLOCKED | 5 | 3 | 0 | 0 | spec-fidelity x1 (3 min) |
| T06 | 20:01-20:03 | round-arbiter CLEAR | 6 | 1 | 0 | 0 | round-arbiter x1 (1 min) |
| T06 | 20:03-20:03 | the tick or the last event | 1 | 0 | 1 | 0 | - |
| T07 | 20:04-20:35 | round-arbiter findings | 114 | 29 | 2 | 0 | claims-triage x1, impl-drift x4, round-arbiter x1 (4 min) |
| T07 | 20:35-20:36 | spec-fidelity CLEAR | 7 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T07 | 20:36-20:52 | the tick or the last event | 10 | 8 | 8 | 0 | - |
| T12 | 20:53-20:59 | round-arbiter findings | 13 | 5 | 0 | 0 | round-arbiter x1 (2 min) |
| T12 | 20:59-21:30 | the tick or the last event | 32 | 8 | 23 | 0 | claims-triage x1, impl-drift x3 (1 min) |
| T08 | 21:31-22:15 | round-arbiter findings | 93 | 42 | 3 | 0 | claims-triage x1, impl-drift x4, round-arbiter x1 (9 min) |
| T08 | 22:15-22:23 | the tick or the last event | 3 | 1 | 7 | 0 | - |
| T09 | 22:24-22:50 | the tick or the last event | 37 | 20 | 7 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T11 | 04:14-04:18 | the tick or the last event | 21 | 4 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 16:43 | started (`make task-start`) | |
| T01 | 16:55 | spec-fidelity-verify returned FAITHFUL (2 min) | |
| T01 | 16:57 | spec-fidelity-verify returned FAITHFUL (1 min) | |
| T01 | 17:05 | ticked | |
| T02 | 17:19 | started (`make task-start`) | |
| T02 | 17:28 | ticked | |
| T04 | 18:49 | started (`make task-start`) | |
| T04 | 18:57 | claims-triage returned (0 min) | |
| T04 | 18:58 | impl-drift returned findings (0 min) | |
| T04 | 19:05 | ticked | |
| T05 | 19:10 | started (`make task-start`) | |
| T05 | 19:29 | round-arbiter returned (0 min) | |
| T05 | 19:30 | escalation-check returned findings (1 min) | |
| T05 | 19:30 | claims-triage returned (0 min) | |
| T05 | 19:30 | impl-drift returned findings (0 min) | |
| T05 | 19:32 | claims-triage returned findings (0 min) | |
| T05 | 19:33 | impl-drift returned findings (1 min) | |
| T05 | 19:37 | impl-drift returned findings (0 min) | |
| T05 | 19:38 | claims-triage returned findings (0 min) | |
| T05 | 19:39 | impl-drift returned findings (1 min) | |
| T05 | 19:44 | ticked | |
| T06 | 19:47 | started (`make task-start`) | |
| T06 | 19:47 | spec-fidelity returned CLEAR (0 min) | |
| T06 | 19:47 | impl-drift returned findings (0 min) | |
| T06 | 19:53 | spec-fidelity returned BLOCKED (3 min) | |
| T06 | 19:57 | spec-fidelity returned BLOCKED (4 min) | |
| T06 | 20:01 | spec-fidelity returned BLOCKED (3 min) | |
| T06 | 20:03 | round-arbiter returned CLEAR (1 min) | |
| T06 | 20:03 | ticked | |
| T07 | 20:04 | started (`make task-start`) | |
| T07 | 20:27 | claims-triage returned (0 min) | |
| T07 | 20:28 | impl-drift returned findings (1 min) | |
| T07 | 20:29 | impl-drift returned findings (1 min) | |
| T07 | 20:33 | impl-drift returned findings (1 min) | |
| T07 | 20:34 | impl-drift returned findings (1 min) | |
| T07 | 20:35 | round-arbiter returned findings (1 min) | |
| T07 | 20:36 | spec-fidelity returned CLEAR (1 min) | |
| T07 | 20:52 | ticked | |
| T12 | 20:53 | started (`make task-start`) | |
| T12 | 20:59 | round-arbiter returned findings (2 min) | |
| T12 | 21:00 | claims-triage returned findings (0 min) | |
| T12 | 21:01 | impl-drift returned findings (1 min) | |
| T12 | 21:03 | impl-drift returned findings (1 min) | |
| T12 | 21:23 | impl-drift returned findings (0 min) | |
| T12 | 21:30 | ticked | |
| T08 | 21:31 | started (`make task-start`) | |
| T08 | 22:01 | claims-triage returned findings (1 min) | |
| T08 | 22:06 | impl-drift returned findings (4 min) | |
| T08 | 22:10 | impl-drift returned findings (1 min) | |
| T08 | 22:11 | impl-drift returned findings (2 min) | |
| T08 | 22:13 | impl-drift returned findings (0 min) | |
| T08 | 22:15 | round-arbiter returned findings (2 min) | |
| T08 | 22:23 | ticked | |
| T09 | 22:24 | started (`make task-start`) | |
| T09 | 22:43 | claims-triage returned (1 min) | |
| T09 | 22:44 | impl-drift returned findings (1 min) | |
| T09 | 22:50 | ticked | |
| T11 | 04:14 | started (`make task-start`) | |

## What each check cost, per changed line (2323 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 6 | 15 min | 2637k | 37.0k | 0.003 | 1.1k |
| spec-fidelity | 13 | 37 min | 1858k | 102.8k | 0.006 | 0.8k |
| impl-drift | 19 | 15 min | 1412k | 59.2k | 0.008 | 0.6k |
| escalation-check | 2 | 1 min | 206k | 6.9k | 0.001 | 0.1k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
