# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 4094 events (2026-10-10T16:27 to 2026-10-12T12:22 UTC), 165 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 28 h 09 min | - |
| thinking | 7 h 29 min | 50% |
| other tool | 4 h 14 min | 28% |
| waiting: the GM | 1 h 35 min | 11% |
| waiting: subagent | 1 h 09 min | 8% |
| test file | 10 min | 1% |
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
| Bash | 2 h 18 min |
| make hooks-test | 31 min |
| make docs | 10 min |
| make durations | 9 min |
| make land-tooling | 7 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 45 | BLOCKED 10, CHANGES REQUIRED 9, CLEAR 11, FAITHFUL 9, NOT-REVIEWABLE 1 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 9, red 4
- spec rounds: CHANGES REQUIRED 10, FAITHFUL 7
- plan reviews BLOCKED: 14 recorded in commits, 10 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 12616 changed lines: cascade ratio 0.00
- tasks ticked: 59 of 60

## Tripwires (FR-010) - what fired, or would have

- none

This report took 2.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
