# T07's measurements: the homestead parts family (US4)

**Load this file when:** you check what T07 removed, or re-measure it.

Seed 39 at 40 households unless named, observed 2026-10-26. Before: `dev/perf-log/20261026T200555Z-fanout-427-T07-start.txt` and
the stage's `.prof` (`dev/perf-raw/20261026T200630Z-seed39-homesteads.prof`); after the first landing group:
`dev/perf-log/20261026T202522Z-fanout-427-T07d.txt` (method: `make perf-fanout STAGES=homesteads`, `make perf-profile`).

## The first landing group

| chain (its leaf) | what changed | before | after |
|---|---|---|---|
| the yard's mats: `_filled_lattice` / `_lay_by_hand` -> `fits` -> `edge_dist` -> `seg_dist` | every spot's and every try's floor test in one `floor_points` call | `edge_dist` 12,658 | 1,406 |
| `gap_ways.trace` -> `seg_closest` per tree leg per cell | `SegFeet`: the tree's legs as arrays, the nearest foot in one pass | 54,021 (`trace`'s generator) | gone |
| `wood_share.corridor_bars` -> `seg_dist` per cell and seat | the projection written inline, compared squared | 39,210 (its generator) | gone |
| `gap_ways.way_out` -> `ok` -> `open_here` -> the three part tests -> `seg_box_within` | the memo read in place; a cell's point tested against the household's boxes listed once (`point_clear`) | `ok` 90,281, `seg_box_within` 75,726 | 10,233, 27,406 (every caller) |
| R8, `capacity.free_seats`: `point_taken` per grid point, a key tuple per point | `FreeGround.points_taken`, the field distance as an array, `np.lexsort` | `point_taken` 81,810, the key 55,570 | 9,449 (other callers), gone |
| `growth.footprint`: four `max` per wood seat | the seats' extremes once | `max` 293,413 under it | 8 a call |
| `lay_fixtures`: `px` per seat offered (the privy's reach, the persimmon's dooryard and shade) | each size once a call | `px` 204,473 | 70,000 |

The stage: 9,709,037 -> 7,791,839 calls at 40 households, 4,550,682 -> 3,699,474 at 20. Every pool manifest unchanged against
HEAD after each step (`make maps-moved`), until the one deliberate change below.

## The one change that moves a map: a way's tread 3 ft off its own kura and byre

The claims round on the lists `point_clear` reads (`part_gaps`, `fixture_gaps`) found `parts_clear` holding the tread's edge
0.5 ft off the household's own kura and byre, where research 0081 keeps "the same 3 ft off a farmstead's other buildings - its
sheds, byre" as off its farmhouse wall (impl-drift DRIFTED; the drift predates 427). The kura and byre now take `house_gap`'s
reading (1.5 + 3 + 0.5 ft from the line); the beds and the well pocket keep the half-foot margin, 0246's map drawing convention.
Kuwabata is the one pool map it moves: its fourth household, reached in HEAD across a neighbor's yard (a pinch passage,
`meta.pinch_passages` 1), now has its own way out (0), and every check of the map passes. The fixtures' 7 ft is relabeled a GUESS
(no page gives a household's own way's clearance off its own fixtures; round arbiter, `ask:427-T07-fixture-gaps-claim`, accept).

## Still standing in the family

- **R4** (`household_reach` lays four whole homesteads per candidate), moved to its own task, T12: `within_reach_of` 73,186
  and `_first` unchanged.
  `hotspots-recompute.md` R4's direction - one envelope per lot and size, moved to the seat - is the household-keyed roll feature
  297 tried and withdrew (its plan C, research R9: keyed on the household, seed 3 seated 9 of 10 and its site was refused); the
  placer rolls a homestead's parts at the seat offered, and `household_reach` rolls them at the same seat, so the reach is exact
  and its templates are the placer's own cache.
- `route.taut` and the ways tree's admission (`tree.judge`) - the lane law's, T10's.

## R8's test and the stage's time: the A/B (FR-003, FR-005)

Two detached trees, the commit before T07 (5a6095082) and T07's (73713d668), each `make perf SCALING=1`, back to back in one
session, alternated base, end, base, end (2026-10-26 20:39-20:46; the snapshots `*-427-T07ab-base-*.json`, taken in the scratch
tree and not kept, and `dev/perf-log/*-427-T07ab-end-*.json`). The homesteads stage at 40 households, seconds, seed by seed:

| seed | base | end |
|---|---|---|
| 4 | 2.84, 2.64 | 2.60, 2.57 |
| 25 | 2.23, 2.11 | 2.06, 1.99 |
| 39 | 1.84, 1.76 | 1.73, 1.67 |
| 47 (R8's seed) | 2.48, 2.64 | 2.48, 2.35 |

Reported, gating nothing (FR-006). The snapshots' call totals: 16,881,165 both base runs; 15,618,765 and 15,619,288 the two end
runs - two counts of one commit 523 calls apart, which the counting pass is meant not to allow (T03's premise: a count moves
only with the code or the seed); filed in `found.jsonl` to measure.
