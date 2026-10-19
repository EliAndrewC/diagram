# Feature report - 391-comparative-money-sources

Written by `make feature-report F=391` from 4137 events (2026-10-18T22:53 to 2026-10-19T04:07 UTC), 15 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 1 h 46 min | 27% |
| waiting: a background run | 1 h 27 min | 22% |
| waiting: the GM | 1 h 21 min | 21% |
| other tool | 1 h 16 min | 19% |
| waiting: source-reader | 15 min | 4% |
| waiting: quote-check | 8 min | 2% |
| waiting: subagent | 6 min | 1% |
| test file | 3 min | 1% |
| waiting: round-arbiter | 3 min | 1% |
| edit | 2 min | 0% |
| waiting: source-applicability | 2 min | 0% |
| waiting: record-format | 1 min | 0% |
| waiting: translation-check | 1 min | 0% |
| writing the spec | 1 min | 0% |
| dispatching: record check | 1 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| waiting: research-pass | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 1114 subagent tool call(s) (of 1819) are counted apart (0 by the subagent transcripts, 1114 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 75 run(s), 3 h 46 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 10 min |
| make record | 3 min |
| make ledger-owed | 2 min |
| make quote-verbatim | 2 min |
| make reserve | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 28 | clean 1, findings 16 |
| research-pass | 16 | findings 8 |
| record-format | 13 | findings 11 |
| quote-check | 12 | findings 10 |
| spec-fidelity | 7 | BLOCKED 2, CHANGES REQUIRED 2, CLEAR 3 |
| round-arbiter | 4 | findings 3 |
| translation-check | 4 | FAITHFUL 2 |
| intro-check | 3 | findings 3 |
| source-applicability | 2 | clean 1, findings 1 |
| spec-fidelity-verify | 2 | FAITHFUL 2 |
| escalation-check | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0251 | 3 |
| quote-check | q-0254 | 3 |
| record-format | q-0251 | 3 |
| record-format | q-0252 | 3 |
| record-format | q-0254 | 3 |
| source-reader | key-enwiki-guinea-coin-whole | 3 |
| quote-check | q-0248 | 2 |
| quote-check | q-0252 | 2 |
| quote-check | q-0253 | 2 |
| record-format | q-0248 | 2 |
| record-format | q-0253 | 2 |
| source-reader | key-cao-2019-dian-minnan-whole | 2 |
| source-reader | key-kotobank-shichichi-whole | 2 |
| source-reader | key-l7r-money-whole | 2 |
| source-reader | key-miyashiro-kumehara-1698-whole | 2 |
| source-reader | key-nakabayashi-2020-kyoho-land-law-whole | 2 |
| source-reader | key-pomeranz-land-markets-lse-whole | 2 |
| source-reader | key-qian-yong-lvyuan-conghua-whole | 2 |
| source-reader | key-washizaki-2007-edo-land-market-whole | 2 |
| source-reader | key-wigmore-1892-servitudes-whole | 2 |
| source-reader | key-ye-mengzhu-yueshibian-whole | 2 |
| source-reader | q-0254 | 2 |
| translation-check | q-0248 | 2 |
| translation-check | q-0251 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 62 over 678 changed lines: cascade ratio 0.09
- tasks ticked: 7 of 9

## Tripwires (FR-010) - what fired, or would have

- 02:51 round:quote-check|q-0254@3
- 02:51 round:record-format|q-0252@3
- 02:51 round:record-format|q-0254@3

## What each check cost, per changed line (678 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| source-reader | 17 | 19 min | 2733k | 75.6k | 0.025 | 4.0k |
| quote-check | 10 | 10 min | 1369k | 48.7k | 0.015 | 2.0k |
| record-format | 11 | 8 min | 1206k | 42.3k | 0.016 | 1.8k |
| spec-fidelity | 7 | 17 min | 1143k | 50.4k | 0.010 | 1.7k |
| source-applicability | 2 | 4 min | 680k | 10.0k | 0.003 | 1.0k |
| spec-fidelity-verify | 2 | 5 min | 304k | 11.5k | 0.003 | 0.4k |
| escalation-check | 1 | 2 min | 301k | 7.5k | 0.001 | 0.4k |
| translation-check | 2 | 2 min | 134k | 8.3k | 0.003 | 0.2k |
| intro-check | 3 | 1 min | 55k | 2.7k | 0.004 | 0.1k |

This report took 1.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
