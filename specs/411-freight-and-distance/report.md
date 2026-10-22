# Feature report - 411-freight-and-distance

Written by `make feature-report F=411` from 3328 events (2026-10-22T09:57 to 2026-10-22T12:55 UTC), 27 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 37 min | 58% |
| idle (over an hour) | 1 h 01 min | - |
| waiting: source-applicability | 40 min | 15% |
| other tool | 31 min | 12% |
| waiting: the GM | 13 min | 5% |
| waiting: source-reader | 13 min | 5% |
| waiting: subagent | 8 min | 3% |
| edit | 4 min | 1% |
| test file | 1 min | 0% |
| waiting: translation-check | 1 min | 0% |
| waiting: quote-check | 0 min | 0% |
| waiting: record-format | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |

The session's own time above; its 714 subagent tool call(s) (of 1524) are counted apart (0 by the subagent transcripts, 714 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 112 run(s), 2 h 50 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 13 min |
| make record | 4 min |
| make apply-edits | 4 min |
| make check-bundle | 2 min |
| WebSearch | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 50 | clean 6, findings 44 |
| source-applicability | 44 | clean 1, findings 26 |
| record-format | 9 | findings 9 |
| quote-check | 8 | findings 8 |
| translation-check | 8 | FAITHFUL 8 |
| research-pass | 4 | findings 2 |
| spec-fidelity | 4 | CHANGES REQUIRED 1, CLEAR 2 |
| intro-check | 2 | findings 2 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-rockhill-1891-land-of-the-lamas-whole | 4 |
| record-format | q-0282 | 3 |
| source-reader | key-cheng-2024-transport-cost-whole | 3 |
| source-reader | key-kibe-1999-hagi-kaimai-unchin-whole | 3 |
| intro-check | intro-0280-4 | 2 |
| quote-check | q-0280 | 2 |
| quote-check | q-0281 | 2 |
| quote-check | q-0282 | 2 |
| quote-check | q-0283 | 2 |
| record-format | q-0280 | 2 |
| record-format | q-0281 | 2 |
| record-format | q-0283 | 2 |
| source-applicability | key-guangdong-xinyu-25 | 2 |
| source-applicability | key-jawiki-uji-saichashi | 2 |
| source-applicability | key-kato-2007-taru-kaisen | 2 |
| source-applicability | key-keihan-oharame | 2 |
| source-applicability | key-kibe-1999-hagi-kaimai-unchin | 2 |
| source-applicability | key-kobe-nada-shuzogyo | 2 |
| source-applicability | key-kotobank-jikata-hanreiroku | 2 |
| source-applicability | key-kyakhta-trade-enwiki | 2 |
| source-applicability | key-michie-siberian-overland | 2 |
| source-applicability | key-mingshi-80-chafa | 2 |
| source-applicability | key-nakamura-2020-fukui-nengu | 2 |
| source-applicability | key-parkes-1854-kyakhta-caravan | 2 |
| source-applicability | key-qingshigao-122-caoyun | 2 |
| source-applicability | key-rockhill-1891-land-of-the-lamas | 2 |
| source-applicability | key-shiji-129-huozhi | 2 |
| source-applicability | key-sukumo-charcoal | 2 |
| source-applicability | key-xutan-2000-market-network | 2 |
| source-reader | key-daxue-yanyi-bu-33-whole | 2 |
| source-reader | key-daxue-yanyi-bu-34-whole | 2 |
| source-reader | key-guangdong-xinyu-25-whole | 2 |
| source-reader | key-kato-2007-taru-kaisen-whole | 2 |
| source-reader | key-kobe-nada-shuzogyo-whole | 2 |
| source-reader | key-mingshi-79-caoyun-whole | 2 |
| source-reader | key-qingshigao-122-caoyun-whole | 2 |
| source-reader | key-xutan-2000-market-network-whole | 2 |
| translation-check | q-0280 | 2 |
| translation-check | q-0281 | 2 |
| translation-check | q-0282 | 2 |
| translation-check | q-0283 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 121 over 1045 changed lines: cascade ratio 0.12
- tasks ticked: 0 of 6

## Tripwires (FR-010) - what fired, or would have

- 12:40 round:source-reader|key-cheng-2024-transport-cost-whole@3
- 12:40 round:source-reader|key-kibe-1999-hagi-kaimai-unchin-whole@3
- 12:45 round:source-reader|key-rockhill-1891-land-of-the-lamas-whole@3
- 12:45 round:record-format|q-0282@3
- 12:47 round:source-reader|key-rockhill-1891-land-of-the-lamas-whole@4

## What each check cost, per changed line (1045 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| source-reader | 50 | 44 min | 4320k | 201.6k | 0.048 | 4.1k |
| source-applicability | 27 | 36 min | 2912k | 117.4k | 0.026 | 2.8k |
| quote-check | 8 | 20 min | 2581k | 89.8k | 0.008 | 2.5k |
| record-format | 9 | 12 min | 1419k | 56.0k | 0.009 | 1.4k |
| spec-fidelity | 3 | 6 min | 510k | 22.5k | 0.003 | 0.5k |
| translation-check | 8 | 8 min | 359k | 39.7k | 0.008 | 0.3k |
| intro-check | 2 | 1 min | 99k | 6.0k | 0.002 | 0.1k |
| spec-fidelity-verify | 1 | 1 min | 83k | 4.0k | 0.001 | 0.1k |

This report took 4.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
