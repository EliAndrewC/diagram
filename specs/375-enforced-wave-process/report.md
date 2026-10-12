# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 2140 events (2026-10-10T16:27 to 2026-10-12T03:32 UTC), 109 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 24 h 56 min | - |
| thinking | 4 h 27 min | 48% |
| other tool | 2 h 52 min | 31% |
| waiting: the GM | 1 h 11 min | 13% |
| waiting: subagent | 35 min | 6% |
| waiting: a background run | 7 min | 1% |
| edit | 4 min | 1% |
| test file | 3 min | 0% |
| writing the spec | 2 min | 0% |
| spec-kit step | 1 min | 0% |
| gate | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 18 min |
| make hooks-test | 24 min |
| make docs | 10 min |
| make durations | 7 min |
| make check-closed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 19 | BLOCKED 5, CHANGES REQUIRED 4, CLEAR 5, FAITHFUL 3 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 5, green 7, red 3
- spec rounds: CHANGES REQUIRED 9, FAITHFUL 6
- plan reviews BLOCKED: 10 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 9633 changed lines: cascade ratio 0.00
- tasks ticked: 43 of 44

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
