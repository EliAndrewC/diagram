# Feature report - 400-campaign-costs-fruit-salt-hemp-wages

Written by `make feature-report F=400` from 2233 events (2026-10-19T13:13 to 2026-10-19T15:44 UTC), 23 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 06 min | 51% |
| waiting: source-reader | 1 h 02 min | 25% |
| other tool | 28 min | 11% |
| waiting: quote-check | 12 min | 5% |
| waiting: source-applicability | 8 min | 3% |
| waiting: subagent | 6 min | 2% |
| waiting: record-format | 2 min | 1% |
| waiting: round-arbiter | 1 min | 1% |
| edit | 1 min | 0% |
| waiting: intro-check | 1 min | 0% |
| dispatching: record check | 1 min | 0% |
| waiting: translation-check | 0 min | 0% |
| test file | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 479 subagent tool call(s) (of 1044) are counted apart (0 by the subagent transcripts, 479 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 91 run(s), 1 h 56 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make record | 4 min |
| make record-owed | 3 min |
| make apply-edits | 2 min |
| make reserve | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 53 | clean 2, findings 35 |
| source-applicability | 28 | clean 1, findings 18 |
| quote-check | 9 | findings 9 |
| record-format | 9 | findings 9 |
| translation-check | 8 | FAITHFUL 8 |
| intro-check | 6 | findings 6 |
| round-arbiter | 3 | findings 3 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-ye-mengzhu-yueshibian-whole | 7 |
| source-reader | key-gao-shouxian-jiuqing-wuliao-whole | 4 |
| source-reader | key-king-1911-farmers-forty-centuries-whole | 4 |
| quote-check | q-0273 | 3 |
| record-format | q-0273 | 3 |
| source-reader | key-handa-museum-otsukawa-1842-prices-whole | 3 |
| source-reader | key-miyashiro-kumehara-1698-whole | 3 |
| source-reader | key-rinseishi-booklet-9-kashimo-whole | 3 |
| translation-check | q-0273 | 3 |
| intro-check | intro-0272 | 2 |
| intro-check | intro-0275 | 2 |
| quote-check | q-0272 | 2 |
| quote-check | q-0274 | 2 |
| quote-check | q-0275 | 2 |
| record-format | q-0272 | 2 |
| record-format | q-0274 | 2 |
| record-format | q-0275 | 2 |
| source-applicability | key-handa-museum-otsukawa-1842-prices | 2 |
| source-applicability | key-king-1911-farmers-forty-centuries | 2 |
| source-applicability | key-ming-huidian-136 | 2 |
| source-applicability | key-ni-2005-tao-shu-piaoyan | 2 |
| source-applicability | key-rinseishi-booklet-9-kashimo | 2 |
| source-applicability | key-saltstory-shio-no-keifu | 2 |
| source-applicability | key-takeya-1999-osaka-tetsudai | 2 |
| source-applicability | key-wu-haibo-qing-sishi | 2 |
| source-applicability | key-ye-mengzhu-yueshibian | 2 |
| source-reader | key-allen-2009-china-wages-whole | 2 |
| source-reader | key-ni-2005-tao-shu-piaoyan-whole | 2 |
| source-reader | key-oamishirasato-tenpo13-bukka-whole | 2 |
| source-reader | key-qingshigao-123-yanfa-whole | 2 |
| source-reader | key-saltstory-shio-no-keifu-whole | 2 |
| source-reader | key-takeya-1999-osaka-tetsudai-whole | 2 |
| source-reader | key-wu-haibo-qing-sishi-whole | 2 |
| translation-check | q-0272 | 2 |
| translation-check | q-0274 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 113 over 863 changed lines: cascade ratio 0.13
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 14:33 round:source-reader|key-gao-shouxian-jiuqing-wuliao-whole@3
- 15:41 round:quote-check|q-0273@3
- 15:41 round:translation-check|q-0273@3
- 15:41 round:record-format|q-0273@3

## What each check cost, per changed line (863 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 9 | 32 min | 5239k | 100.4k | 0.010 | 6.1k |
| source-reader | 37 | 29 min | 3465k | 131.4k | 0.043 | 4.0k |
| source-applicability | 19 | 33 min | 2724k | 98.2k | 0.022 | 3.2k |
| record-format | 9 | 9 min | 1063k | 50.7k | 0.010 | 1.2k |
| translation-check | 8 | 5 min | 350k | 29.2k | 0.009 | 0.4k |
| intro-check | 6 | 2 min | 124k | 8.8k | 0.007 | 0.1k |

This report took 1.9 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
