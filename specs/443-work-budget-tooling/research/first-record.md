# The first standing record (T02) - what it shows

Load this file when: you read `dev/work-budget.md` for the first time, or set a budget for the hinterland or the field.

Measured 2026-10-28 by `make work-budget` (seeds 4, 25, 39, 47, the reference spec, 10/20/40/80 households; the run
`dev/work-budget/20261028T152105Z-45aa176ec9b8.json`, engine 944a517bb).

- **No roll at 80 households.** Every seed's field refuses at 80 (`FieldRefused: no fan at any of 5 aspects is legal`), and seed 4
  refuses at 40 (`WebRefused`). The exponents are fitted over the sizes that rolled - 20 to 40 - not the design's 20 to 80; 444
  owes the field room before an 80-household figure exists.
- **The hinterland is 77% of the roll's counted work**: 8,066,589 of 10,418,688 operations at 40 households, of which 7,624,185
  are `index_examined@RingIndex.inside_many` - the arrays fallback that asks every edge of a ring for each point, taken when shapely
  reads a belt outline as invalid (feature 427 T08's note at the point of change). Its Python calls are only 912,981: the work is
  in numpy, which the call count never saw (S5).
- **labels counts nothing** in its own stage (its seats are asked in `finish`, after the stages), and `water_frame`, `waterward`,
  `pond_stock` and `burial` place by rule without a candidate search.
