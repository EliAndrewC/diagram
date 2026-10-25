# Feature report - 418-hoei-rates-and-canton-cash

Written by `make feature-report F=418` from 2082 events (2026-10-25T03:37 to 2026-10-25T05:41 UTC), 20 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 30 min | 46% |
| other tool | 1 h 02 min | 31% |
| waiting: quote-check | 22 min | 11% |
| waiting: source-reader | 6 min | 3% |
| waiting: source-applicability | 6 min | 3% |
| waiting: subagent | 4 min | 2% |
| waiting: translation-check | 3 min | 2% |
| waiting: record-format | 1 min | 1% |
| writing the spec | 0 min | 0% |
| test file | 0 min | 0% |
| edit | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 521 subagent tool call(s) (of 962) are counted apart (0 by the subagent transcripts, 521 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 51 run(s), 1 h 53 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 7 min |
| make hooks-test | 2 min |
| make record | 1 min |
| make feature-report | 1 min |
| make reserve | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 15 | clean 1, findings 14 |
| source-applicability | 13 | clean 2, findings 11 |
| spec-fidelity | 7 | CHANGES REQUIRED 1, CLEAR 3, NOT-REVIEWABLE 1 |
| quote-check | 5 | findings 5 |
| record-format | 5 | findings 5 |
| round-arbiter | 2 | FAITHFUL 2 |
| translation-check | 2 | FAITHFUL 2 |
| escalation-check | 1 | findings 1 |
| research-pass | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-chinese-repository-vol2-1834-whole | 3 |
| quote-check | q-0287 | 2 |
| quote-check | q-0289 | 2 |
| record-format | q-0287 | 2 |
| record-format | q-0289 | 2 |
| source-applicability | key-chinese-repository-vol2-1834 | 2 |
| source-applicability | key-chinese-repository-vol4-1835 | 2 |
| source-applicability | key-chinese-repository-vol6-1837 | 2 |
| source-reader | key-chinese-repository-vol1-1832-whole | 2 |
| source-reader | key-chinese-repository-vol5-1836-whole | 2 |
| source-reader | key-coin-walk-edo-kahei-nenpyo-whole | 2 |
| translation-check | q-0287 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 40 over 385 changed lines: cascade ratio 0.10
- tasks ticked: 3 of 6

## Tripwires (FR-010) - what fired, or would have

- 05:22 round:source-reader|key-chinese-repository-vol2-1834-whole@3

## What each check cost, per changed line (385 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 5 | 9 min | 421k | 28.0k | 0.013 | 1.1k |
| escalation-check | 1 | 1 min | 99k | 3.4k | 0.003 | 0.3k |
| source-applicability | 1 | 1 min | 65k | 3.5k | 0.003 | 0.2k |
| spec-fidelity-verify | 2 | 1 min | 53k | 5.2k | 0.005 | 0.1k |

This report took 2.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
