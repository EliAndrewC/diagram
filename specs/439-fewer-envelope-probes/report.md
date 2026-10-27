# Feature report - 439-fewer-envelope-probes

Written by `make feature-report F=439` from 125 events (2026-10-27T22:06 to 2026-10-27T22:24 UTC), 9 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 8 min | 43% |
| waiting: spec-fidelity | 4 min | 21% |
| waiting: spec-fidelity-verify | 3 min | 17% |
| other tool | 3 min | 15% |
| waiting: round-arbiter | 1 min | 3% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 22 subagent tool call(s) (of 57) are counted apart (0 by the subagent transcripts, 22 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 3 run(s), 8 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 min |
| make perf-ab | 1 min |
| make perf-fanout | 1 min |
| make cohort | 0 min |
| make feature-report | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| round-arbiter | 1 | findings 1 |
| spec-fidelity | 1 | CHANGES REQUIRED 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 19 changed lines: cascade ratio 0.00
- tasks ticked: 0 of 0

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (19 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 1 | 4 min | 434k | 12.7k | 0.053 | 22.8k |
| spec-fidelity-verify | 1 | 3 min | 334k | 9.5k | 0.053 | 17.6k |

This report took 0.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
