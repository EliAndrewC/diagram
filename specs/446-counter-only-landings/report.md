# Feature report - 446-counter-only-landings

Written by `make feature-report F=446` from 330 events (2026-10-28T16:34 to 2026-10-28T17:09 UTC), 3 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 17 min | 48% |
| waiting: a background run | 6 min | 18% |
| waiting: spec-fidelity | 5 min | 14% |
| other tool | 4 min | 11% |
| test file | 1 min | 3% |
| waiting: spec-fidelity-verify | 1 min | 2% |
| waiting: round-arbiter | 1 min | 2% |
| writing the spec | 0 min | 1% |
| quick test | 0 min | 1% |
| dispatching: spec review | 0 min | 0% |
| edit | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 41 subagent tool call(s) (of 148) are counted apart (0 by the subagent transcripts, 41 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 8 run(s), 12 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 3 min |
| make claims-owed | 0 min |
| make ledger-owed | 0 min |
| make task-start | 0 min |
| make plan-delta | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 6 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 4 |
| round-arbiter | 1 | findings 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 495 changed lines: cascade ratio 0.00
- tasks ticked: 2 of 3

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 7 min | 1 min | 6 min | 1 | 1, 6 |
| T02 | 12 min | 1 min | 11 min | 1 | 1, 11 |
| T03 | 1 min (open) | 0 min | 0 min | 1 | 0, 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 16:49-16:50 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T01 | 16:50-16:56 | the tick or the last event | 2 | 3 | 3 | 0 | - |
| T02 | 16:56-16:57 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T02 | 16:57-17:08 | the tick or the last event | 30 | 8 | 3 | 0 | - |
| T03 | 17:08-17:09 | spec-fidelity CLEAR | 2 | 0 | 0 | 0 | spec-fidelity x1 (0 min) |
| T03 | 17:09-17:09 | the tick or the last event | 0 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 16:49 | started (`make task-start`) | |
| T01 | 16:50 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 16:56 | ticked | |
| T02 | 16:56 | started (`make task-start`) | |
| T02 | 16:57 | spec-fidelity returned CLEAR (1 min) | |
| T02 | 17:08 | ticked | |
| T03 | 17:08 | started (`make task-start`) | |
| T03 | 17:09 | spec-fidelity returned CLEAR (0 min) | |

## What each check cost, per changed line (495 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 6 | 9 min | 1174k | 36.3k | 0.012 | 2.4k |
| spec-fidelity-verify | 1 | 2 min | 112k | 7.2k | 0.002 | 0.2k |

This report took 1.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
