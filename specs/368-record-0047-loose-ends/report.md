# Feature report - 368-record-0047-loose-ends

Written by `make feature-report F=368` from 590 events (2026-10-11T04:11 to 2026-10-11T04:38 UTC), 27 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 18 min | 65% |
| other tool | 8 min | 30% |
| test file | 1 min | 3% |
| dispatching: record check | 0 min | 1% |
| edit | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| make record | 3 min |
| make modal-triage | 1 min |
| make append | 1 min |
| Bash | 1 min |
| make modal-bundle | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| modal-depiction | 16 | clean 9, findings 5 |
| quote-check | 4 | findings 4 |
| record-format | 4 | findings 3 |
| source-reader | 4 | findings 4 |
| general-purpose | 3 | findings 2 |
| round-arbiter | 3 | findings 3 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0047 | 4 |
| record-format | q-0047 | 4 |
| general-purpose | modal-triage | 3 |
| modal-depiction | modal-hamlet-buckwheat | 3 |
| modal-depiction | modal-hamlet-privy | 3 |
| modal-depiction | modal-choice-manure_form--heap | 2 |
| modal-depiction | modal-choice-manure_form--pit | 2 |
| modal-depiction | modal-hamlet-manure-heap | 2 |
| modal-depiction | modal-hamlet-manure-pit | 2 |
| modal-depiction | modal-hamlet-soy | 2 |

## Process signals

- gates: none recorded
- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1
- plan reviews BLOCKED: 1 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 28 over 699 changed lines: cascade ratio 0.04
- tasks ticked: 4 of 6

## Tripwires (FR-010) - what fired, or would have

- 04:26 round:quote-check|q-0047@3
- 04:26 round:record-format|q-0047@3
- 04:29 round:quote-check|q-0047@4

This report took 1.3 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
