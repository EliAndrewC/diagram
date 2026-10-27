# Feature report - 436-perf-ab-quick-first

Written by `make feature-report F=436` from 166 events (2026-10-27T19:27 to 2026-10-27T19:53 UTC), 10 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 11 min | 40% |
| other tool | 8 min | 29% |
| waiting: subagent | 3 min | 12% |
| waiting: spec-fidelity | 3 min | 10% |
| waiting: spec-fidelity-verify | 2 min | 7% |
| quick test | 0 min | 1% |
| test file | 0 min | 1% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| edit | 0 min | 0% |

The session's own time above; its 16 subagent tool call(s) (of 69) are counted apart (0 by the subagent transcripts, 16 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 7 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make claims-checked | 6 min |
| Bash | 1 min |
| make perf-ab | 0 min |
| make ledger-owed | 0 min |
| make claims-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 3 | CHANGES REQUIRED 1, CLEAR 2 |
| spec-fidelity-verify | 3 | CHANGES REQUIRED 1, FAITHFUL 2 |
| impl-drift | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 1 over 548 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 1

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 19 min (open) | 5 min | 14 min | 3 | 1, 4, 1, 14 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 19:34-19:35 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T01 | 19:35-19:38 | spec-fidelity-verify CHANGES REQUIRED | 13 | 2 | 1 | 0 | spec-fidelity-verify x1 (1 min) |
| T01 | 19:38-19:39 | spec-fidelity-verify FAITHFUL | 3 | 0 | 0 | 0 | spec-fidelity-verify x1 (0 min) |
| T01 | 19:39-19:53 | the tick or the last event | 7 | 11 | 3 | 0 | impl-drift x1 (0 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 19:34 | started (`make task-start`) | |
| T01 | 19:35 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 19:38 | spec-fidelity-verify returned CHANGES REQUIRED (1 min) | |
| T01 | 19:39 | spec-fidelity-verify returned FAITHFUL (0 min) | |
| T01 | 19:46 | impl-drift returned findings (0 min) | |

## What each check cost, per changed line (548 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 4 min | 309k | 17.5k | 0.005 | 0.6k |
| spec-fidelity-verify | 3 | 2 min | 145k | 9.2k | 0.005 | 0.3k |
| impl-drift | 1 | 0 min | 20k | 0.4k | 0.002 | 0.0k |

This report took 2.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
