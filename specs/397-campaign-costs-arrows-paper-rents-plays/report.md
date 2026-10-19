# Feature report - 397-campaign-costs-arrows-paper-rents-plays

Written by `make feature-report F=397` from 3210 events (2026-10-19T04:36 to 2026-10-19T11:47 UTC), 29 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 4 h 14 min | 60% |
| idle (over an hour) | 2 h 15 min | - |
| other tool | 55 min | 13% |
| waiting: translation-check | 40 min | 9% |
| waiting: round-arbiter | 34 min | 8% |
| waiting: subagent | 18 min | 4% |
| waiting: source-reader | 8 min | 2% |
| waiting: source-applicability | 5 min | 1% |
| test file | 2 min | 0% |
| waiting: record-format | 1 min | 0% |
| waiting: quote-check | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: modal-research | 1 min | 0% |
| dispatching: record check | 1 min | 0% |
| edit | 1 min | 0% |
| waiting: modal-triage | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| waiting: claims-triage | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: impl-drift | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: research-pass | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 641 subagent tool call(s) (of 1479) are counted apart (0 by the subagent transcripts, 637 by the hook's `by`, 4 by the agents' windows - an estimate; plan D30). The subagents' own work: 117 run(s), 2 h 10 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 26 min |
| make check-bundle | 5 min |
| make record | 4 min |
| make record-owed | 3 min |
| make arbiter-fix-done | 3 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 67 | clean 2, findings 46 |
| record-format | 19 | clean 1, findings 14 |
| translation-check | 15 | FAITHFUL 10 |
| quote-check | 12 | findings 6 |
| source-applicability | 10 | findings 8 |
| modal-research | 7 | clean 7 |
| round-arbiter | 7 | CHANGES REQUIRED 1, findings 6 |
| spec-fidelity | 6 | BLOCKED 1, CHANGES REQUIRED 3, CLEAR 2 |
| modal-triage | 4 | findings 3 |
| intro-check | 3 | findings 2 |
| claims-triage | 2 | - |
| impl-drift | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-gao-shouxian-jiuqing-wuliao-whole | 4 |
| source-reader | key-tanigama-2014-edo-sumo-whole | 3 |
| claims-triage | ct397-0190 | 2 |
| intro-check | ic397 | 2 |
| modal-triage | modal-triage | 2 |
| quote-check | q-0255 | 2 |
| quote-check | q-0256 | 2 |
| quote-check | q-0257 | 2 |
| record-format | rf397-0190 | 2 |
| record-format | rf397-0263 | 2 |
| record-format | rf397-0264 | 2 |
| record-format | rf397-0265 | 2 |
| source-applicability | key-saito-1993-bakumatsu-wages | 2 |
| source-reader | key-bjork-2013-edo-kabuki-theatre-whole | 2 |
| source-reader | key-bjork-2021-troupe-fees-whole | 2 |
| source-reader | key-japanknowledge-jishibai-whole | 2 |
| source-reader | key-kawakami-1991-shrine-funding-whole | 2 |
| source-reader | key-kitano-2026-osaka-day-labor-whole | 2 |
| source-reader | key-kotobank-daidogei-whole | 2 |
| source-reader | key-kotobank-geza-whole | 2 |
| source-reader | key-kotobank-kanjin-no-whole | 2 |
| source-reader | key-kotobank-sajiki-whole | 2 |
| source-reader | key-miyazaki-2000-hagi-yashiki-whole | 2 |
| source-reader | key-qingbai-leichao-xiju-whole | 2 |
| spec-fidelity | plan-397-campaign-costs-arrows-paper-rents-plays-blocks-plan-d6d4889b | 2 |
| translation-check | tc397-0263 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 134 over 1050 changed lines: cascade ratio 0.13
- tasks ticked: 8 of 10

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (1050 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| source-reader | 48 | 33 min | 3626k | 172.0k | 0.046 | 3.5k |
| quote-check | 10 | 19 min | 3017k | 82.5k | 0.010 | 2.9k |
| source-applicability | 8 | 26 min | 2826k | 86.1k | 0.008 | 2.7k |
| record-format | 15 | 13 min | 1885k | 69.7k | 0.014 | 1.8k |
| spec-fidelity | 6 | 18 min | 1577k | 57.6k | 0.006 | 1.5k |
| modal-research | 7 | 4 min | 1316k | 19.7k | 0.007 | 1.3k |
| translation-check | 10 | 8 min | 391k | 33.9k | 0.010 | 0.4k |
| intro-check | 2 | 1 min | 57k | 3.3k | 0.002 | 0.1k |
| impl-drift | 1 | 0 min | 33k | 0.6k | 0.001 | 0.0k |

This report took 2.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
