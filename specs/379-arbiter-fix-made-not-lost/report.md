# Feature report - 379-arbiter-fix-made-not-lost

Written by `make feature-report F=379` from 1235 events (2026-10-10T23:17 to 2026-10-11T02:31 UTC), 31 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 1 h 37 min | 50% |
| thinking | 1 h 09 min | 36% |
| waiting: subagent | 6 min | 3% |
| quick test | 6 min | 3% |
| test file | 5 min | 3% |
| edit | 4 min | 2% |
| writing the spec | 3 min | 1% |
| waiting: the GM | 2 min | 1% |
| waiting: a background run | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make hooks-test | 46 min |
| Bash | 15 min |
| make append | 8 min |
| make guard-log | 1 min |
| make feature-report | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 16 | BLOCKED 4, CHANGES REQUIRED 1, CLEAR 3, FAITHFUL 1 |
| Explore | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 1, green 2
- spec rounds: CHANGES REQUIRED 5, FAITHFUL 3
- plan reviews BLOCKED: 4 recorded in commits, 4 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1043 changed lines: cascade ratio 0.00
- tasks ticked: 10 of 11

## Tripwires (FR-010) - what fired, or would have

- none

This report took 2.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
