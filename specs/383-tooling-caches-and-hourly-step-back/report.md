# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 3227 events (2026-10-13T03:21 to 2026-10-17T18:00 UTC), 88 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 99 h 24 min | - |
| thinking | 5 h 21 min | 48% |
| other tool | 3 h 55 min | 35% |
| waiting: the GM | 53 min | 8% |
| test file | 41 min | 6% |
| waiting: subagent | 18 min | 3% |
| edit | 4 min | 1% |
| writing the spec | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 21 min |
| make hooks-test | 26 min |
| make parts-sweep | 10 min |
| make collect-cost | 8 min |
| make test-full | 5 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 42 | BLOCKED 6, CHANGES REQUIRED 4, CLEAR 14, FAITHFUL 2, NOT-REVIEWABLE 1 |
| round-arbiter | 5 | CHANGES REQUIRED 1, CLEAR 1, findings 3 |
| impl-drift | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 16 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 5, green 3, red 2
- spec rounds: none recorded
- plan reviews BLOCKED: 16 recorded in commits, 6 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 7183 changed lines: cascade ratio 0.00
- tasks ticked: 37 of 38

## Tripwires (FR-010) - what fired, or would have

- none

This report took 2.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
