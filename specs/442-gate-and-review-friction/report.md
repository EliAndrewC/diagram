# Feature report - 442-gate-and-review-friction

Written by `make feature-report F=442` from 163 events (2026-10-28T02:51 to 2026-10-28T03:08 UTC), 6 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 12 min | 70% |
| other tool | 4 min | 21% |
| quick test | 1 min | 5% |
| waiting: spec-fidelity | 0 min | 2% |
| dispatching: spec review | 0 min | 2% |
| test file | 0 min | 0% |

The session's own time above; its 35 subagent tool call(s) (of 76) are counted apart (0 by the subagent transcripts, 35 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 9 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make task-start | 4 min |
| Bash | 2 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 3 | CHANGES REQUIRED 1, CLEAR 2 |
| spec-fidelity-verify | 2 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 405 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 1

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 6 min (open) | 6 min | 0 min | 2 | 1, 5, 0 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 03:02-03:03 | spec-fidelity CLEAR | 0 | 1 | 0 | 0 | - |
| T01 | 03:03-03:08 | spec-fidelity CLEAR | 6 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T01 | 03:08-03:08 | the tick or the last event | 0 | 0 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 03:02 | started (`make task-start`) | |
| T01 | 03:03 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 03:08 | spec-fidelity returned CLEAR (1 min) | |

## What each check cost, per changed line (405 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 8 min | 1334k | 28.0k | 0.007 | 3.3k |
| spec-fidelity-verify | 1 | 1 min | 54k | 3.3k | 0.002 | 0.1k |

This report took 1.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
