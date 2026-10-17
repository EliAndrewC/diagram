# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 4505 events (2026-10-13T03:21 to 2026-10-17T23:22 UTC), 145 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 101 h 22 min | - |
| thinking | 6 h 59 min | 48% |
| other tool | 4 h 56 min | 34% |
| waiting: the GM | 1 h 23 min | 9% |
| test file | 44 min | 5% |
| waiting: subagent | 26 min | 3% |
| edit | 5 min | 1% |
| quick test | 2 min | 0% |
| dispatching: spec review | 1 min | 0% |
| writing the spec | 1 min | 0% |
| spec-kit step | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 59 min |
| make hooks-test | 37 min |
| make parts-sweep | 10 min |
| make collect-cost | 8 min |
| make test-full | 5 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 60 | BLOCKED 7, CHANGES REQUIRED 6, CLEAR 21, FAITHFUL 5, NOT-REVIEWABLE 1 |
| round-arbiter | 6 | CHANGES REQUIRED 1, CLEAR 1, findings 4 |
| general-purpose | 2 | - |
| impl-drift | 2 | findings 1 |
| claude-code-guide | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 24 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 5, green 3, red 2
- spec rounds: none recorded
- plan reviews BLOCKED: 23 recorded in commits, 7 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 11731 changed lines: cascade ratio 0.00
- tasks ticked: 56 of 58

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (11731 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 40 | 1 h 24 min | 11353k | 269.1k | 0.003 | 1.0k |
| spec-fidelity-verify | 17 | 31 min | 2093k | 89.9k | 0.001 | 0.2k |
| impl-drift | 1 | 0 min | 22k | 0.9k | 0.000 | 0.0k |

This report took 2.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
