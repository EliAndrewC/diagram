# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 2649 events (2026-10-13T03:21 to 2026-10-17T16:01 UTC), 74 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 99 h 24 min | - |
| thinking | 4 h 10 min | 45% |
| other tool | 3 h 33 min | 38% |
| waiting: the GM | 44 min | 8% |
| test file | 30 min | 5% |
| waiting: subagent | 12 min | 2% |
| edit | 3 min | 1% |
| writing the spec | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 06 min |
| make hooks-test | 26 min |
| make parts-sweep | 10 min |
| make collect-cost | 8 min |
| make docs | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 37 | BLOCKED 5, CHANGES REQUIRED 4, CLEAR 11, FAITHFUL 1, NOT-REVIEWABLE 1 |
| round-arbiter | 4 | CHANGES REQUIRED 1, CLEAR 1, findings 2 |
| impl-drift | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 12 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 5, green 2, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 12 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 6227 changed lines: cascade ratio 0.00
- tasks ticked: 33 of 34

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
