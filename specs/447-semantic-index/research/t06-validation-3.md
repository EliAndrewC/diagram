# T06 validation 3 - after amendment 4's two fixes (SC-A4)

Run 2026-10-30, a `research-pass` agent, the brief of the earlier validations under KEY=field-size-validation-3, with the
measure passages (FR-A4-1) and the contract's "Report, do not filter" (FR-A4-2) on main. Its usage, from its completion notice:

```
<usage><subagent_tokens>125788</subagent_tokens><tool_uses>17</tool_uses><duration_ms>354068</duration_ms></usage>
```

The agent's own count, from its final report (not the notice; the transcript shows 15 Bash calls): "16 Bash (6 of them
`research-search` runs, the sixth adding nothing), 2 Read, 1 advisor; 19 in all"

In `t05-why.md`'s terms (`analysis/why.py`, run V3 in `t05-why-table.txt`), for the twelve targets:

| run | seen | seen, not reported | never seen | reported |
|---|---|---|---|---|
| S | 9 | 3 | 3 | 6 |
| T | 8 | 1 | 4 | 7 |
| V1 | 9 | 3 | 3 | 6 of the targets by the transcript count (7 by the report's own table) |
| V2 | 9 | 3 | 3 | 6 |
| **V3** | **9** | **0** | **3** (Huizhou, Ofuro, Konosu) | **9** |

The half the two fixes address - a target seen and then dropped - went from 1 to 3 a run to none of the twelve; the half they leave, never
seen, stayed at 3. Off the list, V3 reported what no earlier run did: the Gunma Heian plots (5 to 20 m a side), King's four
paddies near Shanghai ("an area of nearly two acres"), the jori grid's divisions, the Hainan and Jiangyin registers' qiu, Chen
Fu's Nongshu on merging plots, and modern standards beside them, each with its period and what it measures. One drop remains, off the list: Fei, printed
under both its ids with measure passages on holdings ("less than ten mow"), was not reported - a drop FR-A4-2 forbids, since a
holding is a kind it names.

The cost: 125,788 tokens and 354 s, against 51,261 to 73,674 and 127 to 223 s for the earlier runs - the printed passages are
longer (up to five a source), and the report lists 17 findings where the earlier ones listed 9 to 11 (the numbered top-level
items of each final report, counted by the closing review: S 9, T 9, V1 9, V2 11, V3 17).
