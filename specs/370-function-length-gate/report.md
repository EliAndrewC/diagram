# Feature report - 370-function-length-gate

Written by `make feature-report F=370` from 1083 events (2026-10-10T18:22 to 2026-10-10T20:31 UTC), 31 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 23 min | 64% |
| other tool | 23 min | 18% |
| waiting: subagent | 10 min | 8% |
| edit | 5 min | 4% |
| test file | 4 min | 3% |
| waiting: the GM | 2 min | 2% |
| writing the spec | 1 min | 1% |
| waiting: a background run | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: impl-drift | 0 min | 0% |
| gate | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 13 min |
| make claims-checked | 3 min |
| make claims-owed | 2 min |
| make claims-bundle | 2 min |
| make map | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| impl-drift | 24 | findings 14 |
| spec-fidelity | 6 | CHANGES REQUIRED 2, CLEAR 2, FAITHFUL 1, NOT FAITHFUL 1 |
| perf-audit | 1 | - |
| round-arbiter | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-370-cover | 2 |
| impl-drift | claims-370-finish | 2 |
| impl-drift | claims-370-grove_fill | 2 |
| impl-drift | claims-370-paddy | 2 |
| impl-drift | claims-370-parcels | 2 |
| impl-drift | claims-370-stages | 2 |
| impl-drift | claims-370-stands | 2 |
| impl-drift | claims-370-touch | 2 |
| impl-drift | claims-370-web | 2 |
| impl-drift | claims-370c-stages | 2 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 0 returned
- reversals (A -> B -> A): 1 - CLAUDE.md 20:13
- check dispatches 24 over 2797 changed lines: cascade ratio 0.01
- tasks ticked: 17 of 20

## Tripwires (FR-010) - what fired, or would have

- 20:13 reversal:/diagram/.clones/diagram-grooming/CLAUDE.md

This report took 2.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
