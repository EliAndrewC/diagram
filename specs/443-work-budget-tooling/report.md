# Feature report - 443-work-budget-tooling

Written by `make feature-report F=443` from 1703 events (2026-10-28T05:08 to 2026-10-28T19:24 UTC), 19 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 9 h 33 min | - |
| thinking | 1 h 23 min | 29% |
| waiting: a background run | 1 h 11 min | 25% |
| waiting: the GM | 52 min | 18% |
| other tool | 38 min | 13% |
| spec-kit step | 19 min | 7% |
| waiting: spec-fidelity | 6 min | 2% |
| waiting: work-budget | 4 min | 2% |
| test file | 2 min | 1% |
| waiting: round-arbiter | 2 min | 1% |
| edit | 1 min | 0% |
| waiting: escalation-check | 1 min | 0% |
| quick test | 1 min | 0% |
| waiting: impl-drift | 1 min | 0% |
| dispatching: spec review | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 183 subagent tool call(s) (of 736) are counted apart (0 by the subagent transcripts, 183 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 50 run(s), 57 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 20 min |
| make ledger-owed | 8 min |
| make cover-changed | 6 min |
| make hooks-test | 4 min |
| make land-tooling | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 18 | BLOCKED 2, CLEAR 14 |
| impl-drift | 9 | findings 9 |
| work-budget | 8 | findings 5 |
| claims-triage | 6 | findings 3 |
| escalation-check | 4 | clean 1, findings 3 |
| round-arbiter | 4 | CLEAR 1, findings 2 |
| general-purpose | 2 | findings 2 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1, FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-owed | 8 |
| claims-triage | claims-triage | 6 |
| work-budget | work-budget-budget-grid-placer | 5 |
| spec-fidelity | plan-443-work-budget-tooling-T09 | 2 |
| work-budget | work-budget-budget-funnel | 2 |

## Process signals

- gates: green 2
- spec rounds: none recorded
- plan reviews BLOCKED: 13 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 9 over 3963 changed lines: cascade ratio 0.00
- tasks ticked: 12 of 13

## Tripwires (FR-010) - what fired, or would have

- 13:51 round:impl-drift|claims-owed@3
- 13:53 round:impl-drift|claims-owed@4
- 14:15 round:impl-drift|claims-owed@5
- 14:28 round:impl-drift|claims-owed@6
- 15:21 round:impl-drift|claims-owed@7
- 17:36 round:impl-drift|claims-owed@8

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 8 h 13 min | 1 min | 8 h 12 min | 1 | 1, 492 |
| T09 | 22 min | 12 min | 11 min | 3 | 4, 5, 3, 11 |
| T10 | 20 min | 14 min | 6 min | 2 | 1, 13, 6 |
| T11 | 14 min | 9 min | 5 min | 2 | 3, 6, 5 |
| T12 | 13 min | 3 min | 10 min | 2 | 2, 1, 10 |
| T02 | 12 min | 1 min | 10 min | 1 | 1, 10 |
| T03 | 10 min | 1 min | 9 min | 1 | 1, 9 |
| T04 | 14 min | 1 min | 14 min | 1 | 1, 14 |
| T05 | 22 min | 14 min | 8 min | 4 | 1, 8, 2, 3, 8 |
| T06 | 3 min | 1 min | 2 min | 1 | 1, 2 |
| T07 | 10 min | 1 min | 9 min | 1 | 1, 9 |
| T13 | 2 min | 1 min | 2 min | 1 | 1, 2 |
| T08 | 1 min (open) | 1 min | 1 min | 1 | 1, 1 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 05:08-05:10 | spec-fidelity CLEAR | 8 | 1 | 0 | 0 | claims-triage x1, spec-fidelity x1 (1 min) |
| T01 | 05:10-13:22 | the tick or the last event | 32 | 17 | 12 | 463 | impl-drift x1 (0 min) |
| T09 | 13:22-13:26 | spec-fidelity BLOCKED | 9 | 2 | 2 | 0 | spec-fidelity x1 (4 min) |
| T09 | 13:26-13:31 | spec-fidelity BLOCKED | 28 | 5 | 0 | 0 | spec-fidelity x1 (5 min) |
| T09 | 13:31-13:34 | round-arbiter CLEAR | 8 | 3 | 0 | 0 | round-arbiter x1 (1 min) |
| T09 | 13:34-13:45 | the tick or the last event | 22 | 5 | 5 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T10 | 13:45-13:47 | spec-fidelity CLEAR | 7 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T10 | 13:47-13:59 | round-arbiter findings | 49 | 11 | 2 | 0 | claims-triage x2, impl-drift x3, round-arbiter x1 (4 min) |
| T10 | 13:59-14:05 | the tick or the last event | 5 | 1 | 6 | 0 | - |
| T11 | 14:06-14:09 | spec-fidelity CLEAR | 16 | 3 | 0 | 0 | escalation-check x1, spec-fidelity x1 (4 min) |
| T11 | 14:09-14:15 | spec-fidelity-verify CHANGES REQUIRED | 16 | 5 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity-verify x1 (4 min) |
| T11 | 14:15-14:20 | the tick or the last event | 2 | 0 | 4 | 0 | - |
| T12 | 14:21-14:23 | spec-fidelity CLEAR | 12 | 2 | 0 | 0 | escalation-check x1, spec-fidelity x1 (3 min) |
| T12 | 14:23-14:24 | spec-fidelity-verify FAITHFUL | 2 | 1 | 0 | 0 | - |
| T12 | 14:24-14:34 | the tick or the last event | 15 | 8 | 2 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T02 | 15:15-15:17 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T02 | 15:17-15:27 | the tick or the last event | 33 | 6 | 5 | 0 | impl-drift x1 (0 min) |
| T03 | 17:21-17:22 | spec-fidelity CLEAR | 8 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T03 | 17:22-17:31 | the tick or the last event | 30 | 6 | 3 | 0 | - |
| T04 | 17:32-17:33 | spec-fidelity CLEAR | 6 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T04 | 17:33-17:46 | the tick or the last event | 40 | 9 | 5 | 0 | impl-drift x1 (0 min) |
| T05 | 17:47-17:48 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T05 | 17:48-17:56 | spec-fidelity | 39 | 6 | 2 | 0 | escalation-check x1, general-purpose x2, spec-fidelity x1, work-budget x2 (6 min) |
| T05 | 17:56-17:58 | round-arbiter | 10 | 2 | 0 | 0 | round-arbiter x1, work-budget x1 (3 min) |
| T05 | 17:58-18:01 | round-arbiter findings | 10 | 1 | 2 | 0 | round-arbiter x1, work-budget x1 (2 min) |
| T05 | 18:01-18:10 | the tick or the last event | 14 | 3 | 5 | 0 | work-budget x1 (2 min) |
| T06 | 18:10-18:11 | spec-fidelity CLEAR | 6 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T06 | 18:11-18:13 | the tick or the last event | 7 | 2 | 0 | 0 | - |
| T07 | 18:14-18:15 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T07 | 18:15-18:24 | the tick or the last event | 23 | 9 | 0 | 0 | - |
| T13 | 19:16-19:17 | spec-fidelity CLEAR | 2 | 0 | 0 | 0 | spec-fidelity x1 (1 min) |
| T13 | 19:17-19:19 | the tick or the last event | 1 | 2 | 0 | 0 | - |
| T08 | 19:23-19:24 | spec-fidelity CLEAR | 8 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T08 | 19:24-19:24 | the tick or the last event | 2 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 05:08 | started (`make task-start`) | |
| T01 | 05:09 | claims-triage returned findings (0 min) | |
| T01 | 05:10 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 05:12 | impl-drift returned findings (0 min) | |
| T01 | 13:22 | ticked | |
| T09 | 13:22 | started (`make task-start`) | |
| T09 | 13:26 | spec-fidelity returned BLOCKED (4 min) | |
| T09 | 13:31 | spec-fidelity returned BLOCKED (5 min) | |
| T09 | 13:34 | round-arbiter returned CLEAR (1 min) | |
| T09 | 13:36 | claims-triage returned (0 min) | |
| T09 | 13:38 | impl-drift returned findings (1 min) | |
| T09 | 13:45 | ticked | |
| T10 | 13:45 | started (`make task-start`) | |
| T10 | 13:47 | spec-fidelity returned CLEAR (1 min) | |
| T10 | 13:51 | claims-triage returned findings (0 min) | |
| T10 | 13:52 | impl-drift returned findings (1 min) | |
| T10 | 13:54 | impl-drift returned findings (1 min) | |
| T10 | 13:54 | claims-triage returned (0 min) | |
| T10 | 13:58 | impl-drift returned findings (0 min) | |
| T10 | 13:59 | round-arbiter returned findings (1 min) | |
| T10 | 14:05 | ticked | |
| T11 | 14:06 | started (`make task-start`) | |
| T11 | 14:09 | spec-fidelity returned CLEAR (3 min) | |
| T11 | 14:10 | escalation-check returned findings (1 min) | |
| T11 | 14:13 | claims-triage returned (0 min) | |
| T11 | 14:15 | impl-drift returned findings (0 min) | |
| T11 | 14:15 | spec-fidelity-verify returned CHANGES REQUIRED (4 min) | |
| T11 | 14:20 | ticked | |
| T12 | 14:21 | started (`make task-start`) | |
| T12 | 14:23 | spec-fidelity returned CLEAR (2 min) | |
| T12 | 14:24 | escalation-check returned findings (1 min) | |
| T12 | 14:24 | spec-fidelity-verify returned FAITHFUL (3 min) | |
| T12 | 14:28 | claims-triage returned findings (0 min) | |
| T12 | 14:28 | impl-drift returned findings (0 min) | |
| T12 | 14:34 | ticked | |
| T02 | 15:15 | started (`make task-start`) | |
| T02 | 15:17 | spec-fidelity returned CLEAR (1 min) | |
| T02 | 15:21 | impl-drift returned findings (0 min) | |
| T02 | 15:27 | ticked | |
| T03 | 17:21 | started (`make task-start`) | |
| T03 | 17:22 | spec-fidelity returned CLEAR (1 min) | |
| T03 | 17:31 | ticked | |
| T04 | 17:32 | started (`make task-start`) | |
| T04 | 17:33 | spec-fidelity returned CLEAR (1 min) | |
| T04 | 17:36 | impl-drift returned findings (0 min) | |
| T04 | 17:46 | ticked | |
| T05 | 17:47 | started (`make task-start`) | |
| T05 | 17:48 | spec-fidelity returned CLEAR (1 min) | |
| T05 | 17:52 | general-purpose returned findings (0 min) | |
| T05 | 17:53 | escalation-check returned clean (0 min) | |
| T05 | 17:53 | general-purpose returned findings (1 min) | |
| T05 | 17:54 | work-budget returned (0 min) | |
| T05 | 17:56 | spec-fidelity returned (2 min) | |
| T05 | 17:56 | work-budget returned findings (3 min) | |
| T05 | 17:58 | round-arbiter returned (1 min) | |
| T05 | 17:59 | work-budget returned findings (1 min) | |
| T05 | 17:59 | work-budget returned findings (2 min) | |
| T05 | 18:01 | round-arbiter returned findings (1 min) | |
| T05 | 18:03 | work-budget returned findings (2 min) | |
| T05 | 18:10 | ticked | |
| T06 | 18:10 | started (`make task-start`) | |
| T06 | 18:11 | spec-fidelity returned CLEAR (1 min) | |
| T06 | 18:13 | ticked | |
| T07 | 18:14 | started (`make task-start`) | |
| T07 | 18:15 | spec-fidelity returned CLEAR (1 min) | |
| T07 | 18:24 | ticked | |
| T13 | 19:16 | started (`make task-start`) | |
| T13 | 19:17 | spec-fidelity returned CLEAR (1 min) | |
| T13 | 19:19 | ticked | |
| T08 | 19:23 | started (`make task-start`) | |
| T08 | 19:24 | spec-fidelity returned CLEAR (1 min) | |

## What each check cost, per changed line (3963 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 2 | 7 min | 4929k | 20.2k | 0.001 | 1.2k |
| spec-fidelity | 17 | 26 min | 1557k | 99.7k | 0.004 | 0.4k |
| impl-drift | 9 | 4 min | 449k | 22.7k | 0.002 | 0.1k |
| escalation-check | 4 | 3 min | 408k | 14.9k | 0.001 | 0.1k |
| work-budget | 1 | 2 min | 40k | 3.8k | 0.000 | 0.0k |

This report took 2.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
