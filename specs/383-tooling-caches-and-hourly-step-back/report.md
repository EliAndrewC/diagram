# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 2324 events (2026-10-13T03:21 to 2026-10-17T13:56 UTC), 62 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 99 h 24 min | - |
| thinking | 3 h 19 min | 46% |
| other tool | 2 h 36 min | 36% |
| waiting: the GM | 41 min | 10% |
| test file | 21 min | 5% |
| waiting: subagent | 9 min | 2% |
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
| Bash | 1 h 17 min |
| make hooks-test | 15 min |
| make docs | 3 min |
| make land-tooling | 3 min |
| make ledger-owed | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 33 | BLOCKED 5, CHANGES REQUIRED 3, CLEAR 10, FAITHFUL 1, NOT-REVIEWABLE 1 |
| round-arbiter | 3 | CHANGES REQUIRED 1, CLEAR 1, findings 1 |
| impl-drift | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 11 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 4, green 2, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 11 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 5682 changed lines: cascade ratio 0.00
- tasks ticked: 29 of 30

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
