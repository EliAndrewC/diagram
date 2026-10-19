# Feature report - 403-money-earlier-leads

Written by `make feature-report F=403` from 2366 events (2026-10-19T19:49 to 2026-10-19T22:39 UTC), 32 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 2 h 32 min | - |
| thinking | 1 h 36 min | 57% |
| other tool | 35 min | 21% |
| waiting: quote-check | 12 min | 7% |
| waiting: source-reader | 9 min | 5% |
| waiting: source-applicability | 4 min | 3% |
| waiting: record-format | 3 min | 2% |
| dispatching: record check | 1 min | 1% |
| waiting: subagent | 1 min | 1% |
| edit | 1 min | 1% |
| waiting: translation-check | 1 min | 1% |
| waiting: round-arbiter | 1 min | 1% |
| test file | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: spec-fidelity | 1 min | 0% |
| waiting: spec-fidelity-verify | 1 min | 0% |
| spec-kit step | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |

The session's own time above; its 390 subagent tool call(s) (of 1120) are counted apart (0 by the subagent transcripts, 390 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 81 run(s), 1 h 51 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 9 min |
| make quote-verbatim | 7 min |
| make record | 5 min |
| make archive | 3 min |
| make apply-edits | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| record-format | 31 | clean 2, findings 21 |
| quote-check | 27 | clean 2, findings 17 |
| source-reader | 24 | clean 2, findings 12 |
| translation-check | 18 | FAITHFUL 9 |
| source-applicability | 16 | clean 1, findings 8 |
| spec-fidelity | 4 | BLOCKED 1, CHANGES REQUIRED 1, CLEAR 2 |
| round-arbiter | 2 | findings 2 |
| spec-fidelity-verify | 1 | FAITHFUL 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| source-reader | key-allen-2009-china-wages-whole | 4 |
| quote-check | q-0270 | 3 |
| record-format | q-0270 | 3 |
| source-applicability | key-ruiju-kinsei-fuzokushi-jo | 3 |
| source-reader | key-bochum-zhili-wuliao-jiazhi-whole | 3 |
| source-reader | key-gamble-burgess-1921-peking-survey-whole | 3 |
| source-reader | key-takaoka-shiryo-ge-whole | 3 |
| source-reader | key-takaoka-shiryo-jo-whole | 3 |
| translation-check | q-0259 | 3 |
| translation-check | q-0262 | 3 |
| translation-check | q-0265 | 3 |
| translation-check | q-0270 | 3 |
| quote-check | q-0250 | 2 |
| quote-check | q-0259 | 2 |
| quote-check | q-0260 | 2 |
| quote-check | q-0261 | 2 |
| quote-check | q-0262 | 2 |
| quote-check | q-0264 | 2 |
| quote-check | q-0265 | 2 |
| quote-check | q-0266 | 2 |
| record-format | q-0250 | 2 |
| record-format | q-0259 | 2 |
| record-format | q-0260 | 2 |
| record-format | q-0261 | 2 |
| record-format | q-0262 | 2 |
| record-format | q-0264 | 2 |
| record-format | q-0265 | 2 |
| record-format | q-0266 | 2 |
| source-applicability | key-allen-2009-china-wages | 2 |
| source-applicability | key-bochum-zhili-wuliao-jiazhi | 2 |
| source-applicability | key-gamble-burgess-1921-peking-survey | 2 |
| source-applicability | key-ruiju-kinsei-fuzokushi-ge | 2 |
| source-reader | b-ge | 2 |
| source-reader | b-jo | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 3 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 116 over 588 changed lines: cascade ratio 0.20
- tasks ticked: 6 of 7

## Tripwires (FR-010) - what fired, or would have

- 21:50 round:translation-check|q-0270@3
- 21:51 round:record-format|q-0270@3
- 21:51 round:quote-check|q-0270@3

## What each check cost, per changed line (588 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 19 | 43 min | 4730k | 140.9k | 0.032 | 8.0k |
| record-format | 23 | 18 min | 2442k | 98.0k | 0.039 | 4.2k |
| source-reader | 14 | 15 min | 1595k | 62.9k | 0.024 | 2.7k |
| spec-fidelity | 4 | 12 min | 1061k | 34.6k | 0.007 | 1.8k |
| source-applicability | 9 | 13 min | 855k | 39.0k | 0.015 | 1.5k |
| translation-check | 9 | 5 min | 331k | 26.8k | 0.015 | 0.6k |
| spec-fidelity-verify | 1 | 2 min | 198k | 6.1k | 0.002 | 0.3k |

This report took 3.1 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
