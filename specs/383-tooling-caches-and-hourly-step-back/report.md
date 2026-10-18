# Feature report - 383-tooling-caches-and-hourly-step-back

Written by `make feature-report F=383` from 4760 events (2026-10-13T03:21 to 2026-10-18T10:04 UTC), 157 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 110 h 36 min | - |
| thinking | 7 h 49 min | 48% |
| other tool | 5 h 15 min | 33% |
| waiting: the GM | 1 h 24 min | 9% |
| test file | 45 min | 5% |
| waiting: subagent | 42 min | 4% |
| edit | 6 min | 1% |
| quick test | 2 min | 0% |
| dispatching: spec review | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: spec-fidelity | 1 min | 0% |
| spec-kit step | 1 min | 0% |
| gate | 0 min | 0% |
| waiting: round-arbiter | 0 min | 0% |
| waiting: general-purpose | 0 min | 0% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |

The session's own time above; its 336 subagent tool call(s) (of 2147) are counted apart (313 by the subagent transcripts, 23 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 76 run(s), 2 h 16 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 h 53 min |
| make hooks-test | 38 min |
| make parts-sweep | 10 min |
| make land-tooling | 8 min |
| make collect-cost | 8 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 65 | BLOCKED 8, CHANGES REQUIRED 7, CLEAR 22, FAITHFUL 6, NOT-REVIEWABLE 1 |
| round-arbiter | 7 | CHANGES REQUIRED 1, CLEAR 1, FAITHFUL 1, findings 4 |
| general-purpose | 2 | - |
| impl-drift | 2 | findings 1 |
| claude-code-guide | 1 | - |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| spec-fidelity | plan-383-tooling-caches-and-hourly-step-back-blocks | 26 |
| impl-drift | claims-owed | 2 |

## Process signals

- gates: already-verified 5, green 3, red 2
- spec rounds: none recorded
- plan reviews BLOCKED: 25 recorded in commits, 8 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 11904 changed lines: cascade ratio 0.00
- tasks ticked: 60 of 60

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (11904 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 44 | 1 h 29 min | 11776k | 286.6k | 0.004 | 1.0k |
| spec-fidelity-verify | 17 | 31 min | 2093k | 89.9k | 0.001 | 0.2k |
| impl-drift | 1 | 0 min | 22k | 0.9k | 0.000 | 0.0k |

This report took 3.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
