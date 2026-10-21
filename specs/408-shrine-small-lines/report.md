# Feature report - 408-shrine-small-lines

Written by `make feature-report F=408` from 3347 events (2026-10-21T12:23 to 2026-10-21T15:13 UTC), 22 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| thinking | 2 h 45 min | 57% |
| waiting: subagent | 1 h 04 min | 22% |
| other tool | 32 min | 11% |
| waiting: source-reader | 7 min | 2% |
| waiting: source-applicability | 6 min | 2% |
| waiting: quote-check | 4 min | 2% |
| waiting: round-arbiter | 4 min | 1% |
| waiting: translation-check | 3 min | 1% |
| edit | 2 min | 1% |
| waiting: record-format | 2 min | 1% |
| dispatching: record check | 1 min | 1% |
| test file | 0 min | 0% |
| dispatching: spec review | 0 min | 0% |
| writing the spec | 0 min | 0% |
| dispatching: other subagent | 0 min | 0% |
| dispatching: round arbiter | 0 min | 0% |
| waiting: intro-check | 0 min | 0% |

The session's own time above; its 827 subagent tool call(s) (of 1547) are counted apart (0 by the subagent transcripts, 827 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 106 run(s), 3 h 07 min in all, much of it while the session waited or worked on.

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 6 min |
| make record | 5 min |
| make check-bundle | 4 min |
| make quote-verbatim | 3 min |
| make reserve | 2 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-applicability | 48 | clean 1, findings 20 |
| source-reader | 42 | findings 27 |
| quote-check | 22 | clean 1, findings 13 |
| record-format | 22 | clean 1, findings 14 |
| translation-check | 20 | FAITHFUL 14 |
| round-arbiter | 5 | findings 5 |
| spec-fidelity | 5 | BLOCKED 2, CHANGES REQUIRED 1 |
| research-pass | 4 | findings 3 |
| intro-check | 2 | findings 1 |

## Rounds per checked thing (two or more)

| check | subject | rounds |
|---|---|---|
| quote-check | q-0271 | 5 |
| translation-check | q-0271 | 5 |
| quote-check | q-0258 | 4 |
| quote-check | q-0268 | 4 |
| record-format | q-0257 | 4 |
| record-format | q-0258 | 4 |
| record-format | q-0268 | 4 |
| record-format | q-0271 | 4 |
| source-applicability | key-bochum-gansu-wuliao-jiazhi | 4 |
| source-applicability | key-bochum-yunnan-wuliao-jiazhi | 4 |
| source-applicability | key-midu-zhishengdian-1902-wikisource | 4 |
| source-applicability | key-mie-u-tsu-dochu-nikki | 4 |
| source-applicability | key-ruiju-kinsei-fuzokushi-jo | 4 |
| source-applicability | key-yuasa-1986-kaichoba | 4 |
| quote-check | q-0257 | 3 |
| quote-check | q-0260 | 3 |
| quote-check | q-0278 | 3 |
| record-format | q-0260 | 3 |
| record-format | q-0278 | 3 |
| round-arbiter | arbiter-batch | 3 |
| source-applicability | key-doolittle-1865-social-life-1 | 3 |
| source-applicability | key-hinata-1989-nakai-carvers | 3 |
| source-applicability | key-kotobank-jichinsai | 3 |
| source-applicability | key-murata-1986-yamato-river | 3 |
| source-applicability | key-ruiju-kinsei-fuzokushi-ge | 3 |
| source-applicability | key-yangzhou-huafang-lu-17 | 3 |
| source-reader | key-aomori-tonai-senninzuka-whole | 3 |
| source-reader | key-bochum-gansu-wuliao-jiazhi-whole | 3 |
| source-reader | key-bochum-yunnan-wuliao-jiazhi-whole | 3 |
| source-reader | key-hinata-1989-nakai-carvers-whole | 3 |
| source-reader | key-midu-zhishengdian-1902-wikisource-whole | 3 |
| source-reader | key-mie-u-tsu-dochu-nikki-whole | 3 |
| source-reader | key-ruiju-kinsei-fuzokushi-jo-whole | 3 |
| source-reader | key-yuasa-1986-kaichoba-whole | 3 |
| translation-check | q-0257 | 3 |
| translation-check | q-0258 | 3 |
| translation-check | q-0260 | 3 |
| translation-check | q-0268 | 3 |
| translation-check | q-0278 | 3 |
| intro-check | intro-0257-3 | 2 |
| source-applicability | key-aomori-tonai-senninzuka | 2 |
| source-applicability | key-daqing-huidian-zeli-130 | 2 |
| source-applicability | key-yuasa-1991-edo-kaicho | 2 |
| source-reader | key-daqing-huidian-zeli-130-whole | 2 |
| source-reader | key-doolittle-1865-social-life-1-whole | 2 |
| source-reader | key-kotobank-jichinsai-whole | 2 |
| source-reader | key-murata-1986-yamato-river-whole | 2 |
| source-reader | key-ruiju-kinsei-fuzokushi-ge-whole | 2 |
| source-reader | key-yangzhou-huafang-lu-17-whole | 2 |
| source-reader | key-yuasa-1991-edo-kaicho-whole | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 2 returned
- reversals (A -> B -> A): 0
- check dispatches 156 over 830 changed lines: cascade ratio 0.19
- tasks ticked: 0 of 6

## Tripwires (FR-010) - what fired, or would have

- 14:53 round:record-format|q-0257@3
- 14:58 round:quote-check|q-0258@3
- 14:58 round:quote-check|q-0268@3
- 14:58 round:record-format|q-0258@3
- 14:58 round:record-format|q-0271@3
- 15:02 round:translation-check|q-0271@3
- 15:06 round:translation-check|q-0271@4

## What each check cost, per changed line (830 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 14 | 24 min | 3812k | 112.0k | 0.017 | 4.6k |
| record-format | 15 | 14 min | 2261k | 64.1k | 0.018 | 2.7k |
| source-reader | 27 | 25 min | 2059k | 130.0k | 0.033 | 2.5k |
| source-applicability | 21 | 24 min | 1799k | 90.4k | 0.025 | 2.2k |
| spec-fidelity | 3 | 9 min | 829k | 28.9k | 0.004 | 1.0k |
| spec-fidelity-verify | 2 | 8 min | 587k | 21.0k | 0.002 | 0.7k |
| translation-check | 14 | 8 min | 494k | 43.3k | 0.017 | 0.6k |
| intro-check | 1 | 0 min | 27k | 2.8k | 0.001 | 0.0k |

This report took 3.7 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
