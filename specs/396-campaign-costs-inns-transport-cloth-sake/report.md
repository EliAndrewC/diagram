# Feature report - 396-campaign-costs-inns-transport-cloth-sake

Written by `make feature-report F=396` from 2697 events (2026-10-19T04:36 to 2026-10-19T09:04 UTC), 25 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 1 h 35 min | - |
| thinking | 1 h 07 min | 57% |
| other tool | 25 min | 21% |
| waiting: source-applicability | 11 min | 9% |
| waiting: source-reader | 5 min | 4% |
| waiting: round-arbiter | 2 min | 2% |
| waiting: quote-check | 2 min | 2% |
| edit | 1 min | 1% |
| waiting: translation-check | 1 min | 1% |
| waiting: record-format | 1 min | 1% |
| test file | 1 min | 1% |
| dispatching: record check | 1 min | 0% |
| waiting: intro-check | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 653 subagent tool call(s) (of 1224) are counted apart (0 by the subagent transcripts, 653 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 107 run(s), 1 h 49 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 10 min |
| make ledger-owed | 5 min |
| make record | 3 min |
| make reserve | 2 min |
| make check-bundle | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 51 | clean 4, findings 35 |
| source-applicability | 33 | findings 27 |
| quote-check | 10 | findings 10 |
| record-format | 10 | findings 10 |
| translation-check | 8 | FAITHFUL 8 |
| round-arbiter | 6 | findings 5 |
| intro-check | 4 | clean 1, findings 3 |
| spec-fidelity | 4 | BLOCKED 1, CLEAR 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-shimomukai-mitsui-cotton-whole | 5 |
| source-reader | key-allen-2009-china-wages-whole | 4 |
| source-reader | key-ihns-bunongshu-whole | 4 |
| source-reader | key-muraoka-edo-nagaya-life-whole | 4 |
| quote-check | q-0260 | 3 |
| quote-check | q-0261 | 3 |
| record-format | q-0260 | 3 |
| record-format | q-0261 | 3 |
| source-applicability | key-ye-mengzhu-yueshibian | 3 |
| source-reader | key-bassino-ma-2005-whole | 3 |
| source-reader | key-michie-siberian-overland-whole | 3 |
| source-reader | key-muraoka-edo-izakaya-whole | 3 |
| translation-check | q-0261 | 3 |
| quote-check | q-0259 | 2 |
| quote-check | q-0262 | 2 |
| record-format | q-0259 | 2 |
| record-format | q-0262 | 2 |
| round-arbiter | arbiter-batch | 2 |
| source-applicability | key-gao-shouxian-jiuqing-wuliao | 2 |
| source-applicability | key-shimomukai-mitsui-cotton | 2 |
| source-applicability | key-shinagawa-kushi-hatago | 2 |
| source-applicability | key-tachibana-kanbun5-rikujo-kotsu | 2 |
| source-applicability | key-tokaido-qa-mlit-hatago | 2 |
| source-applicability | key-yamamoto-1969-jinba-chinsen | 2 |
| source-reader | key-gao-shouxian-jiuqing-wuliao-whole | 2 |
| source-reader | key-kotobank-tanmono-whole | 2 |
| source-reader | key-nichimen-soba-shinagaki-whole | 2 |
| source-reader | key-oamishirasato-tenpo13-bukka-whole | 2 |
| source-reader | key-saketimes-edo-sake-prices-whole | 2 |
| source-reader | key-ye-mengzhu-yueshibian-whole | 2 |
| spec-fidelity | plan-396-campaign-costs-inns-transport-cloth-sake-blocks-plan-ec946690 | 2 |
| translation-check | q-0259 | 2 |
| translation-check | q-0262 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 116 over 941 changed lines: cascade ratio 0.12
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 08:41 round:source-reader|key-ihns-bunongshu-whole@3
- 08:59 round:quote-check|q-0260@3
- 08:59 round:quote-check|q-0261@3
- 08:59 round:record-format|q-0260@3
- 08:59 round:record-format|q-0261@3
- 08:59 round:translation-check|q-0261@3
- 08:59 round:source-reader|key-allen-2009-china-wages-whole@3
- 09:00 round:source-reader|key-shimomukai-mitsui-cotton-whole@3

## What each check cost, per changed line (941 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 10 | 17 min | 4107k | 77.0k | 0.011 | 4.4k |
| source-applicability | 27 | 37 min | 3400k | 122.6k | 0.029 | 3.6k |
| source-reader | 39 | 29 min | 3274k | 146.6k | 0.041 | 3.5k |
| record-format | 10 | 8 min | 1164k | 43.6k | 0.011 | 1.2k |
| translation-check | 8 | 5 min | 320k | 31.6k | 0.009 | 0.3k |
| spec-fidelity | 2 | 4 min | 201k | 13.2k | 0.002 | 0.2k |
| spec-fidelity-verify | 2 | 3 min | 162k | 8.6k | 0.002 | 0.2k |
| intro-check | 4 | 1 min | 72k | 6.4k | 0.004 | 0.1k |

This report took 2.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
