# Feature report - 428-working-days-and-performances

Written by `make feature-report F=428` from 3101 events (2026-10-26T13:01 to 2026-10-26T14:53 UTC), 34 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 1 h 28 min | 38% |
| thinking | 1 h 24 min | 37% |
| waiting: source-reader | 16 min | 7% |
| waiting: a background run | 12 min | 5% |
| waiting: subagent | 5 min | 2% |
| waiting: source-applicability | 5 min | 2% |
| waiting: modal-form | 4 min | 2% |
| waiting: quote-check | 3 min | 2% |
| waiting: modal-research | 3 min | 1% |
| waiting: record-format | 2 min | 1% |
| waiting: translation-check | 2 min | 1% |
| edit | 1 min | 1% |
| test file | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: modal-depiction | 1 min | 0% |
| waiting: round-arbiter | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| waiting: modal-triage | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 700 subagent tool call(s) (of 1398) are counted apart (0 by the subagent transcripts, 700 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 127 run(s), 2 h 31 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 11 min |
| make land | 9 min |
| make land-tooling | 5 min |
| make record | 4 min |
| make apply-edits | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 48 | clean 1, findings 41 |
| source-applicability | 29 | clean 4, findings 20 |
| record-format | 19 | findings 17 |
| quote-check | 13 | findings 12 |
| translation-check | 8 | FAITHFUL 8 |
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 2 |
| intro-check | 3 | findings 3 |
| modal-research | 3 | clean 1, findings 2 |
| research-pass | 3 | findings 3 |
| claims-triage | 2 | - |
| modal-form | 2 | findings 2 |
| modal-triage | 2 | findings 2 |
| round-arbiter | 2 | findings 2 |
| escalation-check | 1 | findings 1 |
| impl-drift | 1 | findings 1 |
| modal-depiction | 1 | clean 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| record-format | q-0309 | 3 |
| record-format | q-0310 | 3 |
| source-reader | key-kaken-ohtomo-shogun-funerals-whole | 3 |
| claims-triage | claims-triage | 2 |
| quote-check | q-0309 | 2 |
| quote-check | q-0310 | 2 |
| record-format | q-0187 | 2 |
| source-applicability | key-jawiki-kaomise | 2 |
| source-applicability | key-kaken-ohtomo-shogun-funerals | 2 |
| source-applicability | key-kotobank-koshibai | 2 |
| source-applicability | key-kotobank-miyaji-shibai | 2 |
| source-applicability | key-lin-2001-miaohui | 2 |
| source-reader | key-chinanews-2013-biaoju-whole | 2 |
| source-reader | key-edo-sanza-jawiki-whole | 2 |
| source-reader | key-jawiki-kaomise-whole | 2 |
| source-reader | key-kotobank-koshibai-whole | 2 |
| source-reader | key-kotobank-miyaji-shibai-whole | 2 |
| source-reader | key-lin-2001-miaohui-whole | 2 |
| source-reader | key-nact-oedo-kabuki-2026-whole | 2 |
| source-reader | key-park-2014-village-rest-days-whole | 2 |
| source-reader | key-you-2016-qing-litigation-masters-whole | 2 |
| translation-check | q-0309 | 2 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 127 over 883 changed lines: cascade ratio 0.14
- tasks ticked: 2 of 4

## Tripwires (FR-010) - what fired, or would have

- none

## Each task, split at its decision points

| task | start to tick | to its last decision | after it | decisions | segments (min) |
|---|---|---|---|---|---|
| T01 | 13 min | 0 min | 13 min | 0 | 13 |

## Each task's phases (plan D32)

| task | span (UTC) | ended by | session calls | session working (min) | session waiting (min) | idle (min) | subagents started in it |
|---|---|---|---|---|---|---|---|
| T01 | 14:39-14:52 | the tick or the last event | 23 | 12 | 1 | 0 | claims-triage x1, escalation-check x1, impl-drift x1 (3 min) |

## Each task's decision-log skeleton (plan D33) - fill the last column in the retro

| task | UTC | point | what decided it |
|---|---|---|---|
| T01 | 14:39 | started (`make task-start`) | |
| T01 | 14:48 | claims-triage returned (0 min) | |
| T01 | 14:50 | escalation-check returned findings (1 min) | |
| T01 | 14:51 | impl-drift returned findings (2 min) | |
| T01 | 14:52 | ticked | |

## What each check cost, per changed line (883 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 7 | 12 min | 2368k | 48.7k | 0.008 | 2.7k |
| source-reader | 28 | 18 min | 2142k | 86.2k | 0.032 | 2.4k |
| modal-research | 2 | 3 min | 1510k | 18.3k | 0.002 | 1.7k |
| record-format | 9 | 6 min | 1234k | 33.8k | 0.010 | 1.4k |
| source-applicability | 13 | 14 min | 1105k | 48.9k | 0.015 | 1.3k |
| spec-fidelity | 2 | 6 min | 331k | 15.0k | 0.002 | 0.4k |
| translation-check | 6 | 3 min | 190k | 18.3k | 0.007 | 0.2k |
| spec-fidelity-verify | 1 | 3 min | 164k | 5.6k | 0.001 | 0.2k |
| impl-drift | 1 | 2 min | 147k | 4.0k | 0.001 | 0.2k |
| escalation-check | 1 | 1 min | 122k | 3.5k | 0.001 | 0.1k |
| modal-form | 1 | 1 min | 35k | 3.9k | 0.001 | 0.0k |
| intro-check | 1 | 0 min | 19k | 1.0k | 0.001 | 0.0k |

This report took 1.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
