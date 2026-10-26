# Feature report - 425-all-page-opening

Written by `make feature-report F=425` from 33 events (2026-10-26T03:11 to 2026-10-26T03:12 UTC), 3 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 min | 46% |
| waiting: spec-fidelity | 0 min | 33% |
| other tool | 0 min | 19% |
| dispatching: spec review | 0 min | 2% |
| waiting: a background run | 0 min | 1% |

The session's own time above; its 7 subagent tool call(s) (of 12) are counted apart (0 by the subagent transcripts, 7 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 2 run(s), 1 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 2 | CLEAR 1, FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 10 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 1

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (10 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 1 min | 138k | 5.2k | 0.200 | 13.8k |

This report took 1.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
