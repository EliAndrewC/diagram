# Feature report - 374-match-the-research-continued

Written by `make feature-report F=374` from 29219 events (2026-10-10T20:51 to 2026-10-13T13:18 UTC), 270 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 61 h 05 min | - |
| thinking | 25 h 30 min | 51% |
| other tool | 14 h 36 min | 29% |
| waiting: the GM | 4 h 28 min | 9% |
| waiting: subagent | 3 h 10 min | 6% |
| test file | 34 min | 1% |
| waiting: a background run | 29 min | 1% |
| quick test | 28 min | 1% |
| dispatching: review check | 9 min | 0% |
| edit | 5 min | 0% |
| writing the spec | 5 min | 0% |
| dispatching: record check | 4 min | 0% |
| spec-kit step | 3 min | 0% |
| dispatching: spec review | 2 min | 0% |
| dispatching: claims check | 1 min | 0% |
| gate | 1 min | 0% |
| waiting: impl-drift | 1 min | 0% |
| waiting: spec-fidelity | 1 min | 0% |
| waiting: modal-depiction | 0 min | 0% |
| waiting: record-format | 0 min | 0% |
| waiting: general-purpose | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: modal-form | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: modal-research | 0 min | 0% |
| waiting: building-review | 0 min | 0% |
| waiting: round-arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 h 12 min |
| make land-tooling | 1 h 03 min |
| make hooks-test | 30 min |
| make ledger-owed | 25 min |
| make map | 24 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 158 | clean 43, findings 94 |
| impl-drift | 116 | clean 1, findings 112 |
| spec-fidelity | 107 | BLOCKED 26, CHANGES REQUIRED 1, CLEAR 72, findings 1 |
| general-purpose | 87 | findings 50 |
| building-review | 85 | NEEDS-WORK 14, PASS 3, findings 14 |
| glyph-check | 67 | NEEDS-WORK 1, PASS 8, findings 4 |
| quote-check | 67 | clean 6, findings 49 |
| modal-form | 57 | clean 4, findings 51 |
| modal-research | 53 | clean 8, findings 42 |
| record-format | 53 | findings 49 |
| round-arbiter | 40 | FAITHFUL 1, NEEDS-WORK 2, findings 36 |
| size-audit | 12 | PASS 3, findings 2 |
| escalation-check | 10 | findings 10 |
| translation-check | 6 | FAITHFUL 5 |
| source-reader | 5 | findings 5 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-owed | 82 |
| general-purpose | claims-triage | 40 |
| general-purpose | modal-triage | 27 |
| round-arbiter | arbiter-batch | 10 |
| quote-check | batch-1 | 8 |
| quote-check | batch-2 | 7 |
| record-format | q-0075 | 7 |
| modal-form | modal-choice-row_shelter--own_grove | 6 |
| modal-form | modal-sheet-servants--quarters | 6 |
| quote-check | batch-3 | 6 |
| modal-depiction | modal-sheet-servants--quarters | 5 |
| modal-depiction | modal-sheet-well | 5 |
| quote-check | batch-4 | 5 |
| quote-check | q-0033 | 5 |
| record-format | q-0033 | 5 |
| record-format | q-0196 | 5 |
| modal-form | modal-choice-row_shelter--sheltered | 4 |
| modal-form | modal-hamlet-floodplain-meadow | 4 |
| modal-research | modal-sheet-servants--quarters | 4 |
| quote-check | q-0075 | 4 |
| quote-check | q-0196 | 4 |
| record-format | q-0019 | 4 |
| modal-depiction | mb7-residence | 3 |
| modal-depiction | modal-choice-bamboo--both | 3 |
| modal-depiction | modal-choice-bamboo--homestead | 3 |
| modal-depiction | modal-choice-bamboo--thicket | 3 |
| modal-depiction | modal-hamlet-homestead-grove | 3 |
| modal-depiction | modal-hamlet-household-shrine | 3 |
| modal-form | modal-hamlet-paddy-s-grass-hill | 3 |
| modal-research | modal-choice-row_shelter--own_grove | 3 |
| modal-research | modal-choice-row_shelter--sheltered | 3 |
| modal-research | modal-hamlet-homestead-bamboo | 3 |
| quote-check | q-0016 | 3 |
| quote-check | q-0091 | 3 |
| record-format | q-0091 | 3 |
| record-format | q-0115 | 3 |
| record-format | q-0219 | 3 |
| translation-check | q-0219 | 3 |
| impl-drift | b15-t10 | 2 |
| modal-depiction | mb10-field_archetype--polder_grid | 2 |
| modal-depiction | modal-choice-bamboo--none | 2 |
| modal-depiction | modal-choice-grove_sides--2 | 2 |
| modal-depiction | modal-choice-grove_sides--3 | 2 |
| modal-depiction | modal-choice-grove_sides--4 | 2 |
| modal-depiction | modal-choice-row_shelter--own_grove | 2 |
| modal-depiction | modal-choice-row_shelter--sheltered | 2 |
| modal-depiction | modal-choice-washing_form--each_house | 2 |
| modal-depiction | modal-choice-well_siting--cluster | 2 |
| modal-depiction | modal-hamlet-homestead-bamboo | 2 |
| modal-depiction | modal-hamlet-paddy-s-grass-hill | 2 |
| modal-depiction | modal-hamlet-well | 2 |
| modal-depiction | modal-hamlet-woodland-commons | 2 |
| modal-depiction | modal-sheet-residence | 2 |
| modal-depiction | modal-sheet-retainers--quarters | 2 |
| modal-depiction | modal-sheet-stables | 2 |
| modal-depiction | modal-sheet-storehouse | 2 |
| modal-form | modal-choice-washing_form--each_house | 2 |
| modal-form | modal-hamlet-pig-sty | 2 |
| modal-form | modal-sheet-wood-kami-altar | 2 |
| modal-research | modal-choice-bamboo--both | 2 |
| modal-research | modal-choice-bamboo--homestead | 2 |
| modal-research | modal-choice-row_sides--both | 2 |
| modal-research | modal-hamlet-floodplain-meadow | 2 |
| modal-research | modal-hamlet-paddy-s-grass-hill | 2 |
| modal-research | modal-hamlet-pig-sty | 2 |
| modal-research | modal-sheet-well | 2 |
| quote-check | q-0019 | 2 |
| quote-check | q-0065 | 2 |
| quote-check | q-0115 | 2 |
| quote-check | q-0219 | 2 |
| record-format | q-0016 | 2 |
| record-format | q-0049 | 2 |
| record-format | q-0065 | 2 |
| record-format | q-0093 | 2 |
| record-format | q-0236 | 2 |
| source-reader | q-0219 | 2 |

## Process signals

- gates: already-verified 9, green 27, red 12
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 35 recorded in commits, 26 returned
- reversals (A -> B -> A): 0
- check dispatches 679 over 12922 changed lines: cascade ratio 0.05
- tasks ticked: 44 of 49

## Tripwires (FR-010) - what fired, or would have

- 22:55 round:building-review|building-review--ubame-magistracy@3
- 22:55 round:building-review|building-review--hayakawa-magistracy@3
- 06:18 round:impl-drift|claims-owed@3
- 06:39 round:impl-drift|claims-owed@4
- 06:42 round:impl-drift|claims-owed@5
- 07:18 round:impl-drift|claims-owed@6
- 07:35 round:impl-drift|claims-owed@7
- 07:45 round:impl-drift|claims-owed@8
- 07:54 round:modal-depiction|modal-hamlet-household-shrine@3
- 08:07 round:impl-drift|claims-owed@9
- 08:34 round:building-review|building-review--hayakawa-magistracy@4
- 08:34 round:building-review|building-review--county-magistracy-example@3
- 08:34 round:building-review|building-review--ubame-magistracy@4
- 09:14 round:modal-form|modal-sheet-servants--quarters@3
- 09:16 round:modal-form|modal-sheet-servants--quarters@4
- 09:16 round:impl-drift|claims-owed@10
- 09:26 round:impl-drift|claims-owed@11
- 09:26 round:modal-form|modal-sheet-servants--quarters@5
- 09:27 round:modal-research|modal-sheet-servants--quarters@3
- 09:28 round:impl-drift|claims-owed@12
- 09:30 round:impl-drift|claims-owed@13
- 09:30 round:impl-drift|claims-owed@14
- 09:33 round:impl-drift|claims-owed@15
- 09:33 round:modal-form|modal-sheet-servants--quarters@6
- 09:34 round:modal-research|modal-sheet-servants--quarters@4
- 09:38 round:modal-depiction|modal-sheet-servants--quarters@3
- 09:38 round:quote-check|batch-1@3
- 09:40 round:modal-depiction|modal-sheet-servants--quarters@4
- 09:41 round:impl-drift|claims-owed@16
- 09:42 round:record-format|q-0115@3
- 09:42 round:modal-depiction|modal-sheet-servants--quarters@5
- 09:58 round:impl-drift|claims-owed@17
- 10:14 round:building-review|building-review--hayakawa-magistracy@5
- 10:14 round:building-review|building-review--county-magistracy-example@4
- 10:15 round:building-review|building-review--ubame-magistracy@5
- 11:30 round:building-review|building-review--county-magistracy-example@5
- 11:33 round:building-review|building-review--hayakawa-magistracy@6
- 11:33 round:building-review|building-review--hoshigaoka-shrine@3
- 11:33 round:building-review|building-review--ochiba-magistracy@3
- 11:33 round:building-review|building-review--ubame-magistracy@6
- 11:34 round:impl-drift|claims-owed@18
- 12:28 round:impl-drift|claims-owed@19
- 12:33 round:impl-drift|claims-owed@20
- 12:34 round:impl-drift|claims-owed@21
- 12:34 round:building-review|building-review--hayakawa-magistracy@7
- 12:34 round:building-review|building-review--ubame-magistracy@7
- 13:41 round:impl-drift|claims-owed@22
- 13:44 round:modal-depiction|modal-sheet-well@3
- 13:50 round:impl-drift|claims-owed@23
- 13:55 red-gate
- 14:02 round:building-review|building-review--county-magistracy-example@6
- 14:03 round:building-review|building-review--hayakawa-magistracy@8
- 14:03 round:building-review|building-review--ochiba-magistracy@4
- 14:04 round:building-review|building-review--ubame-magistracy@8
- 14:04 round:impl-drift|claims-owed@24
- 14:23 round:impl-drift|claims-owed@25
- 14:28 round:record-format|q-0196@3
- 14:28 round:modal-depiction|modal-sheet-well@4
- 14:28 round:impl-drift|claims-owed@26
- 14:28 round:impl-drift|claims-owed@27
- 14:33 round:quote-check|q-0196@3
- 14:33 round:record-format|q-0196@4
- 14:33 round:modal-depiction|modal-sheet-well@5
- 14:33 round:impl-drift|claims-owed@28
- 14:34 round:impl-drift|claims-owed@29
- 14:43 round:building-review|building-review--county-magistracy-example@7
- 14:43 round:building-review|building-review--hayakawa-magistracy@9
- 14:43 round:building-review|building-review--ochiba-magistracy@5
- 14:43 round:building-review|building-review--ubame-magistracy@9
- 14:54 round:building-review|building-review--county-magistracy-example@8
- 14:55 round:building-review|building-review--hayakawa-magistracy@10
- 14:55 round:building-review|building-review--ochiba-magistracy@6
- 14:55 round:building-review|building-review--ubame-magistracy@10
- 15:55 round:impl-drift|claims-owed@30
- 16:05 round:quote-check|batch-4@3
- 16:05 round:record-format|q-0019@3
- 16:07 round:impl-drift|claims-owed@31
- 16:07 round:quote-check|q-0016@3
- 16:13 round:impl-drift|claims-owed@32
- 16:26 red-gate
- 16:34 round:impl-drift|claims-owed@33
- 16:49 round:impl-drift|claims-owed@34
- 16:50 round:impl-drift|claims-owed@35
- 16:51 round:impl-drift|claims-owed@36
- 17:29 round:impl-drift|claims-owed@37
- 17:36 round:impl-drift|claims-owed@38
- 17:43 round:impl-drift|claims-owed@39
- 17:47 round:impl-drift|claims-owed@40
- 18:36 round:impl-drift|claims-owed@41
- 18:37 round:impl-drift|claims-owed@42
- 19:29 round:impl-drift|claims-owed@43
- 19:32 round:impl-drift|claims-owed@44
- 19:34 round:impl-drift|claims-owed@45
- 20:09 round:impl-drift|claims-owed@46
- 20:10 round:impl-drift|claims-owed@47
- 20:16 round:modal-form|modal-hamlet-floodplain-meadow@3
- 20:19 round:modal-form|modal-hamlet-floodplain-meadow@4
- 21:11 round:impl-drift|claims-owed@48
- 21:13 round:impl-drift|claims-owed@49
- 21:14 round:impl-drift|claims-owed@50
- 21:16 round:impl-drift|claims-owed@51
- 21:18 round:impl-drift|claims-owed@52
- 21:19 round:impl-drift|claims-owed@53
- 21:38 round:impl-drift|claims-owed@54
- 21:55 round:impl-drift|claims-owed@55
- 21:55 round:modal-form|modal-hamlet-paddy-s-grass-hill@3
- 21:57 round:impl-drift|claims-owed@56
- 01:17 round:impl-drift|claims-owed@57
- 01:23 round:quote-check|batch-3@3
- 01:24 round:impl-drift|claims-owed@58
- 01:28 round:impl-drift|claims-owed@59
- 02:02 round:impl-drift|claims-owed@60
- 02:24 round:impl-drift|claims-owed@61
- 02:34 round:impl-drift|claims-owed@62
- 02:35 round:impl-drift|claims-owed@63
- 02:43 round:impl-drift|claims-owed@64
- 03:56 round:quote-check|batch-1@4
- 03:56 round:impl-drift|claims-owed@65
- 04:08 round:impl-drift|claims-owed@66
- 04:10 round:quote-check|batch-1@5
- 04:22 round:impl-drift|claims-owed@67
- 04:47 round:impl-drift|claims-owed@68
- 04:55 round:impl-drift|claims-owed@69
- 05:02 round:impl-drift|claims-owed@70
- 05:50 round:impl-drift|claims-owed@71
- 06:43 round:record-format|q-0075@3
- 06:43 round:quote-check|batch-1@6
- 06:43 round:quote-check|batch-3@4
- 07:10 round:record-format|q-0075@4
- 07:15 round:impl-drift|claims-owed@72
- 07:27 round:impl-drift|claims-owed@73
- 07:28 round:quote-check|q-0033@3
- 07:28 round:record-format|q-0033@3
- 07:28 round:record-format|q-0075@5
- 07:29 round:modal-form|modal-choice-row_shelter--own_grove@3
- 07:29 round:modal-form|modal-choice-row_shelter--sheltered@3
- 07:36 round:quote-check|q-0033@4
- 07:36 round:quote-check|q-0075@3
- 07:36 round:record-format|q-0033@4
- 07:36 round:record-format|q-0075@6
- 07:39 round:modal-form|modal-choice-row_shelter--own_grove@4
- 07:43 round:quote-check|q-0033@5
- 07:43 round:record-format|q-0033@5
- 07:43 round:modal-form|modal-choice-row_shelter--own_grove@5
- 07:43 round:modal-form|modal-choice-row_shelter--sheltered@4
- 07:48 round:impl-drift|claims-owed@74
- 07:55 round:quote-check|q-0075@4
- 07:55 round:record-format|q-0075@7
- 07:57 round:impl-drift|claims-owed@75
- 07:59 round:modal-form|modal-choice-row_shelter--own_grove@6
- 07:59 round:modal-research|modal-choice-row_shelter--sheltered@3
- 07:59 round:modal-depiction|modal-choice-bamboo--thicket@3
- 07:59 round:modal-depiction|modal-hamlet-homestead-grove@3
- 08:00 round:modal-research|modal-choice-row_shelter--own_grove@3
- 08:05 round:modal-research|modal-hamlet-homestead-bamboo@3
- 08:07 round:modal-depiction|modal-choice-bamboo--homestead@3
- 08:08 round:impl-drift|claims-owed@76
- 08:14 round:modal-depiction|modal-choice-bamboo--both@3
- 08:46 round:impl-drift|claims-owed@77
- 08:49 round:impl-drift|claims-owed@78
- 10:43 round:impl-drift|claims-owed@79
- 10:55 round:record-format|q-0196@5
- 10:55 round:quote-check|q-0196@4
- 10:56 round:impl-drift|claims-owed@80
- 10:57 round:quote-check|batch-1@7
- 10:57 round:quote-check|batch-2@3
- 10:57 round:quote-check|batch-3@5
- 10:57 round:quote-check|batch-4@4
- 11:20 round:impl-drift|claims-owed@81
- 11:31 red-gate

This report took 8.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
