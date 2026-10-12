# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 1852 events (2026-10-10T16:27 to 2026-10-12T02:29 UTC), 99 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 24 h 56 min | - |
| thinking | 4 h 06 min | 49% |
| other tool | 2 h 43 min | 33% |
| waiting: the GM | 41 min | 8% |
| waiting: subagent | 35 min | 7% |
| waiting: a background run | 5 min | 1% |
| edit | 4 min | 1% |
| test file | 2 min | 0% |
| writing the spec | 2 min | 0% |
| gate | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 10 min |
| make hooks-test | 23 min |
| make docs | 10 min |
| make durations | 7 min |
| make check-closed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 16 | BLOCKED 5, CHANGES REQUIRED 3, CLEAR 4, FAITHFUL 2 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 6, red 3
- spec rounds: CHANGES REQUIRED 8, FAITHFUL 5
- plan reviews BLOCKED: 10 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 8759 changed lines: cascade ratio 0.00
- tasks ticked: 40 of 41

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
