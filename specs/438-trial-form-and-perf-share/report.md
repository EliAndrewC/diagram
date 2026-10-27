# Feature report - 438-trial-form-and-perf-share

Written by `make feature-report F=438` from 173 events (2026-10-27T21:16 to 2026-10-27T21:38 UTC), 7 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 7 min | 30% |
| other tool | 6 min | 28% |
| quick test | 5 min | 23% |
| waiting: spec-fidelity | 4 min | 16% |
| waiting: spec-fidelity-verify | 1 min | 2% |
| dispatching: spec review | 0 min | 1% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| edit | 0 min | 0% |

The session's own time above; its 30 subagent tool call(s) (of 75) are counted apart (0 by the subagent transcripts, 30 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 7 run(s), 8 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 6 min |
| make ledger-owed | 0 min |
| make found-close | 0 min |
| make claims-checked | 0 min |
| make claims-triage | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 3 |
| impl-drift | 2 | findings 2 |
| spec-fidelity-verify | 2 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-owed | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 2 over 386 changed lines: cascade ratio 0.01
- tasks ticked: 0 of 2

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 14 min (open) | 1 min | 13 min | 2 | 1, 0, 13 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 21:25-21:25 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x2 (1 min) |
| T01 | 21:25-21:25 | spec-fidelity CLEAR | 0 | 0 | 0 | 0 | - |
| T01 | 21:25-21:38 | the tick or the last event | 15 | 13 | 0 | 0 | impl-drift x2 (0 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 21:25 | started (`make task-start`) | |
| T01 | 21:25 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 21:25 | spec-fidelity returned CLEAR (1 min) | |
| T01 | 21:38 | impl-drift returned findings (0 min) | |
| T01 | 21:38 | impl-drift returned findings (0 min) | |

## What each check cost, per changed line (386 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 4 | 7 min | 768k | 26.4k | 0.010 | 2.0k |
| spec-fidelity-verify | 1 | 1 min | 97k | 3.8k | 0.003 | 0.3k |
| impl-drift | 2 | 0 min | 38k | 0.6k | 0.005 | 0.1k |

This report took 1.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
