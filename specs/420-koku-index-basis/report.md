# Feature report - 420-koku-index-basis

Written by `make feature-report F=420` from 6389 events (2026-10-25T12:34 to 2026-10-25T16:36 UTC), 72 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 36 min | 38% |
| other tool | 2 h 04 min | 30% |
| idle (over an hour) | 1 h 51 min | - |
| waiting: source-applicability | 44 min | 11% |
| waiting: source-reader | 38 min | 9% |
| waiting: quote-check | 23 min | 6% |
| waiting: record-format | 10 min | 2% |
| waiting: subagent | 4 min | 1% |
| test file | 3 min | 1% |
| edit | 2 min | 1% |
| waiting: translation-check | 2 min | 1% |
| waiting: intro-check | 1 min | 0% |
| waiting: round-arbiter | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| writing the spec | 0 min | 0% |
| dispatching: record check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 1585 subagent tool call(s) (of 2926) are counted apart (0 by the subagent transcripts, 1585 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 208 run(s), 4 h 56 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 26 min |
| make land-tooling | 9 min |
| make record | 8 min |
| make check-bundle | 5 min |
| make apply-edits | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 92 | clean 6, findings 78 |
| source-applicability | 34 | clean 2, findings 31 |
| quote-check | 29 | clean 1, findings 26 |
| record-format | 29 | clean 3, findings 26 |
| translation-check | 15 | FAITHFUL 15 |
| intro-check | 6 | clean 1, findings 5 |
| research-pass | 6 | findings 5 |
| round-arbiter | 4 | CLEAR 1, findings 3 |
| spec-fidelity | 4 | BLOCKED 2, CHANGES REQUIRED 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-bassino-ma-2005-whole | 8 |
| quote-check | q-0301 | 4 |
| source-reader | key-kobayashi-2017-kahei-shi-whole | 4 |
| source-reader | key-sakai-hanshiro-bakumatsu-whole | 4 |
| source-reader | key-shimomukai-mitsui-cotton-whole | 4 |
| quote-check | q-0265 | 3 |
| quote-check | qc-0302 | 3 |
| record-format | q-0265 | 3 |
| record-format | q-0298 | 3 |
| source-reader | key-bassino-2006-gpih-mitsui-whole | 3 |
| source-reader | key-boj-imes-edo-ichiryo-whole | 3 |
| source-reader | key-ndl-crd-cotton-prices-whole | 3 |
| source-reader | key-tani-1989-osaka-shakuya-whole | 3 |
| source-reader | key-washizaki-2012-edo-lot-yields-whole | 3 |
| translation-check | q-0265 | 3 |
| intro-check | intro-0265 | 2 |
| quote-check | q-0249 | 2 |
| quote-check | q-0261 | 2 |
| quote-check | q-0298 | 2 |
| record-format | q-0249 | 2 |
| record-format | q-0261 | 2 |
| record-format | q-0273 | 2 |
| record-format | q-0286 | 2 |
| record-format | q-0301 | 2 |
| record-format | q-0302 | 2 |
| record-format | rf-0288 | 2 |
| record-format | rf-0302 | 2 |
| source-applicability | key-deaton-heston-2008-understanding-ppps | 2 |
| source-applicability | key-tani-1989-osaka-shakuya | 2 |
| source-applicability | key-washizaki-2012-edo-lot-yields | 2 |
| source-applicability | sa-hong | 2 |
| source-reader | key-allen-2009-china-wages-whole | 2 |
| source-reader | key-allen-2016-nber-absolute-poverty-whole | 2 |
| source-reader | key-allen-2017-lis-absolute-poverty-whole | 2 |
| source-reader | key-broadberry-gupta-2006-great-divergence-whole | 2 |
| source-reader | key-dbnomics-bls-statjp-cpi-whole | 2 |
| source-reader | key-eia-btu-recs-2020-whole | 2 |
| source-reader | key-hud-fmr-fy2027-notice-whole | 2 |
| source-reader | key-measuringworth-explaining-measures-whole | 2 |
| source-reader | key-usda-ers-food-availability-whole | 2 |
| source-reader | key-usda-nass-agricultural-prices-2026-09-whole | 2 |
| source-reader | key-walmart-great-value-flour-whole | 2 |
| source-reader | key-wcax-vermont-firewood-2026-whole | 2 |
| translation-check | q-0249 | 2 |
| translation-check | q-0298 | 2 |
| translation-check | q-0301 | 2 |
| translation-check | tc-0302 | 2 |

## Process signals

- gates: green 1
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 205 over 1867 changed lines: cascade ratio 0.11
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- 13:36 round:source-reader|key-bassino-ma-2005-whole@3
- 13:47 round:source-reader|key-bassino-ma-2005-whole@4
- 13:48 round:source-reader|key-boj-imes-edo-ichiryo-whole@3
- 13:51 round:source-reader|key-bassino-ma-2005-whole@5
- 13:51 round:source-reader|key-kobayashi-2017-kahei-shi-whole@3
- 13:52 round:record-format|q-0298@3
- 13:52 round:source-reader|key-bassino-ma-2005-whole@6
- 13:57 round:source-reader|key-bassino-ma-2005-whole@7
- 14:12 round:source-reader|key-sakai-hanshiro-bakumatsu-whole@3
- 14:12 round:source-reader|key-shimomukai-mitsui-cotton-whole@3
- 15:54 round:quote-check|qc-0302@3
- 16:13 round:record-format|q-0265@3
- 16:13 round:translation-check|q-0265@3
- 16:16 round:quote-check|q-0265@3
- 16:16 round:quote-check|q-0301@3

## What each check cost, per changed line (1867 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| spec-fidelity | 3 | 11 min | 752k | 26.5k | 0.002 | 0.4k |
| spec-fidelity-verify | 1 | 2 min | 137k | 5.1k | 0.001 | 0.1k |

This report took 5.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
