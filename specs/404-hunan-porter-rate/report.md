# Feature report - 404-hunan-porter-rate

Written by `make feature-report F=404` from 512 events (2026-10-19T22:54 to 2026-10-19T23:33 UTC), 15 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| waiting: a background run | 30 min | 43% |
| thinking | 21 min | 30% |
| other tool | 7 min | 11% |
| waiting: quote-check | 3 min | 4% |
| waiting: source-applicability | 2 min | 3% |
| waiting: subagent | 2 min | 3% |
| waiting: record-format | 1 min | 2% |
| waiting: source-reader | 1 min | 2% |
| waiting: translation-check | 1 min | 1% |
| test file | 0 min | 1% |
| waiting: round-arbiter | 0 min | 0% |
| writing the spec | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| edit | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 78 subagent tool call(s) (of 235) are counted apart (0 by the subagent transcripts, 78 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 14 run(s), 20 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make record | 1 min |
| Bash | 1 min |
| make apply-edits | 1 min |
| make quote-verbatim | 1 min |
| make check-bundle | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| record-format | 3 | findings 3 |
| quote-check | 2 | findings 2 |
| source-reader | 2 | findings 2 |
| spec-fidelity | 2 | CHANGES REQUIRED 1, CLEAR 1 |
| translation-check | 2 | FAITHFUL 2 |
| round-arbiter | 1 | findings 1 |
| source-applicability | 1 | findings 1 |
| spec-fidelity-verify | 1 | CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| record-format | q-0260 | 3 |
| quote-check | q-0260 | 2 |
| translation-check | q-0260 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 10 over 186 changed lines: cascade ratio 0.05
- tasks ticked: 3 of 5

## Tripwires (FR-010) - what fired, or would have

- 23:31 round:record-format|q-0260@3

## What each check cost, per changed line (186 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 5 min | 693k | 20.2k | 0.011 | 3.7k |
| quote-check | 2 | 6 min | 493k | 15.5k | 0.011 | 2.7k |
| record-format | 3 | 2 min | 242k | 10.6k | 0.016 | 1.3k |
| source-applicability | 1 | 3 min | 184k | 5.1k | 0.005 | 1.0k |
| source-reader | 2 | 1 min | 93k | 7.6k | 0.011 | 0.5k |
| spec-fidelity-verify | 1 | 1 min | 69k | 3.9k | 0.005 | 0.4k |
| translation-check | 2 | 1 min | 47k | 2.8k | 0.011 | 0.3k |

This report took 2.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
