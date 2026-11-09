# Feature report - 450-cotton-and-new-crops

Written by `make feature-report F=450` from 14682 events (2026-11-09T02:39 to 2026-11-09T14:30 UTC), 94 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 7 h 43 min | 43% |
| idle (over an hour) | 4 h 25 min | - |
| other tool | 1 h 54 min | 11% |
| waiting: source-reader | 1 h 49 min | 10% |
| waiting: source-applicability | 1 h 22 min | 8% |
| waiting: subagent | 1 h 07 min | 6% |
| waiting: the GM | 52 min | 5% |
| waiting: quote-check | 40 min | 4% |
| waiting: intro-check | 26 min | 2% |
| waiting: record-format | 21 min | 2% |
| waiting: research-pass | 17 min | 2% |
| waiting: spec-fidelity | 15 min | 1% |
| waiting: round-arbiter | 14 min | 1% |
| edit | 11 min | 1% |
| waiting: translation-check | 10 min | 1% |
| waiting: a background run | 10 min | 1% |
| waiting: escalation-check | 6 min | 1% |
| test file | 2 min | 0% |
| waiting: impl-drift | 2 min | 0% |
| writing the spec | 2 min | 0% |
| waiting: spec-fidelity-verify | 1 min | 0% |
| dispatching: record check | 1 min | 0% |
| quick test | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 4354 subagent tool call(s) (of 7089) are counted apart (0 by the subagent transcripts, 4339 by the hook's `by`, 15 by the agents' windows - an estimate; plan D30). The subagents' own work: 472 run(s), 18 h 06 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 29 min |
| make record | 22 min |
| make apply-edits | 14 min |
| make check-bundle | 9 min |
| make reserve | 6 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 228 | clean 22, findings 177 |
| source-applicability | 165 | clean 2, findings 127 |
| quote-check | 42 | clean 2, findings 36 |
| record-format | 35 | clean 2, findings 30 |
| translation-check | 31 | FAITHFUL 29 |
| intro-check | 12 | clean 7, findings 4 |
| spec-fidelity | 7 | BLOCKED 1, CHANGES REQUIRED 2, CLEAR 2, NOT-REVIEWABLE 1 |
| round-arbiter | 6 | findings 6 |
| research-pass | 5 | findings 4 |
| escalation-check | 4 | findings 4 |
| impl-drift | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-applicability | key-fortune-1843 | 4 |
| source-reader | key-encykorea-seo-gyeongchang-whole | 4 |
| source-reader | key-li-american-crops-southwest-whole | 4 |
| source-reader | key-newman-2012-american-foods-china-whole | 4 |
| quote-check | q-0328 | 3 |
| record-format | q-0318 | 3 |
| record-format | q-0323 | 3 |
| record-format | q-0328 | 3 |
| record-format | q-0329 | 3 |
| source-applicability | key-guangdong-xinyu-15 | 3 |
| source-applicability | key-liu-ge-song-cotton | 3 |
| source-applicability | key-tiangong-kaiwu-xiafu | 3 |
| source-applicability | key-ye-mengzhu-yueshibian | 3 |
| source-applicability | key-zurndorfer-pune-cotton | 3 |
| source-applicability | key-zurndorfer-resistant-fibre | 3 |
| source-reader | key-li-2020-american-crops-population-whole | 3 |
| source-reader | key-li-hua-1986-shandong-sweet-potato-whole | 3 |
| source-reader | key-maff-kyushu-satsumaimo-whole | 3 |
| source-reader | key-pelliot-notes-marco-polo-cotton-whole | 3 |
| source-reader | key-staunton-1797-embassy-whole | 3 |
| source-reader | key-zurndorfer-resistant-fibre-whole | 3 |
| translation-check | q-0318 | 3 |
| translation-check | q-0319 | 3 |
| translation-check | q-0323 | 3 |
| translation-check | q-0328 | 3 |
| impl-drift | claims-owed | 2 |
| intro-check | intro-0318 | 2 |
| quote-check | batch-1 | 2 |
| quote-check | q-0327 | 2 |
| quote-check | q-0329 | 2 |
| record-format | q-0261 | 2 |
| record-format | q-0319 | 2 |
| record-format | q-0320 | 2 |
| record-format | q-0321 | 2 |
| record-format | q-0324 | 2 |
| record-format | q-0325 | 2 |
| record-format | q-0326 | 2 |
| record-format | q-0327 | 2 |
| source-applicability | key-ai-lisi-2020-tomato | 2 |
| source-applicability | key-buck-1930-farm-economy | 2 |
| source-applicability | key-chen-guodong-indian-cotton | 2 |
| source-applicability | key-chuogeng-lu-24 | 2 |
| source-applicability | key-crosby-2003-new-world-foods | 2 |
| source-applicability | key-daxue-yanyi-bu-22 | 2 |
| source-applicability | key-ergodicity-2013-mazumdar | 2 |
| source-applicability | key-guo-weidong-indian-raw-cotton | 2 |
| source-applicability | key-hou-hanshu-86 | 2 |
| source-applicability | key-laufer-1924-tobacco-asia | 2 |
| source-applicability | key-leng-2020-sunan | 2 |
| source-applicability | key-li-2020-american-crops-population | 2 |
| source-applicability | key-li-hua-1986-shandong-sweet-potato | 2 |
| source-applicability | key-liangshu-54 | 2 |
| source-applicability | key-lingwai-daida-6 | 2 |
| source-applicability | key-maff-kyushu-satsumaimo | 2 |
| source-applicability | key-mingshi-78-fuyi | 2 |
| source-applicability | key-nongsang-jiyao-2 | 2 |
| source-applicability | key-nongzheng-quanshu-35 | 2 |
| source-applicability | key-pelliot-notes-marco-polo-cotton | 2 |
| source-applicability | key-peoples-daily-2024-cotton | 2 |
| source-applicability | key-pomeranz-east-asia-europe-1998 | 2 |
| source-applicability | key-staunton-1797-embassy | 2 |
| source-applicability | key-tiangong-kaiwu-buyi | 2 |
| source-applicability | key-yajima-2017-japan-cotton | 2 |
| source-applicability | key-yuanshi-15 | 2 |
| source-applicability | key-yuanshi-93-shihuo | 2 |
| source-applicability | key-zhufan-zhi-xia | 2 |
| source-applicability | key-zizhi-tongjian-159 | 2 |
| source-reader | eb-1911-cotton | 2 |
| source-reader | han-kim-2021-foreign-monk | 2 |
| source-reader | herodotus-macaulay | 2 |
| source-reader | key-bishop-1898-korea-whole | 2 |
| source-reader | key-bjnews-zhang-american-crops-whole | 2 |
| source-reader | key-chuogeng-lu-24-whole | 2 |
| source-reader | key-fortune-1843-whole | 2 |
| source-reader | key-guangdong-xinyu-15-whole | 2 |
| source-reader | key-horibe-2024-mikawa-cotton-whole | 2 |
| source-reader | key-hou-hanshu-86-whole | 2 |
| source-reader | key-isono-2007-plant-arrivals-whole | 2 |
| source-reader | key-jeong-2015-korea-tobacco-whole | 2 |
| source-reader | key-kawakatsu-2005-spread-of-cotton-whole | 2 |
| source-reader | key-laufer-1924-tobacco-asia-whole | 2 |
| source-reader | key-lingwai-daida-6-whole | 2 |
| source-reader | key-marshman-1862-dharwar-whole | 2 |
| source-reader | key-stephens-2024-korea-upland-cotton-whole | 2 |
| source-reader | key-tiangong-kaiwu-xiafu-whole | 2 |
| source-reader | key-ye-mengzhu-yueshibian-whole | 2 |
| source-reader | kim-dg-late-joseon-markets | 2 |
| source-reader | lee-2003-joseon-japan-cloth | 2 |
| source-reader | sim-2011-baekje-cotton | 2 |
| source-reader | sr2-bishop-1898-korea | 2 |
| source-reader | sr2-fuller-2024-cotton-investment | 2 |
| source-reader | sr2-han-kim-2021-foreign-monk | 2 |
| source-reader | sr2-lee-2003-joseon-japan-cloth | 2 |
| source-reader | sr2-periplus-erythraean-schoff | 2 |
| source-reader | sr2-roy-2011-cotton-cloth-india | 2 |
| source-reader | sr2-sillok-1398-mun-ikjeom-obituary | 2 |
| source-reader | sr2-sim-2011-baekje-cotton | 2 |
| source-reader | sr2-twomey-1983-indian-textiles | 2 |
| source-reader | twomey-1983-indian-textiles | 2 |
| translation-check | q-0320 | 2 |
| translation-check | q-0324 | 2 |
| translation-check | q-0326 | 2 |
| translation-check | q-0327 | 2 |
| translation-check | q-0329 | 2 |

## Process signals

- gates: red 1
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 1 returned
- reversals (A -> B -> A): 1 - 0328-why-did-one-new-crop-spread-quickly-and-another-slowly-in-china-and-japan.html 13:36
- check dispatches 515 over 4884 changed lines: cascade ratio 0.11
- tasks ticked: 5 of 7

## Tripwires (FR-010) - what fired, or would have

- 07:24 round:source-reader|key-pelliot-notes-marco-polo-cotton-whole@3
- 07:27 round:translation-check|q-0319@3
- 09:53 round:translation-check|q-0323@3
- 09:53 round:record-format|q-0323@3
- 11:41 round:source-reader|key-staunton-1797-embassy-whole@3
- 13:36 reversal:/diagram/.clones/diagram-research/research/questions/0328-why-did-one-new-crop-spread-quickly-and-another-slowly-in-china-and-japan.html
- 14:24 round:record-format|q-0329@3

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 2 h 11 min | 2 h 01 min | 10 min | 5 | 110, 4, 4, 2, 1, 10 |
| T02 | 2 h 11 min | 0 min | 2 h 11 min | 0 | 131 |
| T03 | 2 h 26 min | 2 h 24 min | 2 min | 2 | 119, 24, 2 |
| T04 | 2 h 33 min | 2 h 32 min | 1 min | 2 | 114, 38, 1 |
| T05 | 1 h 57 min | 1 h 49 min | 8 min | 2 | 74, 34, 8 |
| T06 | 1 min (open) | 0 min | 1 min | 0 | 1 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 03:10-05:00 | spec-fidelity NOT-REVIEWABLE | 378 | 94 | 30 | 90 | escalation-check x1, impl-drift x1, intro-check x1, quote-check x6, record-format x3, source-applicability x10, source-reader x19, spec-fidelity x2, translation-check x2 (98 min) |
| T01 | 05:00-05:04 | spec-fidelity CHANGES REQUIRED | 1 | 0 | 4 | 0 | - |
| T01 | 05:04-05:07 | spec-fidelity CLEAR | 4 | 1 | 3 | 0 | spec-fidelity x2 (7 min) |
| T01 | 05:07-05:09 | spec-fidelity CHANGES REQUIRED | 0 | 0 | 2 | 0 | - |
| T01 | 05:09-05:10 | spec-fidelity-verify NOT-REVIEWABLE | 3 | 0 | 1 | 0 | spec-fidelity-verify x1 (1 min) |
| T01 | 05:10-05:20 | the tick or the last event | 6 | 6 | 4 | 0 | - |
| T02 | 05:21-07:32 | the tick or the last event | 623 | 138 | 115 | 0 | intro-check x2, quote-check x7, record-format x6, source-applicability x45, source-reader x45, translation-check x7 (257 min) |
| T03 | 07:32-09:32 | round-arbiter findings | 432 | 98 | 55 | 85 | intro-check x2, quote-check x7, record-format x4, round-arbiter x1, source-applicability x27, source-reader x42, translation-check x4 (201 min) |
| T03 | 09:32-09:56 | round-arbiter findings | 41 | 26 | 15 | 0 | escalation-check x1, record-format x3, round-arbiter x1, source-applicability x2, source-reader x10, translation-check x2 (29 min) |
| T03 | 09:56-09:58 | the tick or the last event | 10 | 1 | 1 | 0 | - |
| T04 | 09:58-11:52 | round-arbiter findings | 519 | 114 | 113 | 0 | escalation-check x1, intro-check x3, quote-check x9, record-format x3, round-arbiter x1, source-applicability x27, source-reader x45, translation-check x3 (193 min) |
| T04 | 11:52-12:30 | round-arbiter findings | 107 | 25 | 43 | 0 | escalation-check x1, quote-check x3, record-format x6, round-arbiter x1, source-applicability x4, source-reader x11, translation-check x5 (66 min) |
| T04 | 12:30-12:31 | the tick or the last event | 3 | 1 | 0 | 0 | - |
| T05 | 12:32-13:47 | round-arbiter findings | 422 | 56 | 19 | 74 | intro-check x1, quote-check x1, record-format x1, round-arbiter x1, source-applicability x10, source-reader x23, translation-check x1 (75 min) |
| T05 | 13:47-14:21 | round-arbiter findings | 121 | 15 | 38 | 16 | intro-check x2, quote-check x5, record-format x5, round-arbiter x1, source-applicability x11, source-reader x8, translation-check x5 (74 min) |
| T05 | 14:21-14:29 | the tick or the last event | 22 | 7 | 7 | 0 | record-format x1 (0 min) |
| T06 | 14:30-14:30 | the tick or the last event | 2 | 1 | 0 | 0 | - |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 03:10 | started (`make task-start`) | |
| T01 | 03:38 | source-reader returned findings (1 min) | |
| T01 | 03:38 | source-reader returned findings (1 min) | |
| T01 | 03:38 | source-reader returned findings (1 min) | |
| T01 | 03:39 | source-reader returned findings (2 min) | |
| T01 | 03:39 | source-reader returned findings (2 min) | |
| T01 | 03:39 | source-reader returned findings (2 min) | |
| T01 | 03:39 | source-reader returned findings (2 min) | |
| T01 | 03:39 | source-reader returned findings (3 min) | |
| T01 | 03:39 | source-reader returned findings (2 min) | |
| T01 | 03:43 | source-reader returned findings (6 min) | |
| T01 | 04:26 | quote-check returned clean (0 min) | |
| T01 | 04:27 | source-reader returned findings (1 min) | |
| T01 | 04:27 | source-reader returned findings (1 min) | |
| T01 | 04:27 | source-reader returned clean (1 min) | |
| T01 | 04:27 | source-reader returned findings (1 min) | |
| T01 | 04:27 | source-reader returned findings (1 min) | |
| T01 | 04:27 | source-applicability returned findings (1 min) | |
| T01 | 04:28 | source-applicability returned findings (1 min) | |
| T01 | 04:28 | source-applicability returned findings (1 min) | |
| T01 | 04:28 | source-applicability returned findings (1 min) | |
| T01 | 04:28 | source-applicability returned findings (1 min) | |
| T01 | 04:28 | source-applicability returned findings (2 min) | |
| T01 | 04:28 | source-reader returned findings (2 min) | |
| T01 | 04:28 | source-applicability returned findings (2 min) | |
| T01 | 04:28 | source-applicability returned findings (2 min) | |
| T01 | 04:28 | quote-check returned findings (2 min) | |
| T01 | 04:29 | source-applicability returned findings (2 min) | |
| T01 | 04:29 | quote-check returned findings (3 min) | |
| T01 | 04:29 | quote-check returned findings (3 min) | |
| T01 | 04:30 | source-reader returned findings (4 min) | |
| T01 | 04:34 | quote-check returned findings (8 min) | |
| T01 | 04:39 | intro-check returned clean (0 min) | |
| T01 | 04:39 | source-reader returned findings (1 min) | |
| T01 | 04:40 | source-reader returned findings (1 min) | |
| T01 | 04:40 | record-format returned findings (1 min) | |
| T01 | 04:40 | translation-check returned FAITHFUL (2 min) | |
| T01 | 04:41 | source-applicability returned findings (3 min) | |
| T01 | 04:41 | escalation-check returned findings (1 min) | |
| T01 | 04:43 | quote-check returned clean (5 min) | |
| T01 | 04:44 | record-format returned findings (5 min) | |
| T01 | 04:46 | translation-check returned FAITHFUL (0 min) | |
| T01 | 04:50 | record-format returned findings (4 min) | |
| T01 | 05:00 | spec-fidelity returned NOT-REVIEWABLE (2 min) | |
| T01 | 05:02 | impl-drift returned findings (4 min) | |
| T01 | 05:04 | spec-fidelity returned CHANGES REQUIRED (6 min) | |
| T01 | 05:07 | spec-fidelity returned CLEAR (3 min) | |
| T01 | 05:09 | spec-fidelity returned CHANGES REQUIRED (4 min) | |
| T01 | 05:10 | spec-fidelity-verify returned NOT-REVIEWABLE (1 min) | |
| T01 | 05:20 | ticked | |
| T02 | 05:21 | started (`make task-start`) | |
| T02 | 05:43 | source-reader returned findings (1 min) | |
| T02 | 05:43 | source-reader returned findings (1 min) | |
| T02 | 05:43 | source-reader returned findings (1 min) | |
| T02 | 05:43 | source-reader returned findings (2 min) | |
| T02 | 05:43 | source-reader returned findings (2 min) | |
| T02 | 05:44 | source-reader returned findings (2 min) | |
| T02 | 05:44 | source-reader returned findings (2 min) | |
| T02 | 05:44 | source-reader returned findings (2 min) | |
| T02 | 05:44 | source-reader returned findings (3 min) | |
| T02 | 05:48 | source-reader returned findings (7 min) | |
| T02 | 06:15 | source-reader returned findings (1 min) | |
| T02 | 06:15 | source-reader returned findings (1 min) | |
| T02 | 06:15 | source-reader returned findings (1 min) | |
| T02 | 06:15 | source-reader returned findings (1 min) | |
| T02 | 06:16 | source-reader returned findings (1 min) | |
| T02 | 06:16 | source-reader returned findings (1 min) | |
| T02 | 06:16 | source-reader returned findings (2 min) | |
| T02 | 06:16 | source-reader returned findings (2 min) | |
| T02 | 06:17 | source-reader returned findings (2 min) | |
| T02 | 06:17 | source-reader returned findings (2 min) | |
| T02 | 06:17 | source-reader returned findings (2 min) | |
| T02 | 06:31 | source-reader returned findings (3 min) | |
| T02 | 06:38 | intro-check returned clean (0 min) | |
| T02 | 06:39 | intro-check returned findings (0 min) | |
| T02 | 06:39 | source-reader returned clean (1 min) | |
| T02 | 06:39 | source-reader returned findings (1 min) | |
| T02 | 06:40 | source-reader returned findings (1 min) | |
| T02 | 06:40 | translation-check returned FAITHFUL (1 min) | |
| T02 | 06:40 | source-reader returned findings (1 min) | |
| T02 | 06:40 | source-reader returned findings (1 min) | |
| T02 | 06:40 | source-reader returned findings (2 min) | |
| T02 | 06:40 | source-reader returned findings (2 min) | |
| T02 | 06:41 | source-reader returned findings (2 min) | |
| T02 | 06:41 | record-format returned findings (3 min) | |
| T02 | 06:41 | source-reader returned findings (3 min) | |
| T02 | 06:41 | source-reader returned findings (3 min) | |
| T02 | 06:42 | record-format returned findings (4 min) | |
| T02 | 06:42 | quote-check returned findings (4 min) | |
| T02 | 06:42 | translation-check returned FAITHFUL (4 min) | |
| T02 | 06:43 | quote-check returned findings (4 min) | |
| T02 | 06:43 | source-reader returned findings (4 min) | |
| T02 | 06:43 | source-reader returned findings (5 min) | |
| T02 | 06:45 | quote-check returned findings (7 min) | |
| T02 | 06:47 | quote-check returned findings (9 min) | |
| T02 | 06:49 | source-reader returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (1 min) | |
| T02 | 06:49 | source-reader returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (2 min) | |
| T02 | 06:49 | source-applicability returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (1 min) | |
| T02 | 06:49 | source-applicability returned findings (2 min) | |
| T02 | 06:49 | source-reader returned findings (2 min) | |
| T02 | 06:49 | source-applicability returned findings (2 min) | |
| T02 | 06:50 | source-applicability returned findings (2 min) | |
| T02 | 06:50 | source-applicability returned findings (2 min) | |
| T02 | 06:50 | source-applicability returned findings (2 min) | |
| T02 | 06:50 | source-applicability returned findings (2 min) | |
| T02 | 06:50 | source-applicability returned findings (3 min) | |
| T02 | 06:51 | source-applicability returned findings (3 min) | |
| T02 | 06:52 | source-applicability returned findings (4 min) | |
| T02 | 06:52 | source-applicability returned findings (4 min) | |
| T02 | 06:52 | source-applicability returned findings (4 min) | |
| T02 | 06:53 | source-applicability returned findings (1 min) | |
| T02 | 06:54 | source-applicability returned findings (1 min) | |
| T02 | 06:54 | source-applicability returned findings (2 min) | |
| T02 | 06:54 | source-applicability returned findings (2 min) | |
| T02 | 06:54 | source-applicability returned findings (2 min) | |
| T02 | 06:54 | source-applicability returned findings (2 min) | |
| T02 | 06:54 | source-applicability returned findings (2 min) | |
| T02 | 06:56 | source-applicability returned findings (3 min) | |
| T02 | 06:56 | source-applicability returned findings (4 min) | |
| T02 | 06:56 | source-applicability returned findings (4 min) | |
| T02 | 06:58 | source-applicability returned findings (6 min) | |
| T02 | 07:08 | translation-check returned FAITHFUL (1 min) | |
| T02 | 07:08 | source-reader returned findings (1 min) | |
| T02 | 07:08 | source-reader returned findings (1 min) | |
| T02 | 07:09 | translation-check returned FAITHFUL (2 min) | |
| T02 | 07:09 | record-format returned findings (2 min) | |
| T02 | 07:09 | source-applicability returned findings (1 min) | |
| T02 | 07:09 | source-reader returned findings (2 min) | |
| T02 | 07:09 | source-applicability returned findings (2 min) | |
| T02 | 07:09 | source-reader returned findings (2 min) | |
| T02 | 07:09 | source-applicability returned findings (2 min) | |
| T02 | 07:09 | source-reader returned findings (2 min) | |
| T02 | 07:09 | record-format returned findings (2 min) | |
| T02 | 07:10 | source-reader returned findings (2 min) | |
| T02 | 07:10 | source-applicability returned findings (3 min) | |
| T02 | 07:10 | source-applicability returned findings (3 min) | |
| T02 | 07:10 | source-applicability returned findings (3 min) | |
| T02 | 07:10 | source-applicability returned findings (3 min) | |
| T02 | 07:10 | quote-check returned findings (3 min) | |
| T02 | 07:13 | source-reader returned findings (6 min) | |
| T02 | 07:13 | quote-check returned findings (6 min) | |
| T02 | 07:15 | source-applicability returned findings (1 min) | |
| T02 | 07:17 | source-applicability returned clean (3 min) | |
| T02 | 07:17 | source-applicability returned findings (3 min) | |
| T02 | 07:25 | translation-check returned FAITHFUL (1 min) | |
| T02 | 07:25 | source-reader returned findings (1 min) | |
| T02 | 07:25 | translation-check returned FAITHFUL (1 min) | |
| T02 | 07:26 | record-format returned findings (2 min) | |
| T02 | 07:26 | source-applicability returned (2 min) | |
| T02 | 07:26 | source-applicability returned (2 min) | |
| T02 | 07:26 | record-format returned findings (2 min) | |
| T02 | 07:26 | source-applicability returned (2 min) | |
| T02 | 07:27 | source-applicability returned (3 min) | |
| T02 | 07:27 | translation-check returned FAITHFUL (0 min) | |
| T02 | 07:27 | source-applicability returned (3 min) | |
| T02 | 07:28 | quote-check returned findings (1 min) | |
| T02 | 07:28 | source-applicability returned (4 min) | |
| T02 | 07:29 | source-applicability returned (5 min) | |
| T02 | 07:32 | ticked | |
| T03 | 07:32 | started (`make task-start`) | |
| T03 | 07:52 | source-reader returned findings (1 min) | |
| T03 | 07:52 | source-reader returned findings (1 min) | |
| T03 | 07:53 | source-reader returned findings (2 min) | |
| T03 | 07:54 | source-reader returned findings (3 min) | |
| T03 | 07:55 | source-reader returned findings (5 min) | |
| T03 | 07:56 | source-reader returned findings (1 min) | |
| T03 | 07:56 | source-reader returned findings (1 min) | |
| T03 | 07:56 | source-reader returned findings (1 min) | |
| T03 | 07:56 | source-reader returned findings (1 min) | |
| T03 | 07:58 | source-reader returned findings (2 min) | |
| T03 | 08:28 | source-reader returned findings (0 min) | |
| T03 | 08:28 | source-reader returned findings (1 min) | |
| T03 | 08:28 | source-reader returned findings (1 min) | |
| T03 | 08:28 | source-reader returned findings (1 min) | |
| T03 | 08:28 | source-reader returned findings (1 min) | |
| T03 | 08:29 | source-reader returned findings (1 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:29 | source-reader returned findings (2 min) | |
| T03 | 08:30 | source-reader returned findings (3 min) | |
| T03 | 08:30 | source-reader returned findings (3 min) | |
| T03 | 08:32 | source-reader returned findings (5 min) | |
| T03 | 08:37 | source-reader returned clean (1 min) | |
| T03 | 08:37 | source-reader returned findings (1 min) | |
| T03 | 08:38 | source-reader returned findings (1 min) | |
| T03 | 08:38 | source-reader returned clean (1 min) | |
| T03 | 08:38 | source-reader returned findings (1 min) | |
| T03 | 08:40 | source-reader returned findings (3 min) | |
| T03 | 08:41 | source-reader returned findings (4 min) | |
| T03 | 08:51 | source-reader returned findings (0 min) | |
| T03 | 08:51 | intro-check returned clean (0 min) | |
| T03 | 08:51 | intro-check returned clean (0 min) | |
| T03 | 08:51 | source-reader returned clean (0 min) | |
| T03 | 08:51 | source-reader returned findings (1 min) | |
| T03 | 08:51 | source-reader returned clean (0 min) | |
| T03 | 08:51 | translation-check returned FAITHFUL (0 min) | |
| T03 | 08:51 | source-reader returned clean (1 min) | |
| T03 | 08:52 | translation-check returned FAITHFUL (1 min) | |
| T03 | 08:53 | source-applicability returned findings (2 min) | |
| T03 | 08:53 | record-format returned findings (2 min) | |
| T03 | 08:53 | source-applicability returned findings (2 min) | |
| T03 | 08:53 | source-applicability returned findings (3 min) | |
| T03 | 08:54 | source-applicability returned findings (3 min) | |
| T03 | 08:55 | quote-check returned findings (4 min) | |
| T03 | 08:56 | record-format returned findings (6 min) | |
| T03 | 08:59 | quote-check returned findings (8 min) | |
| T03 | 08:59 | quote-check returned findings (8 min) | |
| T03 | 08:59 | quote-check returned findings (8 min) | |
| T03 | 09:00 | quote-check returned findings (10 min) | |
| T03 | 09:01 | source-applicability returned findings (1 min) | |
| T03 | 09:01 | source-applicability returned findings (1 min) | |
| T03 | 09:01 | source-applicability returned findings (1 min) | |
| T03 | 09:01 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (2 min) | |
| T03 | 09:02 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (1 min) | |
| T03 | 09:02 | source-applicability returned findings (2 min) | |
| T03 | 09:02 | source-applicability returned findings (2 min) | |
| T03 | 09:02 | source-applicability returned findings (2 min) | |
| T03 | 09:02 | source-applicability returned findings (2 min) | |
| T03 | 09:03 | source-applicability returned findings (3 min) | |
| T03 | 09:03 | source-applicability returned findings (3 min) | |
| T03 | 09:05 | source-applicability returned findings (5 min) | |
| T03 | 09:05 | source-applicability returned findings (5 min) | |
| T03 | 09:15 | source-reader returned clean (0 min) | |
| T03 | 09:15 | source-reader returned findings (0 min) | |
| T03 | 09:16 | source-applicability returned findings (1 min) | |
| T03 | 09:17 | source-applicability returned findings (2 min) | |
| T03 | 09:18 | source-applicability returned findings (4 min) | |
| T03 | 09:18 | source-reader returned findings (3 min) | |
| T03 | 09:19 | source-applicability returned findings (4 min) | |
| T03 | 09:19 | source-applicability returned findings (4 min) | |
| T03 | 09:21 | quote-check returned findings (6 min) | |
| T03 | 09:24 | quote-check returned findings (9 min) | |
| T03 | 09:25 | translation-check returned FAITHFUL (0 min) | |
| T03 | 09:25 | translation-check returned FAITHFUL (1 min) | |
| T03 | 09:25 | record-format returned clean (1 min) | |
| T03 | 09:26 | record-format returned findings (2 min) | |
| T03 | 09:32 | round-arbiter returned findings (5 min) | |
| T03 | 09:32 | source-reader returned findings (0 min) | |
| T03 | 09:32 | source-reader returned clean (0 min) | |
| T03 | 09:32 | source-reader returned clean (1 min) | |
| T03 | 09:32 | source-reader returned findings (1 min) | |
| T03 | 09:32 | source-reader returned findings (0 min) | |
| T03 | 09:32 | source-reader returned findings (1 min) | |
| T03 | 09:32 | source-reader returned findings (1 min) | |
| T03 | 09:33 | source-reader returned clean (1 min) | |
| T03 | 09:37 | source-reader returned findings (5 min) | |
| T03 | 09:48 | escalation-check returned findings (5 min) | |
| T03 | 09:50 | record-format returned clean (1 min) | |
| T03 | 09:50 | source-reader returned findings (1 min) | |
| T03 | 09:50 | source-applicability returned findings (1 min) | |
| T03 | 09:51 | record-format returned findings (2 min) | |
| T03 | 09:52 | translation-check returned FAITHFUL (3 min) | |
| T03 | 09:53 | source-applicability returned findings (4 min) | |
| T03 | 09:53 | translation-check returned FAITHFUL (0 min) | |
| T03 | 09:54 | record-format returned findings (1 min) | |
| T03 | 09:56 | round-arbiter returned findings (3 min) | |
| T03 | 09:58 | ticked | |
| T04 | 09:58 | started (`make task-start`) | |
| T04 | 10:00 | escalation-check returned findings (1 min) | |
| T04 | 10:16 | source-reader returned findings (1 min) | |
| T04 | 10:16 | source-reader returned findings (1 min) | |
| T04 | 10:18 | source-reader returned findings (3 min) | |
| T04 | 10:19 | source-reader returned findings (4 min) | |
| T04 | 10:20 | source-reader returned findings (1 min) | |
| T04 | 10:20 | source-reader returned findings (1 min) | |
| T04 | 10:20 | source-reader returned findings (1 min) | |
| T04 | 10:20 | source-reader returned findings (1 min) | |
| T04 | 10:21 | source-reader returned findings (1 min) | |
| T04 | 10:21 | source-reader returned findings (1 min) | |
| T04 | 10:45 | source-reader returned findings (0 min) | |
| T04 | 10:45 | source-reader returned findings (1 min) | |
| T04 | 10:45 | source-reader returned findings (1 min) | |
| T04 | 10:45 | source-reader returned findings (1 min) | |
| T04 | 10:45 | source-reader returned findings (1 min) | |
| T04 | 10:45 | source-reader returned findings (1 min) | |
| T04 | 10:46 | source-reader returned findings (1 min) | |
| T04 | 10:46 | source-reader returned findings (1 min) | |
| T04 | 10:46 | source-reader returned findings (2 min) | |
| T04 | 10:47 | source-reader returned findings (2 min) | |
| T04 | 10:47 | source-reader returned findings (2 min) | |
| T04 | 10:47 | source-reader returned findings (2 min) | |
| T04 | 10:47 | source-reader returned findings (3 min) | |
| T04 | 10:47 | source-reader returned findings (3 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned clean (0 min) | |
| T04 | 11:19 | source-reader returned clean (0 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:19 | source-reader returned findings (1 min) | |
| T04 | 11:20 | source-reader returned findings (2 min) | |
| T04 | 11:20 | source-reader returned findings (1 min) | |
| T04 | 11:20 | source-reader returned findings (2 min) | |
| T04 | 11:20 | source-reader returned findings (2 min) | |
| T04 | 11:21 | source-reader returned findings (3 min) | |
| T04 | 11:21 | source-reader returned findings (3 min) | |
| T04 | 11:22 | source-reader returned findings (4 min) | |
| T04 | 11:33 | intro-check returned findings (0 min) | |
| T04 | 11:33 | intro-check returned clean (0 min) | |
| T04 | 11:33 | intro-check returned findings (0 min) | |
| T04 | 11:34 | translation-check returned FAITHFUL (1 min) | |
| T04 | 11:34 | translation-check returned FAITHFUL (2 min) | |
| T04 | 11:35 | quote-check returned findings (3 min) | |
| T04 | 11:36 | quote-check returned findings (3 min) | |
| T04 | 11:36 | quote-check returned findings (3 min) | |
| T04 | 11:36 | quote-check returned findings (3 min) | |
| T04 | 11:36 | quote-check returned findings (3 min) | |
| T04 | 11:36 | record-format returned findings (3 min) | |
| T04 | 11:36 | record-format returned findings (3 min) | |
| T04 | 11:37 | translation-check returned FAITHFUL (4 min) | |
| T04 | 11:38 | quote-check returned findings (5 min) | |
| T04 | 11:38 | record-format returned findings (5 min) | |
| T04 | 11:40 | quote-check returned findings (7 min) | |
| T04 | 11:40 | quote-check returned findings (7 min) | |
| T04 | 11:41 | quote-check returned findings (8 min) | |
| T04 | 11:41 | source-reader returned clean (0 min) | |
| T04 | 11:42 | source-reader returned clean (1 min) | |
| T04 | 11:42 | source-reader returned findings (1 min) | |
| T04 | 11:43 | source-applicability returned findings (1 min) | |
| T04 | 11:43 | source-applicability returned findings (2 min) | |
| T04 | 11:43 | source-applicability returned findings (2 min) | |
| T04 | 11:44 | source-applicability returned findings (3 min) | |
| T04 | 11:45 | source-reader returned findings (4 min) | |
| T04 | 11:45 | source-applicability returned findings (4 min) | |
| T04 | 11:45 | source-applicability returned findings (4 min) | |
| T04 | 11:45 | source-applicability returned findings (4 min) | |
| T04 | 11:46 | source-applicability returned findings (4 min) | |
| T04 | 11:50 | source-applicability returned findings (9 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | round-arbiter returned findings (2 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (2 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (1 min) | |
| T04 | 11:52 | source-applicability returned findings (2 min) | |
| T04 | 11:52 | source-applicability returned findings (2 min) | |
| T04 | 11:53 | source-applicability returned findings (2 min) | |
| T04 | 11:53 | source-applicability returned findings (2 min) | |
| T04 | 11:53 | source-applicability returned findings (2 min) | |
| T04 | 11:53 | source-applicability returned findings (2 min) | |
| T04 | 11:53 | source-applicability returned findings (3 min) | |
| T04 | 11:54 | source-applicability returned findings (3 min) | |
| T04 | 11:55 | source-applicability returned findings (4 min) | |
| T04 | 12:08 | translation-check returned FAITHFUL (1 min) | |
| T04 | 12:08 | source-reader returned clean (0 min) | |
| T04 | 12:08 | source-reader returned clean (0 min) | |
| T04 | 12:08 | source-reader returned clean (0 min) | |
| T04 | 12:08 | source-reader returned clean (0 min) | |
| T04 | 12:09 | source-reader returned clean (1 min) | |
| T04 | 12:09 | record-format returned findings (1 min) | |
| T04 | 12:09 | translation-check returned FAITHFUL (1 min) | |
| T04 | 12:09 | source-reader returned findings (1 min) | |
| T04 | 12:09 | record-format returned findings (2 min) | |
| T04 | 12:10 | record-format returned findings (2 min) | |
| T04 | 12:10 | source-applicability returned findings (2 min) | |
| T04 | 12:11 | translation-check returned FAITHFUL (3 min) | |
| T04 | 12:11 | quote-check returned findings (3 min) | |
| T04 | 12:11 | source-reader returned findings (3 min) | |
| T04 | 12:11 | source-applicability returned findings (4 min) | |
| T04 | 12:12 | source-applicability returned findings (4 min) | |
| T04 | 12:13 | quote-check returned findings (6 min) | |
| T04 | 12:14 | quote-check returned findings (6 min) | |
| T04 | 12:22 | escalation-check returned findings (1 min) | |
| T04 | 12:24 | translation-check returned FAITHFUL (1 min) | |
| T04 | 12:25 | record-format returned findings (1 min) | |
| T04 | 12:25 | translation-check returned FAITHFUL (1 min) | |
| T04 | 12:25 | record-format returned findings (1 min) | |
| T04 | 12:25 | source-reader returned (1 min) | |
| T04 | 12:26 | source-reader returned (1 min) | |
| T04 | 12:26 | source-reader returned (1 min) | |
| T04 | 12:26 | source-reader returned (1 min) | |
| T04 | 12:27 | record-format returned findings (4 min) | |
| T04 | 12:29 | source-applicability returned findings (5 min) | |
| T04 | 12:30 | round-arbiter returned findings (6 min) | |
| T04 | 12:31 | ticked | |
| T05 | 12:32 | started (`make task-start`) | |
| T05 | 12:53 | source-reader returned clean (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:53 | source-reader returned findings (1 min) | |
| T05 | 12:54 | source-reader returned findings (2 min) | |
| T05 | 12:55 | source-reader returned findings (3 min) | |
| T05 | 12:56 | source-reader returned findings (4 min) | |
| T05 | 12:56 | source-reader returned findings (4 min) | |
| T05 | 13:22 | intro-check returned clean (0 min) | |
| T05 | 13:23 | source-applicability returned findings (1 min) | |
| T05 | 13:23 | source-reader returned findings (1 min) | |
| T05 | 13:23 | source-applicability returned findings (1 min) | |
| T05 | 13:23 | source-applicability returned findings (1 min) | |
| T05 | 13:23 | source-reader returned findings (2 min) | |
| T05 | 13:23 | source-applicability returned findings (1 min) | |
| T05 | 13:24 | source-reader returned findings (2 min) | |
| T05 | 13:24 | translation-check returned FAITHFUL (2 min) | |
| T05 | 13:24 | source-reader returned findings (2 min) | |
| T05 | 13:24 | source-applicability returned findings (2 min) | |
| T05 | 13:24 | source-reader returned findings (3 min) | |
| T05 | 13:26 | source-reader returned findings (5 min) | |
| T05 | 13:27 | record-format returned findings (5 min) | |
| T05 | 13:28 | quote-check returned findings (7 min) | |
| T05 | 13:39 | source-applicability returned findings (1 min) | |
| T05 | 13:40 | source-applicability returned findings (1 min) | |
| T05 | 13:41 | source-applicability returned findings (2 min) | |
| T05 | 13:41 | source-applicability returned findings (2 min) | |
| T05 | 13:41 | source-applicability returned clean (2 min) | |
| T05 | 13:47 | round-arbiter returned findings (5 min) | |
| T05 | 13:48 | source-reader returned findings (0 min) | |
| T05 | 13:49 | source-reader returned findings (1 min) | |
| T05 | 13:49 | source-reader returned findings (1 min) | |
| T05 | 13:49 | translation-check returned FAITHFUL (1 min) | |
| T05 | 13:52 | record-format returned findings (4 min) | |
| T05 | 13:54 | quote-check returned findings (6 min) | |
| T05 | 14:02 | source-reader returned findings (1 min) | |
| T05 | 14:02 | source-reader returned findings (1 min) | |
| T05 | 14:02 | intro-check returned clean (1 min) | |
| T05 | 14:02 | source-reader returned findings (1 min) | |
| T05 | 14:02 | translation-check returned FAITHFUL (1 min) | |
| T05 | 14:02 | source-reader returned clean (1 min) | |
| T05 | 14:02 | translation-check returned FAITHFUL (1 min) | |
| T05 | 14:03 | intro-check returned findings (1 min) | |
| T05 | 14:05 | record-format returned findings (3 min) | |
| T05 | 14:06 | record-format returned findings (4 min) | |
| T05 | 14:06 | quote-check returned findings (5 min) | |
| T05 | 14:09 | quote-check returned findings (8 min) | |
| T05 | 14:10 | source-applicability returned findings (1 min) | |
| T05 | 14:11 | source-applicability returned findings (1 min) | |
| T05 | 14:11 | source-applicability returned findings (1 min) | |
| T05 | 14:11 | source-applicability returned findings (2 min) | |
| T05 | 14:11 | source-applicability returned findings (2 min) | |
| T05 | 14:11 | source-applicability returned findings (2 min) | |
| T05 | 14:11 | source-applicability returned findings (2 min) | |
| T05 | 14:11 | source-applicability returned findings (2 min) | |
| T05 | 14:12 | source-applicability returned findings (2 min) | |
| T05 | 14:12 | source-applicability returned findings (2 min) | |
| T05 | 14:18 | translation-check returned FAITHFUL (0 min) | |
| T05 | 14:18 | translation-check returned FAITHFUL (0 min) | |
| T05 | 14:19 | record-format returned findings (1 min) | |
| T05 | 14:19 | record-format returned findings (1 min) | |
| T05 | 14:20 | quote-check returned findings (2 min) | |
| T05 | 14:20 | source-reader returned findings (2 min) | |
| T05 | 14:21 | round-arbiter returned findings (3 min) | |
| T05 | 14:21 | source-applicability returned findings (3 min) | |
| T05 | 14:21 | quote-check returned findings (3 min) | |
| T05 | 14:24 | record-format returned findings (0 min) | |
| T05 | 14:29 | ticked | |
| T06 | 14:30 | started (`make task-start`) | |

## What each check cost, per changed line (4884 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 38 | 3 h 18 min | 24147k | 764.3k | 0.008 | 4.9k |
| source-reader | 203 | 5 h 17 min | 23898k | 1612.2k | 0.042 | 4.9k |
| source-applicability | 136 | 5 h 10 min | 21373k | 1109.8k | 0.028 | 4.4k |
| record-format | 32 | 1 h 21 min | 6452k | 398.7k | 0.007 | 1.3k |
| translation-check | 29 | 38 min | 2212k | 208.5k | 0.006 | 0.5k |
| spec-fidelity | 6 | 24 min | 1934k | 103.0k | 0.001 | 0.4k |
| escalation-check | 4 | 7 min | 517k | 32.5k | 0.001 | 0.1k |
| intro-check | 11 | 4 min | 243k | 15.2k | 0.002 | 0.0k |
| impl-drift | 1 | 4 min | 144k | 8.2k | 0.000 | 0.0k |
| spec-fidelity-verify | 1 | 1 min | 89k | 6.2k | 0.000 | 0.0k |

This report took 5.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
