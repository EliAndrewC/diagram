# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 1070 events (2026-10-10T16:27 to 2026-10-10T23:17 UTC), 65 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 3 h 07 min | 51% |
| other tool | 1 h 55 min | 32% |
| waiting: subagent | 35 min | 10% |
| waiting: the GM | 20 min | 5% |
| waiting: a background run | 3 min | 1% |
| edit | 3 min | 1% |
| test file | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| writing the spec | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 41 min |
| make hooks-test | 21 min |
| make docs | 10 min |
| make durations | 7 min |
| make check-closed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 5 | BLOCKED 3, CLEAR 2 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 2, green 5, red 3
- spec rounds: CHANGES REQUIRED 3, FAITHFUL 2
- plan reviews BLOCKED: 6 recorded in commits, 3 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 7003 changed lines: cascade ratio 0.00
- tasks ticked: 29 of 30

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
