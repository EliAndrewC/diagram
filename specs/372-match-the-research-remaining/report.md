# Feature report - 372-match-the-research-remaining

Written by `make feature-report F=372` from 2343 events (2026-10-10T06:09 to 2026-10-10T15:12 UTC), 59 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 3 h 38 min | 40% |
| other tool | 2 h 18 min | 25% |
| waiting: a background run | 59 min | 11% |
| waiting: spec-fidelity | 48 min | 9% |
| waiting: glyph-check | 20 min | 4% |
| waiting: impl-drift | 15 min | 3% |
| quick test | 9 min | 2% |
| waiting: building-review | 8 min | 1% |
| dispatching: spec review | 6 min | 1% |
| dispatching: claims check | 4 min | 1% |
| test file | 4 min | 1% |
| spec-kit step | 3 min | 1% |
| dispatching: record check | 2 min | 0% |
| waiting: escalation-check | 2 min | 0% |
| waiting: modal-research | 2 min | 0% |
| dispatching: review check | 2 min | 0% |
| waiting: modal-form | 1 min | 0% |
| waiting: modal-depiction | 1 min | 0% |
| edit | 0 min | 0% |
| writing the spec | 0 min | 0% |
| waiting: quote-check | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| waiting: general-purpose | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 1 h 42 min |
| make claims-checked | 14 min |
| make map | 6 min |
| make pack-audit | 5 min |
| make record-checked | 5 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 47 | clean 31, findings 16 |
| impl-drift | 42 | findings 42 |
| spec-fidelity | 30 | BLOCKED 9, CHANGES REQUIRED 1, CLEAR 18, FAITHFUL 1, findings 1 |
| glyph-check | 26 | NEEDS-WORK 1, NOT-REVIEWABLE 1, PASS 4, findings 4 |
| building-review | 11 | NEEDS-WORK 3, findings 2 |
| general-purpose | 10 | findings 6 |
| quote-check | 10 | findings 10 |
| record-format | 10 | findings 10 |
| escalation-check | 6 | findings 6 |
| modal-form | 5 | clean 1, findings 4 |
| modal-research | 5 | clean 2, findings 3 |
| size-audit | 4 | NOT-REVIEWABLE 1 |
| source-reader | 1 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| modal-depiction | modal-sheet-fire-water-tubs | 13 |
| general-purpose | claims-triage | 10 |
| modal-depiction | modal-sheet-storehouse | 7 |
| modal-depiction | modal-sheet-tax-archive | 7 |
| modal-depiction | modal-sheet-bath | 6 |
| modal-depiction | modal-sheet-granary | 6 |
| quote-check | q-0105 | 6 |
| record-format | q-0105 | 6 |
| modal-depiction | modal-sheet-well | 5 |
| quote-check | q-0100 | 4 |
| record-format | q-0100 | 4 |
| modal-depiction | modal-sheet-gatehouse | 3 |
| modal-form | modal-sheet-gatehouse | 3 |
| modal-research | modal-sheet-gatehouse | 3 |
| modal-form | modal-sheet-fire-water-tubs | 2 |
| modal-research | modal-sheet-fire-water-tubs | 2 |

## Process signals

- gates: already-verified 5, green 6, red 8
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 8 recorded in commits, 9 returned
- reversals (A -> B -> A): 0
- check dispatches 161 over 644 changed lines: cascade ratio 0.25
- tasks ticked: 14 of 14

## Tripwires (FR-010) - what fired, or would have

- 08:11 round:modal-research|modal-sheet-gatehouse@3
- 08:11 round:modal-form|modal-sheet-gatehouse@3
- 08:11 round:modal-depiction|modal-sheet-gatehouse@3
- 11:40 round:modal-depiction|modal-sheet-granary@3
- 11:41 round:modal-depiction|modal-sheet-storehouse@3
- 11:41 round:modal-depiction|modal-sheet-tax-archive@3
- 11:44 round:modal-depiction|modal-sheet-fire-water-tubs@3
- 11:44 round:modal-depiction|modal-sheet-tax-archive@4
- 11:48 round:modal-depiction|modal-sheet-fire-water-tubs@4
- 11:48 round:modal-depiction|modal-sheet-granary@4
- 11:48 round:modal-depiction|modal-sheet-storehouse@4
- 11:48 round:modal-depiction|modal-sheet-tax-archive@5
- 11:51 round:modal-depiction|modal-sheet-storehouse@5
- 12:23 round:general-purpose|claims-triage@3
- 12:23 round:quote-check|q-0100@3
- 12:23 round:record-format|q-0100@3
- 12:23 round:modal-depiction|modal-sheet-fire-water-tubs@5
- 12:23 round:modal-depiction|modal-sheet-granary@5
- 12:24 round:modal-depiction|modal-sheet-storehouse@6
- 12:24 round:modal-depiction|modal-sheet-tax-archive@6
- 12:27 red-gate
- 12:35 round:quote-check|q-0100@4
- 12:35 round:record-format|q-0100@4
- 12:35 round:modal-depiction|modal-sheet-fire-water-tubs@6
- 12:35 round:modal-depiction|modal-sheet-granary@6
- 12:36 round:modal-depiction|modal-sheet-storehouse@7
- 12:36 round:modal-depiction|modal-sheet-tax-archive@7
- 12:44 round:building-review|building-review--county-magistracy-example@3
- 12:44 round:building-review|building-review--county-magistracy-example@4
- 12:45 round:building-review|building-review--county-magistracy-example@5 (ran on the GM's waiver)
- 12:46 round:modal-depiction|modal-sheet-fire-water-tubs@7
- 13:07 round:general-purpose|claims-triage@4
- 13:10 red-gate
- 13:11 round:modal-depiction|modal-sheet-fire-water-tubs@8
- 13:19 red-gate
- 13:27 red-gate
- 13:36 round:glyph-check|glyph-check--fire-water-tubs@3
- 13:36 round:building-review|building-review--county-magistracy-example@6 (ran on the GM's waiver)
- 13:36 round:glyph-check|glyph-check--door@3
- 13:36 round:size-audit|size-audit--door@3
- 13:36 round:size-audit|size-audit--door@4
- 14:15 round:general-purpose|claims-triage@5
- 14:15 round:modal-depiction|modal-sheet-fire-water-tubs@9
- 14:17 round:general-purpose|claims-triage@6
- 14:32 round:general-purpose|claims-triage@7
- 14:32 round:modal-depiction|modal-sheet-fire-water-tubs@10
- 14:40 round:quote-check|q-0105@3
- 14:40 round:record-format|q-0105@3
- 14:40 round:modal-depiction|modal-sheet-bath@3
- 14:40 round:modal-depiction|modal-sheet-fire-water-tubs@11
- 14:40 round:modal-depiction|modal-sheet-well@3
- 14:41 round:general-purpose|claims-triage@8
- 14:54 round:quote-check|q-0105@4
- 14:54 round:record-format|q-0105@4
- 15:00 round:general-purpose|claims-triage@9
- 15:00 round:quote-check|q-0105@5
- 15:00 round:record-format|q-0105@5
- 15:00 round:modal-depiction|modal-sheet-bath@4
- 15:00 round:modal-depiction|modal-sheet-fire-water-tubs@12
- 15:00 round:modal-depiction|modal-sheet-well@4
- 15:01 round:modal-depiction|modal-sheet-bath@5
- 15:09 round:general-purpose|claims-triage@10
- 15:09 round:quote-check|q-0105@6
- 15:09 round:record-format|q-0105@6
- 15:09 round:modal-depiction|modal-sheet-bath@6
- 15:09 round:modal-depiction|modal-sheet-fire-water-tubs@13
- 15:09 round:modal-depiction|modal-sheet-well@5

This report took 4.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
