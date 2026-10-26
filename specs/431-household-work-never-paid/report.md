# Feature report - 431-household-work-never-paid

Written by `make feature-report F=431` from 5143 events (2026-10-26T16:22 to 2026-10-26T19:09 UTC), 54 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 3 h 13 min | 51% |
| other tool | 59 min | 16% |
| waiting: source-reader | 23 min | 6% |
| waiting: a background run | 23 min | 6% |
| waiting: source-applicability | 20 min | 5% |
| waiting: quote-check | 17 min | 4% |
| waiting: subagent | 14 min | 4% |
| waiting: the GM | 6 min | 2% |
| waiting: record-format | 6 min | 2% |
| waiting: round-arbiter | 3 min | 1% |
| waiting: translation-check | 3 min | 1% |
| edit | 3 min | 1% |
| writing the spec | 2 min | 0% |
| waiting: intro-check | 2 min | 0% |
| test file | 1 min | 0% |
| waiting: modal-research | 1 min | 0% |
| waiting: impl-drift | 1 min | 0% |
| waiting: escalation-check | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| waiting: modal-form | 0 min | 0% |
| quick test | 0 min | 0% |
| waiting: modal-triage | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |

The session's own time above; its 1163 subagent tool call(s) (of 2310) are counted apart (0 by the subagent transcripts, 1163 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 189 run(s), 4 h 03 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 27 min |
| make check-bundle | 6 min |
| make record | 5 min |
| make apply-edits | 5 min |
| make record-owed | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 65 | clean 6, findings 59 |
| record-format | 38 | clean 1, findings 34 |
| source-applicability | 29 | clean 4, findings 23 |
| quote-check | 22 | clean 2, findings 16 |
| translation-check | 17 | FAITHFUL 14 |
| intro-check | 7 | findings 6 |
| spec-fidelity | 6 | BLOCKED 2, CLEAR 2, FAITHFUL 2 |
| research-pass | 5 | PASS 1, findings 4 |
| round-arbiter | 3 | findings 3 |
| claims-triage | 2 | findings 2 |
| escalation-check | 2 | findings 2 |
| impl-drift | 2 | findings 2 |
| modal-triage | 2 | findings 1 |
| modal-form | 1 | findings 1 |
| modal-research | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| record-format | q-0312 | 7 |
| record-format | q-0313 | 5 |
| translation-check | q-0312 | 5 |
| quote-check | q-0312 | 4 |
| quote-check | q-0313 | 4 |
| record-format | q-0311 | 4 |
| record-format | q-0314 | 4 |
| record-format | q-0315 | 4 |
| source-reader | key-tomioku-village-life-tiikijiten-whole | 4 |
| translation-check | q-0313 | 4 |
| record-format | q-0183 | 3 |
| source-applicability | key-tiangong-kaiwu-zhisi | 3 |
| source-applicability | sa-431-c | 3 |
| source-applicability | sa-431-d | 3 |
| source-reader | key-buck-1930-farm-economy-whole | 3 |
| source-reader | key-fei-1939-whole | 3 |
| source-reader | key-pomeranz-cotton-textiles-women-whole | 3 |
| source-reader | key-sukumo-shishi-kinsei-nomin-whole | 3 |
| source-reader | key-tiangong-kaiwu-zhisi-whole | 3 |
| claims-triage | claims-triage | 2 |
| impl-drift | claims-owed | 2 |
| intro-check | intro-0312-3 | 2 |
| intro-check | intro-0315 | 2 |
| quote-check | q-0183 | 2 |
| quote-check | q-0311 | 2 |
| quote-check | q-0314 | 2 |
| quote-check | q-0315 | 2 |
| record-format | q-0004 | 2 |
| record-format | q-0306 | 2 |
| source-applicability | sa-431-a | 2 |
| source-applicability | sa-431-b | 2 |
| source-reader | key-huang-pomeranz-jas-2003-whole | 2 |
| source-reader | key-ihns-bunongshu-whole | 2 |
| source-reader | key-mannering-2021-viking-age-whole | 2 |
| source-reader | key-nagashima-2017-farm-women-whole | 2 |
| source-reader | key-saito-factor-markets-labour-whole | 2 |
| source-reader | key-tanimoto-cotton-peasant-economy-whole | 2 |
| translation-check | q-0311 | 2 |
| translation-check | q-0315 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 2 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 182 over 1339 changed lines: cascade ratio 0.14
- tasks ticked: 1 of 4

## Tripwires (FR-010) - what fired, or would have

- 17:34 round:record-format|q-0311@3
- 17:34 round:record-format|q-0315@3
- 18:23 round:record-format|q-0312@3
- 18:23 round:record-format|q-0313@3
- 18:23 round:record-format|q-0314@3
- 18:23 round:source-reader|key-pomeranz-cotton-textiles-women-whole@3
- 18:36 round:record-format|q-0312@4
- 18:36 round:record-format|q-0313@4
- 18:36 round:translation-check|q-0312@3
- 18:36 round:source-reader|key-buck-1930-farm-economy-whole@3
- 18:36 round:source-reader|key-fei-1939-whole@3
- 18:36 round:source-reader|key-sukumo-shishi-kinsei-nomin-whole@3
- 18:36 round:source-reader|key-tomioku-village-life-tiikijiten-whole@3
- 18:44 round:record-format|q-0312@5
- 18:44 round:translation-check|q-0312@4
- 18:44 round:source-reader|key-tomioku-village-life-tiikijiten-whole@4
- 18:48 round:source-applicability|key-tiangong-kaiwu-zhisi@3
- 18:56 round:record-format|q-0311@4
- 18:56 round:record-format|q-0312@6
- 18:56 round:record-format|q-0313@5
- 18:56 round:record-format|q-0315@4
- 18:56 round:translation-check|q-0313@3
- 18:56 round:source-reader|key-tiangong-kaiwu-zhisi-whole@3
- 19:02 round:record-format|q-0183@3

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 2 h 11 min (open) | 2 h 01 min | 10 min | 4 | 91, 12, 5, 13, 10 |
| T03 | 19 min (open) | 9 min | 10 min | 1 | 9, 10 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 16:58-18:29 | spec-fidelity CLEAR | 830 | 179 | 88 | 0 | claims-triage x1, impl-drift x1, intro-check x6, modal-triage x1, quote-check x17, record-format x24, source-applicability x23, source-reader x56, spec-fidelity x1, translation-check x10 (148 min) |
| T01 | 18:29-18:41 | round-arbiter findings | 70 | 13 | 11 | 0 | escalation-check x1, record-format x2, round-arbiter x1, source-applicability x1, source-reader x7, translation-check x2 (13 min) |
| T01 | 18:41-18:46 | round-arbiter findings | 26 | 3 | 7 | 0 | record-format x1, round-arbiter x1, source-applicability x2, source-reader x1, translation-check x1 (4 min) |
| T01 | 18:46-18:59 | round-arbiter findings | 94 | 16 | 10 | 0 | modal-triage x1, quote-check x1, record-format x7, round-arbiter x1, source-applicability x1, source-reader x1, translation-check x1 (8 min) |
| T01 | 18:59-19:09 | the tick or the last event | 57 | 14 | 2 | 0 | claims-triage x1, escalation-check x1, impl-drift x1, modal-form x1, modal-research x1, record-format x1 (3 min) |
| T03 | 18:50-18:59 | round-arbiter findings | 73 | 12 | 6 | 0 | modal-triage x1, quote-check x1, record-format x7, round-arbiter x1, source-reader x1, translation-check x1 (8 min) |
| T03 | 18:59-19:09 | the tick or the last event | 57 | 14 | 2 | 0 | claims-triage x1, escalation-check x1, impl-drift x1, modal-form x1, modal-research x1, record-format x1 (3 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 16:58 | started (`make task-start`) | |
| T01 | 17:16 | intro-check returned findings (0 min) | |
| T01 | 17:16 | record-format returned findings (0 min) | |
| T01 | 17:16 | quote-check returned findings (0 min) | |
| T01 | 17:16 | source-reader returned clean (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | record-format returned findings (0 min) | |
| T01 | 17:16 | quote-check returned clean (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (1 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (0 min) | |
| T01 | 17:16 | source-reader returned findings (1 min) | |
| T01 | 17:16 | quote-check returned findings (1 min) | |
| T01 | 17:16 | record-format returned findings (1 min) | |
| T01 | 17:16 | source-reader returned findings (1 min) | |
| T01 | 17:16 | record-format returned findings (1 min) | |
| T01 | 17:16 | source-reader returned findings (1 min) | |
| T01 | 17:16 | source-reader returned findings (1 min) | |
| T01 | 17:16 | modal-triage returned (0 min) | |
| T01 | 17:17 | source-reader returned findings (1 min) | |
| T01 | 17:17 | translation-check returned FAITHFUL (1 min) | |
| T01 | 17:18 | source-reader returned findings (2 min) | |
| T01 | 17:18 | source-applicability returned findings (2 min) | |
| T01 | 17:19 | source-applicability returned findings (3 min) | |
| T01 | 17:21 | quote-check returned findings (5 min) | |
| T01 | 17:27 | intro-check returned findings (0 min) | |
| T01 | 17:28 | translation-check returned FAITHFUL (0 min) | |
| T01 | 17:28 | record-format returned findings (0 min) | |
| T01 | 17:28 | translation-check returned FAITHFUL (1 min) | |
| T01 | 17:28 | record-format returned findings (1 min) | |
| T01 | 17:28 | quote-check returned findings (1 min) | |
| T01 | 17:30 | quote-check returned clean (0 min) | |
| T01 | 17:30 | source-reader returned clean (0 min) | |
| T01 | 17:31 | source-reader returned findings (0 min) | |
| T01 | 17:31 | source-reader returned findings (0 min) | |
| T01 | 17:31 | source-reader returned findings (0 min) | |
| T01 | 17:31 | source-reader returned findings (0 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:31 | record-format returned findings (0 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:31 | source-applicability returned findings (4 min) | |
| T01 | 17:31 | quote-check returned findings (1 min) | |
| T01 | 17:31 | source-reader returned findings (1 min) | |
| T01 | 17:32 | source-reader returned findings (1 min) | |
| T01 | 17:32 | source-reader returned findings (1 min) | |
| T01 | 17:32 | source-reader returned findings (1 min) | |
| T01 | 17:32 | record-format returned findings (1 min) | |
| T01 | 17:32 | source-applicability returned findings (4 min) | |
| T01 | 17:32 | source-reader returned findings (2 min) | |
| T01 | 17:32 | source-reader returned findings (2 min) | |
| T01 | 17:32 | record-format returned findings (1 min) | |
| T01 | 17:32 | intro-check returned findings (0 min) | |
| T01 | 17:33 | record-format returned findings (1 min) | |
| T01 | 17:33 | translation-check returned FAITHFUL (1 min) | |
| T01 | 17:33 | quote-check returned findings (3 min) | |
| T01 | 17:33 | record-format returned findings (1 min) | |
| T01 | 17:33 | translation-check returned FAITHFUL (1 min) | |
| T01 | 17:34 | source-applicability returned findings (3 min) | |
| T01 | 17:34 | record-format returned findings (0 min) | |
| T01 | 17:34 | quote-check returned findings (0 min) | |
| T01 | 17:34 | record-format returned findings (0 min) | |
| T01 | 17:35 | source-applicability returned findings (4 min) | |
| T01 | 17:35 | claims-triage returned findings (0 min) | |
| T01 | 17:36 | source-applicability returned findings (4 min) | |
| T01 | 17:36 | impl-drift returned findings (0 min) | |
| T01 | 17:37 | source-applicability returned findings (5 min) | |
| T01 | 17:40 | quote-check returned findings (10 min) | |
| T01 | 18:01 | source-reader returned findings (0 min) | |
| T01 | 18:01 | source-reader returned findings (0 min) | |
| T01 | 18:01 | source-reader returned findings (0 min) | |
| T01 | 18:01 | source-reader returned findings (0 min) | |
| T01 | 18:01 | source-reader returned findings (0 min) | |
| T01 | 18:01 | source-reader returned findings (1 min) | |
| T01 | 18:01 | source-reader returned findings (1 min) | |
| T01 | 18:02 | source-reader returned findings (1 min) | |
| T01 | 18:02 | source-reader returned findings (1 min) | |
| T01 | 18:02 | source-reader returned findings (1 min) | |
| T01 | 18:02 | source-reader returned findings (1 min) | |
| T01 | 18:05 | source-applicability returned clean (0 min) | |
| T01 | 18:05 | source-applicability returned findings (0 min) | |
| T01 | 18:05 | source-applicability returned clean (1 min) | |
| T01 | 18:05 | source-applicability returned findings (1 min) | |
| T01 | 18:05 | source-applicability returned findings (1 min) | |
| T01 | 18:05 | source-applicability returned clean (1 min) | |
| T01 | 18:05 | source-applicability returned findings (1 min) | |
| T01 | 18:05 | source-applicability returned findings (1 min) | |
| T01 | 18:05 | source-applicability returned findings (1 min) | |
| T01 | 18:06 | source-applicability returned findings (2 min) | |
| T01 | 18:07 | source-reader returned findings (0 min) | |
| T01 | 18:07 | source-reader returned findings (0 min) | |
| T01 | 18:07 | record-format returned findings (1 min) | |
| T01 | 18:07 | source-reader returned findings (0 min) | |
| T01 | 18:07 | quote-check returned findings (1 min) | |
| T01 | 18:07 | source-applicability returned findings (2 min) | |
| T01 | 18:07 | source-reader returned findings (0 min) | |
| T01 | 18:07 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:07 | record-format returned findings (1 min) | |
| T01 | 18:07 | record-format returned findings (1 min) | |
| T01 | 18:07 | source-reader returned findings (1 min) | |
| T01 | 18:07 | source-reader returned clean (1 min) | |
| T01 | 18:07 | source-reader returned findings (1 min) | |
| T01 | 18:07 | source-reader returned findings (1 min) | |
| T01 | 18:07 | source-reader returned findings (1 min) | |
| T01 | 18:08 | source-reader returned findings (1 min) | |
| T01 | 18:08 | quote-check returned findings (2 min) | |
| T01 | 18:09 | intro-check returned findings (0 min) | |
| T01 | 18:09 | intro-check returned findings (0 min) | |
| T01 | 18:10 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:10 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:10 | record-format returned findings (1 min) | |
| T01 | 18:10 | record-format returned findings (1 min) | |
| T01 | 18:11 | quote-check returned findings (2 min) | |
| T01 | 18:11 | quote-check returned findings (2 min) | |
| T01 | 18:11 | source-applicability returned findings (5 min) | |
| T01 | 18:12 | source-applicability returned findings (6 min) | |
| T01 | 18:16 | source-reader returned findings (0 min) | |
| T01 | 18:16 | source-reader returned findings (0 min) | |
| T01 | 18:16 | intro-check returned findings (0 min) | |
| T01 | 18:16 | translation-check returned FAITHFUL (0 min) | |
| T01 | 18:16 | source-reader returned clean (0 min) | |
| T01 | 18:16 | translation-check returned FAITHFUL (0 min) | |
| T01 | 18:16 | record-format returned findings (1 min) | |
| T01 | 18:16 | record-format returned findings (1 min) | |
| T01 | 18:16 | source-applicability returned findings (1 min) | |
| T01 | 18:16 | quote-check returned findings (1 min) | |
| T01 | 18:19 | quote-check returned findings (0 min) | |
| T01 | 18:19 | record-format returned findings (1 min) | |
| T01 | 18:19 | quote-check returned findings (2 min) | |
| T01 | 18:20 | source-applicability returned findings (3 min) | |
| T01 | 18:23 | record-format returned findings (0 min) | |
| T01 | 18:23 | record-format returned findings (0 min) | |
| T01 | 18:24 | source-reader returned findings (1 min) | |
| T01 | 18:24 | record-format returned findings (1 min) | |
| T01 | 18:29 | spec-fidelity returned CLEAR (0 min) | |
| T01 | 18:31 | escalation-check returned findings (0 min) | |
| T01 | 18:37 | source-reader returned findings (0 min) | |
| T01 | 18:37 | record-format returned findings (0 min) | |
| T01 | 18:37 | source-reader returned findings (0 min) | |
| T01 | 18:37 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:37 | source-reader returned findings (0 min) | |
| T01 | 18:37 | source-reader returned clean (1 min) | |
| T01 | 18:37 | record-format returned findings (1 min) | |
| T01 | 18:37 | source-reader returned findings (1 min) | |
| T01 | 18:37 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:37 | source-reader returned findings (1 min) | |
| T01 | 18:38 | source-reader returned findings (2 min) | |
| T01 | 18:38 | source-applicability returned findings (2 min) | |
| T01 | 18:41 | round-arbiter returned findings (2 min) | |
| T01 | 18:44 | record-format returned findings (0 min) | |
| T01 | 18:44 | source-applicability returned clean (0 min) | |
| T01 | 18:44 | source-reader returned findings (0 min) | |
| T01 | 18:45 | translation-check returned FAITHFUL (1 min) | |
| T01 | 18:46 | round-arbiter returned findings (1 min) | |
| T01 | 18:46 | source-applicability returned findings (1 min) | |
| T01 | 18:48 | source-applicability returned findings (0 min) | |
| T01 | 18:56 | record-format returned findings (0 min) | |
| T01 | 18:56 | modal-triage returned findings (0 min) | |
| T01 | 18:56 | translation-check returned FAITHFUL (0 min) | |
| T01 | 18:56 | record-format returned findings (0 min) | |
| T01 | 18:56 | source-reader returned clean (0 min) | |
| T01 | 18:56 | record-format returned findings (1 min) | |
| T01 | 18:56 | record-format returned clean (1 min) | |
| T01 | 18:57 | record-format returned findings (1 min) | |
| T01 | 18:57 | record-format returned findings (1 min) | |
| T01 | 18:57 | record-format returned findings (1 min) | |
| T01 | 18:58 | quote-check returned findings (2 min) | |
| T01 | 18:59 | round-arbiter returned findings (1 min) | |
| T01 | 19:01 | modal-research returned findings (1 min) | |
| T01 | 19:02 | record-format returned findings (0 min) | |
| T01 | 19:02 | modal-form returned findings (0 min) | |
| T01 | 19:07 | claims-triage returned findings (0 min) | |
| T01 | 19:08 | impl-drift returned findings (0 min) | |
| T01 | 19:09 | escalation-check returned findings (1 min) | |
| T03 | 18:50 | started (`make task-start`) | |
| T03 | 18:56 | record-format returned findings (0 min) | |
| T03 | 18:56 | modal-triage returned findings (0 min) | |
| T03 | 18:56 | translation-check returned FAITHFUL (0 min) | |
| T03 | 18:56 | record-format returned findings (0 min) | |
| T03 | 18:56 | source-reader returned clean (0 min) | |
| T03 | 18:56 | record-format returned findings (1 min) | |
| T03 | 18:56 | record-format returned clean (1 min) | |
| T03 | 18:57 | record-format returned findings (1 min) | |
| T03 | 18:57 | record-format returned findings (1 min) | |
| T03 | 18:57 | record-format returned findings (1 min) | |
| T03 | 18:58 | quote-check returned findings (2 min) | |
| T03 | 18:59 | round-arbiter returned findings (1 min) | |
| T03 | 19:01 | modal-research returned findings (1 min) | |
| T03 | 19:02 | record-format returned findings (0 min) | |
| T03 | 19:02 | modal-form returned findings (0 min) | |
| T03 | 19:07 | claims-triage returned findings (0 min) | |
| T03 | 19:08 | impl-drift returned findings (0 min) | |
| T03 | 19:09 | escalation-check returned findings (1 min) | |

## What each check cost, per changed line (1339 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 8 | 21 min | 5975k | 85.1k | 0.006 | 4.5k |
| source-reader | 36 | 26 min | 3382k | 139.9k | 0.027 | 2.5k |
| source-applicability | 11 | 33 min | 2699k | 90.9k | 0.008 | 2.0k |
| record-format | 22 | 14 min | 2662k | 79.1k | 0.016 | 2.0k |
| spec-fidelity | 5 | 15 min | 806k | 43.4k | 0.004 | 0.6k |
| translation-check | 7 | 6 min | 397k | 32.7k | 0.005 | 0.3k |
| modal-research | 1 | 1 min | 279k | 5.3k | 0.001 | 0.2k |
| escalation-check | 1 | 1 min | 142k | 3.8k | 0.001 | 0.1k |
| modal-form | 1 | 0 min | 33k | 1.9k | 0.001 | 0.0k |
| impl-drift | 1 | 0 min | 32k | 1.0k | 0.001 | 0.0k |
| intro-check | 1 | 0 min | 24k | 2.6k | 0.001 | 0.0k |

This report took 2.2 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
