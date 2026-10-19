# Feature report - 395-shrine-building-costs

Written by `make feature-report F=395` from 2508 events (2026-10-19T04:31 to 2026-10-19T07:03 UTC), 20 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 2 h 17 min | - |
| thinking | 1 h 09 min | 53% |
| other tool | 31 min | 24% |
| waiting: source-reader | 13 min | 10% |
| waiting: source-applicability | 4 min | 3% |
| waiting: quote-check | 4 min | 3% |
| edit | 3 min | 2% |
| waiting: round-arbiter | 2 min | 1% |
| waiting: record-format | 1 min | 1% |
| waiting: translation-check | 1 min | 1% |
| dispatching: record check | 1 min | 1% |
| test file | 1 min | 1% |
| waiting: intro-check | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: subagent | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 623 subagent tool call(s) (of 1264) are counted apart (0 by the subagent transcripts, 616 by the hook's `by`, 7 by the agents' windows - an estimate; plan D30). The subagents' own work: 78 run(s), 2 h 06 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 17 min |
| make record | 3 min |
| make check-bundle | 2 min |
| make apply-edits | 2 min |
| make archive-inbox | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-applicability | 32 | findings 15 |
| source-reader | 27 | clean 3, findings 17 |
| translation-check | 17 | FAITHFUL 12 |
| quote-check | 15 | findings 11 |
| record-format | 12 | findings 8 |
| intro-check | 8 | findings 4 |
| round-arbiter | 2 | findings 2 |
| spec-fidelity | 2 | CHANGES REQUIRED 1 |
| research-pass | 1 | - |
| spec-fidelity-verify | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| translation-check | q-0257 | 5 |
| quote-check | q-0255 | 4 |
| quote-check | q-0256 | 4 |
| quote-check | q-0257 | 4 |
| source-applicability | key-kitano-2026-genna-stonewalls | 4 |
| source-applicability | key-miyazaki-2000-hagi-yashiki | 4 |
| source-reader | key-jindoh-2023-carpenter-budget-whole | 4 |
| source-reader | key-kitano-2026-osaka-day-labor-whole | 4 |
| source-reader | key-miyashiro-kumehara-1698-whole | 4 |
| translation-check | q-0255 | 4 |
| translation-check | q-0256 | 4 |
| translation-check | q-0258 | 4 |
| quote-check | q-0258 | 3 |
| record-format | q-0255 | 3 |
| record-format | q-0256 | 3 |
| record-format | q-0257 | 3 |
| record-format | q-0258 | 3 |
| source-applicability | key-jindoh-2023-carpenter-budget | 3 |
| source-applicability | key-kitano-2026-osaka-day-labor | 3 |
| source-applicability | key-matsumoto-2019-anchin | 3 |
| source-applicability | key-miyashiro-kumehara-1698 | 3 |
| source-applicability | key-oya-museum-stone-transport | 3 |
| source-applicability | key-saito-1993-bakumatsu-wages | 3 |
| source-reader | key-kawakami-1992-shrine-headman-whole | 3 |
| source-reader | key-miyazaki-2000-hagi-yashiki-whole | 3 |
| intro-check | intro-0255 | 2 |
| intro-check | intro-0256 | 2 |
| intro-check | intro-0257 | 2 |
| intro-check | intro-0258 | 2 |
| source-applicability | key-hatogamine-great-torii | 2 |
| source-applicability | key-kawakami-1991-shrine-funding | 2 |
| source-applicability | key-kawakami-1992-shrine-headman | 2 |
| source-reader | key-kawakami-1991-shrine-funding-whole | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 111 over 1151 changed lines: cascade ratio 0.10
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 06:53 round:translation-check|q-0255@3
- 06:53 round:translation-check|q-0256@3
- 06:53 round:translation-check|q-0258@3
- 06:53 round:quote-check|q-0255@3
- 06:53 round:quote-check|q-0256@3
- 06:53 round:quote-check|q-0257@3
- 06:53 round:source-reader|key-kitano-2026-osaka-day-labor-whole@3
- 06:53 round:translation-check|q-0257@3

## What each check cost, per changed line (1151 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| source-reader | 20 | 38 min | 7780k | 151.1k | 0.017 | 6.8k |
| quote-check | 11 | 27 min | 3120k | 108.3k | 0.010 | 2.7k |
| source-applicability | 15 | 27 min | 1944k | 85.3k | 0.013 | 1.7k |
| record-format | 12 | 11 min | 1146k | 57.4k | 0.010 | 1.0k |
| spec-fidelity | 2 | 6 min | 572k | 18.0k | 0.002 | 0.5k |
| translation-check | 12 | 9 min | 459k | 47.2k | 0.010 | 0.4k |
| spec-fidelity-verify | 1 | 2 min | 266k | 7.8k | 0.001 | 0.2k |
| intro-check | 4 | 2 min | 71k | 6.5k | 0.003 | 0.1k |

This report took 1.6 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
