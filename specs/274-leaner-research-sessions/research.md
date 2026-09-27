# Research - feature 274: where the research sessions' tokens went, after feature 250 landed

## R1 - the measurement (2026-09-27, the GM's question in request.md)

**Method.** Every page session since feature 250 landed (2026-09-27 ~05:00 UTC) was aggregated from its transcript's
`usage` fields, folded per message id as `specs/250-close-the-record-checks/measure/tokens.py` folds them: 282
sessions in 65 groups, from 250's tail and features 267, 269, 271 and 272, 1.17 B tokens. A group is a write session and
its check sessions; a thing checked is a question, an `entry-drift` modal or a registry key, as in 250's R10/R11. The
per-group table is `measure/groups-table.txt` (and `groups.json`); the scripts that made it are in `measure/`.
Prices are Opus rates relative to uncached input: cache read 0.1x, 1-hour cache write 2x, 5-minute write 1.25x,
output 5x.

**Against 250's band (49 complete groups).**

| | 250 R8-R11 | now: median (IQR) |
|---|---|---|
| per thing checked | 0.7-1.1 M | 1.02 M (0.86-1.20) |
| largest context any turn | 102-171 K | 246 K |
| mean main turn | 56-90 K | 85 K |
| group total | 6-10 M | 22 M, for 21 things |

The cost per thing held. The largest context doubled, and that is the write sessions: median 74 turns, peak 237 K,
mean turn 147 K. A write session's cost correlates 0.92 with its turn count and 0.54 with its key count. Groups are
about twice R11's size, and because every turn re-reads the context so far, a session's cost grows roughly with the
square of its length. The outliers were all long write sessions: one 272 write session cost 24.5 M over 109 turns,
peaking at 385 K. Two 271 write sessions cost 20.0 M and 13.2 M.

**Where the tokens go.** Write sessions' main context is 48.5% of raw tokens (36.6% by price); check sessions' main
context is 37.8% (31.5% by price); agents are 11.7% raw but about 30% by price. In a check session's main input the
fixed floor is the largest part at 34%: about 20 K a turn, of which the clone's root CLAUDE.md is about 5.2 K and the
research CLAUDE.md about 3.5 K.

**What the per-page rounds could not see.**

- **Coordination files are re-read whole.** 619 reads of the cross-session claims file across 172 sessions (~30 M
  carried), 418 reads of a group's handoff across 254 sessions (~20 M, though the briefs say "read only your own
  lines"), and 388 reads of a checks report across 183 sessions (~12 M), mostly to append a line. Together that is
  about 60 M, or 5%.
- **Not worth changing:**
  - Resumes after a usage limit cost under 0.5%.
  - Merging check sessions would cost more: the floor is paid every turn, and a merged session carries the first
    half's context. Two questions a session measured 1.01 M a question.
  - Sources are almost never read twice by different groups.
  - The quote-check re-checks find a real problem 13% of the time after fixes, so they stay.

**The candidates.**

1. Cap a write session at about 4 questions or 10 keys: est. 188-231 M saved (16-20% raw, about 10% by price).
2. Own lines only for coordination files: est. 40-50 M (about 4% raw).
3. A slim instructions file for headless sessions: about 5 K a turn over about 12,500 turns, 60 M raw, about 2% by price.
4. Batch source-applicability keys: about 3% by price, but a "fewer, bigger checks" change that would need seeded-fault
   runs. Not requested.
