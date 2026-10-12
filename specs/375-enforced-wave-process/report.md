# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 4276 events (2026-10-10T16:27 to 2026-10-12T12:49 UTC), 176 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 28 h 09 min | - |
| thinking | 7 h 49 min | 51% |
| other tool | 4 h 16 min | 28% |
| waiting: the GM | 1 h 35 min | 10% |
| waiting: subagent | 1 h 12 min | 8% |
| test file | 13 min | 1% |
| waiting: a background run | 9 min | 1% |
| edit | 5 min | 1% |
| spec-kit step | 3 min | 0% |
| writing the spec | 2 min | 0% |
| quick test | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 21 min |
| make hooks-test | 31 min |
| make docs | 10 min |
| make durations | 9 min |
| make land-tooling | 7 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 50 | BLOCKED 11, CHANGES REQUIRED 10, CLEAR 12, FAITHFUL 11, NOT-REVIEWABLE 2 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 9, red 4
- spec rounds: CHANGES REQUIRED 10, FAITHFUL 7
- plan reviews BLOCKED: 15 recorded in commits, 11 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 12765 changed lines: cascade ratio 0.00
- tasks ticked: 61 of 62

## Tripwires (FR-010) - what fired, or would have

- none

This report took 2.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
