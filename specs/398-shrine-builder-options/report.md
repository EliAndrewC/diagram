# Feature report - 398-shrine-builder-options

Written by `make feature-report F=398` from 2754 events (2026-10-19T09:08 to 2026-10-19T13:31 UTC), 17 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 2 h 40 min | - |
| thinking | 1 h 18 min | 44% |
| waiting: source-reader | 48 min | 27% |
| other tool | 23 min | 13% |
| waiting: quote-check | 8 min | 5% |
| waiting: subagent | 5 min | 3% |
| waiting: round-arbiter | 5 min | 3% |
| waiting: source-applicability | 3 min | 2% |
| test file | 3 min | 2% |
| waiting: record-format | 1 min | 1% |
| edit | 1 min | 1% |
| dispatching: record check | 1 min | 0% |
| waiting: translation-check | 1 min | 0% |
| writing the spec | 1 min | 0% |
| waiting: spec-fidelity-verify | 0 min | 0% |
| spec-kit step | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| waiting: a background run | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |

The session's own time above; its 777 subagent tool call(s) (of 1231) are counted apart (0 by the subagent transcripts, 777 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 86 run(s), 3 h 08 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 8 min |
| make hooks-test | 6 min |
| make arbiter-fix-done | 2 min |
| make reserve | 2 min |
| make apply-edits | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-reader | 26 | findings 23 |
| quote-check | 17 | findings 11 |
| source-applicability | 15 | clean 1, findings 10 |
| spec-fidelity | 10 | BLOCKED 1, CHANGES REQUIRED 2, CLEAR 2 |
| translation-check | 10 | FAITHFUL 10 |
| record-format | 8 | findings 8 |
| research-pass | 6 | findings 5 |
| intro-check | 4 | findings 4 |
| round-arbiter | 4 | FAITHFUL 1, findings 3 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | r3-398-qc-0268 | 3 |
| quote-check | r3-398-qc-0269 | 3 |
| quote-check | r3-398-qc-0270 | 3 |
| source-applicability | key-takaoka-sekino-mirror | 3 |
| source-applicability | key-tao-2025-runli | 3 |
| quote-check | q-0268 | 2 |
| quote-check | q-0269 | 2 |
| quote-check | q-0270 | 2 |
| quote-check | q-0271 | 2 |
| record-format | q-0268 | 2 |
| record-format | q-0269 | 2 |
| record-format | q-0270 | 2 |
| record-format | q-0271 | 2 |
| source-reader | kawakami2 | 2 |
| source-reader | kume | 2 |
| source-reader | shakkan | 2 |
| translation-check | q-0268 | 2 |
| translation-check | q-0270 | 2 |
| translation-check | q-0271 | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 0 recorded in commits, 1 returned
- reversals (A -> B -> A): 0
- check dispatches 80 over 642 changed lines: cascade ratio 0.12
- tasks ticked: 6 of 8

## Tripwires (FR-010) - what fired, or would have

- none

## What each check cost, per changed line (642 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 11 | 31 min | 6275k | 114.0k | 0.017 | 9.8k |
| source-reader | 23 | 22 min | 1932k | 93.0k | 0.036 | 3.0k |
| spec-fidelity | 5 | 13 min | 1840k | 47.4k | 0.008 | 2.9k |
| source-applicability | 11 | 16 min | 1091k | 46.0k | 0.017 | 1.7k |
| record-format | 8 | 9 min | 987k | 43.7k | 0.012 | 1.5k |
| spec-fidelity-verify | 4 | 5 min | 536k | 17.1k | 0.006 | 0.8k |
| translation-check | 10 | 6 min | 353k | 29.4k | 0.016 | 0.5k |
| intro-check | 4 | 1 min | 72k | 2.6k | 0.006 | 0.1k |

This report took 1.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
