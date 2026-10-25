# Feature report - 416-three-metals

Written by `make feature-report F=416` from 3928 events (2026-10-24T17:54 to 2026-10-25T05:06 UTC), 26 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 3 h 52 min | 45% |
| idle (over an hour) | 3 h 18 min | - |
| waiting: a background run | 2 h 01 min | 24% |
| other tool | 1 h 52 min | 22% |
| waiting: subagent | 15 min | 3% |
| waiting: source-reader | 10 min | 2% |
| edit | 6 min | 1% |
| waiting: source-applicability | 3 min | 1% |
| waiting: record-format | 3 min | 1% |
| waiting: quote-check | 2 min | 0% |
| waiting: round-arbiter | 2 min | 0% |
| waiting: translation-check | 2 min | 0% |
| writing the spec | 1 min | 0% |
| test file | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 737 subagent tool call(s) (of 1771) are counted apart (0 by the subagent transcripts, 733 by the hook's `by`, 4 by the agents' windows - an estimate; plan D30). The subagents' own work: 106 run(s), 3 h 05 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 33 min |
| make land | 17 min |
| make record | 7 min |
| make ledger-owed | 3 min |
| make apply-edits | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 42 | clean 3, findings 37 |
| record-format | 13 | findings 12 |
| spec-fidelity | 12 | BLOCKED 5, CHANGES REQUIRED 1, CLEAR 5, NOT-REVIEWABLE 1 |
| quote-check | 11 | findings 10 |
| translation-check | 11 | FAITHFUL 11 |
| source-applicability | 5 | findings 5 |
| round-arbiter | 4 | findings 4 |
| spec-fidelity-verify | 4 | CHANGES REQUIRED 3, FAITHFUL 3 |
| research-pass | 2 | findings 2 |
| escalation-check | 1 | findings 1 |
| intro-check | 1 | clean 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0288 | 3 |
| record-format | q-0289 | 3 |
| translation-check | q-0288 | 3 |
| quote-check | q-0289 | 2 |
| record-format | q-0250 | 2 |
| record-format | q-0288 | 2 |
| round-arbiter | arbiter-batch | 2 |
| source-reader | key-chinese-repository-1835-diet-whole | 2 |
| source-reader | s416-sr-jawiki-sanka-seido | 2 |
| source-reader | s416-sr-saito-1993-bakumatsu-wages | 2 |
| source-reader | s416b-sr-mingshi-81-qianchao | 2 |
| source-reader | s416b-sr-qingshigao-123-yanfa | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 5 returned
- reversals (A -> B -> A): 0
- check dispatches 83 over 860 changed lines: cascade ratio 0.10
- tasks ticked: 3 of 6

## Tripwires (FR-010) - what fired, or would have

- 22:58 round:quote-check|q-0288@3
- 22:59 round:translation-check|q-0288@3

## What each check cost, per changed line (860 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| record-format | 10 | 9 min | 1803k | 47.7k | 0.012 | 2.1k |
| quote-check | 6 | 6 min | 1558k | 25.8k | 0.007 | 1.8k |
| spec-fidelity | 12 | 38 min | 1496k | 120.2k | 0.014 | 1.7k |
| spec-fidelity-verify | 6 | 10 min | 979k | 33.9k | 0.007 | 1.1k |
| source-reader | 5 | 3 min | 560k | 17.9k | 0.006 | 0.7k |
| escalation-check | 1 | 2 min | 279k | 7.8k | 0.001 | 0.3k |
| translation-check | 5 | 3 min | 278k | 18.7k | 0.006 | 0.3k |
| source-applicability | 1 | 1 min | 79k | 3.9k | 0.001 | 0.1k |

This report took 2.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
