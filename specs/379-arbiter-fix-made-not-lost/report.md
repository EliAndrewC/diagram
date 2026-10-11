# Feature report - 379-arbiter-fix-made-not-lost

Written by `make feature-report F=379` from 329 events (2026-10-10T23:17 to 2026-10-11T00:12 UTC), 7 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 34 min | 62% |
| thinking | 12 min | 23% |
| quick test | 6 min | 10% |
| edit | 2 min | 4% |
| writing the spec | 0 min | 1% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: the GM | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make hooks-test | 19 min |
| Bash | 5 min |
| make append | 3 min |
| make guard-log | 0 min |
| make map | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 3 | CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: green 1
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 304 changed lines: cascade ratio 0.00
- tasks ticked: 5 of 5

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
