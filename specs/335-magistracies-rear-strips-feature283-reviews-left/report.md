# Feature report - 335-magistracies-rear-strips-feature283-reviews-left

Written by `make feature-report F=335` from 654 events (2026-10-11T04:31 to 2026-10-11T05:15 UTC), 46 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 26 min | 61% |
| other tool | 16 min | 36% |
| test file | 1 min | 2% |
| writing the spec | 0 min | 1% |
| dispatching: record check | 0 min | 0% |
| edit | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make record | 3 min |
| make check-bundle | 2 min |
| make quote-verbatim | 2 min |
| make modal-triaged | 1 min |
| make modal-bundle | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 10 | clean 2, findings 8 |
| source-applicability | 8 | findings 8 |
| source-reader | 6 | findings 6 |
| quote-check | 4 | findings 3 |
| record-format | 4 | findings 3 |
| general-purpose | 2 | findings 2 |
| round-arbiter | 2 | findings 2 |
| translation-check | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0104 | 3 |
| record-format | q-0104 | 3 |
| source-applicability | key-adachi-matsue-bukeyashiki | 3 |
| general-purpose | modal-triage | 2 |
| modal-depiction | modal-sheet-outer-court | 2 |
| source-applicability | key-kasama-iwama-jinya | 2 |
| source-applicability | key-kotobank-teien | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 33 over 1936 changed lines: cascade ratio 0.02
- tasks ticked: 7 of 9

## Tripwires (FR-010) - what fired, or would have

- 05:08 round:source-applicability|key-adachi-matsue-bukeyashiki@3

This report took 1.0 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
