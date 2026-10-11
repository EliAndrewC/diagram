# Feature report - 352-village-lane-ever-run-between-house

Written by `make feature-report F=352` from 1831 events (2026-10-11T06:39 to 2026-10-11T10:14 UTC), 27 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 3 h 24 min | - |
| thinking | 2 h 16 min | 60% |
| other tool | 1 h 08 min | 30% |
| waiting: the GM | 15 min | 7% |
| waiting: subagent | 3 min | 1% |
| edit | 2 min | 1% |
| writing the spec | 1 min | 0% |
| dispatching: record check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| gate | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 46 min |
| make modal-bundle | 5 min |
| make record | 2 min |
| make record-owed | 2 min |
| make check-bundle | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 16 | clean 4, findings 12 |
| modal-research | 14 | clean 1, findings 13 |
| modal-form | 7 | findings 7 |
| spec-fidelity | 5 | CHANGES REQUIRED 1, CLEAR 1 |
| impl-drift | 4 | findings 4 |
| general-purpose | 3 | findings 2 |
| round-arbiter | 3 | findings 3 |
| source-reader | 3 | findings 2 |
| quote-check | 2 | findings 2 |
| record-format | 2 | findings 2 |
| source-applicability | 2 | findings 2 |
| translation-check | 2 | FAITHFUL 2 |
| entry-drift | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| general-purpose | modal-triage | 2 |
| round-arbiter | arbiter-batch | 2 |

## Process signals

- gates: green 1
- spec rounds: CHANGES REQUIRED 2, FAITHFUL 1
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 53 over 660 changed lines: cascade ratio 0.08
- tasks ticked: 3 of 5

## Tripwires (FR-010) - what fired, or would have

- none

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
