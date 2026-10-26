# Feature report - 429-memory-rules-as-guards

Written by `make feature-report F=429` from 440 events (2026-10-26T13:36 to 2026-10-26T14:32 UTC), 9 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 28 min | 49% |
| other tool | 18 min | 32% |
| waiting: subagent | 5 min | 8% |
| waiting: spec-fidelity-verify | 2 min | 3% |
| writing the spec | 1 min | 2% |
| waiting: a background run | 1 min | 2% |
| waiting: the GM | 1 min | 1% |
| edit | 1 min | 1% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

The session's own time above; its 41 subagent tool call(s) (of 195) are counted apart (0 by the subagent transcripts, 41 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 22 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 9 min |
| make hooks-test | 5 min |
| make docs | 0 min |
| make static | 0 min |
| make guard-edit | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 7 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 3 |
| general-purpose | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 822 changed lines: cascade ratio 0.00
- tasks ticked: 7 of 7

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 0 min | 0 min | 0 min | 0 | 0 |
| T02 | 0 min | 0 min | 0 min | 0 | 0 |
| T03 | 0 min | 0 min | 0 min | 0 | 0 |
| T04 | 0 min | 0 min | 0 min | 0 | 0 |
| T05 | 0 min | 0 min | 0 min | 0 | 0 |
| T06 | 0 min | 0 min | 0 min | 0 | 0 |
| T07 | 0 min (open) | 0 min | 0 min | 0 | 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 14:09-14:10 | the tick or the last event | 4 | 0 | 0 | 0 | - |
| T02 | 14:09-14:10 | the tick or the last event | 2 | 0 | 0 | 0 | - |
| T03 | 14:09-14:10 | the tick or the last event | 2 | 0 | 0 | 0 | - |
| T04 | 14:09-14:10 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T05 | 14:09-14:10 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T06 | 14:09-14:10 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T07 | 14:32-14:32 | the tick or the last event | 1 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 14:09 | started (`make task-start`) | |
| T01 | 14:10 | ticked | |
| T02 | 14:09 | started (`make task-start`) | |
| T02 | 14:10 | ticked | |
| T03 | 14:09 | started (`make task-start`) | |
| T03 | 14:10 | ticked | |
| T04 | 14:09 | started (`make task-start`) | |
| T04 | 14:10 | ticked | |
| T05 | 14:09 | started (`make task-start`) | |
| T05 | 14:10 | ticked | |
| T06 | 14:09 | started (`make task-start`) | |
| T06 | 14:10 | ticked | |
| T07 | 14:32 | started (`make task-start`) | |

## What each check cost, per changed line (822 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 2 | 9 min | 902k | 20.2k | 0.002 | 1.1k |
| spec-fidelity | 5 | 9 min | 571k | 27.3k | 0.006 | 0.7k |

This report took 0.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
