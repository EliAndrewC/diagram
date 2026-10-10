# Feature report - 378-research-findings-checked-against-code

Written by `make feature-report F=378` from 720 events (2026-10-10T21:44 to 2026-10-10T22:47 UTC), 11 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 30 min | 47% |
| gate | 21 min | 32% |
| other tool | 6 min | 9% |
| waiting: subagent | 3 min | 5% |
| test file | 2 min | 3% |
| edit | 1 min | 2% |
| writing the spec | 1 min | 1% |
| quick test | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: the GM | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 5 min |
| WebSearch | 2 min |
| WebFetch | 1 min |
| make claims-bundle | 0 min |
| make archive-find | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 10 | BLOCKED 1, CHANGES REQUIRED 3, CLEAR 1 |
| general-purpose | 4 | findings 1 |
| impl-drift | 3 | findings 3 |
| round-arbiter | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: red 3
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 3 over 413 changed lines: cascade ratio 0.01
- tasks ticked: 4 of 6

## Tripwires (FR-010) - what fired, or would have

- 22:25 red-gate
- 22:25 red-gate

This report took 0.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
