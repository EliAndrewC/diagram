# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 4122 events (2026-10-13T03:21 to 2026-10-17T20:29 UTC), 132 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 99 h 24 min | - |
| thinking | 6 h 34 min | 48% |
| other tool | 4 h 33 min | 33% |
| waiting: the GM | 1 h 23 min | 10% |
| test file | 43 min | 5% |
| waiting: subagent | 22 min | 3% |
| edit | 5 min | 1% |
| writing the spec | 1 min | 0% |
| dispatching: spec review | 1 min | 0% |
| spec-kit step | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| quick test | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 40 min |
| make hooks-test | 35 min |
| make parts-sweep | 10 min |
| make collect-cost | 8 min |
| make test-full | 5 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 54 | BLOCKED 7, CHANGES REQUIRED 4, CLEAR 19, FAITHFUL 4, NOT-REVIEWABLE 1 |
| round-arbiter | 6 | CHANGES REQUIRED 1, CLEAR 1, findings 4 |
| general-purpose | 2 | - |
| impl-drift | 2 | findings 1 |
| claude-code-guide | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 22 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 5, green 3, red 2
- spec rounds: none recorded
- plan reviews BLOCKED: 22 recorded in commits, 7 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 10695 changed lines: cascade ratio 0.00
- tasks ticked: 51 of 52

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
