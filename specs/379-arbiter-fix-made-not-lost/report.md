# Feature report - 379-arbiter-fix-made-not-lost

Written by `make feature-report F=379` from 1555 events (2026-10-10T23:17 to 2026-10-11T03:26 UTC), 40 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 1 h 56 min | 47% |
| thinking | 1 h 26 min | 35% |
| waiting: subagent | 13 min | 5% |
| waiting: the GM | 12 min | 5% |
| quick test | 6 min | 2% |
| edit | 6 min | 2% |
| test file | 5 min | 2% |
| writing the spec | 3 min | 1% |
| waiting: a background run | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make hooks-test | 46 min |
| Bash | 21 min |
| make append | 8 min |
| make guard-log | 1 min |
| make feature-report | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 19 | BLOCKED 4, CHANGES REQUIRED 2, CLEAR 4, FAITHFUL 1 |
| Explore | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 1, green 3
- spec rounds: CHANGES REQUIRED 6, FAITHFUL 4
- plan reviews BLOCKED: 4 recorded in commits, 4 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 2370 changed lines: cascade ratio 0.00
- tasks ticked: 12 of 12

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
