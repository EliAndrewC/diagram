# Feature report - 375-enforced-wave-process

Written by `make feature-report F=375` from 345 events (2026-10-10T16:07 to 2026-10-10T16:52 UTC), 10 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 30 min | 68% |
| other tool | 9 min | 20% |
| waiting: spec-fidelity | 2 min | 5% |
| quick test | 2 min | 5% |
| test file | 0 min | 1% |
| edit | 0 min | 1% |
| writing the spec | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| gate | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 9 min |
| make gm-reviewed | 2 min |
| make feature-report | 0 min |
| make any | 0 min |
| make target | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 5 | BLOCKED 2, CHANGES REQUIRED 1, CLEAR 1, FAITHFUL 1 |
| claude-code-guide | 1 | findings 1 |
| general-purpose | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 2 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1478 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 8

This report took 0.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
