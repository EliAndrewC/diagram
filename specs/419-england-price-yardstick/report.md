# Feature report - 419-england-price-yardstick

Written by `make feature-report F=419` from 479 events (2026-10-25T11:04 to 2026-10-25T11:46 UTC), 16 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 42 min | 57% |
| thinking | 25 min | 34% |
| waiting: source-applicability | 2 min | 3% |
| waiting: record-format | 1 min | 1% |
| test file | 1 min | 1% |
| waiting: source-reader | 1 min | 1% |
| writing the spec | 1 min | 1% |
| waiting: subagent | 0 min | 1% |
| edit | 0 min | 1% |
| waiting: intro-check | 0 min | 0% |
| waiting: quote-check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 50 subagent tool call(s) (of 220) are counted apart (0 by the subagent transcripts, 50 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 15 run(s), 14 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 min |
| make record | 2 min |
| make source-outcome | 1 min |
| make apply-edits | 0 min |
| make reserve | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| record-format | 4 | findings 4 |
| source-applicability | 3 | findings 3 |
| spec-fidelity | 3 | CHANGES REQUIRED 1, CLEAR 1 |
| intro-check | 2 | findings 2 |
| source-reader | 2 | findings 2 |
| quote-check | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| intro-check | intro-0297 | 2 |
| record-format | q-0291 | 2 |
| record-format | q-0297 | 2 |
| source-applicability | key-clark-2006-gpih-england-prices-wages | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 12 over 131 changed lines: cascade ratio 0.09
- tasks ticked: 2 of 4

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 1 min | 0 min | 1 min | 0 | 1 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 11:44-11:45 | the tick or the last event | 0 | 1 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 11:44 | started (`make task-start`) | |
| T01 | 11:45 | ticked | |

## What each check cost, per changed line (131 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 4 min | 404k | 12.8k | 0.015 | 3.1k |
| spec-fidelity-verify | 1 | 1 min | 65k | 3.0k | 0.008 | 0.5k |

This report took 2.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
