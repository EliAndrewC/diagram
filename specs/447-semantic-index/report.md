# Feature report - 447-semantic-index

Written by `make feature-report F=447` from 1003 events (2026-10-29T15:10 to 2026-10-30T21:00 UTC), 43 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 25 h 13 min | - |
| waiting: the GM | 2 h 18 min | 50% |
| other tool | 51 min | 19% |
| thinking | 46 min | 17% |
| waiting: research-pass | 13 min | 5% |
| waiting: spec-fidelity | 12 min | 4% |
| waiting: spec-fidelity-verify | 4 min | 1% |
| waiting: escalation-check | 4 min | 1% |
| edit | 3 min | 1% |
| waiting: general-purpose | 2 min | 1% |
| test file | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 209 subagent tool call(s) (of 439) are counted apart (0 by the subagent transcripts, 209 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 24 run(s), 52 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 13 min |
| make hooks-test | 4 min |
| make ledger-owed | 3 min |
| make docs | 0 min |
| make archive-find | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| escalation-check | 8 | findings 8 |
| spec-fidelity | 8 | CHANGES REQUIRED 3, FAITHFUL 1 |
| research-pass | 5 | findings 4 |
| general-purpose | 3 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | trial-review-447 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1130 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (1130 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 16 min | 1605k | 46.6k | 0.004 | 1.4k |
| escalation-check | 8 | 6 min | 578k | 27.7k | 0.007 | 0.5k |
| spec-fidelity-verify | 4 | 10 min | 504k | 27.7k | 0.004 | 0.4k |

This report took 2.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
