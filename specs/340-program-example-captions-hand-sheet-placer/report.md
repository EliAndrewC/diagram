# Feature report - 340-program-example-captions-hand-sheet-placer

Written by `make feature-report F=340` from 474 events (2026-10-11T08:43 to 2026-10-11T10:07 UTC), 17 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 51 min | 60% |
| waiting: the GM | 13 min | 15% |
| other tool | 10 min | 12% |
| test file | 4 min | 5% |
| waiting: subagent | 3 min | 3% |
| writing the spec | 1 min | 2% |
| waiting: a background run | 1 min | 1% |
| edit | 1 min | 1% |
| dispatching: review check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 10 min |
| make cov-file | 2 min |
| make map | 0 min |
| make spec-harness | 0 min |
| make claims-checked | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 6 | BLOCKED 4, CHANGES REQUIRED 1, CLEAR 1 |
| building-review | 2 | PASS 1 |
| impl-drift | 1 | findings 1 |
| spec-fidelity-verify | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 1, green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 4 recorded in commits, 4 returned
- reversals (A -> B -> A): 0
- check dispatches 3 over 659 changed lines: cascade ratio 0.00
- tasks ticked: 3 of 4

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
