# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 1765 events (2026-10-13T03:21 to 2026-10-13T14:04 UTC), 38 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 5 h 27 min | - |
| thinking | 2 h 36 min | 49% |
| other tool | 1 h 44 min | 33% |
| waiting: the GM | 30 min | 9% |
| test file | 16 min | 5% |
| waiting: subagent | 6 min | 2% |
| edit | 2 min | 1% |
| writing the spec | 1 min | 0% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 44 min |
| make land-tooling | 3 min |
| make docs | 3 min |
| make step-back | 0 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 25 | BLOCKED 4, CHANGES REQUIRED 2, CLEAR 6, FAITHFUL 1, NOT-REVIEWABLE 1 |
| impl-drift | 2 | findings 1 |
| round-arbiter | 2 | CHANGES REQUIRED 1, findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 5 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 3, green 2, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 6 recorded in commits, 4 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 4290 changed lines: cascade ratio 0.00
- tasks ticked: 22 of 24

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
