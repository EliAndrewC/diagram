# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 3143 events (2026-10-10T16:27 to 2026-10-12T06:53 UTC), 133 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 24 h 56 min | - |
| thinking | 6 h 14 min | 49% |
| other tool | 3 h 34 min | 28% |
| waiting: the GM | 1 h 35 min | 12% |
| waiting: subagent | 56 min | 7% |
| waiting: a background run | 7 min | 1% |
| test file | 7 min | 1% |
| edit | 4 min | 1% |
| spec-kit step | 2 min | 0% |
| writing the spec | 2 min | 0% |
| quick test | 1 min | 0% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 55 min |
| make hooks-test | 27 min |
| make docs | 10 min |
| make durations | 9 min |
| make check-closed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 29 | BLOCKED 7, CHANGES REQUIRED 6, CLEAR 8, FAITHFUL 5, NOT-REVIEWABLE 1 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 8, red 3
- spec rounds: CHANGES REQUIRED 10, FAITHFUL 7
- plan reviews BLOCKED: 12 recorded in commits, 7 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 11290 changed lines: cascade ratio 0.00
- tasks ticked: 49 of 51

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
