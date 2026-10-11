# Feature report - 343-receiving-court-swept

Written by `make feature-report F=343` from 4295 events (2026-10-11T00:35 to 2026-10-11T05:42 UTC), 33 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| other tool | 5 h 02 min | 44% |
| thinking | 4 h 49 min | 42% |
| test file | 45 min | 6% |
| waiting: subagent | 34 min | 5% |
| waiting: the GM | 11 min | 2% |
| dispatching: record check | 5 min | 1% |
| edit | 4 min | 1% |
| waiting: general-purpose | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: claims check | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: spec-fidelity | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| gate | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 16 min |
| make modal-bundle | 9 min |
| make arbiter-ruled | 6 min |
| make quote-verbatim | 4 min |
| make record-owed | 4 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 75 | clean 20, findings 30 |
| modal-research | 48 | clean 4, findings 28 |
| modal-form | 28 | findings 28 |
| round-arbiter | 22 | clean 1, findings 16 |
| quote-check | 12 | findings 9 |
| record-format | 12 | findings 9 |
| impl-drift | 8 | findings 6 |
| source-reader | 8 | findings 3 |
| spec-fidelity | 7 | CLEAR 6 |
| general-purpose | 6 | findings 5 |
| source-applicability | 5 | findings 5 |
| translation-check | 4 | FAITHFUL 4 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| impl-drift | claims-l7r-diagram-compound-parts-py | 5 |
| quote-check | q-0047 | 5 |
| record-format | q-0047 | 5 |
| source-reader | q-0047 | 5 |
| general-purpose | modal-triage | 4 |
| modal-depiction | modal-sheet-office-hall | 4 |
| modal-research | modal-sheet-office-hall | 4 |
| modal-research | modal-sheet-outer-court | 4 |
| impl-drift | claims-owed | 3 |
| modal-depiction | modal-choice-fan_middle--cleared | 3 |
| modal-depiction | modal-choice-fan_middle--wild | 3 |
| modal-depiction | modal-hamlet-barley | 3 |
| modal-depiction | modal-hamlet-buckwheat | 3 |
| modal-depiction | modal-hamlet-farm-holding | 3 |
| modal-depiction | modal-hamlet-millet | 3 |
| modal-depiction | modal-hamlet-privy | 3 |
| modal-depiction | modal-hamlet-soy | 3 |
| modal-depiction | modal-sheet-clerks--seats | 3 |
| modal-depiction | modal-sheet-door | 3 |
| modal-depiction | modal-sheet-garden | 3 |
| modal-depiction | modal-sheet-garden-pond | 3 |
| modal-depiction | modal-sheet-genkan | 3 |
| modal-depiction | modal-sheet-guest-quarters | 3 |
| modal-depiction | modal-sheet-kneeling-positions | 3 |
| modal-depiction | modal-sheet-magistrate-s-dais | 3 |
| modal-depiction | modal-sheet-main-gate | 3 |
| modal-depiction | modal-sheet-nakamon | 3 |
| modal-depiction | modal-sheet-outer-court | 3 |
| modal-depiction | modal-sheet-residence | 3 |
| modal-depiction | modal-sheet-side-gate | 3 |
| modal-research | modal-sheet-border-court | 3 |
| modal-research | modal-sheet-clerks--seats | 3 |
| modal-research | modal-sheet-door | 3 |
| modal-research | modal-sheet-garden | 3 |
| modal-research | modal-sheet-garden-pond | 3 |
| modal-research | modal-sheet-genkan | 3 |
| modal-research | modal-sheet-guest-quarters | 3 |
| modal-research | modal-sheet-kneeling-positions | 3 |
| modal-research | modal-sheet-magistrate-s-dais | 3 |
| modal-research | modal-sheet-main-gate | 3 |
| modal-research | modal-sheet-nakamon | 3 |
| modal-research | modal-sheet-residence | 3 |
| modal-research | modal-sheet-side-gate | 3 |
| quote-check | q-0104 | 3 |
| record-format | q-0104 | 3 |
| general-purpose | claims-triage | 2 |
| modal-depiction | modal-sheet-border-court | 2 |
| modal-depiction | modal-sheet-hearing-court | 2 |
| modal-form | modal-sheet-border-court | 2 |
| modal-form | modal-sheet-clerks--seats | 2 |
| modal-form | modal-sheet-garden | 2 |
| modal-form | modal-sheet-garden-pond | 2 |
| modal-form | modal-sheet-genkan | 2 |
| modal-form | modal-sheet-guest-quarters | 2 |
| modal-form | modal-sheet-kneeling-positions | 2 |
| modal-form | modal-sheet-magistrate-s-dais | 2 |
| modal-form | modal-sheet-main-gate | 2 |
| modal-form | modal-sheet-nakamon | 2 |
| modal-form | modal-sheet-outer-court | 2 |
| modal-form | modal-sheet-residence | 2 |
| modal-form | modal-sheet-side-gate | 2 |
| quote-check | q-0006 | 2 |
| quote-check | q-0099 | 2 |
| record-format | q-0006 | 2 |
| record-format | q-0099 | 2 |
| translation-check | q-0099 | 2 |
| translation-check | q-0104 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 0 returned
- reversals (A -> B -> A): 1 - 0047-farm-privies-and-their-night-soil-benjo.drawing.html 02:01
- check dispatches 200 over 740 changed lines: cascade ratio 0.27
- tasks ticked: 3 of 5

## Tripwires (FR-010) - what fired, or would have

- 00:38 round:impl-drift|claims-l7r-diagram-compound-parts-py@3
- 00:39 round:impl-drift|claims-l7r-diagram-compound-parts-py@4
- 00:40 round:impl-drift|claims-l7r-diagram-compound-parts-py@5
- 02:01 reversal:/diagram/.clones/diagram-research/research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html
- 02:19 round:quote-check|q-0047@3
- 02:19 round:record-format|q-0047@3
- 03:46 round:modal-research|modal-sheet-guest-quarters@3
- 04:03 round:modal-research|modal-sheet-outer-court@3

This report took 2.4 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
