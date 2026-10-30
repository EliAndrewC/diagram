# Feature report - 447-semantic-index

Written by `make feature-report F=447` from 177 events (2026-10-29T15:10 to 2026-10-30T00:30 UTC), 8 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 8 h 16 min | - |
| other tool | 33 min | 52% |
| thinking | 15 min | 23% |
| waiting: the GM | 9 min | 15% |
| waiting: spec-fidelity | 4 min | 6% |
| edit | 1 min | 2% |
| writing the spec | 1 min | 1% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 7 subagent tool call(s) (of 84) are counted apart (0 by the subagent transcripts, 7 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 1 run(s), 4 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make hooks-test | 4 min |
| Bash | 4 min |
| make guard-edit | 0 min |
| make semantic-index | 0 min |
| make trial-review | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
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
- check dispatches 0 over 485 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (485 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 1 | 4 min | 241k | 11.2k | 0.002 | 0.5k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
