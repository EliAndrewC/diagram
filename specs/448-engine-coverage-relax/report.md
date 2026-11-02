# Feature report - 448-engine-coverage-relax

Written by `make feature-report F=448` from 513 events (2026-11-02T06:52 to 2026-11-02T13:03 UTC), 11 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 3 h 47 min | - |
| waiting: subagent | 58 min | 40% |
| thinking | 35 min | 24% |
| waiting: a background run | 22 min | 15% |
| other tool | 19 min | 13% |
| waiting: spec-fidelity-verify | 5 min | 3% |
| waiting: spec-fidelity | 3 min | 2% |
| edit | 1 min | 1% |
| writing the spec | 1 min | 1% |
| test file | 1 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| gate | 0 min | 0% |

The session's own time above; its 44 subagent tool call(s) (of 232) are counted apart (0 by the subagent transcripts, 44 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 10 run(s), 25 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 17 min |
| make plan-delta | 0 min |
| make docs | 0 min |
| make claims-triage | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 11 | BLOCKED 3, CHANGES REQUIRED 1, CLEAR 3 |
| impl-drift | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-l7r-diagram-invocation-py-operations-invocation-guard | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 4 recorded in commits, 3 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 696 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 2

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 1 h 17 min (open) | 38 min | 38 min | 9 | 3, 6, 2, 15, 0, 4, 3, 2, 2, 38 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 11:46-11:49 | spec-fidelity BLOCKED | 11 | 3 | 0 | 0 | - |
| T01 | 11:49-11:55 | spec-fidelity BLOCKED | 33 | 6 | 0 | 0 | spec-fidelity x1 (4 min) |
| T01 | 11:55-11:58 | spec-fidelity CLEAR | 9 | 2 | 0 | 0 | spec-fidelity x1 (2 min) |
| T01 | 11:58-12:13 | spec-fidelity CHANGES REQUIRED | 42 | 13 | 2 | 0 | impl-drift x1, spec-fidelity x2 (7 min) |
| T01 | 12:13-12:13 | spec-fidelity BLOCKED | 2 | 0 | 0 | 0 | - |
| T01 | 12:13-12:17 | spec-fidelity CLEAR | 16 | 4 | 1 | 0 | spec-fidelity x1, spec-fidelity-verify x1 (6 min) |
| T01 | 12:17-12:21 | spec-fidelity-verify CHANGES REQUIRED | 2 | 0 | 3 | 0 | - |
| T01 | 12:21-12:22 | spec-fidelity CLEAR | 6 | 1 | 1 | 0 | spec-fidelity x1, spec-fidelity-verify x1 (4 min) |
| T01 | 12:22-12:24 | spec-fidelity-verify FAITHFUL | 0 | 0 | 2 | 0 | - |
| T01 | 12:24-13:03 | the tick or the last event | 14 | 14 | 25 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 11:46 | started (`make task-start`) | |
| T01 | 11:49 | spec-fidelity returned BLOCKED (3 min) | |
| T01 | 11:55 | spec-fidelity returned BLOCKED (4 min) | |
| T01 | 11:58 | spec-fidelity returned CLEAR (2 min) | |
| T01 | 11:58 | impl-drift returned findings (0 min) | |
| T01 | 12:13 | spec-fidelity returned CHANGES REQUIRED (4 min) | |
| T01 | 12:13 | spec-fidelity returned BLOCKED (3 min) | |
| T01 | 12:17 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 12:21 | spec-fidelity-verify returned CHANGES REQUIRED (4 min) | |
| T01 | 12:22 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 12:24 | spec-fidelity-verify returned FAITHFUL (3 min) | |
| T01 | 12:35 | `make done` (0 min) | |

## What each check cost, per changed line (696 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 7 | 18 min | 995k | 54.9k | 0.010 | 1.4k |
| spec-fidelity-verify | 2 | 7 min | 460k | 16.4k | 0.003 | 0.7k |
| impl-drift | 1 | 0 min | 22k | 0.5k | 0.001 | 0.0k |

This report took 2.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
