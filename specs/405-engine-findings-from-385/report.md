# Feature report - 405-engine-findings-from-385

Written by `make feature-report F=405` from 12710 events (2026-10-19T23:09 to 2026-10-25T02:25 UTC), 385 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 79 h 59 min | - |
| thinking | 26 h 09 min | 58% |
| other tool | 12 h 24 min | 27% |
| waiting: subagent | 2 h 18 min | 5% |
| waiting: the GM | 1 h 14 min | 3% |
| waiting: a background run | 33 min | 1% |
| waiting: modal-depiction | 33 min | 1% |
| waiting: research-pass | 25 min | 1% |
| test file | 22 min | 1% |
| dispatching: spec review | 17 min | 1% |
| dispatching: claims check | 17 min | 1% |
| waiting: source-applicability | 10 min | 0% |
| edit | 7 min | 0% |
| waiting: quote-check | 7 min | 0% |
| writing the spec | 5 min | 0% |
| waiting: impl-drift | 4 min | 0% |
| waiting: record-format | 3 min | 0% |
| waiting: claims-triage | 3 min | 0% |
| waiting: source-reader | 3 min | 0% |
| quick test | 2 min | 0% |
| waiting: modal-triage | 2 min | 0% |
| waiting: round-arbiter | 2 min | 0% |
| gate | 1 min | 0% |
| waiting: spec-fidelity | 1 min | 0% |
| waiting: translation-check | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| spec-kit step | 0 min | 0% |

The session's own time above; its 1770 subagent tool call(s) (of 5457) are counted apart (0 by the subagent transcripts, 1741 by the hook's `by`, 29 by the agents' windows - an estimate; plan D30). The subagents' own work: 391 run(s), 8 h 34 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 6 h 27 min |
| make land | 50 min |
| make ledger-owed | 43 min |
| make cohort | 25 min |
| make task-start | 10 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| spec-fidelity | 121 | BLOCKED 14, CHANGES REQUIRED 1, CLEAR 100 |
| impl-drift | 113 | findings 103 |
| claims-triage | 46 | findings 24 |
| quote-check | 21 | clean 2, findings 17 |
| record-format | 21 | PASS 1, findings 18 |
| modal-depiction | 18 | clean 9, findings 7 |
| round-arbiter | 14 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 2, findings 8 |
| source-reader | 14 | clean 3, findings 11 |
| modal-triage | 7 | findings 7 |
| source-applicability | 7 | findings 7 |
| research-pass | 4 | findings 3 |
| translation-check | 3 | FAITHFUL 3 |
| general-purpose | 1 | findings 1 |
| intro-check | 1 | findings 1 |
| spec-fidelity-verify | 1 | FAITHFUL 1, findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-owed | 69 |
| claims-triage | claims-triage | 46 |
| modal-triage | modal-triage-diagram-backlog-pages | 7 |
| modal-depiction | modal-batch | 6 |
| record-format | q-0246 | 4 |
| quote-check | q-0246 | 3 |
| spec-fidelity | plan-405-engine-findings-from-385-T26 | 3 |
| impl-drift | claims-owed-b10b | 2 |
| impl-drift | claims-owed-b7c | 2 |
| impl-drift | claims-owed-b9e | 2 |
| modal-depiction | modal-hamlet-village-lane | 2 |
| modal-depiction | modal-sheet-road | 2 |
| quote-check | batch-1 | 2 |
| quote-check | p405-0196 | 2 |
| quote-check | q-0014 | 2 |
| quote-check | q-0084 | 2 |
| quote-check | q-0284 | 2 |
| quote-check | q-0285 | 2 |
| record-format | q-0014 | 2 |
| record-format | q-0081 | 2 |
| record-format | q-0084 | 2 |
| record-format | q-0196 | 2 |
| record-format | q-0284 | 2 |
| record-format | q-0285 | 2 |
| source-applicability | key-mencius-14-21-chinakongzi | 2 |
| source-applicability | key-tang-code-juan26-wikisource | 2 |
| source-reader | key-buck-1930-farm-economy-whole | 2 |
| source-reader | key-miyashiro-hyakken-honmura-shiryo-whole | 2 |
| source-reader | key-ushijima-2020-manchu-whole | 2 |
| spec-fidelity | plan-385-approach-checklist-T11 | 2 |
| spec-fidelity | plan-405-engine-findings-from-385-T12 | 2 |
| spec-fidelity | plan-405-engine-findings-from-385-blocks-plan-9de1422c | 2 |
| translation-check | q-0285 | 2 |

## Process signals

- gates: already-verified 1, green 22, red 5
- spec rounds: none recorded
- plan reviews BLOCKED: 108 recorded in commits, 14 returned
- reversals (A -> B -> A): 0
- check dispatches 198 over 13272 changed lines: cascade ratio 0.01
- tasks ticked: 130 of 167

## Tripwires (FR-010) - what fired, or would have

- 03:30 round:impl-drift|claims-owed@3
- 03:34 round:impl-drift|claims-owed@4
- 03:37 round:impl-drift|claims-owed@5
- 04:47 round:impl-drift|claims-owed@6
- 11:31 round:impl-drift|claims-owed@7
- 12:02 round:impl-drift|claims-owed@8
- 12:33 round:impl-drift|claims-owed@9
- 13:03 round:impl-drift|claims-owed@10
- 13:35 round:impl-drift|claims-owed@11
- 13:55 round:impl-drift|claims-owed@12
- 14:03 round:impl-drift|claims-owed@13
- 14:24 round:impl-drift|claims-owed@14
- 14:30 round:impl-drift|claims-owed@15
- 14:44 round:impl-drift|claims-owed@16
- 14:55 round:impl-drift|claims-owed@17
- 14:57 round:impl-drift|claims-owed@18
- 14:59 round:impl-drift|claims-owed@19
- 15:13 round:impl-drift|claims-owed@20
- 04:31 round:impl-drift|claims-owed@21
- 04:34 round:impl-drift|claims-owed@22
- 08:45 round:impl-drift|claims-owed@23
- 09:10 round:impl-drift|claims-owed@24
- 09:29 round:impl-drift|claims-owed@25
- 09:32 round:impl-drift|claims-owed@26
- 09:34 round:impl-drift|claims-owed@27
- 09:36 round:impl-drift|claims-owed@28
- 09:41 round:impl-drift|claims-owed@29
- 09:48 round:impl-drift|claims-owed@30
- 09:53 round:impl-drift|claims-owed@31
- 09:59 round:impl-drift|claims-owed@32
- 10:07 round:impl-drift|claims-owed@33
- 10:09 round:impl-drift|claims-owed@34
- 10:21 round:impl-drift|claims-owed@35
- 10:22 round:impl-drift|claims-owed@36
- 10:24 round:impl-drift|claims-owed@37
- 12:57 round:impl-drift|claims-owed@38
- 13:09 round:impl-drift|claims-owed@39
- 13:18 round:impl-drift|claims-owed@40
- 13:26 round:modal-depiction|modal-batch@3
- 13:27 round:impl-drift|claims-owed@41
- 13:28 round:modal-depiction|modal-batch@4
- 13:30 round:impl-drift|claims-owed@42
- 13:33 round:impl-drift|claims-owed@43
- 14:07 round:impl-drift|claims-owed@44
- 14:29 round:impl-drift|claims-owed@45
- 14:53 round:impl-drift|claims-owed@46
- 15:05 round:impl-drift|claims-owed@47
- 15:09 round:record-format|q-0246@3
- 15:20 round:impl-drift|claims-owed@48
- 15:27 round:modal-depiction|modal-batch@5
- 15:30 round:modal-depiction|modal-batch@6
- 16:04 round:impl-drift|claims-owed@49
- 05:18 round:impl-drift|claims-owed@50
- 05:33 round:impl-drift|claims-owed@51
- 09:43 round:impl-drift|claims-owed@52
- 09:57 round:impl-drift|claims-owed@53
- 10:07 round:impl-drift|claims-owed@54
- 11:31 round:impl-drift|claims-owed@55
- 11:34 round:impl-drift|claims-owed@56
- 11:39 round:impl-drift|claims-owed@57
- 11:46 round:impl-drift|claims-owed@58
- 13:58 round:impl-drift|claims-owed@59
- 14:02 round:impl-drift|claims-owed@60
- 00:05 round:impl-drift|claims-owed@61
- 00:07 round:impl-drift|claims-owed@62

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T12 | 34 min | 25 min | 8 min | 6 | 2, 2, 0, 4, 16, 2, 8 |
| T32 | 27 min | 24 min | 3 min | 2 | 4, 20, 3 |
| T14 | 38 min | 11 min | 26 min | 2 | 6, 5, 26 |
| T36 | 24 min | 23 min | 1 min | 3 | 4, 4, 15, 1 |
| T11 | 35 min | 22 min | 14 min | 2 | 2, 20, 14 |
| T43 | 14 min | 12 min | 2 min | 4 | 3, 3, 0, 6, 2 |
| T19 | 12 min | 2 min | 10 min | 1 | 2, 10 |
| T48 | 5 min | 3 min | 2 min | 1 | 3, 2 |
| T13 | 9 min | 2 min | 7 min | 1 | 2, 7 |
| T50 | 6 min | 3 min | 3 min | 1 | 3, 3 |
| T49 | 8 min | 1 min | 6 min | 1 | 1, 6 |
| T52 | 3 min | 2 min | 1 min | 1 | 2, 1 |
| T53 | 3 min | 1 min | 2 min | 1 | 1, 2 |
| T17 | 48 min | 43 min | 4 min | 6 | 1, 26, 2, 3, 2, 9, 4 |
| T29 | 10 min | 8 min | 2 min | 3 | 6, 1, 1, 2 |
| T62 | 9 min | 2 min | 7 min | 1 | 2, 7 |
| T72 | 21 min | 11 min | 10 min | 2 | 7, 4, 10 |
| T64 | 17 min | 7 min | 10 min | 2 | 3, 4, 10 |
| T55 | 26 min | 17 min | 8 min | 1 | 17, 8 |
| T74 | 30 min | 19 min | 11 min | 5 | 7, 2, 7, 2, 1, 11 |
| T81 | 38 min | 14 min | 24 min | 2 | 6, 8, 24 |
| T82 | 37 min | 13 min | 24 min | 2 | 4, 8, 24 |
| T20 | 35 min | 11 min | 24 min | 2 | 2, 8, 24 |
| T54 | 1 h 04 min | 54 min | 10 min | 5 | 3, 7, 20, 4, 21, 10 |
| T83 | 1 h 04 min | 54 min | 10 min | 5 | 2, 7, 20, 4, 21, 10 |
| T84 | 1 h 04 min | 54 min | 10 min | 5 | 2, 7, 20, 4, 21, 10 |
| T85 | 1 h 04 min | 54 min | 10 min | 5 | 2, 7, 20, 4, 21, 10 |
| T87 | 1 h 04 min | 54 min | 10 min | 5 | 2, 7, 20, 4, 21, 10 |
| T90 | 33 min | 23 min | 10 min | 2 | 1, 21, 10 |
| T18 | 55 min | 39 min | 15 min | 3 | 6, 5, 28, 15 |
| T86 | 55 min | 39 min | 15 min | 3 | 6, 5, 28, 15 |
| T89 | 55 min | 39 min | 15 min | 3 | 6, 5, 28, 15 |
| T22 | 55 min | 39 min | 15 min | 3 | 6, 5, 28, 15 |
| T23 | 55 min | 39 min | 15 min | 3 | 6, 5, 28, 15 |
| T95 | 54 min | 36 min | 18 min | 6 | 1, 10, 6, 6, 10, 4, 18 |
| T96 | 54 min | 36 min | 18 min | 6 | 1, 10, 6, 6, 10, 4, 18 |
| T97 | 54 min | 36 min | 18 min | 6 | 1, 10, 6, 6, 10, 4, 18 |
| T100 | 54 min | 36 min | 18 min | 6 | 1, 10, 6, 6, 10, 4, 18 |
| T26 | 67 h 23 min | 67 h 07 min | 16 min | 64 | 1, 11, 12, 6, 4, 24, 24, 475, 5, 6, 25, 226, 15, 13, 19, 11, 6, 2, 4, 5, 8, 13, 120, 22, 8, 8, 12, 9, 9, 24, 17, 11, 11, 7, 16, 13, 14, 15, 6, 3, 8, 13, 14, 3, 16, 9, 2, 7, 682, 4, 5, 49, 17, 6, 242, 18, 10, 1523, 14, 102, 26, 7, 7, 6, 16 |
| T103 | 30 min | 29 min | 1 min | 4 | 1, 11, 12, 6, 1 |
| T105 | 16 min | 1 min | 15 min | 1 | 1, 15 |
| T10 | 18 min | 1 min | 17 min | 1 | 1, 17 |
| T67 | 21 min | 1 min | 20 min | 1 | 1, 20 |
| T107 | 1 h 01 min | 45 min | 15 min | 3 | 35, 5, 6, 15 |
| T91 | 24 min | 18 min | 7 min | 2 | 2, 15, 7 |
| T113 | 8 min | 1 min | 7 min | 1 | 1, 7 |
| T93 | 4 min | 1 min | 3 min | 1 | 1, 3 |
| T115 | 10 min | 1 min | 9 min | 1 | 1, 9 |
| T116 | 12 min | 9 min | 2 min | 3 | 1, 6, 2, 2 |
| T117 | 4 min | 1 min | 2 min | 1 | 1, 2 |
| T118 | 20 min | 10 min | 10 min | 2 | 2, 8, 10 |
| T108 | 13 min | 2 min | 12 min | 1 | 2, 12 |
| T120 | 7 min | 2 min | 5 min | 1 | 2, 5 |
| T102 | 4 min | 1 min | 3 min | 1 | 1, 3 |
| T99 | 3 min | 1 min | 2 min | 1 | 1, 2 |
| T09 | 53 min | 34 min | 19 min | 4 | 4, 12, 9, 9, 19 |
| T114 | 28 min | 18 min | 10 min | 2 | 1, 17, 10 |
| T126 | 11 min | 2 min | 10 min | 1 | 2, 10 |
| T70 | 1 min | 0 min | 1 min | 0 | 1 |
| T119 | 17 min | 11 min | 7 min | 2 | 3, 7, 7 |
| T128 | 9 min | 2 min | 7 min | 1 | 2, 7 |
| T121 | 14 min | 4 min | 9 min | 1 | 4, 9 |
| T124 | 13 min | 3 min | 9 min | 1 | 3, 9 |
| T127 | 58 h 55 min (open) | 57 h 00 min | 1 h 54 min | 31 | 4, 6, 3, 8, 13, 14, 3, 16, 9, 2, 7, 682, 4, 5, 49, 17, 6, 242, 18, 10, 1523, 14, 102, 26, 7, 7, 6, 566, 28, 2, 24, 114 |
| T110 | 1 min | 0 min | 1 min | 0 | 1 |
| T130 | 14 min | 6 min | 7 min | 2 | 3, 3, 7 |
| T129 | 15 min | 12 min | 3 min | 3 | 3, 2, 7, 3 |
| T133 | 5 min | 1 min | 4 min | 1 | 1, 4 |
| T134 | 34 min | 25 min | 9 min | 3 | 3, 17, 6, 9 |
| T07 | 1 h 09 min | 41 min | 28 min | 3 | 13, 18, 10, 28 |
| T135 | 23 min | 15 min | 8 min | 2 | 1, 14, 8 |
| T106 | 6 h 39 min (open) | 4 h 45 min | 1 h 54 min | 4 | 231, 28, 2, 24, 114 |
| T138 | 24 min | 3 min | 21 min | 2 | 1, 2, 21 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T12 | 12:02-12:05 | spec-fidelity | 9 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T12 | 12:05-12:06 | spec-fidelity CLEAR | 9 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T12 | 12:06-12:06 | spec-fidelity CHANGES REQUIRED | 1 | 0 | 0 | 0 | - |
| T12 | 12:06-12:10 | spec-fidelity-verify FAITHFUL | 13 | 4 | 0 | 0 | spec-fidelity-verify x1 (1 min) |
| T12 | 12:10-12:26 | spec-fidelity CLEAR | 31 | 10 | 5 | 0 | claims-triage x1, impl-drift x2, round-arbiter x1, spec-fidelity x1 (4 min) |
| T12 | 12:26-12:28 | round-arbiter CHANGES REQUIRED | 0 | 2 | 0 | 0 | - |
| T12 | 12:28-12:36 | the tick or the last event | 8 | 5 | 3 | 0 | - |
| T32 | 13:41-13:44 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | spec-fidelity x1 (4 min) |
| T32 | 13:44-14:05 | round-arbiter CLEAR | 50 | 18 | 3 | 0 | round-arbiter x1 (2 min) |
| T32 | 14:05-14:07 | the tick or the last event | 3 | 3 | 0 | 0 | - |
| T14 | 03:17-03:24 | spec-fidelity CLEAR | 12 | 6 | 0 | 0 | spec-fidelity x1 (1 min) |
| T14 | 03:24-03:29 | round-arbiter | 18 | 5 | 0 | 0 | claims-triage x1, round-arbiter x1 (2 min) |
| T14 | 03:29-03:55 | the tick or the last event | 83 | 26 | 0 | 0 | claims-triage x1, impl-drift x3 (3 min) |
| T36 | 04:18-04:22 | spec-fidelity BLOCKED | 18 | 4 | 0 | 0 | - |
| T36 | 04:22-04:26 | spec-fidelity CLEAR | 14 | 4 | 0 | 0 | spec-fidelity x1 (3 min) |
| T36 | 04:26-04:41 | round-arbiter BLOCKED | 46 | 15 | 0 | 0 | round-arbiter x1 (1 min) |
| T36 | 04:41-04:42 | the tick or the last event | 2 | 1 | 0 | 0 | - |
| T11 | 04:42-04:44 | spec-fidelity CLEAR | 6 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T11 | 04:44-05:04 | spec-fidelity CLEAR | 41 | 20 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (1 min) |
| T11 | 05:04-05:17 | the tick or the last event | 15 | 14 | 0 | 0 | - |
| T43 | 10:20-10:23 | spec-fidelity BLOCKED | 11 | 3 | 0 | 0 | spec-fidelity x1 (3 min) |
| T43 | 10:23-10:26 | spec-fidelity CLEAR | 15 | 3 | 0 | 0 | round-arbiter x1, spec-fidelity x1 (2 min) |
| T43 | 10:26-10:26 | round-arbiter findings | 1 | 0 | 0 | 0 | - |
| T43 | 10:26-10:32 | spec-fidelity CLEAR | 11 | 6 | 0 | 0 | spec-fidelity x1 (1 min) |
| T43 | 10:32-10:34 | the tick or the last event | 2 | 2 | 0 | 0 | - |
| T19 | 10:34-10:36 | spec-fidelity CLEAR | 9 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T19 | 10:36-10:46 | the tick or the last event | 8 | 7 | 3 | 0 | - |
| T48 | 11:21-11:24 | spec-fidelity CLEAR | 11 | 3 | 0 | 0 | spec-fidelity x1 (3 min) |
| T48 | 11:24-11:27 | the tick or the last event | 2 | 2 | 0 | 0 | - |
| T13 | 11:28-11:30 | spec-fidelity | 8 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T13 | 11:30-11:38 | the tick or the last event | 8 | 4 | 3 | 0 | impl-drift x1 (0 min) |
| T50 | 11:50-11:53 | spec-fidelity CLEAR | 10 | 3 | 0 | 0 | spec-fidelity x1 (3 min) |
| T50 | 11:53-11:56 | the tick or the last event | 4 | 3 | 0 | 0 | - |
| T49 | 11:58-11:59 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T49 | 11:59-12:06 | the tick or the last event | 14 | 3 | 3 | 0 | impl-drift x1 (0 min) |
| T52 | 12:07-12:09 | spec-fidelity CLEAR | 5 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T52 | 12:09-12:10 | the tick or the last event | 1 | 1 | 0 | 0 | - |
| T53 | 12:21-12:22 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T53 | 12:22-12:24 | the tick or the last event | 2 | 2 | 0 | 0 | - |
| T17 | 12:29-12:30 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T17 | 12:30-12:56 | spec-fidelity CLEAR | 54 | 26 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (11 min) |
| T17 | 12:56-12:58 | spec-fidelity CLEAR | 6 | 2 | 0 | 0 | claims-triage x1, spec-fidelity x1 (1 min) |
| T17 | 12:58-13:02 | spec-fidelity CLEAR | 14 | 3 | 0 | 0 | spec-fidelity x1 (2 min) |
| T17 | 13:02-13:04 | spec-fidelity CLEAR | 9 | 2 | 0 | 0 | impl-drift x1, spec-fidelity x1 (5 min) |
| T17 | 13:04-13:13 | spec-fidelity CLEAR | 16 | 8 | 1 | 0 | spec-fidelity x1 (1 min) |
| T17 | 13:13-13:17 | the tick or the last event | 6 | 4 | 0 | 0 | general-purpose x1 (4 min) |
| T29 | 13:19-13:25 | spec-fidelity BLOCKED | 4 | 6 | 0 | 0 | spec-fidelity x1 (4 min) |
| T29 | 13:25-13:26 | spec-fidelity-verify findings | 2 | 1 | 0 | 0 | spec-fidelity-verify x1 (0 min) |
| T29 | 13:26-13:27 | spec-fidelity CLEAR | 1 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T29 | 13:27-13:29 | the tick or the last event | 1 | 2 | 0 | 0 | - |
| T62 | 13:31-13:33 | spec-fidelity CLEAR | 8 | 2 | 0 | 0 | spec-fidelity x1 (2 min) |
| T62 | 13:33-13:40 | the tick or the last event | 16 | 5 | 2 | 0 | claims-triage x1, impl-drift x2 (1 min) |
| T72 | 13:43-13:50 | spec-fidelity BLOCKED | 14 | 7 | 0 | 0 | spec-fidelity x1 (3 min) |
| T72 | 13:50-13:54 | spec-fidelity CLEAR | 5 | 4 | 0 | 0 | spec-fidelity x1 (3 min) |
| T72 | 13:54-14:04 | the tick or the last event | 14 | 8 | 2 | 0 | claims-triage x1, impl-drift x3 (7 min) |
| T64 | 13:47-13:50 | spec-fidelity BLOCKED | 3 | 3 | 0 | 0 | spec-fidelity x1 (3 min) |
| T64 | 13:50-13:54 | spec-fidelity CLEAR | 5 | 4 | 0 | 0 | spec-fidelity x1 (3 min) |
| T64 | 13:54-14:04 | the tick or the last event | 14 | 8 | 2 | 0 | claims-triage x1, impl-drift x3 (7 min) |
| T55 | 14:06-14:23 | spec-fidelity CLEAR | 27 | 17 | 0 | 0 | spec-fidelity x1 (1 min) |
| T55 | 14:23-14:32 | the tick or the last event | 17 | 8 | 1 | 0 | claims-triage x1, impl-drift x4 (6 min) |
| T74 | 14:35-14:42 | spec-fidelity BLOCKED | 11 | 6 | 1 | 0 | spec-fidelity x1 (3 min) |
| T74 | 14:42-14:44 | spec-fidelity CLEAR | 3 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T74 | 14:44-14:51 | spec-fidelity CLEAR | 17 | 6 | 1 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T74 | 14:51-14:52 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T74 | 14:52-14:54 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T74 | 14:54-15:05 | the tick or the last event | 29 | 9 | 2 | 0 | claims-triage x2, impl-drift x4 (3 min) |
| T81 | 15:06-15:12 | spec-fidelity CLEAR | 16 | 6 | 0 | 0 | spec-fidelity x1 (1 min) |
| T81 | 15:12-15:20 | spec-fidelity CLEAR | 22 | 8 | 0 | 0 | claims-triage x1, impl-drift x3, spec-fidelity x1 (5 min) |
| T81 | 15:20-15:44 | the tick or the last event | 55 | 24 | 0 | 0 | impl-drift x2 (3 min) |
| T82 | 15:08-15:12 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | spec-fidelity x1 (1 min) |
| T82 | 15:12-15:20 | spec-fidelity CLEAR | 22 | 8 | 0 | 0 | claims-triage x1, impl-drift x3, spec-fidelity x1 (5 min) |
| T82 | 15:20-15:44 | the tick or the last event | 55 | 24 | 0 | 0 | impl-drift x2 (3 min) |
| T20 | 15:10-15:12 | spec-fidelity CLEAR | 7 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T20 | 15:12-15:20 | spec-fidelity CLEAR | 22 | 8 | 0 | 0 | claims-triage x1, impl-drift x3, spec-fidelity x1 (5 min) |
| T20 | 15:20-15:44 | the tick or the last event | 55 | 24 | 0 | 0 | impl-drift x2 (3 min) |
| T54 | 15:52-15:55 | spec-fidelity BLOCKED | 3 | 3 | 0 | 0 | - |
| T54 | 15:55-16:02 | spec-fidelity CLEAR | 4 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T54 | 16:02-16:22 | spec-fidelity CLEAR | 68 | 20 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T54 | 16:22-16:25 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T54 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T54 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T83 | 15:52-15:55 | spec-fidelity BLOCKED | 3 | 2 | 0 | 0 | - |
| T83 | 15:55-16:02 | spec-fidelity CLEAR | 4 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T83 | 16:02-16:22 | spec-fidelity CLEAR | 68 | 20 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T83 | 16:22-16:25 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T83 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T83 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T84 | 15:52-15:55 | spec-fidelity BLOCKED | 3 | 2 | 0 | 0 | - |
| T84 | 15:55-16:02 | spec-fidelity CLEAR | 4 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T84 | 16:02-16:22 | spec-fidelity CLEAR | 68 | 20 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T84 | 16:22-16:25 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T84 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T84 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T85 | 15:52-15:55 | spec-fidelity BLOCKED | 3 | 2 | 0 | 0 | - |
| T85 | 15:55-16:02 | spec-fidelity CLEAR | 4 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T85 | 16:02-16:22 | spec-fidelity CLEAR | 68 | 20 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T85 | 16:22-16:25 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T85 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T85 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T87 | 15:52-15:55 | spec-fidelity BLOCKED | 3 | 2 | 0 | 0 | - |
| T87 | 15:55-16:02 | spec-fidelity CLEAR | 4 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T87 | 16:02-16:22 | spec-fidelity CLEAR | 68 | 20 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (4 min) |
| T87 | 16:22-16:25 | spec-fidelity CLEAR | 12 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T87 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T87 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T90 | 16:24-16:25 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T90 | 16:25-16:47 | round-arbiter findings | 47 | 21 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T90 | 16:47-16:57 | the tick or the last event | 4 | 10 | 0 | 0 | - |
| T18 | 17:04-17:11 | spec-fidelity CLEAR | 20 | 6 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (7 min) |
| T18 | 17:11-17:15 | spec-fidelity CLEAR | 5 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T18 | 17:15-17:43 | spec-fidelity CLEAR | 54 | 28 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T18 | 17:43-17:59 | the tick or the last event | 30 | 15 | 0 | 0 | impl-drift x4 (3 min) |
| T86 | 17:04-17:11 | spec-fidelity CLEAR | 20 | 6 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (7 min) |
| T86 | 17:11-17:15 | spec-fidelity CLEAR | 5 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T86 | 17:15-17:43 | spec-fidelity CLEAR | 54 | 28 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T86 | 17:43-17:59 | the tick or the last event | 30 | 15 | 0 | 0 | impl-drift x4 (3 min) |
| T89 | 17:04-17:11 | spec-fidelity CLEAR | 20 | 6 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (7 min) |
| T89 | 17:11-17:15 | spec-fidelity CLEAR | 5 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T89 | 17:15-17:43 | spec-fidelity CLEAR | 54 | 28 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T89 | 17:43-17:59 | the tick or the last event | 30 | 15 | 0 | 0 | impl-drift x4 (3 min) |
| T22 | 17:04-17:11 | spec-fidelity CLEAR | 20 | 6 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (7 min) |
| T22 | 17:11-17:15 | spec-fidelity CLEAR | 5 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T22 | 17:15-17:43 | spec-fidelity CLEAR | 54 | 28 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T22 | 17:43-17:59 | the tick or the last event | 30 | 15 | 0 | 0 | impl-drift x4 (3 min) |
| T23 | 17:04-17:11 | spec-fidelity CLEAR | 20 | 6 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (7 min) |
| T23 | 17:11-17:15 | spec-fidelity CLEAR | 5 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T23 | 17:15-17:43 | spec-fidelity CLEAR | 54 | 28 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T23 | 17:43-17:59 | the tick or the last event | 30 | 15 | 0 | 0 | impl-drift x4 (3 min) |
| T95 | 18:05-18:06 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | - |
| T95 | 18:06-18:16 | spec-fidelity BLOCKED | 9 | 10 | 0 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T95 | 18:16-18:21 | spec-fidelity BLOCKED | 7 | 6 | 0 | 0 | spec-fidelity x1 (2 min) |
| T95 | 18:21-18:27 | round-arbiter findings | 6 | 6 | 0 | 0 | round-arbiter x1 (2 min) |
| T95 | 18:27-18:37 | spec-fidelity CLEAR | 11 | 10 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T95 | 18:37-18:40 | spec-fidelity CLEAR | 7 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T95 | 18:40-18:59 | the tick or the last event | 14 | 18 | 0 | 0 | - |
| T96 | 18:05-18:06 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | - |
| T96 | 18:06-18:16 | spec-fidelity BLOCKED | 9 | 10 | 0 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T96 | 18:16-18:21 | spec-fidelity BLOCKED | 7 | 6 | 0 | 0 | spec-fidelity x1 (2 min) |
| T96 | 18:21-18:27 | round-arbiter findings | 6 | 6 | 0 | 0 | round-arbiter x1 (2 min) |
| T96 | 18:27-18:37 | spec-fidelity CLEAR | 11 | 10 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T96 | 18:37-18:40 | spec-fidelity CLEAR | 7 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T96 | 18:40-18:59 | the tick or the last event | 14 | 18 | 0 | 0 | - |
| T97 | 18:05-18:06 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | - |
| T97 | 18:06-18:16 | spec-fidelity BLOCKED | 9 | 10 | 0 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T97 | 18:16-18:21 | spec-fidelity BLOCKED | 7 | 6 | 0 | 0 | spec-fidelity x1 (2 min) |
| T97 | 18:21-18:27 | round-arbiter findings | 6 | 6 | 0 | 0 | round-arbiter x1 (2 min) |
| T97 | 18:27-18:37 | spec-fidelity CLEAR | 11 | 10 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T97 | 18:37-18:40 | spec-fidelity CLEAR | 7 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T97 | 18:40-18:59 | the tick or the last event | 14 | 18 | 0 | 0 | - |
| T100 | 18:05-18:06 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | - |
| T100 | 18:06-18:16 | spec-fidelity BLOCKED | 9 | 10 | 0 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T100 | 18:16-18:21 | spec-fidelity BLOCKED | 7 | 6 | 0 | 0 | spec-fidelity x1 (2 min) |
| T100 | 18:21-18:27 | round-arbiter findings | 6 | 6 | 0 | 0 | round-arbiter x1 (2 min) |
| T100 | 18:27-18:37 | spec-fidelity CLEAR | 11 | 10 | 0 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T100 | 18:37-18:40 | spec-fidelity CLEAR | 7 | 4 | 0 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T100 | 18:40-18:59 | the tick or the last event | 14 | 18 | 0 | 0 | - |
| T26 | 19:03-19:04 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | - |
| T26 | 19:04-19:15 | spec-fidelity CLEAR | 21 | 11 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (3 min) |
| T26 | 19:15-19:27 | spec-fidelity CLEAR | 23 | 12 | 0 | 0 | impl-drift x1, spec-fidelity x1 (3 min) |
| T26 | 19:27-19:33 | spec-fidelity CLEAR | 12 | 6 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 19:33-19:37 | spec-fidelity CLEAR | 10 | 4 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 19:37-20:01 | spec-fidelity CLEAR | 31 | 24 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (2 min) |
| T26 | 20:01-20:25 | spec-fidelity CLEAR | 30 | 24 | 0 | 0 | impl-drift x2, spec-fidelity x1 (3 min) |
| T26 | 20:25-04:20 | spec-fidelity CLEAR | 128 | 143 | 24 | 307 | impl-drift x3, research-pass x1, spec-fidelity x1 (15 min) |
| T26 | 04:20-04:25 | spec-fidelity CLEAR | 3 | 4 | 0 | 0 | spec-fidelity x1 (4 min) |
| T26 | 04:25-04:31 | spec-fidelity CLEAR | 9 | 5 | 1 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T26 | 04:31-04:56 | round-arbiter findings | 36 | 18 | 7 | 0 | impl-drift x2, round-arbiter x1 (4 min) |
| T26 | 04:56-08:41 | spec-fidelity CLEAR | 24 | 62 | 3 | 160 | spec-fidelity x1 (1 min) |
| T26 | 08:41-08:57 | spec-fidelity CLEAR | 45 | 15 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 08:57-09:10 | spec-fidelity CLEAR | 18 | 8 | 5 | 0 | spec-fidelity x1 (1 min) |
| T26 | 09:10-09:29 | spec-fidelity CLEAR | 14 | 15 | 4 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T26 | 09:29-09:40 | spec-fidelity CLEAR | 29 | 10 | 1 | 0 | impl-drift x4, spec-fidelity x1 (3 min) |
| T26 | 09:40-09:46 | spec-fidelity CLEAR | 10 | 5 | 1 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 09:46-09:48 | spec-fidelity CLEAR | 6 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 09:48-09:52 | spec-fidelity CLEAR | 8 | 4 | 1 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 09:52-09:57 | spec-fidelity CLEAR | 8 | 5 | 0 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T26 | 09:57-10:05 | spec-fidelity CLEAR | 11 | 7 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (5 min) |
| T26 | 10:05-10:18 | spec-fidelity CLEAR | 16 | 8 | 5 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (3 min) |
| T26 | 10:18-12:18 | spec-fidelity CLEAR | 37 | 112 | 7 | 0 | claims-triage x1, impl-drift x3, spec-fidelity x1 (3 min) |
| T26 | 12:18-12:40 | spec-fidelity CLEAR | 78 | 22 | 10 | 0 | research-pass x1, spec-fidelity x1 (6 min) |
| T26 | 12:40-12:48 | spec-fidelity CLEAR | 74 | 11 | 5 | 0 | modal-triage x1, quote-check x5, record-format x5, research-pass x1, source-reader x1, spec-fidelity x1 (15 min) |
| T26 | 12:48-12:56 | spec-fidelity CLEAR | 62 | 16 | 1 | 0 | quote-check x3, record-format x3, source-reader x1, spec-fidelity x1 (4 min) |
| T26 | 12:56-13:08 | spec-fidelity CLEAR | 59 | 13 | 8 | 0 | claims-triage x1, impl-drift x1, modal-depiction x1, modal-triage x1, spec-fidelity x1 (5 min) |
| T26 | 13:08-13:17 | spec-fidelity CLEAR | 67 | 15 | 3 | 0 | impl-drift x1, modal-depiction x1, modal-triage x1, quote-check x3, record-format x3, source-applicability x2, source-reader x2, spec-fidelity x1, translation-check x1 (13 min) |
| T26 | 13:17-13:26 | spec-fidelity CLEAR | 62 | 13 | 5 | 0 | claims-triage x1, impl-drift x2, modal-depiction x1, modal-triage x1, quote-check x1, record-format x1, source-applicability x2, spec-fidelity x1 (7 min) |
| T26 | 13:26-13:50 | spec-fidelity CLEAR | 56 | 21 | 10 | 0 | claims-triage x1, impl-drift x3, modal-depiction x1, spec-fidelity x1 (8 min) |
| T26 | 13:50-14:07 | spec-fidelity CLEAR | 24 | 15 | 2 | 0 | claims-triage x1, impl-drift x10, spec-fidelity x1 (37 min) |
| T26 | 14:07-14:18 | spec-fidelity CLEAR | 15 | 8 | 4 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T26 | 14:18-14:29 | spec-fidelity CLEAR | 16 | 11 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 14:29-14:36 | spec-fidelity CLEAR | 13 | 7 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (3 min) |
| T26 | 14:36-14:52 | spec-fidelity CLEAR | 59 | 18 | 6 | 0 | impl-drift x1, research-pass x1, spec-fidelity x1 (6 min) |
| T26 | 14:52-15:05 | spec-fidelity CLEAR | 52 | 15 | 10 | 0 | impl-drift x1, spec-fidelity x1 (1 min) |
| T26 | 15:05-15:19 | spec-fidelity CLEAR | 61 | 20 | 8 | 0 | claims-triage x1, impl-drift x2, intro-check x1, modal-triage x1, quote-check x3, record-format x4, source-applicability x2, source-reader x7, spec-fidelity x1, translation-check x1 (27 min) |
| T26 | 15:19-15:34 | spec-fidelity BLOCKED | 65 | 22 | 8 | 0 | claims-triage x1, impl-drift x2, modal-depiction x2, modal-triage x1, quote-check x2, record-format x2, source-applicability x1, source-reader x3, spec-fidelity x1, translation-check x1 (14 min) |
| T26 | 15:34-15:39 | spec-fidelity BLOCKED | 17 | 9 | 0 | 0 | spec-fidelity x1 (4 min) |
| T26 | 15:39-15:43 | round-arbiter CLEAR | 12 | 3 | 0 | 0 | round-arbiter x1 (2 min) |
| T26 | 15:43-15:50 | spec-fidelity BLOCKED | 9 | 7 | 1 | 0 | claims-triage x1, impl-drift x4, spec-fidelity x1 (32 min) |
| T26 | 15:50-16:03 | spec-fidelity CLEAR | 14 | 11 | 2 | 0 | spec-fidelity x1 (3 min) |
| T26 | 16:03-16:17 | spec-fidelity BLOCKED | 22 | 13 | 1 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (8 min) |
| T26 | 16:17-16:21 | spec-fidelity CLEAR | 7 | 3 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 16:21-16:36 | round-arbiter findings | 52 | 17 | 6 | 0 | modal-depiction x8, modal-triage x1, quote-check x1, record-format x1, round-arbiter x1 (8 min) |
| T26 | 16:36-16:45 | spec-fidelity BLOCKED | 34 | 7 | 7 | 0 | modal-depiction x2, quote-check x1, spec-fidelity x1 (5 min) |
| T26 | 16:45-16:47 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 16:47-16:54 | spec-fidelity CLEAR | 4 | 6 | 1 | 0 | claims-triage x1, impl-drift x4, spec-fidelity x1 (12 min) |
| T26 | 16:54-04:16 | spec-fidelity CLEAR | 44 | 127 | 8 | 546 | spec-fidelity x1 (1 min) |
| T26 | 04:16-04:19 | spec-fidelity CLEAR | 14 | 4 | 0 | 0 | spec-fidelity x1 (2 min) |
| T26 | 04:19-04:24 | spec-fidelity CLEAR | 17 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T26 | 04:24-05:14 | spec-fidelity CLEAR | 36 | 49 | 0 | 0 | spec-fidelity x1 (2 min) |
| T26 | 05:14-05:31 | spec-fidelity CLEAR | 46 | 17 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (4 min) |
| T26 | 05:31-05:36 | spec-fidelity CLEAR | 12 | 5 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 05:36-09:38 | spec-fidelity CLEAR | 80 | 32 | 9 | 201 | spec-fidelity x1 (1 min) |
| T26 | 09:38-09:56 | spec-fidelity CLEAR | 36 | 18 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T26 | 09:56-10:07 | spec-fidelity CLEAR | 13 | 9 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (3 min) |
| T26 | 10:07-11:29 | spec-fidelity CLEAR | 27 | 39 | 9 | 1474 | impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 11:29-11:43 | round-arbiter findings | 29 | 9 | 4 | 0 | claims-triage x2, impl-drift x3, round-arbiter x1 (6 min) |
| T26 | 11:43-13:25 | spec-fidelity CLEAR | 90 | 95 | 7 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T26 | 13:25-13:50 | spec-fidelity CLEAR | 36 | 25 | 0 | 0 | spec-fidelity x1 (4 min) |
| T26 | 13:50-13:57 | spec-fidelity CLEAR | 4 | 6 | 0 | 0 | spec-fidelity x1 (6 min) |
| T26 | 13:57-14:04 | round-arbiter | 16 | 6 | 1 | 0 | claims-triage x1, impl-drift x4, round-arbiter x1 (4 min) |
| T26 | 14:04-14:10 | spec-fidelity CLEAR | 5 | 5 | 1 | 0 | spec-fidelity x1 (4 min) |
| T26 | 14:10-14:26 | the tick or the last event | 6 | 9 | 7 | 0 | - |
| T103 | 19:03-19:04 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | - |
| T103 | 19:04-19:15 | spec-fidelity CLEAR | 21 | 11 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (3 min) |
| T103 | 19:15-19:27 | spec-fidelity CLEAR | 23 | 12 | 0 | 0 | impl-drift x1, spec-fidelity x1 (3 min) |
| T103 | 19:27-19:33 | spec-fidelity CLEAR | 12 | 6 | 0 | 0 | spec-fidelity x1 (1 min) |
| T103 | 19:33-19:33 | the tick or the last event | 2 | 1 | 0 | 0 | - |
| T105 | 19:36-19:37 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T105 | 19:37-19:52 | the tick or the last event | 18 | 15 | 0 | 0 | claims-triage x1, impl-drift x2 (2 min) |
| T10 | 20:00-20:01 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T10 | 20:01-20:18 | the tick or the last event | 17 | 17 | 0 | 0 | impl-drift x2 (2 min) |
| T67 | 20:24-20:25 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T67 | 20:25-20:45 | the tick or the last event | 15 | 20 | 0 | 0 | impl-drift x3 (3 min) |
| T107 | 03:45-04:20 | spec-fidelity CLEAR | 51 | 30 | 5 | 0 | spec-fidelity x1 (4 min) |
| T107 | 04:20-04:25 | spec-fidelity CLEAR | 3 | 4 | 0 | 0 | spec-fidelity x1 (4 min) |
| T107 | 04:25-04:31 | spec-fidelity CLEAR | 9 | 5 | 1 | 0 | claims-triage x1, spec-fidelity x1 (3 min) |
| T107 | 04:31-04:46 | the tick or the last event | 18 | 11 | 4 | 0 | impl-drift x2 (2 min) |
| T91 | 08:39-08:41 | spec-fidelity CLEAR | 8 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T91 | 08:41-08:57 | spec-fidelity CLEAR | 45 | 15 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T91 | 08:57-09:03 | the tick or the last event | 8 | 3 | 3 | 0 | - |
| T113 | 08:55-08:57 | spec-fidelity CLEAR | 5 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T113 | 08:57-09:03 | the tick or the last event | 8 | 3 | 3 | 0 | - |
| T93 | 09:08-09:10 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T93 | 09:10-09:12 | the tick or the last event | 6 | 2 | 1 | 0 | impl-drift x1 (0 min) |
| T115 | 09:28-09:29 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T115 | 09:29-09:38 | the tick or the last event | 25 | 9 | 1 | 0 | impl-drift x4 (3 min) |
| T116 | 09:39-09:40 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T116 | 09:40-09:46 | spec-fidelity CLEAR | 10 | 5 | 1 | 0 | impl-drift x1, spec-fidelity x1 (2 min) |
| T116 | 09:46-09:48 | spec-fidelity CLEAR | 6 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T116 | 09:48-09:50 | the tick or the last event | 5 | 2 | 0 | 0 | impl-drift x1 (1 min) |
| T117 | 09:51-09:52 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T117 | 09:52-09:55 | the tick or the last event | 3 | 2 | 0 | 0 | impl-drift x1 (0 min) |
| T118 | 09:55-09:57 | spec-fidelity CLEAR | 4 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T118 | 09:57-10:05 | spec-fidelity CLEAR | 11 | 7 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (5 min) |
| T118 | 10:05-10:15 | the tick or the last event | 11 | 6 | 4 | 0 | claims-triage x1, impl-drift x2 (2 min) |
| T108 | 10:16-10:18 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T108 | 10:18-10:29 | the tick or the last event | 16 | 7 | 4 | 0 | claims-triage x1, impl-drift x3 (2 min) |
| T120 | 12:15-12:18 | spec-fidelity CLEAR | 7 | 2 | 0 | 0 | spec-fidelity x1 (1 min) |
| T120 | 12:18-12:23 | the tick or the last event | 7 | 5 | 0 | 0 | - |
| T102 | 12:38-12:40 | spec-fidelity CLEAR | 6 | 3 | 0 | 0 | spec-fidelity x1 (1 min) |
| T102 | 12:40-12:42 | the tick or the last event | 24 | 5 | 0 | 0 | - |
| T99 | 12:47-12:48 | spec-fidelity CLEAR | 8 | 0 | 2 | 0 | quote-check x2, record-format x2, spec-fidelity x1 (4 min) |
| T99 | 12:48-12:50 | the tick or the last event | 24 | 3 | 0 | 0 | - |
| T09 | 12:52-12:56 | spec-fidelity CLEAR | 22 | 8 | 0 | 0 | quote-check x3, record-format x3, source-reader x1, spec-fidelity x1 (4 min) |
| T09 | 12:56-13:08 | spec-fidelity CLEAR | 59 | 13 | 8 | 0 | claims-triage x1, impl-drift x1, modal-depiction x1, modal-triage x1, spec-fidelity x1 (5 min) |
| T09 | 13:08-13:17 | spec-fidelity CLEAR | 67 | 15 | 3 | 0 | impl-drift x1, modal-depiction x1, modal-triage x1, quote-check x3, record-format x3, source-applicability x2, source-reader x2, spec-fidelity x1, translation-check x1 (13 min) |
| T09 | 13:17-13:26 | spec-fidelity CLEAR | 62 | 13 | 5 | 0 | claims-triage x1, impl-drift x2, modal-depiction x1, modal-triage x1, quote-check x1, record-format x1, source-applicability x2, spec-fidelity x1 (7 min) |
| T09 | 13:26-13:45 | the tick or the last event | 45 | 16 | 10 | 0 | claims-triage x1, impl-drift x3, modal-depiction x1 (7 min) |
| T114 | 13:49-13:50 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T114 | 13:50-14:07 | spec-fidelity CLEAR | 24 | 15 | 2 | 0 | claims-triage x1, impl-drift x10, spec-fidelity x1 (37 min) |
| T114 | 14:07-14:16 | the tick or the last event | 11 | 6 | 4 | 0 | impl-drift x1 (1 min) |
| T126 | 14:05-14:07 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T126 | 14:07-14:16 | the tick or the last event | 11 | 6 | 4 | 0 | impl-drift x1 (1 min) |
| T70 | 14:19-14:20 | the tick or the last event | 0 | 1 | 0 | 0 | - |
| T119 | 14:26-14:29 | spec-fidelity CLEAR | 3 | 3 | 0 | 0 | spec-fidelity x1 (1 min) |
| T119 | 14:29-14:36 | spec-fidelity CLEAR | 13 | 7 | 0 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (3 min) |
| T119 | 14:36-14:43 | the tick or the last event | 5 | 7 | 0 | 0 | impl-drift x1 (0 min) |
| T128 | 14:51-14:52 | spec-fidelity CLEAR | 5 | 0 | 3 | 0 | spec-fidelity x1 (1 min) |
| T128 | 14:52-15:00 | the tick or the last event | 35 | 5 | 10 | 0 | impl-drift x1 (0 min) |
| T121 | 15:01-15:05 | spec-fidelity CLEAR | 10 | 8 | 0 | 0 | spec-fidelity x1 (1 min) |
| T121 | 15:05-15:14 | the tick or the last event | 41 | 13 | 6 | 0 | claims-triage x1, impl-drift x2, intro-check x1, modal-triage x1, quote-check x3, record-format x4, source-applicability x2, source-reader x7, translation-check x1 (26 min) |
| T124 | 15:16-15:19 | spec-fidelity CLEAR | 17 | 7 | 0 | 0 | spec-fidelity x1 (1 min) |
| T124 | 15:19-15:28 | the tick or the last event | 51 | 16 | 2 | 0 | claims-triage x1, impl-drift x2, modal-depiction x1, modal-triage x1, quote-check x2, record-format x2, source-applicability x1, source-reader x3, translation-check x1 (8 min) |
| T127 | 15:30-15:34 | spec-fidelity BLOCKED | 8 | 2 | 6 | 0 | modal-depiction x1, spec-fidelity x1 (5 min) |
| T127 | 15:34-15:39 | spec-fidelity BLOCKED | 17 | 9 | 0 | 0 | spec-fidelity x1 (4 min) |
| T127 | 15:39-15:43 | round-arbiter CLEAR | 12 | 3 | 0 | 0 | round-arbiter x1 (2 min) |
| T127 | 15:43-15:50 | spec-fidelity BLOCKED | 9 | 7 | 1 | 0 | claims-triage x1, impl-drift x4, spec-fidelity x1 (32 min) |
| T127 | 15:50-16:03 | spec-fidelity CLEAR | 14 | 11 | 2 | 0 | spec-fidelity x1 (3 min) |
| T127 | 16:03-16:17 | spec-fidelity BLOCKED | 22 | 13 | 1 | 0 | claims-triage x1, impl-drift x2, spec-fidelity x1 (8 min) |
| T127 | 16:17-16:21 | spec-fidelity CLEAR | 7 | 3 | 0 | 0 | spec-fidelity x1 (1 min) |
| T127 | 16:21-16:36 | round-arbiter findings | 52 | 17 | 6 | 0 | modal-depiction x8, modal-triage x1, quote-check x1, record-format x1, round-arbiter x1 (8 min) |
| T127 | 16:36-16:45 | spec-fidelity BLOCKED | 34 | 7 | 7 | 0 | modal-depiction x2, quote-check x1, spec-fidelity x1 (5 min) |
| T127 | 16:45-16:47 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T127 | 16:47-16:54 | spec-fidelity CLEAR | 4 | 6 | 1 | 0 | claims-triage x1, impl-drift x4, spec-fidelity x1 (12 min) |
| T127 | 16:54-04:16 | spec-fidelity CLEAR | 44 | 127 | 8 | 546 | spec-fidelity x1 (1 min) |
| T127 | 04:16-04:19 | spec-fidelity CLEAR | 14 | 4 | 0 | 0 | spec-fidelity x1 (2 min) |
| T127 | 04:19-04:24 | spec-fidelity CLEAR | 17 | 5 | 0 | 0 | spec-fidelity x1 (1 min) |
| T127 | 04:24-05:14 | spec-fidelity CLEAR | 36 | 49 | 0 | 0 | spec-fidelity x1 (2 min) |
| T127 | 05:14-05:31 | spec-fidelity CLEAR | 46 | 17 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (4 min) |
| T127 | 05:31-05:36 | spec-fidelity CLEAR | 12 | 5 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T127 | 05:36-09:38 | spec-fidelity CLEAR | 80 | 32 | 9 | 201 | spec-fidelity x1 (1 min) |
| T127 | 09:38-09:56 | spec-fidelity CLEAR | 36 | 18 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T127 | 09:56-10:07 | spec-fidelity CLEAR | 13 | 9 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (3 min) |
| T127 | 10:07-11:29 | spec-fidelity CLEAR | 27 | 39 | 9 | 1474 | impl-drift x1, spec-fidelity x1 (2 min) |
| T127 | 11:29-11:43 | round-arbiter findings | 29 | 9 | 4 | 0 | claims-triage x2, impl-drift x3, round-arbiter x1 (6 min) |
| T127 | 11:43-13:25 | spec-fidelity CLEAR | 90 | 95 | 7 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T127 | 13:25-13:50 | spec-fidelity CLEAR | 36 | 25 | 0 | 0 | spec-fidelity x1 (4 min) |
| T127 | 13:50-13:57 | spec-fidelity CLEAR | 4 | 6 | 0 | 0 | spec-fidelity x1 (6 min) |
| T127 | 13:57-14:04 | round-arbiter | 16 | 6 | 1 | 0 | claims-triage x1, impl-drift x4, round-arbiter x1 (4 min) |
| T127 | 14:04-14:10 | spec-fidelity CLEAR | 5 | 5 | 1 | 0 | spec-fidelity x1 (4 min) |
| T127 | 14:10-23:36 | round-arbiter findings | 148 | 137 | 33 | 396 | round-arbiter x1 (2 min) |
| T127 | 23:36-00:04 | spec-fidelity CLEAR | 12 | 28 | 0 | 0 | spec-fidelity x1 (1 min) |
| T127 | 00:04-00:07 | spec-fidelity CLEAR | 7 | 2 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T127 | 00:07-00:30 | round-arbiter findings | 14 | 23 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T127 | 00:30-02:25 | the tick or the last event | 19 | 75 | 39 | 0 | - |
| T110 | 16:10-16:11 | the tick or the last event | 0 | 1 | 0 | 0 | - |
| T130 | 16:14-16:17 | spec-fidelity BLOCKED | 2 | 3 | 0 | 0 | spec-fidelity x1 (2 min) |
| T130 | 16:17-16:21 | spec-fidelity CLEAR | 7 | 3 | 0 | 0 | spec-fidelity x1 (1 min) |
| T130 | 16:21-16:28 | the tick or the last event | 1 | 7 | 0 | 0 | - |
| T129 | 16:42-16:45 | spec-fidelity BLOCKED | 2 | 3 | 0 | 0 | spec-fidelity x1 (2 min) |
| T129 | 16:45-16:47 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T129 | 16:47-16:54 | spec-fidelity CLEAR | 4 | 6 | 1 | 0 | claims-triage x1, impl-drift x4, spec-fidelity x1 (12 min) |
| T129 | 16:54-16:57 | the tick or the last event | 2 | 3 | 0 | 0 | - |
| T133 | 04:23-04:24 | spec-fidelity CLEAR | 4 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T133 | 04:24-04:28 | the tick or the last event | 5 | 4 | 0 | 0 | - |
| T134 | 05:11-05:14 | spec-fidelity CLEAR | 5 | 3 | 0 | 0 | spec-fidelity x1 (2 min) |
| T134 | 05:14-05:31 | spec-fidelity CLEAR | 46 | 17 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (4 min) |
| T134 | 05:31-05:36 | spec-fidelity CLEAR | 12 | 5 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T134 | 05:36-05:45 | the tick or the last event | 8 | 3 | 6 | 0 | - |
| T07 | 09:25-09:38 | spec-fidelity CLEAR | 29 | 13 | 0 | 0 | spec-fidelity x1 (1 min) |
| T07 | 09:38-09:56 | spec-fidelity CLEAR | 36 | 18 | 0 | 0 | claims-triage x2, impl-drift x1, spec-fidelity x1 (3 min) |
| T07 | 09:56-10:07 | spec-fidelity CLEAR | 13 | 9 | 1 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (3 min) |
| T07 | 10:07-10:34 | the tick or the last event | 7 | 24 | 4 | 0 | impl-drift x1 (1 min) |
| T135 | 11:28-11:29 | spec-fidelity CLEAR | 3 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T135 | 11:29-11:43 | round-arbiter findings | 29 | 9 | 4 | 0 | claims-triage x2, impl-drift x3, round-arbiter x1 (6 min) |
| T135 | 11:43-11:51 | the tick or the last event | 11 | 4 | 4 | 0 | claims-triage x1, impl-drift x1 (1 min) |
| T106 | 19:45-23:36 | round-arbiter findings | 30 | 15 | 0 | 216 | round-arbiter x1 (2 min) |
| T106 | 23:36-00:04 | spec-fidelity CLEAR | 12 | 28 | 0 | 0 | spec-fidelity x1 (1 min) |
| T106 | 00:04-00:07 | spec-fidelity CLEAR | 7 | 2 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T106 | 00:07-00:30 | round-arbiter findings | 14 | 23 | 0 | 0 | impl-drift x1, round-arbiter x1 (3 min) |
| T106 | 00:30-02:25 | the tick or the last event | 19 | 75 | 39 | 0 | - |
| T138 | 00:04-00:04 | spec-fidelity CLEAR | 2 | 1 | 0 | 0 | spec-fidelity x1 (1 min) |
| T138 | 00:04-00:07 | spec-fidelity CLEAR | 7 | 2 | 0 | 0 | claims-triage x1, impl-drift x1, spec-fidelity x1 (2 min) |
| T138 | 00:07-00:27 | the tick or the last event | 9 | 20 | 0 | 0 | impl-drift x1 (2 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T12 | 12:02 | started (`make task-start`) | |
| T12 | 12:05 | spec-fidelity returned (1 min) | |
| T12 | 12:06 | spec-fidelity returned CLEAR (1 min) | |
| T12 | 12:06 | spec-fidelity returned CHANGES REQUIRED (5 min) | |
| T12 | 12:10 | spec-fidelity-verify returned FAITHFUL (1 min) | |
| T12 | 12:11 | `make cohort` (1 min) | |
| T12 | 12:11 | claims-triage returned findings (0 min) | |
| T12 | 12:12 | impl-drift returned findings (0 min) | |
| T12 | 12:14 | impl-drift returned findings (1 min) | |
| T12 | 12:16 | `make done` (0 min) | |
| T12 | 12:26 | spec-fidelity returned CLEAR (1 min) | |
| T12 | 12:28 | round-arbiter returned CHANGES REQUIRED (3 min) | |
| T12 | 12:29 | `make cohort-landing` (0 min) | |
| T12 | 12:36 | part B written | |
| T12 | 12:36 | ticked | |
| T32 | 13:41 | started (`make task-start`) | |
| T32 | 13:44 | spec-fidelity returned CLEAR (4 min) | |
| T32 | 14:05 | part B written | |
| T32 | 14:05 | round-arbiter returned CLEAR (2 min) | |
| T32 | 14:07 | ticked | |
| T14 | 03:17 | started (`make task-start`) | |
| T14 | 03:24 | spec-fidelity returned CLEAR (1 min) | |
| T14 | 03:27 | `make cohort` (0 min) | |
| T14 | 03:29 | part B written | |
| T14 | 03:29 | claims-triage returned findings (0 min) | |
| T14 | 03:29 | round-arbiter returned (1 min) | |
| T14 | 03:29 | `make done` (0 min) | |
| T14 | 03:30 | impl-drift returned findings (1 min) | |
| T14 | 03:34 | claims-triage returned (0 min) | |
| T14 | 03:36 | impl-drift returned findings (1 min) | |
| T14 | 03:37 | impl-drift returned findings (1 min) | |
| T14 | 03:55 | ticked | |
| T36 | 04:18 | started (`make task-start`) | |
| T36 | 04:22 | spec-fidelity returned BLOCKED (4 min) | |
| T36 | 04:26 | spec-fidelity returned CLEAR (3 min) | |
| T36 | 04:41 | round-arbiter returned BLOCKED (1 min) | |
| T36 | 04:42 | ticked | |
| T11 | 04:42 | started (`make task-start`) | |
| T11 | 04:44 | spec-fidelity returned CLEAR (1 min) | |
| T11 | 04:46 | `make done` (0 min) | |
| T11 | 04:47 | claims-triage returned (0 min) | |
| T11 | 04:48 | impl-drift returned findings (0 min) | |
| T11 | 05:04 | spec-fidelity returned CLEAR (1 min) | |
| T11 | 05:17 | ticked | |
| T43 | 10:20 | started (`make task-start`) | |
| T43 | 10:23 | spec-fidelity returned BLOCKED (3 min) | |
| T43 | 10:26 | spec-fidelity returned CLEAR (1 min) | |
| T43 | 10:26 | round-arbiter returned findings (1 min) | |
| T43 | 10:32 | spec-fidelity returned CLEAR (1 min) | |
| T43 | 10:34 | ticked | |
| T19 | 10:34 | started (`make task-start`) | |
| T19 | 10:36 | spec-fidelity returned CLEAR (1 min) | |
| T19 | 10:36 | `make done` (0 min) | |
| T19 | 10:46 | ticked | |
| T48 | 11:21 | started (`make task-start`) | |
| T48 | 11:24 | spec-fidelity returned CLEAR (3 min) | |
| T48 | 11:27 | ticked | |
| T13 | 11:28 | started (`make task-start`) | |
| T13 | 11:30 | spec-fidelity returned (1 min) | |
| T13 | 11:31 | impl-drift returned findings (0 min) | |
| T13 | 11:38 | ticked | |
| T50 | 11:50 | started (`make task-start`) | |
| T50 | 11:53 | spec-fidelity returned CLEAR (3 min) | |
| T50 | 11:56 | ticked | |
| T49 | 11:58 | started (`make task-start`) | |
| T49 | 11:59 | spec-fidelity returned CLEAR (1 min) | |
| T49 | 12:02 | impl-drift returned findings (0 min) | |
| T49 | 12:06 | ticked | |
| T52 | 12:07 | started (`make task-start`) | |
| T52 | 12:09 | spec-fidelity returned CLEAR (1 min) | |
| T52 | 12:10 | ticked | |
| T53 | 12:21 | started (`make task-start`) | |
| T53 | 12:22 | spec-fidelity returned CLEAR (1 min) | |
| T53 | 12:24 | ticked | |
| T17 | 12:29 | started (`make task-start`) | |
| T17 | 12:30 | spec-fidelity returned CLEAR (1 min) | |
| T17 | 12:32 | claims-triage returned (0 min) | |
| T17 | 12:42 | impl-drift returned findings (9 min) | |
| T17 | 12:55 | claims-triage returned findings (0 min) | |
| T17 | 12:56 | Approach re-answered | |
| T17 | 12:56 | spec-fidelity returned CLEAR (2 min) | |
| T17 | 12:57 | claims-triage returned findings (0 min) | |
| T17 | 12:58 | spec-fidelity returned CLEAR (1 min) | |
| T17 | 13:02 | spec-fidelity returned CLEAR (2 min) | |
| T17 | 13:04 | spec-fidelity returned CLEAR (1 min) | |
| T17 | 13:08 | impl-drift returned findings (4 min) | |
| T17 | 13:10 | `make done` (0 min) | |
| T17 | 13:13 | spec-fidelity returned CLEAR (1 min) | |
| T17 | 13:17 | ticked | |
| T29 | 13:19 | started (`make task-start`) | |
| T29 | 13:25 | spec-fidelity returned BLOCKED (4 min) | |
| T29 | 13:26 | spec-fidelity-verify returned findings (0 min) | |
| T29 | 13:27 | spec-fidelity returned CLEAR (1 min) | |
| T29 | 13:29 | ticked | |
| T62 | 13:31 | started (`make task-start`) | |
| T62 | 13:33 | spec-fidelity returned CLEAR (2 min) | |
| T62 | 13:35 | claims-triage returned (0 min) | |
| T62 | 13:35 | impl-drift returned findings (1 min) | |
| T62 | 13:36 | impl-drift returned findings (1 min) | |
| T62 | 13:40 | ticked | |
| T72 | 13:43 | started (`make task-start`) | |
| T72 | 13:50 | spec-fidelity returned BLOCKED (3 min) | |
| T72 | 13:54 | spec-fidelity returned CLEAR (3 min) | |
| T72 | 13:55 | claims-triage returned findings (0 min) | |
| T72 | 13:56 | impl-drift returned findings (0 min) | |
| T72 | 14:01 | impl-drift returned findings (6 min) | |
| T72 | 14:03 | impl-drift returned findings (1 min) | |
| T72 | 14:04 | ticked | |
| T64 | 13:47 | started (`make task-start`) | |
| T64 | 13:50 | spec-fidelity returned BLOCKED (3 min) | |
| T64 | 13:54 | spec-fidelity returned CLEAR (3 min) | |
| T64 | 13:55 | claims-triage returned findings (0 min) | |
| T64 | 13:56 | impl-drift returned findings (0 min) | |
| T64 | 14:01 | impl-drift returned findings (6 min) | |
| T64 | 14:03 | impl-drift returned findings (1 min) | |
| T64 | 14:04 | ticked | |
| T55 | 14:06 | started (`make task-start`) | |
| T55 | 14:15 | `make cohort` (3 min) | |
| T55 | 14:20 | `make cohort` (3 min) | |
| T55 | 14:23 | spec-fidelity returned CLEAR (1 min) | |
| T55 | 14:24 | claims-triage returned findings (0 min) | |
| T55 | 14:26 | impl-drift returned findings (1 min) | |
| T55 | 14:26 | impl-drift returned findings (2 min) | |
| T55 | 14:29 | impl-drift returned findings (2 min) | |
| T55 | 14:31 | impl-drift returned findings (1 min) | |
| T55 | 14:32 | ticked | |
| T74 | 14:35 | started (`make task-start`) | |
| T74 | 14:38 | `make cohort` (0 min) | |
| T74 | 14:42 | spec-fidelity returned BLOCKED (3 min) | |
| T74 | 14:44 | spec-fidelity returned CLEAR (1 min) | |
| T74 | 14:45 | claims-triage returned (0 min) | |
| T74 | 14:45 | impl-drift returned findings (1 min) | |
| T74 | 14:46 | impl-drift returned findings (1 min) | |
| T74 | 14:48 | `make cohort` (0 min) | |
| T74 | 14:51 | spec-fidelity returned CLEAR (2 min) | |
| T74 | 14:52 | spec-fidelity returned CLEAR (1 min) | |
| T74 | 14:54 | spec-fidelity returned CLEAR (1 min) | |
| T74 | 14:54 | claims-triage returned (0 min) | |
| T74 | 14:56 | impl-drift returned findings (1 min) | |
| T74 | 14:58 | impl-drift returned findings (1 min) | |
| T74 | 14:59 | `make cohort` (0 min) | |
| T74 | 15:00 | claims-triage returned (0 min) | |
| T74 | 15:00 | impl-drift returned findings (0 min) | |
| T74 | 15:01 | impl-drift returned findings (1 min) | |
| T74 | 15:05 | ticked | |
| T81 | 15:06 | started (`make task-start`) | |
| T81 | 15:10 | `make cohort` (0 min) | |
| T81 | 15:12 | spec-fidelity returned CLEAR (1 min) | |
| T81 | 15:13 | claims-triage returned findings (0 min) | |
| T81 | 15:15 | impl-drift returned findings (1 min) | |
| T81 | 15:15 | impl-drift returned findings (2 min) | |
| T81 | 15:20 | spec-fidelity returned CLEAR (1 min) | |
| T81 | 15:21 | impl-drift returned findings (1 min) | |
| T81 | 15:26 | impl-drift returned findings (3 min) | |
| T81 | 15:30 | impl-drift returned findings (1 min) | |
| T81 | 15:44 | ticked | |
| T82 | 15:08 | started (`make task-start`) | |
| T82 | 15:10 | `make cohort` (0 min) | |
| T82 | 15:12 | spec-fidelity returned CLEAR (1 min) | |
| T82 | 15:13 | claims-triage returned findings (0 min) | |
| T82 | 15:15 | impl-drift returned findings (1 min) | |
| T82 | 15:15 | impl-drift returned findings (2 min) | |
| T82 | 15:20 | spec-fidelity returned CLEAR (1 min) | |
| T82 | 15:21 | impl-drift returned findings (1 min) | |
| T82 | 15:26 | impl-drift returned findings (3 min) | |
| T82 | 15:30 | impl-drift returned findings (1 min) | |
| T82 | 15:44 | ticked | |
| T20 | 15:10 | started (`make task-start`) | |
| T20 | 15:10 | `make cohort` (0 min) | |
| T20 | 15:12 | spec-fidelity returned CLEAR (1 min) | |
| T20 | 15:13 | claims-triage returned findings (0 min) | |
| T20 | 15:15 | impl-drift returned findings (1 min) | |
| T20 | 15:15 | impl-drift returned findings (2 min) | |
| T20 | 15:20 | spec-fidelity returned CLEAR (1 min) | |
| T20 | 15:21 | impl-drift returned findings (1 min) | |
| T20 | 15:26 | impl-drift returned findings (3 min) | |
| T20 | 15:30 | impl-drift returned findings (1 min) | |
| T20 | 15:44 | ticked | |
| T54 | 15:52 | started (`make task-start`) | |
| T54 | 15:55 | spec-fidelity returned BLOCKED (3 min) | |
| T54 | 16:02 | spec-fidelity returned CLEAR (1 min) | |
| T54 | 16:10 | `make cohort` (0 min) | |
| T54 | 16:12 | claims-triage returned (0 min) | |
| T54 | 16:13 | impl-drift returned findings (1 min) | |
| T54 | 16:15 | impl-drift returned findings (1 min) | |
| T54 | 16:17 | `make cohort` (0 min) | |
| T54 | 16:21 | `make cohort` (0 min) | |
| T54 | 16:22 | spec-fidelity returned CLEAR (1 min) | |
| T54 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T54 | 16:26 | impl-drift returned findings (1 min) | |
| T54 | 16:28 | impl-drift returned findings (1 min) | |
| T54 | 16:47 | round-arbiter returned findings (3 min) | |
| T54 | 16:57 | ticked | |
| T83 | 15:52 | started (`make task-start`) | |
| T83 | 15:55 | spec-fidelity returned BLOCKED (3 min) | |
| T83 | 16:02 | spec-fidelity returned CLEAR (1 min) | |
| T83 | 16:10 | `make cohort` (0 min) | |
| T83 | 16:12 | claims-triage returned (0 min) | |
| T83 | 16:13 | impl-drift returned findings (1 min) | |
| T83 | 16:15 | impl-drift returned findings (1 min) | |
| T83 | 16:17 | `make cohort` (0 min) | |
| T83 | 16:21 | `make cohort` (0 min) | |
| T83 | 16:22 | spec-fidelity returned CLEAR (1 min) | |
| T83 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T83 | 16:26 | impl-drift returned findings (1 min) | |
| T83 | 16:28 | impl-drift returned findings (1 min) | |
| T83 | 16:47 | round-arbiter returned findings (3 min) | |
| T83 | 16:57 | ticked | |
| T84 | 15:52 | started (`make task-start`) | |
| T84 | 15:55 | spec-fidelity returned BLOCKED (3 min) | |
| T84 | 16:02 | spec-fidelity returned CLEAR (1 min) | |
| T84 | 16:10 | `make cohort` (0 min) | |
| T84 | 16:12 | claims-triage returned (0 min) | |
| T84 | 16:13 | impl-drift returned findings (1 min) | |
| T84 | 16:15 | impl-drift returned findings (1 min) | |
| T84 | 16:17 | `make cohort` (0 min) | |
| T84 | 16:21 | `make cohort` (0 min) | |
| T84 | 16:22 | spec-fidelity returned CLEAR (1 min) | |
| T84 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T84 | 16:26 | impl-drift returned findings (1 min) | |
| T84 | 16:28 | impl-drift returned findings (1 min) | |
| T84 | 16:47 | round-arbiter returned findings (3 min) | |
| T84 | 16:57 | ticked | |
| T85 | 15:52 | started (`make task-start`) | |
| T85 | 15:55 | spec-fidelity returned BLOCKED (3 min) | |
| T85 | 16:02 | spec-fidelity returned CLEAR (1 min) | |
| T85 | 16:10 | `make cohort` (0 min) | |
| T85 | 16:12 | claims-triage returned (0 min) | |
| T85 | 16:13 | impl-drift returned findings (1 min) | |
| T85 | 16:15 | impl-drift returned findings (1 min) | |
| T85 | 16:17 | `make cohort` (0 min) | |
| T85 | 16:21 | `make cohort` (0 min) | |
| T85 | 16:22 | spec-fidelity returned CLEAR (1 min) | |
| T85 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T85 | 16:26 | impl-drift returned findings (1 min) | |
| T85 | 16:28 | impl-drift returned findings (1 min) | |
| T85 | 16:47 | round-arbiter returned findings (3 min) | |
| T85 | 16:57 | ticked | |
| T87 | 15:52 | started (`make task-start`) | |
| T87 | 15:55 | spec-fidelity returned BLOCKED (3 min) | |
| T87 | 16:02 | spec-fidelity returned CLEAR (1 min) | |
| T87 | 16:10 | `make cohort` (0 min) | |
| T87 | 16:12 | claims-triage returned (0 min) | |
| T87 | 16:13 | impl-drift returned findings (1 min) | |
| T87 | 16:15 | impl-drift returned findings (1 min) | |
| T87 | 16:17 | `make cohort` (0 min) | |
| T87 | 16:21 | `make cohort` (0 min) | |
| T87 | 16:22 | spec-fidelity returned CLEAR (1 min) | |
| T87 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T87 | 16:26 | impl-drift returned findings (1 min) | |
| T87 | 16:28 | impl-drift returned findings (1 min) | |
| T87 | 16:47 | round-arbiter returned findings (3 min) | |
| T87 | 16:57 | ticked | |
| T90 | 16:24 | started (`make task-start`) | |
| T90 | 16:25 | spec-fidelity returned CLEAR (1 min) | |
| T90 | 16:26 | impl-drift returned findings (1 min) | |
| T90 | 16:28 | impl-drift returned findings (1 min) | |
| T90 | 16:47 | round-arbiter returned findings (3 min) | |
| T90 | 16:57 | ticked | |
| T18 | 17:04 | started (`make task-start`) | |
| T18 | 17:05 | claims-triage returned findings (0 min) | |
| T18 | 17:07 | impl-drift returned findings (1 min) | |
| T18 | 17:10 | `make cohort` (0 min) | |
| T18 | 17:10 | impl-drift returned findings (5 min) | |
| T18 | 17:11 | spec-fidelity returned CLEAR (1 min) | |
| T18 | 17:15 | spec-fidelity returned CLEAR (1 min) | |
| T18 | 17:18 | claims-triage returned (0 min) | |
| T18 | 17:19 | impl-drift returned findings (1 min) | |
| T18 | 17:43 | spec-fidelity returned CLEAR (1 min) | |
| T18 | 17:44 | claims-triage returned (0 min) | |
| T18 | 17:45 | impl-drift returned findings (1 min) | |
| T18 | 17:45 | impl-drift returned findings (1 min) | |
| T18 | 17:48 | impl-drift returned findings (1 min) | |
| T18 | 17:50 | impl-drift returned findings (1 min) | |
| T18 | 17:59 | ticked | |
| T86 | 17:04 | started (`make task-start`) | |
| T86 | 17:05 | claims-triage returned findings (0 min) | |
| T86 | 17:07 | impl-drift returned findings (1 min) | |
| T86 | 17:10 | `make cohort` (0 min) | |
| T86 | 17:10 | impl-drift returned findings (5 min) | |
| T86 | 17:11 | spec-fidelity returned CLEAR (1 min) | |
| T86 | 17:15 | spec-fidelity returned CLEAR (1 min) | |
| T86 | 17:18 | claims-triage returned (0 min) | |
| T86 | 17:19 | impl-drift returned findings (1 min) | |
| T86 | 17:43 | spec-fidelity returned CLEAR (1 min) | |
| T86 | 17:44 | claims-triage returned (0 min) | |
| T86 | 17:45 | impl-drift returned findings (1 min) | |
| T86 | 17:45 | impl-drift returned findings (1 min) | |
| T86 | 17:48 | impl-drift returned findings (1 min) | |
| T86 | 17:50 | impl-drift returned findings (1 min) | |
| T86 | 17:59 | ticked | |
| T89 | 17:04 | started (`make task-start`) | |
| T89 | 17:05 | claims-triage returned findings (0 min) | |
| T89 | 17:07 | impl-drift returned findings (1 min) | |
| T89 | 17:10 | `make cohort` (0 min) | |
| T89 | 17:10 | impl-drift returned findings (5 min) | |
| T89 | 17:11 | spec-fidelity returned CLEAR (1 min) | |
| T89 | 17:15 | spec-fidelity returned CLEAR (1 min) | |
| T89 | 17:18 | claims-triage returned (0 min) | |
| T89 | 17:19 | impl-drift returned findings (1 min) | |
| T89 | 17:43 | spec-fidelity returned CLEAR (1 min) | |
| T89 | 17:44 | claims-triage returned (0 min) | |
| T89 | 17:45 | impl-drift returned findings (1 min) | |
| T89 | 17:45 | impl-drift returned findings (1 min) | |
| T89 | 17:48 | impl-drift returned findings (1 min) | |
| T89 | 17:50 | impl-drift returned findings (1 min) | |
| T89 | 17:59 | ticked | |
| T22 | 17:04 | started (`make task-start`) | |
| T22 | 17:05 | claims-triage returned findings (0 min) | |
| T22 | 17:07 | impl-drift returned findings (1 min) | |
| T22 | 17:10 | `make cohort` (0 min) | |
| T22 | 17:10 | impl-drift returned findings (5 min) | |
| T22 | 17:11 | spec-fidelity returned CLEAR (1 min) | |
| T22 | 17:15 | spec-fidelity returned CLEAR (1 min) | |
| T22 | 17:18 | claims-triage returned (0 min) | |
| T22 | 17:19 | impl-drift returned findings (1 min) | |
| T22 | 17:43 | spec-fidelity returned CLEAR (1 min) | |
| T22 | 17:44 | claims-triage returned (0 min) | |
| T22 | 17:45 | impl-drift returned findings (1 min) | |
| T22 | 17:45 | impl-drift returned findings (1 min) | |
| T22 | 17:48 | impl-drift returned findings (1 min) | |
| T22 | 17:50 | impl-drift returned findings (1 min) | |
| T22 | 17:59 | ticked | |
| T23 | 17:04 | started (`make task-start`) | |
| T23 | 17:05 | claims-triage returned findings (0 min) | |
| T23 | 17:07 | impl-drift returned findings (1 min) | |
| T23 | 17:10 | `make cohort` (0 min) | |
| T23 | 17:10 | impl-drift returned findings (5 min) | |
| T23 | 17:11 | spec-fidelity returned CLEAR (1 min) | |
| T23 | 17:15 | spec-fidelity returned CLEAR (1 min) | |
| T23 | 17:18 | claims-triage returned (0 min) | |
| T23 | 17:19 | impl-drift returned findings (1 min) | |
| T23 | 17:43 | spec-fidelity returned CLEAR (1 min) | |
| T23 | 17:44 | claims-triage returned (0 min) | |
| T23 | 17:45 | impl-drift returned findings (1 min) | |
| T23 | 17:45 | impl-drift returned findings (1 min) | |
| T23 | 17:46 | part B written | |
| T23 | 17:48 | impl-drift returned findings (1 min) | |
| T23 | 17:50 | impl-drift returned findings (1 min) | |
| T23 | 17:59 | ticked | |
| T95 | 18:05 | started (`make task-start`) | |
| T95 | 18:06 | spec-fidelity returned CLEAR (1 min) | |
| T95 | 18:14 | claims-triage returned findings (0 min) | |
| T95 | 18:16 | spec-fidelity returned BLOCKED (2 min) | |
| T95 | 18:21 | spec-fidelity returned BLOCKED (2 min) | |
| T95 | 18:27 | round-arbiter returned findings (2 min) | |
| T95 | 18:34 | impl-drift returned findings (1 min) | |
| T95 | 18:37 | spec-fidelity returned CLEAR (1 min) | |
| T95 | 18:40 | impl-drift returned findings (0 min) | |
| T95 | 18:40 | spec-fidelity returned CLEAR (1 min) | |
| T95 | 18:59 | ticked | |
| T96 | 18:05 | started (`make task-start`) | |
| T96 | 18:06 | spec-fidelity returned CLEAR (1 min) | |
| T96 | 18:14 | claims-triage returned findings (0 min) | |
| T96 | 18:16 | spec-fidelity returned BLOCKED (2 min) | |
| T96 | 18:21 | spec-fidelity returned BLOCKED (2 min) | |
| T96 | 18:27 | round-arbiter returned findings (2 min) | |
| T96 | 18:34 | impl-drift returned findings (1 min) | |
| T96 | 18:37 | spec-fidelity returned CLEAR (1 min) | |
| T96 | 18:40 | impl-drift returned findings (0 min) | |
| T96 | 18:40 | spec-fidelity returned CLEAR (1 min) | |
| T96 | 18:59 | ticked | |
| T97 | 18:05 | started (`make task-start`) | |
| T97 | 18:06 | spec-fidelity returned CLEAR (1 min) | |
| T97 | 18:14 | claims-triage returned findings (0 min) | |
| T97 | 18:16 | spec-fidelity returned BLOCKED (2 min) | |
| T97 | 18:21 | spec-fidelity returned BLOCKED (2 min) | |
| T97 | 18:27 | round-arbiter returned findings (2 min) | |
| T97 | 18:34 | impl-drift returned findings (1 min) | |
| T97 | 18:37 | spec-fidelity returned CLEAR (1 min) | |
| T97 | 18:40 | impl-drift returned findings (0 min) | |
| T97 | 18:40 | spec-fidelity returned CLEAR (1 min) | |
| T97 | 18:59 | ticked | |
| T100 | 18:05 | started (`make task-start`) | |
| T100 | 18:06 | spec-fidelity returned CLEAR (1 min) | |
| T100 | 18:14 | claims-triage returned findings (0 min) | |
| T100 | 18:16 | spec-fidelity returned BLOCKED (2 min) | |
| T100 | 18:21 | spec-fidelity returned BLOCKED (2 min) | |
| T100 | 18:27 | round-arbiter returned findings (2 min) | |
| T100 | 18:34 | impl-drift returned findings (1 min) | |
| T100 | 18:37 | spec-fidelity returned CLEAR (1 min) | |
| T100 | 18:40 | impl-drift returned findings (0 min) | |
| T100 | 18:40 | spec-fidelity returned CLEAR (1 min) | |
| T100 | 18:59 | ticked | |
| T26 | 19:03 | started (`make task-start`) | |
| T26 | 19:04 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 19:09 | claims-triage returned (0 min) | |
| T26 | 19:10 | impl-drift returned findings (1 min) | |
| T26 | 19:11 | impl-drift returned findings (0 min) | |
| T26 | 19:15 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 19:18 | impl-drift returned findings (1 min) | |
| T26 | 19:19 | `make verify` (0 min) | |
| T26 | 19:27 | spec-fidelity returned CLEAR (2 min) | |
| T26 | 19:33 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 19:37 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 19:38 | impl-drift returned findings (1 min) | |
| T26 | 19:50 | claims-triage returned findings (0 min) | |
| T26 | 19:51 | impl-drift returned findings (0 min) | |
| T26 | 19:57 | `make cohort` (2 min) | |
| T26 | 20:01 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 20:03 | `make cohort` (2 min) | |
| T26 | 20:05 | impl-drift returned findings (1 min) | |
| T26 | 20:07 | impl-drift returned findings (1 min) | |
| T26 | 20:25 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 20:27 | `make cohort` (3 min) | |
| T26 | 20:29 | impl-drift returned findings (1 min) | |
| T26 | 20:35 | impl-drift returned findings (1 min) | |
| T26 | 20:41 | impl-drift returned findings (1 min) | |
| T26 | 03:42 | `make cohort` (0 min) | |
| T26 | 03:47 | `make cohort` (0 min) | |
| T26 | 03:48 | `make cohort` (0 min) | |
| T26 | 03:49 | research-pass returned findings (9 min) | |
| T26 | 03:56 | `make cohort` (0 min) | |
| T26 | 04:01 | `make cohort` (0 min) | |
| T26 | 04:12 | `make cohort` (3 min) | |
| T26 | 04:20 | spec-fidelity returned CLEAR (4 min) | |
| T26 | 04:25 | spec-fidelity returned CLEAR (4 min) | |
| T26 | 04:26 | claims-triage returned findings (0 min) | |
| T26 | 04:31 | spec-fidelity returned CLEAR (3 min) | |
| T26 | 04:32 | impl-drift returned findings (2 min) | |
| T26 | 04:35 | impl-drift returned findings (1 min) | |
| T26 | 04:56 | round-arbiter returned findings (2 min) | |
| T26 | 04:59 | `make cohort` (3 min) | |
| T26 | 08:41 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 08:45 | claims-triage returned findings (0 min) | |
| T26 | 08:46 | impl-drift returned findings (1 min) | |
| T26 | 08:57 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:10 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:11 | impl-drift returned findings (0 min) | |
| T26 | 09:29 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:30 | impl-drift returned findings (1 min) | |
| T26 | 09:33 | impl-drift returned findings (1 min) | |
| T26 | 09:35 | impl-drift returned findings (1 min) | |
| T26 | 09:37 | impl-drift returned findings (0 min) | |
| T26 | 09:40 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:42 | impl-drift returned findings (1 min) | |
| T26 | 09:46 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:48 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:49 | impl-drift returned findings (1 min) | |
| T26 | 09:52 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:54 | impl-drift returned findings (0 min) | |
| T26 | 09:57 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:59 | claims-triage returned findings (0 min) | |
| T26 | 10:03 | impl-drift returned findings (4 min) | |
| T26 | 10:05 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 10:07 | claims-triage returned (0 min) | |
| T26 | 10:08 | impl-drift returned findings (1 min) | |
| T26 | 10:10 | impl-drift returned findings (1 min) | |
| T26 | 10:18 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 10:21 | claims-triage returned findings (0 min) | |
| T26 | 10:22 | impl-drift returned findings (1 min) | |
| T26 | 10:23 | impl-drift returned findings (1 min) | |
| T26 | 10:24 | impl-drift returned findings (0 min) | |
| T26 | 12:18 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 12:35 | research-pass returned findings (5 min) | |
| T26 | 12:40 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 12:45 | quote-check returned findings (0 min) | |
| T26 | 12:45 | quote-check returned findings (0 min) | |
| T26 | 12:46 | record-format returned findings (0 min) | |
| T26 | 12:46 | modal-triage returned findings (0 min) | |
| T26 | 12:46 | quote-check returned findings (1 min) | |
| T26 | 12:46 | record-format returned findings (1 min) | |
| T26 | 12:46 | record-format returned findings (1 min) | |
| T26 | 12:47 | source-reader returned findings (2 min) | |
| T26 | 12:47 | quote-check returned findings (0 min) | |
| T26 | 12:48 | record-format returned findings (1 min) | |
| T26 | 12:48 | quote-check returned clean (1 min) | |
| T26 | 12:48 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 12:48 | record-format returned PASS (1 min) | |
| T26 | 12:51 | research-pass returned (5 min) | |
| T26 | 12:56 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 12:56 | quote-check returned findings (0 min) | |
| T26 | 12:56 | record-format returned findings (0 min) | |
| T26 | 12:56 | quote-check returned findings (0 min) | |
| T26 | 12:56 | record-format returned findings (0 min) | |
| T26 | 12:56 | source-reader returned clean (0 min) | |
| T26 | 12:56 | record-format returned findings (0 min) | |
| T26 | 12:56 | quote-check returned clean (0 min) | |
| T26 | 12:57 | claims-triage returned findings (0 min) | |
| T26 | 12:58 | modal-triage returned findings (0 min) | |
| T26 | 12:58 | impl-drift returned findings (1 min) | |
| T26 | 13:01 | modal-depiction returned findings (3 min) | |
| T26 | 13:08 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 13:11 | impl-drift returned findings (2 min) | |
| T26 | 13:16 | quote-check returned findings (0 min) | |
| T26 | 13:16 | record-format returned findings (0 min) | |
| T26 | 13:16 | translation-check returned FAITHFUL (0 min) | |
| T26 | 13:16 | modal-triage returned findings (0 min) | |
| T26 | 13:16 | record-format returned findings (0 min) | |
| T26 | 13:16 | quote-check returned findings (1 min) | |
| T26 | 13:16 | quote-check returned findings (1 min) | |
| T26 | 13:16 | record-format returned findings (1 min) | |
| T26 | 13:16 | source-reader returned findings (1 min) | |
| T26 | 13:17 | source-reader returned findings (1 min) | |
| T26 | 13:17 | source-applicability returned findings (1 min) | |
| T26 | 13:17 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 13:17 | source-applicability returned findings (1 min) | |
| T26 | 13:19 | claims-triage returned findings (0 min) | |
| T26 | 13:19 | modal-depiction returned findings (3 min) | |
| T26 | 13:19 | impl-drift returned findings (1 min) | |
| T26 | 13:20 | impl-drift returned findings (1 min) | |
| T26 | 13:26 | quote-check returned findings (0 min) | |
| T26 | 13:26 | record-format returned findings (0 min) | |
| T26 | 13:26 | modal-triage returned findings (0 min) | |
| T26 | 13:26 | source-applicability returned findings (0 min) | |
| T26 | 13:26 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 13:27 | source-applicability returned findings (2 min) | |
| T26 | 13:28 | modal-depiction returned findings (2 min) | |
| T26 | 13:28 | claims-triage returned (0 min) | |
| T26 | 13:28 | impl-drift returned findings (1 min) | |
| T26 | 13:32 | impl-drift returned findings (1 min) | |
| T26 | 13:32 | modal-depiction returned findings (4 min) | |
| T26 | 13:34 | impl-drift returned findings (1 min) | |
| T26 | 13:50 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 13:54 | claims-triage returned findings (2 min) | |
| T26 | 13:55 | impl-drift returned (2 min) | |
| T26 | 13:55 | impl-drift returned (2 min) | |
| T26 | 13:55 | impl-drift returned (2 min) | |
| T26 | 13:55 | impl-drift returned (2 min) | |
| T26 | 13:55 | impl-drift returned (3 min) | |
| T26 | 13:55 | impl-drift returned (3 min) | |
| T26 | 13:58 | impl-drift returned findings (2 min) | |
| T26 | 13:58 | impl-drift returned (6 min) | |
| T26 | 13:59 | impl-drift returned findings (4 min) | |
| T26 | 14:00 | impl-drift returned (8 min) | |
| T26 | 14:07 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 14:08 | impl-drift returned findings (1 min) | |
| T26 | 14:18 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 14:29 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 14:30 | claims-triage returned findings (0 min) | |
| T26 | 14:30 | impl-drift returned findings (1 min) | |
| T26 | 14:32 | impl-drift returned findings (2 min) | |
| T26 | 14:36 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 14:38 | impl-drift returned findings (0 min) | |
| T26 | 14:52 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 14:53 | impl-drift returned findings (0 min) | |
| T26 | 14:54 | research-pass returned findings (5 min) | |
| T26 | 15:05 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 15:06 | claims-triage returned (0 min) | |
| T26 | 15:06 | impl-drift returned findings (0 min) | |
| T26 | 15:08 | impl-drift returned findings (1 min) | |
| T26 | 15:10 | intro-check returned findings (0 min) | |
| T26 | 15:10 | quote-check returned findings (0 min) | |
| T26 | 15:10 | translation-check returned FAITHFUL (0 min) | |
| T26 | 15:10 | record-format returned findings (0 min) | |
| T26 | 15:10 | source-reader returned clean (0 min) | |
| T26 | 15:10 | modal-triage returned findings (0 min) | |
| T26 | 15:10 | source-reader returned findings (0 min) | |
| T26 | 15:10 | record-format returned findings (1 min) | |
| T26 | 15:10 | source-reader returned findings (0 min) | |
| T26 | 15:10 | source-reader returned findings (1 min) | |
| T26 | 15:10 | record-format returned findings (1 min) | |
| T26 | 15:10 | quote-check returned findings (1 min) | |
| T26 | 15:10 | record-format returned findings (1 min) | |
| T26 | 15:10 | source-reader returned findings (1 min) | |
| T26 | 15:11 | source-reader returned findings (1 min) | |
| T26 | 15:11 | source-reader returned findings (1 min) | |
| T26 | 15:12 | source-applicability returned findings (3 min) | |
| T26 | 15:15 | source-applicability returned findings (6 min) | |
| T26 | 15:16 | quote-check returned findings (6 min) | |
| T26 | 15:19 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 15:20 | claims-triage returned (0 min) | |
| T26 | 15:20 | impl-drift returned findings (0 min) | |
| T26 | 15:21 | impl-drift returned findings (0 min) | |
| T26 | 15:27 | translation-check returned FAITHFUL (0 min) | |
| T26 | 15:27 | quote-check returned findings (0 min) | |
| T26 | 15:27 | modal-triage returned findings (0 min) | |
| T26 | 15:27 | source-reader returned clean (0 min) | |
| T26 | 15:27 | source-reader returned findings (0 min) | |
| T26 | 15:27 | record-format returned findings (1 min) | |
| T26 | 15:27 | source-reader returned findings (1 min) | |
| T26 | 15:27 | quote-check returned findings (1 min) | |
| T26 | 15:27 | record-format returned findings (1 min) | |
| T26 | 15:28 | modal-depiction returned findings (1 min) | |
| T26 | 15:28 | source-applicability returned findings (2 min) | |
| T26 | 15:32 | modal-depiction returned findings (2 min) | |
| T26 | 15:34 | spec-fidelity returned BLOCKED (3 min) | |
| T26 | 15:39 | spec-fidelity returned BLOCKED (4 min) | |
| T26 | 15:43 | round-arbiter returned CLEAR (2 min) | |
| T26 | 15:46 | claims-triage returned findings (1 min) | |
| T26 | 15:50 | impl-drift returned (4 min) | |
| T26 | 15:50 | spec-fidelity returned BLOCKED (2 min) | |
| T26 | 15:51 | impl-drift returned (6 min) | |
| T26 | 15:54 | impl-drift returned (9 min) | |
| T26 | 15:55 | impl-drift returned (10 min) | |
| T26 | 16:03 | spec-fidelity returned CLEAR (3 min) | |
| T26 | 16:04 | claims-triage returned findings (0 min) | |
| T26 | 16:05 | impl-drift returned findings (0 min) | |
| T26 | 16:08 | impl-drift returned findings (5 min) | |
| T26 | 16:17 | spec-fidelity returned BLOCKED (2 min) | |
| T26 | 16:21 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 16:32 | modal-triage returned findings (0 min) | |
| T26 | 16:32 | quote-check returned findings (0 min) | |
| T26 | 16:33 | record-format returned findings (1 min) | |
| T26 | 16:33 | `make cohort-seeds` (0 min) | |
| T26 | 16:34 | modal-depiction returned clean (0 min) | |
| T26 | 16:34 | modal-depiction returned clean (0 min) | |
| T26 | 16:34 | modal-depiction returned clean (1 min) | |
| T26 | 16:34 | modal-depiction returned clean (1 min) | |
| T26 | 16:34 | modal-depiction returned clean (1 min) | |
| T26 | 16:34 | modal-depiction returned clean (1 min) | |
| T26 | 16:34 | modal-depiction returned clean (1 min) | |
| T26 | 16:35 | modal-depiction returned clean (1 min) | |
| T26 | 16:36 | round-arbiter returned findings (2 min) | |
| T26 | 16:37 | modal-depiction returned findings (1 min) | |
| T26 | 16:37 | modal-depiction returned clean (1 min) | |
| T26 | 16:39 | quote-check returned findings (0 min) | |
| T26 | 16:45 | spec-fidelity returned BLOCKED (2 min) | |
| T26 | 16:47 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 16:48 | claims-triage returned (1 min) | |
| T26 | 16:50 | impl-drift returned findings (1 min) | |
| T26 | 16:50 | impl-drift returned (2 min) | |
| T26 | 16:50 | impl-drift returned (2 min) | |
| T26 | 16:53 | impl-drift returned (5 min) | |
| T26 | 16:54 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 04:15 | `make cohort` (0 min) | |
| T26 | 04:16 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 04:17 | `make cohort-seeds` (0 min) | |
| T26 | 04:19 | spec-fidelity returned CLEAR (2 min) | |
| T26 | 04:24 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 05:14 | spec-fidelity returned CLEAR (2 min) | |
| T26 | 05:17 | claims-triage returned (0 min) | |
| T26 | 05:19 | impl-drift returned (1 min) | |
| T26 | 05:27 | `make cohort` (0 min) | |
| T26 | 05:31 | spec-fidelity returned CLEAR (2 min) | |
| T26 | 05:32 | claims-triage returned (0 min) | |
| T26 | 05:34 | impl-drift returned findings (1 min) | |
| T26 | 05:36 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 05:47 | `make cohort` (0 min) | |
| T26 | 09:27 | `make cohort` (1 min) | |
| T26 | 09:27 | `make cohort` (0 min) | |
| T26 | 09:34 | `make cohort` (0 min) | |
| T26 | 09:38 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:41 | `make cohort` (1 min) | |
| T26 | 09:43 | claims-triage returned (0 min) | |
| T26 | 09:44 | `make cohort` (0 min) | |
| T26 | 09:44 | impl-drift returned findings (1 min) | |
| T26 | 09:56 | claims-triage returned findings (0 min) | |
| T26 | 09:56 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 09:58 | impl-drift returned findings (1 min) | |
| T26 | 10:05 | claims-triage returned findings (0 min) | |
| T26 | 10:07 | spec-fidelity returned CLEAR (2 min) | |
| T26 | 10:08 | impl-drift returned findings (1 min) | |
| T26 | 10:36 | `make cohort` (0 min) | |
| T26 | 10:49 | `make cohort` (0 min) | |
| T26 | 11:29 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 11:30 | `make cohort` (0 min) | |
| T26 | 11:31 | claims-triage returned (0 min) | |
| T26 | 11:33 | impl-drift returned findings (1 min) | |
| T26 | 11:35 | impl-drift returned findings (1 min) | |
| T26 | 11:39 | claims-triage returned (0 min) | |
| T26 | 11:40 | impl-drift returned findings (1 min) | |
| T26 | 11:43 | round-arbiter returned findings (2 min) | |
| T26 | 11:44 | `make cohort` (1 min) | |
| T26 | 11:45 | claims-triage returned findings (0 min) | |
| T26 | 11:46 | impl-drift returned findings (1 min) | |
| T26 | 13:25 | spec-fidelity returned CLEAR (1 min) | |
| T26 | 13:47 | `make cohort` (0 min) | |
| T26 | 13:50 | spec-fidelity returned CLEAR (4 min) | |
| T26 | 13:57 | spec-fidelity returned CLEAR (6 min) | |
| T26 | 13:58 | claims-triage returned findings (0 min) | |
| T26 | 13:58 | impl-drift returned (0 min) | |
| T26 | 13:58 | impl-drift returned (0 min) | |
| T26 | 14:00 | impl-drift returned findings (2 min) | |
| T26 | 14:03 | impl-drift returned findings (1 min) | |
| T26 | 14:04 | round-arbiter returned (1 min) | |
| T26 | 14:10 | spec-fidelity returned CLEAR (4 min) | |
| T26 | 14:26 | ticked | |
| T103 | 19:03 | started (`make task-start`) | |
| T103 | 19:04 | spec-fidelity returned CLEAR (1 min) | |
| T103 | 19:09 | claims-triage returned (0 min) | |
| T103 | 19:10 | impl-drift returned findings (1 min) | |
| T103 | 19:11 | impl-drift returned findings (0 min) | |
| T103 | 19:15 | spec-fidelity returned CLEAR (1 min) | |
| T103 | 19:18 | impl-drift returned findings (1 min) | |
| T103 | 19:19 | `make verify` (0 min) | |
| T103 | 19:27 | spec-fidelity returned CLEAR (2 min) | |
| T103 | 19:33 | spec-fidelity returned CLEAR (1 min) | |
| T103 | 19:33 | ticked | |
| T105 | 19:36 | started (`make task-start`) | |
| T105 | 19:37 | spec-fidelity returned CLEAR (1 min) | |
| T105 | 19:38 | impl-drift returned findings (1 min) | |
| T105 | 19:50 | claims-triage returned findings (0 min) | |
| T105 | 19:51 | impl-drift returned findings (0 min) | |
| T105 | 19:52 | ticked | |
| T10 | 20:00 | started (`make task-start`) | |
| T10 | 20:01 | spec-fidelity returned CLEAR (1 min) | |
| T10 | 20:03 | `make cohort` (2 min) | |
| T10 | 20:05 | impl-drift returned findings (1 min) | |
| T10 | 20:07 | impl-drift returned findings (1 min) | |
| T10 | 20:18 | ticked | |
| T67 | 20:24 | started (`make task-start`) | |
| T67 | 20:25 | spec-fidelity returned CLEAR (1 min) | |
| T67 | 20:27 | `make cohort` (3 min) | |
| T67 | 20:29 | impl-drift returned findings (1 min) | |
| T67 | 20:35 | impl-drift returned findings (1 min) | |
| T67 | 20:41 | impl-drift returned findings (1 min) | |
| T67 | 20:45 | ticked | |
| T107 | 03:45 | started (`make task-start`) | |
| T107 | 03:47 | `make cohort` (0 min) | |
| T107 | 03:48 | `make cohort` (0 min) | |
| T107 | 03:49 | research-pass returned findings (9 min) | |
| T107 | 03:56 | `make cohort` (0 min) | |
| T107 | 04:01 | `make cohort` (0 min) | |
| T107 | 04:12 | `make cohort` (3 min) | |
| T107 | 04:20 | spec-fidelity returned CLEAR (4 min) | |
| T107 | 04:25 | spec-fidelity returned CLEAR (4 min) | |
| T107 | 04:26 | claims-triage returned findings (0 min) | |
| T107 | 04:31 | spec-fidelity returned CLEAR (3 min) | |
| T107 | 04:32 | impl-drift returned findings (2 min) | |
| T107 | 04:35 | impl-drift returned findings (1 min) | |
| T107 | 04:46 | ticked | |
| T91 | 08:39 | started (`make task-start`) | |
| T91 | 08:41 | spec-fidelity returned CLEAR (1 min) | |
| T91 | 08:45 | claims-triage returned findings (0 min) | |
| T91 | 08:46 | impl-drift returned findings (1 min) | |
| T91 | 08:57 | spec-fidelity returned CLEAR (1 min) | |
| T91 | 09:03 | ticked | |
| T113 | 08:55 | started (`make task-start`) | |
| T113 | 08:57 | spec-fidelity returned CLEAR (1 min) | |
| T113 | 09:03 | ticked | |
| T93 | 09:08 | started (`make task-start`) | |
| T93 | 09:10 | spec-fidelity returned CLEAR (1 min) | |
| T93 | 09:11 | impl-drift returned findings (0 min) | |
| T93 | 09:12 | ticked | |
| T115 | 09:28 | started (`make task-start`) | |
| T115 | 09:29 | spec-fidelity returned CLEAR (1 min) | |
| T115 | 09:30 | impl-drift returned findings (1 min) | |
| T115 | 09:33 | impl-drift returned findings (1 min) | |
| T115 | 09:35 | impl-drift returned findings (1 min) | |
| T115 | 09:37 | impl-drift returned findings (0 min) | |
| T115 | 09:38 | ticked | |
| T116 | 09:39 | started (`make task-start`) | |
| T116 | 09:40 | spec-fidelity returned CLEAR (1 min) | |
| T116 | 09:42 | impl-drift returned findings (1 min) | |
| T116 | 09:46 | spec-fidelity returned CLEAR (1 min) | |
| T116 | 09:48 | spec-fidelity returned CLEAR (1 min) | |
| T116 | 09:49 | impl-drift returned findings (1 min) | |
| T116 | 09:50 | ticked | |
| T117 | 09:51 | started (`make task-start`) | |
| T117 | 09:52 | spec-fidelity returned CLEAR (1 min) | |
| T117 | 09:54 | impl-drift returned findings (0 min) | |
| T117 | 09:55 | ticked | |
| T118 | 09:55 | started (`make task-start`) | |
| T118 | 09:57 | spec-fidelity returned CLEAR (1 min) | |
| T118 | 09:59 | claims-triage returned findings (0 min) | |
| T118 | 10:03 | impl-drift returned findings (4 min) | |
| T118 | 10:05 | spec-fidelity returned CLEAR (1 min) | |
| T118 | 10:07 | claims-triage returned (0 min) | |
| T118 | 10:08 | impl-drift returned findings (1 min) | |
| T118 | 10:10 | impl-drift returned findings (1 min) | |
| T118 | 10:15 | ticked | |
| T108 | 10:16 | started (`make task-start`) | |
| T108 | 10:18 | spec-fidelity returned CLEAR (1 min) | |
| T108 | 10:21 | claims-triage returned findings (0 min) | |
| T108 | 10:22 | impl-drift returned findings (1 min) | |
| T108 | 10:23 | impl-drift returned findings (1 min) | |
| T108 | 10:24 | impl-drift returned findings (0 min) | |
| T108 | 10:29 | ticked | |
| T120 | 12:15 | started (`make task-start`) | |
| T120 | 12:18 | spec-fidelity returned CLEAR (1 min) | |
| T120 | 12:23 | ticked | |
| T102 | 12:38 | started (`make task-start`) | |
| T102 | 12:40 | spec-fidelity returned CLEAR (1 min) | |
| T102 | 12:42 | ticked | |
| T99 | 12:47 | started (`make task-start`) | |
| T99 | 12:47 | source-reader returned findings (2 min) | |
| T99 | 12:47 | quote-check returned findings (0 min) | |
| T99 | 12:48 | record-format returned findings (1 min) | |
| T99 | 12:48 | quote-check returned clean (1 min) | |
| T99 | 12:48 | spec-fidelity returned CLEAR (1 min) | |
| T99 | 12:48 | record-format returned PASS (1 min) | |
| T99 | 12:50 | ticked | |
| T09 | 12:52 | started (`make task-start`) | |
| T09 | 12:56 | spec-fidelity returned CLEAR (1 min) | |
| T09 | 12:56 | quote-check returned findings (0 min) | |
| T09 | 12:56 | record-format returned findings (0 min) | |
| T09 | 12:56 | quote-check returned findings (0 min) | |
| T09 | 12:56 | record-format returned findings (0 min) | |
| T09 | 12:56 | source-reader returned clean (0 min) | |
| T09 | 12:56 | record-format returned findings (0 min) | |
| T09 | 12:56 | quote-check returned clean (0 min) | |
| T09 | 12:57 | claims-triage returned findings (0 min) | |
| T09 | 12:58 | modal-triage returned findings (0 min) | |
| T09 | 12:58 | impl-drift returned findings (1 min) | |
| T09 | 13:01 | modal-depiction returned findings (3 min) | |
| T09 | 13:08 | spec-fidelity returned CLEAR (1 min) | |
| T09 | 13:11 | impl-drift returned findings (2 min) | |
| T09 | 13:16 | quote-check returned findings (0 min) | |
| T09 | 13:16 | record-format returned findings (0 min) | |
| T09 | 13:16 | translation-check returned FAITHFUL (0 min) | |
| T09 | 13:16 | modal-triage returned findings (0 min) | |
| T09 | 13:16 | record-format returned findings (0 min) | |
| T09 | 13:16 | quote-check returned findings (1 min) | |
| T09 | 13:16 | quote-check returned findings (1 min) | |
| T09 | 13:16 | record-format returned findings (1 min) | |
| T09 | 13:16 | source-reader returned findings (1 min) | |
| T09 | 13:17 | source-reader returned findings (1 min) | |
| T09 | 13:17 | source-applicability returned findings (1 min) | |
| T09 | 13:17 | spec-fidelity returned CLEAR (1 min) | |
| T09 | 13:17 | source-applicability returned findings (1 min) | |
| T09 | 13:19 | claims-triage returned findings (0 min) | |
| T09 | 13:19 | modal-depiction returned findings (3 min) | |
| T09 | 13:19 | impl-drift returned findings (1 min) | |
| T09 | 13:20 | impl-drift returned findings (1 min) | |
| T09 | 13:26 | quote-check returned findings (0 min) | |
| T09 | 13:26 | record-format returned findings (0 min) | |
| T09 | 13:26 | modal-triage returned findings (0 min) | |
| T09 | 13:26 | source-applicability returned findings (0 min) | |
| T09 | 13:26 | spec-fidelity returned CLEAR (1 min) | |
| T09 | 13:27 | source-applicability returned findings (2 min) | |
| T09 | 13:28 | modal-depiction returned findings (2 min) | |
| T09 | 13:28 | claims-triage returned (0 min) | |
| T09 | 13:28 | impl-drift returned findings (1 min) | |
| T09 | 13:32 | impl-drift returned findings (1 min) | |
| T09 | 13:32 | modal-depiction returned findings (4 min) | |
| T09 | 13:34 | impl-drift returned findings (1 min) | |
| T09 | 13:45 | ticked | |
| T114 | 13:49 | started (`make task-start`) | |
| T114 | 13:50 | spec-fidelity returned CLEAR (1 min) | |
| T114 | 13:54 | claims-triage returned findings (2 min) | |
| T114 | 13:55 | impl-drift returned (2 min) | |
| T114 | 13:55 | impl-drift returned (2 min) | |
| T114 | 13:55 | impl-drift returned (2 min) | |
| T114 | 13:55 | impl-drift returned (2 min) | |
| T114 | 13:55 | impl-drift returned (3 min) | |
| T114 | 13:55 | impl-drift returned (3 min) | |
| T114 | 13:58 | impl-drift returned findings (2 min) | |
| T114 | 13:58 | impl-drift returned (6 min) | |
| T114 | 13:59 | impl-drift returned findings (4 min) | |
| T114 | 14:00 | impl-drift returned (8 min) | |
| T114 | 14:07 | spec-fidelity returned CLEAR (1 min) | |
| T114 | 14:08 | impl-drift returned findings (1 min) | |
| T114 | 14:16 | ticked | |
| T126 | 14:05 | started (`make task-start`) | |
| T126 | 14:07 | spec-fidelity returned CLEAR (1 min) | |
| T126 | 14:08 | impl-drift returned findings (1 min) | |
| T126 | 14:16 | ticked | |
| T70 | 14:19 | started (`make task-start`) | |
| T70 | 14:20 | ticked | |
| T119 | 14:26 | started (`make task-start`) | |
| T119 | 14:29 | spec-fidelity returned CLEAR (1 min) | |
| T119 | 14:30 | claims-triage returned findings (0 min) | |
| T119 | 14:30 | impl-drift returned findings (1 min) | |
| T119 | 14:32 | impl-drift returned findings (2 min) | |
| T119 | 14:36 | spec-fidelity returned CLEAR (1 min) | |
| T119 | 14:38 | impl-drift returned findings (0 min) | |
| T119 | 14:43 | ticked | |
| T128 | 14:51 | started (`make task-start`) | |
| T128 | 14:52 | spec-fidelity returned CLEAR (1 min) | |
| T128 | 14:53 | impl-drift returned findings (0 min) | |
| T128 | 14:54 | research-pass returned findings (5 min) | |
| T128 | 15:00 | ticked | |
| T121 | 15:01 | started (`make task-start`) | |
| T121 | 15:05 | spec-fidelity returned CLEAR (1 min) | |
| T121 | 15:06 | claims-triage returned (0 min) | |
| T121 | 15:06 | impl-drift returned findings (0 min) | |
| T121 | 15:08 | impl-drift returned findings (1 min) | |
| T121 | 15:10 | intro-check returned findings (0 min) | |
| T121 | 15:10 | quote-check returned findings (0 min) | |
| T121 | 15:10 | translation-check returned FAITHFUL (0 min) | |
| T121 | 15:10 | record-format returned findings (0 min) | |
| T121 | 15:10 | source-reader returned clean (0 min) | |
| T121 | 15:10 | modal-triage returned findings (0 min) | |
| T121 | 15:10 | source-reader returned findings (0 min) | |
| T121 | 15:10 | record-format returned findings (1 min) | |
| T121 | 15:10 | source-reader returned findings (0 min) | |
| T121 | 15:10 | source-reader returned findings (1 min) | |
| T121 | 15:10 | record-format returned findings (1 min) | |
| T121 | 15:10 | quote-check returned findings (1 min) | |
| T121 | 15:10 | record-format returned findings (1 min) | |
| T121 | 15:10 | source-reader returned findings (1 min) | |
| T121 | 15:11 | source-reader returned findings (1 min) | |
| T121 | 15:11 | source-reader returned findings (1 min) | |
| T121 | 15:12 | source-applicability returned findings (3 min) | |
| T121 | 15:14 | ticked | |
| T124 | 15:16 | started (`make task-start`) | |
| T124 | 15:16 | quote-check returned findings (6 min) | |
| T124 | 15:19 | spec-fidelity returned CLEAR (1 min) | |
| T124 | 15:20 | claims-triage returned (0 min) | |
| T124 | 15:20 | impl-drift returned findings (0 min) | |
| T124 | 15:21 | impl-drift returned findings (0 min) | |
| T124 | 15:27 | translation-check returned FAITHFUL (0 min) | |
| T124 | 15:27 | quote-check returned findings (0 min) | |
| T124 | 15:27 | modal-triage returned findings (0 min) | |
| T124 | 15:27 | source-reader returned clean (0 min) | |
| T124 | 15:27 | source-reader returned findings (0 min) | |
| T124 | 15:27 | record-format returned findings (1 min) | |
| T124 | 15:27 | source-reader returned findings (1 min) | |
| T124 | 15:27 | quote-check returned findings (1 min) | |
| T124 | 15:27 | record-format returned findings (1 min) | |
| T124 | 15:28 | modal-depiction returned findings (1 min) | |
| T124 | 15:28 | source-applicability returned findings (2 min) | |
| T124 | 15:28 | ticked | |
| T127 | 15:30 | started (`make task-start`) | |
| T127 | 15:32 | modal-depiction returned findings (2 min) | |
| T127 | 15:34 | spec-fidelity returned BLOCKED (3 min) | |
| T127 | 15:39 | spec-fidelity returned BLOCKED (4 min) | |
| T127 | 15:43 | round-arbiter returned CLEAR (2 min) | |
| T127 | 15:46 | claims-triage returned findings (1 min) | |
| T127 | 15:50 | impl-drift returned (4 min) | |
| T127 | 15:50 | spec-fidelity returned BLOCKED (2 min) | |
| T127 | 15:51 | impl-drift returned (6 min) | |
| T127 | 15:54 | impl-drift returned (9 min) | |
| T127 | 15:55 | impl-drift returned (10 min) | |
| T127 | 16:03 | spec-fidelity returned CLEAR (3 min) | |
| T127 | 16:04 | claims-triage returned findings (0 min) | |
| T127 | 16:05 | impl-drift returned findings (0 min) | |
| T127 | 16:08 | impl-drift returned findings (5 min) | |
| T127 | 16:17 | spec-fidelity returned BLOCKED (2 min) | |
| T127 | 16:21 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 16:32 | modal-triage returned findings (0 min) | |
| T127 | 16:32 | quote-check returned findings (0 min) | |
| T127 | 16:33 | record-format returned findings (1 min) | |
| T127 | 16:33 | `make cohort-seeds` (0 min) | |
| T127 | 16:34 | modal-depiction returned clean (0 min) | |
| T127 | 16:34 | modal-depiction returned clean (0 min) | |
| T127 | 16:34 | modal-depiction returned clean (1 min) | |
| T127 | 16:34 | modal-depiction returned clean (1 min) | |
| T127 | 16:34 | modal-depiction returned clean (1 min) | |
| T127 | 16:34 | modal-depiction returned clean (1 min) | |
| T127 | 16:34 | modal-depiction returned clean (1 min) | |
| T127 | 16:35 | modal-depiction returned clean (1 min) | |
| T127 | 16:36 | round-arbiter returned findings (2 min) | |
| T127 | 16:37 | modal-depiction returned findings (1 min) | |
| T127 | 16:37 | modal-depiction returned clean (1 min) | |
| T127 | 16:39 | quote-check returned findings (0 min) | |
| T127 | 16:45 | spec-fidelity returned BLOCKED (2 min) | |
| T127 | 16:47 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 16:48 | claims-triage returned (1 min) | |
| T127 | 16:50 | impl-drift returned findings (1 min) | |
| T127 | 16:50 | impl-drift returned (2 min) | |
| T127 | 16:50 | impl-drift returned (2 min) | |
| T127 | 16:53 | impl-drift returned (5 min) | |
| T127 | 16:54 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 04:15 | `make cohort` (0 min) | |
| T127 | 04:16 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 04:17 | `make cohort-seeds` (0 min) | |
| T127 | 04:19 | spec-fidelity returned CLEAR (2 min) | |
| T127 | 04:24 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 05:14 | spec-fidelity returned CLEAR (2 min) | |
| T127 | 05:17 | claims-triage returned (0 min) | |
| T127 | 05:19 | impl-drift returned (1 min) | |
| T127 | 05:27 | `make cohort` (0 min) | |
| T127 | 05:31 | spec-fidelity returned CLEAR (2 min) | |
| T127 | 05:32 | claims-triage returned (0 min) | |
| T127 | 05:34 | impl-drift returned findings (1 min) | |
| T127 | 05:36 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 05:47 | `make cohort` (0 min) | |
| T127 | 09:27 | `make cohort` (1 min) | |
| T127 | 09:27 | `make cohort` (0 min) | |
| T127 | 09:34 | `make cohort` (0 min) | |
| T127 | 09:38 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 09:41 | `make cohort` (1 min) | |
| T127 | 09:43 | claims-triage returned (0 min) | |
| T127 | 09:44 | `make cohort` (0 min) | |
| T127 | 09:44 | impl-drift returned findings (1 min) | |
| T127 | 09:56 | claims-triage returned findings (0 min) | |
| T127 | 09:56 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 09:58 | impl-drift returned findings (1 min) | |
| T127 | 10:05 | claims-triage returned findings (0 min) | |
| T127 | 10:07 | spec-fidelity returned CLEAR (2 min) | |
| T127 | 10:08 | impl-drift returned findings (1 min) | |
| T127 | 10:36 | `make cohort` (0 min) | |
| T127 | 10:49 | `make cohort` (0 min) | |
| T127 | 11:29 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 11:30 | `make cohort` (0 min) | |
| T127 | 11:31 | claims-triage returned (0 min) | |
| T127 | 11:33 | impl-drift returned findings (1 min) | |
| T127 | 11:35 | impl-drift returned findings (1 min) | |
| T127 | 11:39 | claims-triage returned (0 min) | |
| T127 | 11:40 | impl-drift returned findings (1 min) | |
| T127 | 11:43 | round-arbiter returned findings (2 min) | |
| T127 | 11:44 | `make cohort` (1 min) | |
| T127 | 11:45 | claims-triage returned findings (0 min) | |
| T127 | 11:46 | impl-drift returned findings (1 min) | |
| T127 | 13:25 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 13:47 | `make cohort` (0 min) | |
| T127 | 13:50 | spec-fidelity returned CLEAR (4 min) | |
| T127 | 13:57 | spec-fidelity returned CLEAR (6 min) | |
| T127 | 13:58 | claims-triage returned findings (0 min) | |
| T127 | 13:58 | impl-drift returned (0 min) | |
| T127 | 13:58 | impl-drift returned (0 min) | |
| T127 | 14:00 | impl-drift returned findings (2 min) | |
| T127 | 14:03 | impl-drift returned findings (1 min) | |
| T127 | 14:04 | round-arbiter returned (1 min) | |
| T127 | 14:10 | spec-fidelity returned CLEAR (4 min) | |
| T127 | 23:30 | `make verify` (0 min) | |
| T127 | 23:36 | round-arbiter returned findings (2 min) | |
| T127 | 00:04 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 00:06 | claims-triage returned (1 min) | |
| T127 | 00:06 | impl-drift returned findings (1 min) | |
| T127 | 00:07 | spec-fidelity returned CLEAR (1 min) | |
| T127 | 00:10 | impl-drift returned findings (2 min) | |
| T127 | 00:30 | round-arbiter returned findings (1 min) | |
| T110 | 16:10 | started (`make task-start`) | |
| T110 | 16:11 | ticked | |
| T130 | 16:14 | started (`make task-start`) | |
| T130 | 16:17 | spec-fidelity returned BLOCKED (2 min) | |
| T130 | 16:21 | spec-fidelity returned CLEAR (1 min) | |
| T130 | 16:28 | ticked | |
| T129 | 16:42 | started (`make task-start`) | |
| T129 | 16:45 | spec-fidelity returned BLOCKED (2 min) | |
| T129 | 16:47 | spec-fidelity returned CLEAR (1 min) | |
| T129 | 16:48 | claims-triage returned (1 min) | |
| T129 | 16:50 | impl-drift returned findings (1 min) | |
| T129 | 16:50 | impl-drift returned (2 min) | |
| T129 | 16:50 | impl-drift returned (2 min) | |
| T129 | 16:53 | impl-drift returned (5 min) | |
| T129 | 16:54 | spec-fidelity returned CLEAR (1 min) | |
| T129 | 16:57 | ticked | |
| T133 | 04:23 | started (`make task-start`) | |
| T133 | 04:24 | spec-fidelity returned CLEAR (1 min) | |
| T133 | 04:28 | ticked | |
| T134 | 05:11 | started (`make task-start`) | |
| T134 | 05:14 | spec-fidelity returned CLEAR (2 min) | |
| T134 | 05:17 | claims-triage returned (0 min) | |
| T134 | 05:19 | impl-drift returned (1 min) | |
| T134 | 05:27 | `make cohort` (0 min) | |
| T134 | 05:31 | spec-fidelity returned CLEAR (2 min) | |
| T134 | 05:32 | claims-triage returned (0 min) | |
| T134 | 05:34 | impl-drift returned findings (1 min) | |
| T134 | 05:36 | spec-fidelity returned CLEAR (1 min) | |
| T134 | 05:45 | ticked | |
| T07 | 09:25 | started (`make task-start`) | |
| T07 | 09:27 | `make cohort` (1 min) | |
| T07 | 09:27 | `make cohort` (0 min) | |
| T07 | 09:34 | `make cohort` (0 min) | |
| T07 | 09:38 | spec-fidelity returned CLEAR (1 min) | |
| T07 | 09:41 | `make cohort` (1 min) | |
| T07 | 09:43 | claims-triage returned (0 min) | |
| T07 | 09:44 | `make cohort` (0 min) | |
| T07 | 09:44 | impl-drift returned findings (1 min) | |
| T07 | 09:56 | claims-triage returned findings (0 min) | |
| T07 | 09:56 | spec-fidelity returned CLEAR (1 min) | |
| T07 | 09:58 | impl-drift returned findings (1 min) | |
| T07 | 10:05 | claims-triage returned findings (0 min) | |
| T07 | 10:07 | spec-fidelity returned CLEAR (2 min) | |
| T07 | 10:08 | impl-drift returned findings (1 min) | |
| T07 | 10:34 | ticked | |
| T135 | 11:28 | started (`make task-start`) | |
| T135 | 11:29 | spec-fidelity returned CLEAR (1 min) | |
| T135 | 11:30 | `make cohort` (0 min) | |
| T135 | 11:31 | claims-triage returned (0 min) | |
| T135 | 11:33 | impl-drift returned findings (1 min) | |
| T135 | 11:35 | impl-drift returned findings (1 min) | |
| T135 | 11:39 | claims-triage returned (0 min) | |
| T135 | 11:40 | impl-drift returned findings (1 min) | |
| T135 | 11:43 | round-arbiter returned findings (2 min) | |
| T135 | 11:44 | `make cohort` (1 min) | |
| T135 | 11:45 | claims-triage returned findings (0 min) | |
| T135 | 11:46 | impl-drift returned findings (1 min) | |
| T135 | 11:51 | ticked | |
| T106 | 19:45 | started (`make task-start`) | |
| T106 | 23:04 | Approach re-answered | |
| T106 | 23:30 | `make verify` (0 min) | |
| T106 | 23:36 | round-arbiter returned findings (2 min) | |
| T106 | 00:04 | spec-fidelity returned CLEAR (1 min) | |
| T106 | 00:06 | claims-triage returned (1 min) | |
| T106 | 00:06 | impl-drift returned findings (1 min) | |
| T106 | 00:07 | spec-fidelity returned CLEAR (1 min) | |
| T106 | 00:10 | impl-drift returned findings (2 min) | |
| T106 | 00:30 | round-arbiter returned findings (1 min) | |
| T138 | 00:04 | started (`make task-start`) | |
| T138 | 00:04 | spec-fidelity returned CLEAR (1 min) | |
| T138 | 00:06 | claims-triage returned (1 min) | |
| T138 | 00:06 | impl-drift returned findings (1 min) | |
| T138 | 00:07 | spec-fidelity returned CLEAR (1 min) | |
| T138 | 00:10 | impl-drift returned findings (2 min) | |
| T138 | 00:27 | ticked | |

## What each check cost, per changed line (13272 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| impl-drift | 121 | 3 h 10 min | 17843k | 681.2k | 0.009 | 1.3k |
| spec-fidelity | 117 | 2 h 59 min | 9607k | 509.4k | 0.009 | 0.7k |
| spec-fidelity-verify | 2 | 1 min | 78k | 7.3k | 0.000 | 0.0k |

This report took 12.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
