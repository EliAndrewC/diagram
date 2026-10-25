# Feature report - 412-money-basket-every-era

Written by `make feature-report F=412` from 4204 events (2026-10-24T17:59 to 2026-10-25T00:13 UTC), 78 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 34 min | 69% |
| other tool | 43 min | 19% |
| waiting: source-reader | 12 min | 5% |
| edit | 8 min | 3% |
| writing the spec | 4 min | 2% |
| test file | 2 min | 1% |
| dispatching: record check | 1 min | 0% |
| waiting: quote-check | 0 min | 0% |
| quick test | 0 min | 0% |

The session's own time above; its 739 subagent tool call(s) (of 1984) are counted apart (0 by the subagent transcripts, 739 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 116 run(s), 2 h 43 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 13 min |
| make record | 10 min |
| make check-bundle | 4 min |
| make apply-edits | 3 min |
| make money-candidates | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-applicability | 55 | clean 1, findings 29 |
| source-reader | 54 | clean 5, findings 40 |
| record-format | 16 | clean 2, findings 14 |
| quote-check | 13 | findings 13 |
| translation-check | 12 | FAITHFUL 10 |
| intro-check | 2 | clean 1, findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-applicability | key-jacks-2008-gpih-beijing-prices | 3 |
| source-applicability | key-ma-2004-gpih-china-wages | 3 |
| source-reader | key-jawiki-sanka-seido-whole | 3 |
| source-reader | key-jawiki-tenpo-chogin-whole | 3 |
| translation-check | q-0288 | 3 |
| translation-check | q-0289 | 3 |
| quote-check | q-0250 | 2 |
| quote-check | q-0273 | 2 |
| quote-check | q-0286 | 2 |
| quote-check | q-0288 | 2 |
| quote-check | q-0289 | 2 |
| record-format | q-0250 | 2 |
| record-format | q-0265 | 2 |
| record-format | q-0273 | 2 |
| record-format | q-0279 | 2 |
| record-format | q-0286 | 2 |
| record-format | q-0287 | 2 |
| record-format | q-0288 | 2 |
| record-format | q-0289 | 2 |
| source-applicability | key-allen-2009-china-wages | 2 |
| source-applicability | key-allen-2010-gpih-beijing-prices | 2 |
| source-applicability | key-bassino-2006-gpih-mitsui | 2 |
| source-applicability | key-boj-imes-edo-ichiryo | 2 |
| source-applicability | key-chinese-repository-1835-diet | 2 |
| source-applicability | key-coin-walk-edo-kahei-nenpyo | 2 |
| source-applicability | key-fao-1990-energy-conservation-forest-industries | 2 |
| source-applicability | key-gamble-burgess-1921-peking-survey | 2 |
| source-applicability | key-huang-guoxin-2021-qing-yanzheng | 2 |
| source-applicability | key-iwahashi-1981-gpih-rice-prices | 2 |
| source-applicability | key-jawiki-genbun-chogin | 2 |
| source-applicability | key-jawiki-ichibu-gin | 2 |
| source-applicability | key-jawiki-koban | 2 |
| source-applicability | key-jawiki-tenpo-chogin | 2 |
| source-applicability | key-kimura-1987-gpih-osaka-prices | 2 |
| source-applicability | key-kumon-2022-gpih-japanese-wages | 2 |
| source-applicability | key-liu-2005-gpih-china-rice-prices | 2 |
| source-applicability | key-liu-2022-china-wages-1530-1840 | 2 |
| source-applicability | key-ma-2012-china-money-overview | 2 |
| source-applicability | key-mingshi-81-qianchao | 2 |
| source-applicability | key-qian-yong-lvyuan-conghua | 2 |
| source-applicability | key-qingshigao-123-yanfa | 2 |
| source-applicability | key-ye-mengzhu-yueshibian | 2 |
| source-reader | key-allen-2009-china-wages-whole | 2 |
| source-reader | key-bassino-2006-gpih-mitsui-whole | 2 |
| source-reader | key-boj-imes-edo-ichiryo-whole | 2 |
| source-reader | key-chinese-repository-1835-diet-whole | 2 |
| source-reader | key-fao-1990-energy-conservation-forest-industries-whole | 2 |
| source-reader | key-gao-shouxian-jiuqing-wuliao-whole | 2 |
| source-reader | key-huang-guoxin-2021-qing-yanzheng-whole | 2 |
| source-reader | key-jawiki-chogin-whole | 2 |
| source-reader | key-jawiki-koban-whole | 2 |
| source-reader | key-jawiki-nanryo-nishugin-whole | 2 |
| source-reader | key-kimura-1987-gpih-osaka-prices-whole | 2 |
| source-reader | key-kumon-2022-gpih-japanese-wages-whole | 2 |
| source-reader | key-liu-2022-china-wages-1530-1840-whole | 2 |
| source-reader | key-ma-2012-china-money-overview-whole | 2 |
| source-reader | key-qingshigao-123-yanfa-whole | 2 |
| source-reader | key-rinseishi-booklet-9-kashimo-whole | 2 |
| source-reader | key-ye-mengzhu-yueshibian-whole | 2 |
| translation-check | q-0273 | 2 |
| translation-check | q-0286 | 2 |
| translation-check | q-0287 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 152 over 2801 changed lines: cascade ratio 0.05
- tasks ticked: 5 of 8

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 1 h 29 min | 0 min | 1 h 29 min | 0 | 89 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 23:07-00:36 | the tick or the last event | 513 | 65 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 23:07 | started (`make task-start`) | |
| T01 | 00:36 | ticked | |

This report took 2.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
