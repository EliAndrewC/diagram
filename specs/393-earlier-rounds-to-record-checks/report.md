# Feature report - 393-earlier-rounds-to-record-checks

Written by `make feature-report F=393` from 207 events (2026-10-19T00:21 to 2026-10-19T00:40 UTC), 4 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 11 min | 59% |
| other tool | 6 min | 31% |
| writing the spec | 1 min | 6% |
| edit | 1 min | 4% |
| test file | 0 min | 1% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| quick test | 0 min | 0% |
| waiting: a background run | 0 min | 0% |

The session's own time above; its 25 subagent tool call(s) (of 90) are counted apart (0 by the subagent transcripts, 25 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 8 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 6 min |
| make ledger-owed | 0 min |
| SendMessage | 0 min |
| Read | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 356 changed lines: cascade ratio 0.00
- tasks ticked: 2 of 3

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (356 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 6 min | 624k | 21.9k | 0.006 | 1.8k |
| spec-fidelity-verify | 2 | 2 min | 202k | 9.3k | 0.006 | 0.6k |

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
