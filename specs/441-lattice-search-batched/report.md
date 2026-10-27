# Feature report - 441-lattice-search-batched

Written by `make feature-report F=441` from 56 events (2026-10-27T23:45 to 2026-10-27T23:54 UTC), 1 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| waiting: spec-fidelity | 5 min | 60% |
| thinking | 3 min | 37% |
| other tool | 0 min | 2% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 13 subagent tool call(s) (of 26) are counted apart (0 by the subagent transcripts, 13 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 1 run(s), 6 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 0 min |
| make feature-report | 0 min |
| make perf-share | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 0 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (0 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 1 | 6 min | 470k | 11.8k | 1.000 | 470.0k |

This report took 0.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
