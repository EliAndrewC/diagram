# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 1346 events (2026-10-13T03:21 to 2026-10-13T12:37 UTC), 27 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 5 h 27 min | - |
| thinking | 1 h 37 min | 43% |
| other tool | 1 h 30 min | 39% |
| waiting: the GM | 27 min | 12% |
| test file | 9 min | 4% |
| waiting: subagent | 3 min | 1% |
| edit | 1 min | 1% |
| writing the spec | 1 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| gate | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 34 min |
| make docs | 3 min |
| make land-tooling | 3 min |
| make step-back | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 18 | BLOCKED 3, CHANGES REQUIRED 1, CLEAR 5, FAITHFUL 1, NOT-REVIEWABLE 1 |
| impl-drift | 2 | findings 1 |
| round-arbiter | 2 | CHANGES REQUIRED 1, findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 3 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 2, green 2, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 5 recorded in commits, 3 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 3825 changed lines: cascade ratio 0.00
- tasks ticked: 17 of 19

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
