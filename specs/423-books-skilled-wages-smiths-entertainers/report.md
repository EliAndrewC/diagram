# Feature report - 423-books-skilled-wages-smiths-entertainers

Written by `make feature-report F=423` from 3433 events (2026-10-26T00:05 to 2026-10-26T02:11 UTC), 30 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 30 min | 31% |
| other tool | 1 h 20 min | 28% |
| spec-kit step | 58 min | 20% |
| waiting: source-reader | 28 min | 10% |
| waiting: source-applicability | 15 min | 5% |
| waiting: quote-check | 5 min | 2% |
| waiting: record-format | 3 min | 1% |
| waiting: subagent | 3 min | 1% |
| edit | 2 min | 1% |
| test file | 1 min | 0% |
| waiting: translation-check | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| waiting: research-pass | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: round-arbiter | 0 min | 0% |

The session's own time above; its 778 subagent tool call(s) (of 1565) are counted apart (0 by the subagent transcripts, 778 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 122 run(s), 3 h 26 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 11 min |
| make record | 8 min |
| make quote-verbatim | 5 min |
| make check-bundle | 4 min |
| make apply-edits | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 47 | clean 1, findings 46 |
| source-applicability | 28 | clean 1, findings 27 |
| record-format | 14 | clean 1, findings 13 |
| quote-check | 10 | findings 10 |
| translation-check | 10 | FAITHFUL 10 |
| intro-check | 5 | findings 5 |
| research-pass | 4 | findings 2 |
| spec-fidelity | 3 | CHANGES REQUIRED 1, CLEAR 1 |
| round-arbiter | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| record-format | q-0305 | 3 |
| record-format | q-0306 | 3 |
| source-reader | key-kawashima-2012-kaji-review-whole | 3 |
| source-reader | key-sato-1994-bakin-junpitsuryo-whole | 3 |
| translation-check | q-0305 | 3 |
| translation-check | q-0306 | 3 |
| intro-check | intro-0306 | 2 |
| quote-check | q-0305 | 2 |
| quote-check | q-0306 | 2 |
| quote-check | qc-0308 | 2 |
| record-format | rf-0307 | 2 |
| record-format | rf-0308 | 2 |
| source-applicability | key-brook-2025-price-of-collapse-excerpt | 2 |
| source-applicability | key-sato-1994-bakin-junpitsuryo | 2 |
| source-reader | chinanews-beijing-biaoju | 2 |
| source-reader | key-brook-2025-price-of-collapse-excerpt-whole | 2 |
| source-reader | key-fukui-kenshi-takefu-sales-whole | 2 |
| source-reader | key-kawashima-2010-nogu-benriron-whole | 2 |
| source-reader | key-zhwiki-siku-quanshu-whole | 2 |
| source-reader | kotobank-tedai | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 114 over 1062 changed lines: cascade ratio 0.11
- tasks ticked: 2 of 4

## Tripwires (FR-010) - what fired, or would have

- 01:50 round:source-reader|key-sato-1994-bakin-junpitsuryo-whole@3
- 01:50 round:source-reader|key-kawashima-2012-kaji-review-whole@3
- 01:58 round:record-format|q-0305@3
- 01:58 round:record-format|q-0306@3
- 01:58 round:translation-check|q-0305@3
- 01:58 round:translation-check|q-0306@3

## What each check cost, per changed line (1062 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 2 | 3 min | 227k | 12.6k | 0.002 | 0.2k |
| spec-fidelity-verify | 1 | 1 min | 42k | 2.1k | 0.001 | 0.0k |

This report took 2.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
