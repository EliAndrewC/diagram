# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 825 events (2026-10-13T03:21 to 2026-10-13T04:39 UTC), 13 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 44 min | 57% |
| waiting: the GM | 16 min | 21% |
| other tool | 13 min | 17% |
| test file | 1 min | 2% |
| edit | 1 min | 1% |
| writing the spec | 1 min | 1% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 13 min |
| make step-back | 0 min |
| make append | 0 min |
| make ledger-owed | 0 min |
| make docs | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 6 | BLOCKED 2, CHANGES REQUIRED 1, CLEAR 1 |
| round-arbiter | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 1, green 1, red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 3030 changed lines: cascade ratio 0.00
- tasks ticked: 14 of 16

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
