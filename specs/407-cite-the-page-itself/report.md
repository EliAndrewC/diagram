# Feature report - 407-cite-the-page-itself

Written by `make feature-report F=407` from 555 events (2026-10-20T03:50 to 2026-10-20T04:29 UTC), 9 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 22 min | 57% |
| other tool | 15 min | 39% |
| waiting: subagent | 1 min | 2% |
| spec-kit step | 0 min | 1% |
| waiting: quote-check | 0 min | 1% |
| dispatching: spec review | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| test file | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 183 subagent tool call(s) (of 246) are counted apart (0 by the subagent transcripts, 167 by the hook's `by`, 16 by the agents' windows - an estimate; plan D30). The subagents' own work: 23 run(s), 33 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 3 min |
| make quote-verbatim | 2 min |
| make check-bundle | 2 min |
| make record-checked | 1 min |
| Workflow | 0 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 3 | CHANGES REQUIRED 1, CLEAR 2 |
| record-format | 2 | findings 2 |
| source-reader | 2 | findings 2 |
| round-arbiter | 1 | findings 1 |
| spec-fidelity-verify | 1 | FAITHFUL 1 |
| translation-check | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| - | - | - |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 5 over 189 changed lines: cascade ratio 0.03
- tasks ticked: 1 of 4

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (189 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 13 | 24 min | 3018k | 63.2k | 0.069 | 16.0k |
| spec-fidelity | 3 | 4 min | 357k | 17.9k | 0.016 | 1.9k |
| record-format | 2 | 2 min | 208k | 8.5k | 0.011 | 1.1k |
| source-reader | 2 | 1 min | 91k | 4.8k | 0.011 | 0.5k |
| spec-fidelity-verify | 1 | 0 min | 45k | 2.1k | 0.005 | 0.2k |
| translation-check | 1 | 0 min | 23k | 0.8k | 0.005 | 0.1k |

This report took 2.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
