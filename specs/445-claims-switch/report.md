# Feature report - 445-claims-switch

Written by `make feature-report F=445` from 454 events (2026-10-28T14:30 to 2026-10-28T16:21 UTC), 9 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 01 min | 55% |
| waiting: a background run | 25 min | 23% |
| other tool | 10 min | 9% |
| waiting: spec-fidelity | 5 min | 5% |
| quick test | 3 min | 3% |
| waiting: spec-fidelity-verify | 3 min | 2% |
| waiting: round-arbiter | 2 min | 2% |
| test file | 1 min | 1% |
| waiting: escalation-check | 1 min | 1% |
| edit | 1 min | 1% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 47 subagent tool call(s) (of 190) are counted apart (0 by the subagent transcripts, 47 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 12 run(s), 15 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make hooks-test | 1 min |
| make task-start | 0 min |
| make claims-bundle | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 7 | CHANGES REQUIRED 1, CLEAR 6 |
| round-arbiter | 2 | findings 2 |
| claims-triage | 1 | - |
| escalation-check | 1 | findings 1 |
| impl-drift | 1 | findings 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 1 over 254 changed lines: cascade ratio 0.00
- tasks ticked: 3 of 4

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 29 min | 23 min | 5 min | 4 | 2, 1, 2, 18, 5 |
| T02 | 16 min | 1 min | 15 min | 1 | 1, 15 |
| T03 | 1 min | 1 min | 0 min | 1 | 1, 0 |
| T04 | 1 min (open) | 1 min | 0 min | 1 | 1, 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 15:31-15:34 | spec-fidelity CLEAR | 15 | 2 | 0 | 0 | spec-fidelity x1 (2 min) |
| T01 | 15:34-15:34 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (0 min) |
| T01 | 15:34-15:37 | spec-fidelity CLEAR | 9 | 1 | 1 | 0 | spec-fidelity x1 (1 min) |
| T01 | 15:37-15:55 | round-arbiter findings | 32 | 4 | 14 | 0 | impl-drift x1, round-arbiter x1 (2 min) |
| T01 | 15:55-16:00 | the tick or the last event | 3 | 0 | 5 | 0 | - |
| T02 | 16:01-16:01 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T02 | 16:01-16:17 | the tick or the last event | 24 | 15 | 0 | 0 | - |
| T03 | 16:17-16:18 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T03 | 16:18-16:18 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T04 | 16:20-16:21 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (0 min) |
| T04 | 16:21-16:21 | the tick or the last event | 0 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 15:31 | started (`make task-start`) | |
| T01 | 15:34 | spec-fidelity returned CLEAR (2 min) | |
| T01 | 15:34 | spec-fidelity returned CLEAR (0 min) | |
| T01 | 15:37 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 15:45 | impl-drift returned findings (0 min) | |
| T01 | 15:55 | part B written | |
| T01 | 15:55 | round-arbiter returned findings (2 min) | |
| T01 | 16:00 | ticked | |
| T02 | 16:01 | started (`make task-start`) | |
| T02 | 16:01 | spec-fidelity returned CLEAR (1 min) | |
| T02 | 16:17 | ticked | |
| T03 | 16:17 | started (`make task-start`) | |
| T03 | 16:18 | spec-fidelity returned CLEAR (1 min) | |
| T03 | 16:18 | ticked | |
| T04 | 16:20 | started (`make task-start`) | |
| T04 | 16:21 | spec-fidelity returned CLEAR (0 min) | |

## What each check cost, per changed line (254 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 7 | 9 min | 872k | 36.3k | 0.028 | 3.4k |
| spec-fidelity-verify | 1 | 3 min | 149k | 5.4k | 0.004 | 0.6k |
| escalation-check | 1 | 1 min | 57k | 2.9k | 0.004 | 0.2k |
| impl-drift | 1 | 0 min | 21k | 0.6k | 0.004 | 0.1k |

This report took 1.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
