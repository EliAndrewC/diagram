# Feature report - 390-money-foundation-research

Written by `make feature-report F=390` from 2066 events (2026-10-18T23:11 to 2026-10-19T01:28 UTC), 29 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 40 min | 39% |
| other tool | 22 min | 21% |
| waiting: quote-check | 16 min | 16% |
| waiting: source-reader | 10 min | 10% |
| waiting: source-applicability | 5 min | 4% |
| waiting: round-arbiter | 2 min | 2% |
| waiting: record-format | 2 min | 2% |
| test file | 1 min | 1% |
| waiting: intro-check | 1 min | 1% |
| waiting: translation-check | 1 min | 1% |
| edit | 1 min | 1% |
| writing the spec | 1 min | 1% |
| dispatching: record check | 0 min | 0% |
| quick test | 0 min | 0% |

The session's own time above; its 533 subagent tool call(s) (of 979) are counted apart (0 by the subagent transcripts, 533 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 99 run(s), 2 h 14 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 6 min |
| make record | 3 min |
| make check-bundle | 2 min |
| make canon | 2 min |
| make quote-verbatim | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 57 | findings 30 |
| source-applicability | 45 | clean 3, findings 26 |
| record-format | 17 | findings 12 |
| quote-check | 13 | findings 12 |
| translation-check | 10 | FAITHFUL 8 |
| intro-check | 7 | clean 3, findings 3 |
| round-arbiter | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| record-format | q-0251 | 6 |
| quote-check | q-0251 | 5 |
| record-format | q-0248 | 5 |
| translation-check | q-0248 | 5 |
| translation-check | q-0251 | 5 |
| intro-check | intro-0248 | 4 |
| quote-check | q-0248 | 4 |
| source-applicability | key-ihns-bunongshu | 4 |
| source-reader | sr-koku-enwiki | 4 |
| source-reader | sr-kokudaka-jawiki | 4 |
| source-reader | sr-l7r-budgets | 4 |
| source-reader | sr-maff-2023-genmai-density | 4 |
| source-reader | sr-shugiin-1950-genmai-koku | 4 |
| source-reader | sr-shugiin-1950-genmai-koku-question | 4 |
| record-format | q-0249 | 3 |
| record-format | q-0250 | 3 |
| source-applicability | key-koku-enwiki | 3 |
| source-reader | key-washizaki-2007-edo-land-market-whole | 3 |
| quote-check | q-0249 | 2 |
| quote-check | q-0250 | 2 |
| source-applicability | key-fuchi-kotobank | 2 |
| source-applicability | key-koku-unit-jawiki | 2 |
| source-applicability | key-kokudaka-jawiki | 2 |
| source-applicability | key-kyomasu-jawiki | 2 |
| source-applicability | key-l7r-budgets | 2 |
| source-applicability | key-l7r-money | 2 |
| source-applicability | key-maff-2023-genmai-density | 2 |
| source-applicability | key-miyashiro-kumehara-1698 | 2 |
| source-applicability | key-nakabayashi-2020-kyoho-land-law | 2 |
| source-applicability | key-pomeranz-land-markets-lse | 2 |
| source-applicability | key-saito-2003-wages | 2 |
| source-applicability | key-shugiin-1950-genmai-koku-question | 2 |
| source-applicability | key-tawara-unit-jawiki | 2 |
| source-applicability | key-washizaki-2007-edo-land-market | 2 |
| source-applicability | key-wigmore-1892-servitudes | 2 |
| source-applicability | key-ye-mengzhu-yueshibian | 2 |
| source-reader | key-allen-2009-china-wages-whole | 2 |
| source-reader | key-bassino-ma-2005-whole | 2 |
| source-reader | key-cao-2019-dian-minnan-whole | 2 |
| source-reader | key-l7r-budgets-whole | 2 |
| source-reader | key-miyashiro-kumehara-1698-whole | 2 |
| source-reader | key-saito-2003-wages-whole | 2 |
| source-reader | q-0248 | 2 |
| source-reader | q-0251 | 2 |
| source-reader | sr-allen-2009-china-wages | 2 |
| source-reader | sr-bassino-ma-2005 | 2 |
| source-reader | sr-saito-2003-wages | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 149 over 1301 changed lines: cascade ratio 0.11
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 01:08 round:quote-check|q-0248@3
- 01:08 round:quote-check|q-0251@3
- 01:08 round:record-format|q-0248@3
- 01:08 round:record-format|q-0251@3
- 01:08 round:intro-check|intro-0248@3
- 01:08 round:translation-check|q-0248@3
- 01:08 round:translation-check|q-0251@3
- 01:18 round:quote-check|q-0248@4
- 01:18 round:quote-check|q-0251@4
- 01:18 round:record-format|q-0248@4
- 01:18 round:record-format|q-0251@4
- 01:18 round:translation-check|q-0248@4
- 01:18 round:translation-check|q-0251@4

## What each check cost, per changed line (1301 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 12 | 39 min | 6191k | 143.0k | 0.009 | 4.8k |
| source-reader | 30 | 31 min | 4626k | 124.0k | 0.023 | 3.6k |
| source-applicability | 29 | 38 min | 3295k | 127.6k | 0.022 | 2.5k |
| record-format | 12 | 14 min | 1553k | 71.7k | 0.009 | 1.2k |
| translation-check | 8 | 7 min | 337k | 41.9k | 0.006 | 0.3k |
| intro-check | 6 | 2 min | 108k | 6.9k | 0.005 | 0.1k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
