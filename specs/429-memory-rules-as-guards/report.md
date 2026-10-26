# Feature report - 429-memory-rules-as-guards

Written by `make feature-report F=429` from 311 events (2026-10-26T13:36 to 2026-10-26T14:10 UTC), 5 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 17 min | 50% |
| other tool | 12 min | 36% |
| waiting: spec-fidelity-verify | 2 min | 5% |
| writing the spec | 1 min | 3% |
| waiting: subagent | 1 min | 3% |
| edit | 1 min | 2% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |

The session's own time above; its 21 subagent tool call(s) (of 142) are counted apart (0 by the subagent transcripts, 21 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 16 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make hooks-test | 2 min |
| make static | 0 min |
| make guard-edit | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 721 changed lines: cascade ratio 0.00
- tasks ticked: 5 of 6

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 0 min (open) | 0 min | 0 min | 0 | 0 |
| T02 | 0 min (open) | 0 min | 0 min | 0 | 0 |
| T03 | 0 min (open) | 0 min | 0 min | 0 | 0 |
| T04 | 0 min (open) | 0 min | 0 min | 0 | 0 |
| T05 | 0 min (open) | 0 min | 0 min | 0 | 0 |
| T06 | 0 min (open) | 0 min | 0 min | 0 | 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 14:09-14:10 | the tick or the last event | 3 | 0 | 0 | 0 | - |
| T02 | 14:09-14:10 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T03 | 14:09-14:10 | the tick or the last event | 1 | 0 | 0 | 0 | - |
| T04 | 14:09-14:10 | the tick or the last event | 0 | 0 | 0 | 0 | - |
| T05 | 14:09-14:10 | the tick or the last event | 0 | 0 | 0 | 0 | - |
| T06 | 14:09-14:10 | the tick or the last event | 0 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 14:09 | started (`make task-start`) | |
| T02 | 14:09 | started (`make task-start`) | |
| T03 | 14:09 | started (`make task-start`) | |
| T04 | 14:09 | started (`make task-start`) | |
| T05 | 14:09 | started (`make task-start`) | |
| T06 | 14:09 | started (`make task-start`) | |

## What each check cost, per changed line (721 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 8 min | 509k | 23.8k | 0.006 | 0.7k |
| spec-fidelity-verify | 1 | 5 min | 262k | 8.9k | 0.001 | 0.4k |

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
