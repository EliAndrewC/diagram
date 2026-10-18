# Feature report - 386-landing-cohort

Written by `make feature-report F=386` from 350 events (2026-10-18T03:57 to 2026-10-18T04:49 UTC), 7 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 26 min | 49% |
| waiting: a background run | 20 min | 39% |
| other tool | 2 min | 4% |
| waiting: spec-fidelity-verify | 2 min | 3% |
| edit | 1 min | 2% |
| writing the spec | 1 min | 2% |
| waiting: subagent | 1 min | 2% |
| test file | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| quick test | 0 min | 0% |

The session's own time above; its 33 subagent tool call(s) (of 154) are counted apart (0 by the subagent transcripts, 33 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 4 run(s), 17 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 2 min |
| make hooks-test | 0 min |
| make ledger-owed | 0 min |
| make cohort-landing | 0 min |
| make cohort | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 0 over 662 changed lines: cascade ratio 0.00
- tasks ticked: 1 of 2

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (662 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 10 min | 621k | 26.7k | 0.003 | 0.9k |
| spec-fidelity-verify | 2 | 7 min | 506k | 18.2k | 0.003 | 0.8k |

This report took 0.5 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
