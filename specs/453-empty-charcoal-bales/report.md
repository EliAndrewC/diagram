# Feature report - 453-empty-charcoal-bales

Written by `make feature-report F=453` from 1953 events (2026-11-24T15:01 to 2026-11-24T17:48 UTC), 18 commits, the run log and the spec.

## Where the time went

| category | time | share |
|---|---|---|
| idle (over an hour) | 2 h 22 min | - |
| thinking | 1 h 12 min | 60% |
| other tool | 12 min | 10% |
| review | 10 min | 8% |
| waiting: source-applicability | 8 min | 7% |
| waiting: a background run | 5 min | 4% |
| waiting: source-reader | 4 min | 3% |
| waiting: record-format | 2 min | 2% |
| docs | 2 min | 1% |
| edit | 1 min | 1% |
| waiting: round-arbiter | 1 min | 1% |
| waiting: quote-check | 1 min | 1% |
| waiting: translation-check | 1 min | 1% |
| waiting: intro-check | 1 min | 0% |
| land | 0 min | 0% |
| writing the spec | 0 min | 0% |
| dispatching: record check | 0 min | 0% |

The session's own time above; its 499 subagent tool call(s) (of 925) are counted apart (0 by the subagent transcripts, 499 by the hook's `by`, 0 by the agents' windows - an estimate; plan D30). The subagents' own work: 78 run(s), 1 h 42 min in all, much of it while the session waited or worked on.

## The critical path and what was spent beside it (`make where-time`'s columns, feature 451 T11)

| task | total | model | tests | compile | hook suites | map generation | gate | land | review | docs | spec-kit step | tools | background run | plan review | claims check | record/modal checks | glyph check | arbiter | other subagent | waiting on work | the GM | the GM away | idle | another feature |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| - | 270 | 76 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 3 | 0 | 11 | 0 | 4 | 0 | 17 | 0 | 1 | 0 | 5 | 0 | 0 | 0 | 142 |
| T01 | 18 | 3 | 0 | 0 | 0 | 0 | 6 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 |
| all | 288 | 79 | 0 | 0 | 0 | 0 | 6 | 1 | 11 | 3 | 0 | 11 | 0 | 4 | 0 | 17 | 0 | 1 | 0 | 5 | 0 | 0 | 0 | 151 |

| task | agents | agent minutes | k tokens in | k tokens out | k advisor in | k advisor out | refused landings | plan re-rounds | by kind (count) |
|---|---|---|---|---|---|---|---|---|---|
| - | 81 | 109 | 16010.2 | 427.0 | 469.0 | 118.5 | 0 | 0 | source-reader 24, source-applicability 24, record-format 9, translation-check 8, quote-check 7, intro-check 5, spec-fidelity 3, round-arbiter 1 |
| T01 | 0 | 0 | - | - | - | - | 3 | 0 |  |
| all | 81 | 109 | 16010.2 | 427.0 | 469.0 | 118.5 | 3 | 0 | |

the critical path: 288 min of wall clock; beside it, the agents' own minutes summed: 109 min over 81 agents, 16010.2k tokens in and 427.0k out (0 with no count), the advisor's own 469.0k in and 118.5k out beside them (0 with no count); rework: 3 refused landings, 0 plan re-rounds (feature 451 T10, D7)

booked by: the mark 270 min, carried 18 min, named 0 min (feature 385 T89: the task a call names, else the last named, else the mark)

the waits between turns on work, by what held them: a background shell 7 min, an agent 4 min, a monitor alone 0 min, none 5 min (feature 451 T09)

| task | runs | minutes | tests | compile | hook suites | map generation | gate | land | review | docs | spec-kit step | other | in the background |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| - | 142 | 23.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.8 | 3.6 | 0.0 | 9.6 | 4.9 |
| T01 | 4 | 7.5 | 0.0 | 0.0 | 0.0 | 0.0 | 5.9 | 1.6 | 0.0 | 0.0 | 0.0 | 0.0 | 7.5 |
| all | 146 | 30.6 | 0.0 | 0.0 | 0.0 | 0.0 | 5.9 | 1.6 | 9.8 | 3.6 | 0.0 | 9.6 | 12.4 |

runs: 146 Bash calls of every session and agent (5 in the background, 0 open at the window's end), booked by their `make` target through the guard's table (feature 451 T08); machine minutes, which overlap, never the wall clock; 5 refused before running; phases tied to no run: 0 (0.0 min)

## Inside `other tool` (the five largest)

| tool or make target | time |
|---|---|
| Bash | 4 min |
| make apply-edits | 3 min |
| make archive | 2 min |
| make reserve | 2 min |
| make source-outcome | 1 min |

## Dispatches

| agent | dispatches | returned, by verdict |
|---|---|---|
| source-applicability | 26 | clean 1, findings 23 |
| source-reader | 24 | findings 24 |
| record-format | 13 | findings 9 |
| translation-check | 11 | FAITHFUL 8 |
| intro-check | 8 | clean 1, findings 4 |
| quote-check | 8 | clean 1, findings 6 |
| round-arbiter | 1 | findings 1 |

## Rounds per checked thing (two or more)

Counted inside the window: a subject's rounds before SINCE are not, so its rounds past the first are those within the window, and where SINCE falls between its rounds this table reads fewer than the plan re-rounds above, which count a later round whose first fell before SINCE (feature 451 T11).

| check | subject | rounds |
|---|---|---|
| record-format | q-0335 | 4 |
| record-format | q-0337 | 4 |
| translation-check | q-0335 | 4 |
| translation-check | q-0337 | 4 |
| intro-check | intro-0336 | 3 |
| intro-check | intro-0337 | 3 |
| quote-check | q-0335 | 3 |
| record-format | q-0336 | 3 |
| translation-check | q-0336 | 3 |
| intro-check | intro-0335 | 2 |
| quote-check | q-0336 | 2 |
| quote-check | q-0337 | 2 |
| record-format | q-0279 | 2 |
| source-applicability | key-edo-shussui-ikken-54-1802 | 2 |
| source-applicability | key-edo-tatekawa-sarai-kakitome-1808 | 2 |
| source-applicability | key-miyashiro-kumehara-1698 | 2 |
| source-applicability | key-norinsho-1931-mokutan-seisan-ido | 2 |
| source-applicability | key-norinsho-1933-mokutan-shiryo-1 | 2 |
| source-applicability | key-seiryo-2023-sumiyaki-ishikawa | 2 |
| source-applicability | key-tamagawa-josui-tome-119-1870 | 2 |
| source-reader | key-bokumin-kinkan-13-whole | 2 |
| source-reader | key-gao-shouxian-jiuqing-wuliao-whole | 2 |

## Process signals

- gates: none recorded
- spec rounds: none recorded
- plan reviews BLOCKED: 1 recorded in commits, 0 returned
- reversals (A -> B -> A): 0
- check dispatches 90 over 868 changed lines: cascade ratio 0.10
- tasks ticked: 1 of 3

## Tripwires (FR-010) - what fired, or would have

- 17:10 round:record-format|q-0335@3
- 17:10 round:record-format|q-0337@3
- 17:10 round:translation-check|q-0335@3
- 17:10 round:translation-check|q-0337@3

## What each check cost, per changed line (868 lines)

| check | passes | wall | tokens in | tokens out | passes per line | tokens in per line |
|---|---|---|---|---|---|---|
| quote-check | 7 | 17 min | 5714k | 77.0k | 0.008 | 6.6k |
| source-applicability | 24 | 50 min | 4843k | 136.9k | 0.028 | 5.6k |
| source-reader | 24 | 21 min | 2631k | 111.3k | 0.028 | 3.0k |
| record-format | 9 | 7 min | 1190k | 36.0k | 0.010 | 1.4k |
| translation-check | 8 | 4 min | 356k | 28.1k | 0.009 | 0.4k |
| intro-check | 5 | 1 min | 124k | 7.7k | 0.006 | 0.1k |

This report took 2.8 s to build; its own runs are the `make feature-report` rows of the event log (category `other tool`).
