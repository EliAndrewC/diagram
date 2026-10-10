# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 1322 events (2026-10-10T16:07 to 2026-10-10T19:55 UTC), 47 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 09 min | 57% |
| other tool | 51 min | 22% |
| waiting: subagent | 19 min | 8% |
| waiting: a background run | 17 min | 7% |
| waiting: the GM | 4 min | 2% |
| waiting: spec-fidelity | 2 min | 1% |
| edit | 2 min | 1% |
| quick test | 2 min | 1% |
| test file | 1 min | 0% |
| writing the spec | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| gate | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 44 min |
| make durations | 7 min |
| make replay-owing | 5 min |
| make check-closed | 4 min |
| make preflight | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 10 | BLOCKED 5, CHANGES REQUIRED 1, CLEAR 3, FAITHFUL 1 |
| general-purpose | 2 | - |
| claude-code-guide | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: already-verified 2, green 4, red 3
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 5 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 6471 changed lines: cascade ratio 0.00
- tasks ticked: 20 of 27

## Tripwires (FR-010) - what fired, or would have

- none

This report took 0.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
