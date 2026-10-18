# Feature report - 389-money-research-section

Written by `make feature-report F=389` from 240 events (2026-10-18T21:17 to 2026-10-18T21:47 UTC), 6 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 17 min | 56% |
| waiting: a background run | 6 min | 20% |
| other tool | 3 min | 11% |
| waiting: subagent | 2 min | 6% |
| writing the spec | 1 min | 2% |
| test file | 1 min | 2% |
| edit | 0 min | 1% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| quick test | 0 min | 0% |
| spec-kit step | 0 min | 0% |

The session's own time above; its 31 subagent tool call(s) (of 98) are counted apart (0 by the subagent transcripts, 31 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 14 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 3 min |
| make ledger-owed | 0 min |
| make record | 0 min |
| make impl-check | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity-verify | 4 | CHANGES REQUIRED 2, FAITHFUL 1, NOT-REVIEWABLE 1 |
| spec-fidelity | 3 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 3 changed lines: cascade ratio 0.00
- tasks ticked: 3 of 4

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (3 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 8 min | 591k | 26.0k | 1.000 | 197.0k |
| spec-fidelity-verify | 4 | 6 min | 297k | 12.3k | 1.333 | 99.0k |

This report took 0.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
