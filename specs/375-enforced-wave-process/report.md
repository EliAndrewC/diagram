# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 3737 events (2026-10-10T16:27 to 2026-10-12T09:20 UTC), 154 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 26 h 08 min | - |
| thinking | 6 h 58 min | 50% |
| other tool | 3 h 51 min | 28% |
| waiting: the GM | 1 h 35 min | 11% |
| waiting: subagent | 1 h 05 min | 8% |
| test file | 9 min | 1% |
| waiting: a background run | 9 min | 1% |
| edit | 5 min | 1% |
| spec-kit step | 2 min | 0% |
| writing the spec | 2 min | 0% |
| quick test | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 06 min |
| make hooks-test | 27 min |
| make docs | 10 min |
| make durations | 9 min |
| make check-closed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 39 | BLOCKED 8, CHANGES REQUIRED 8, CLEAR 10, FAITHFUL 8, NOT-REVIEWABLE 1 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 9, red 4
- spec rounds: CHANGES REQUIRED 10, FAITHFUL 7
- plan reviews BLOCKED: 13 recorded in commits, 8 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 12169 changed lines: cascade ratio 0.00
- tasks ticked: 55 of 57

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
