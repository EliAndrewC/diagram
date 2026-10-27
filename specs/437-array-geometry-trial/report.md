# Feature report - 437-array-geometry-trial

Written by `make feature-report F=437` from 147 events (2026-10-27T20:54 to 2026-10-27T21:11 UTC), 14 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 9 min | 54% |
| waiting: spec-fidelity-verify | 4 min | 21% |
| other tool | 2 min | 10% |
| waiting: a background run | 2 min | 9% |
| test file | 1 min | 5% |
| dispatching: spec review | 0 min | 1% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 18 subagent tool call(s) (of 65) are counted apart (0 by the subagent transcripts, 18 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 12 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make phase-calls | 1 min |
| Bash | 1 min |
| make perf-profile | 0 min |
| make ledger-owed | 0 min |
| make feature-report | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity-verify | 3 | CHANGES REQUIRED 2 |
| round-arbiter | 1 | CHANGES REQUIRED 1 |
| spec-fidelity | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 117 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (117 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity-verify | 2 | 7 min | 298k | 22.2k | 0.017 | 2.5k |
| spec-fidelity | 1 | 3 min | 192k | 9.2k | 0.009 | 1.6k |

This report took 0.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
