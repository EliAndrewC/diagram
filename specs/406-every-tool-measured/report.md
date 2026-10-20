# Feature report - 406-every-tool-measured

Written by `make feature-report F=406` from 565 events (2026-10-20T03:42 to 2026-10-20T04:54 UTC), 16 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 50 min | 70% |
| other tool | 17 min | 24% |
| test file | 2 min | 2% |
| edit | 1 min | 2% |
| waiting: subagent | 1 min | 1% |
| dispatching: spec review | 0 min | 1% |
| writing the spec | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |

The session's own time above; its 53 subagent tool call(s) (of 254) are counted apart (0 by the subagent transcripts, 53 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 9 run(s), 27 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 12 min |
| make guard-edit | 2 min |
| make fix-yield | 1 min |
| make ledger-owed | 0 min |
| make arbiter-bundle | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 8 | BLOCKED 3, CHANGES REQUIRED 1 |
| round-arbiter | 3 | findings 3 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 4 recorded in commits, 3 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 1763 changed lines: cascade ratio 0.00
- tasks ticked: 7 of 9

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (1763 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 17 min | 1174k | 59.0k | 0.002 | 0.7k |
| spec-fidelity-verify | 2 | 4 min | 167k | 8.7k | 0.001 | 0.1k |

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
