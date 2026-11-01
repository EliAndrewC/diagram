# The field's hem against its budget (feature 444 T16, 2026-11-01)

Measured by `make work-budget` at commit 64052e53e (`dev/work-budget/20261101T052925Z-09749d8a15da.json`), after the MODE
AUDIT's UNCOUNTED was applied: every counter added in its loop, the hem's lap test indexed (`index::Boxes`), its outline test
by bands (`index::Bands`), its refusal tests short-circuited, the brook laid off the axes with no move.

## The field's count, split at the hem

The hem's keys are `write@hem_index`, `candidate@hem_index` and `pt_test@hem_onto`; "rest" is every other key.

| households | seed | total | hem | rest | dry plots |
|---|---|---|---|---|---|
| 40 | 4 | 35,761 | 9,215 | 26,546 | 227 |
| 40 | 25 | 72,266 | 45,849 | 26,417 | 227 |
| 40 | 39 | 35,160 | 9,367 | 25,793 | 227 |
| 40 | 47 | 26,891 | 0 | 26,891 | 0 (barley met the need) |
| 80 | 4 | 66,093 | 18,960 | 47,133 | 454 |
| 80 | 25 | 122,308 | 76,324 | 45,984 | 454 |
| 80 | 39 | 68,753 | 22,760 | 45,993 | 454 |
| 80 | 47 | 48,391 | 0 | 48,391 | 0 |

The budget (`phases/field_greenfield.derivation.md`, pinned): 23,988 at 40, 42,070 at 80, exponent 0.79. The median total
is 42,334 at 40 (1.8x); without the hem the field is 1.1x at 40 and 1.09x at 80. Measured exponent 0.92.

## Why the hem is not in the budget

- The derivation's only hem line is "the dry plots' polygons (4)", charged at its Bounds' dry plots: 13 and 26 at 10 and 20,
  carried as 47 at 40 (188 operations). The hem's SEARCH - each candidate plot tested against the field's outline, the plots
  already laid and the water - has no line at all.
- The Rust hem climbs band by band until the plots hold the grain the hamlet needs
  (research/questions/0011-where-a-farming-hamlet-grew-its-coarse-grain.drawing.html: "the dry plots climb out as far from the
  canal as the ground runs, until they hold the grain"). It lays 57, 114, 227 and 454 plots at 10, 20, 40 and 80 when the
  winter crop is not barley. The derivation's 13 and 26 were measured on reference rolls where barley met most of the need;
  main's own pool shows the spread (Kashikawa at 20: 68 plots on main, a barley roll; 164 on this clone, no winter crop).
- A temporary tally on seed 25 at 20 households: 445 candidates for 114 plots laid - 173 refused onto the field's rice, 150
  onto a plot already laid, 8 in the water. Seed 25's line meets its own plots at the canal's corners, so it tries about four
  candidates a plot; seeds 4 and 39 try fewer.

## What would close it, priced

- A budget amendment (`make budget-change`, which takes the GM's words): a hem row in the derivation - the plots at the
  grain need's count (0011) and each candidate's tests at the measured cells (about 20 cells a candidate across the two
  indexes and the outline's band) - re-derived and put to MODE BUDGET.
- A cheaper hem: skip candidates that geometry already refuses (a corner of the canal's line, where the next band's plots fold
  onto the last's) - about a third of the hem's work at most, leaving the hem's count well over its 188.
- Neither changes the remaining 1.1x outside the hem, which is `index_examined@Standing.conflicts` (the Python registry
  recording the field, about 4,900 at 40, no derivation line) and the comb's measured basins.
