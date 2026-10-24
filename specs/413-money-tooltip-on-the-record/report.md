# Feature report - 413-money-tooltip-on-the-record

Written by `make feature-report F=413` from 1339 events (2026-10-24T15:55 to 2026-10-24T17:43 UTC), 3 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 49 min | 45% |
| spec-kit step | 27 min | 25% |
| other tool | 17 min | 16% |
| waiting: a background run | 13 min | 12% |
| waiting: subagent | 1 min | 1% |
| writing the spec | 1 min | 1% |
| quick test | 1 min | 1% |
| test file | 0 min | 0% |
| edit | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| gate | 0 min | 0% |

The session's own time above; its 373 subagent tool call(s) (of 573) are counted apart (0 by the subagent transcripts, 373 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 16 run(s), 1 h 34 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make land | 10 min |
| make ledger-owed | 4 min |
| Bash | 3 min |
| make record-owed | 0 min |
| make record | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 9 | BLOCKED 4, CHANGES REQUIRED 1, CLEAR 3 |
| research-pass | 5 | findings 5 |
| spec-fidelity-verify | 2 | CHANGES REQUIRED 1, FAITHFUL 1 |
| general-purpose | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 4 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 931 changed lines: cascade ratio 0.00
- tasks ticked: 3 of 6

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 31 min | 3 min | 28 min | 1 | 3, 28 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 17:10-17:13 | spec-fidelity CLEAR | 9 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T01 | 17:13-17:41 | the tick or the last event | 23 | 17 | 11 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 17:10 | started (`make task-start`) | |
| T01 | 17:13 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 17:16 | research-pass returned findings (10 min) | |
| T01 | 17:17 | `make done` (0 min) | |
| T01 | 17:25 | `make done` (0 min) | |
| T01 | 17:41 | ticked | |

## What each check cost, per changed line (931 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 9 | 29 min | 1536k | 82.8k | 0.010 | 1.6k |
| spec-fidelity-verify | 2 | 1 min | 63k | 4.4k | 0.002 | 0.1k |

This report took 1.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
