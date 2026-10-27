# The trial inventory (FR-012, task T52)

**Load this file when:** you start a speed task of 417 (T53-T56) or ask where a roll still searches by trial.

T03's inventory listed the repair passes; this lists the SEARCH BY TRIAL: a placer that lays a candidate out in full and then
refuses it, and a check asked again of a whole network as it grows. Measured 2026-10-26 on seed 39 at 40 households (method:
`make perf-profile SEED=39 STAGE=<stage> HOUSEHOLDS=40`, each stage's `.prof` read with `pstats`; `dev/perf-raw/20261027T02*`;
the stage totals from `make perf-fanout` at fb19852b5, `dev/perf-log/20261027T030656Z-fanout-417-start.txt`, the field's after
427's T09). Profiled seconds are
cProfile's, about twice the unprofiled; they rank, they gate nothing.

## The sites, largest first

| # | stage | site | what it does before it refuses | calls | profiled s | task |
|---|---|---|---|---|---|---|
| 1 | web (10.5M calls) | `ways/checks.py` `served_network` (from `ways/serve.py:501`, `ways/reach.py:56,86`, `ways/law.py:694`, `ways/checks.py:422`) | regrows the connected network from the connector over every pair of lanes (`lanes_share_tread`), each time it is asked, as the web grows | 45 calls; 26,974 lane pairs; 954,516 `seg_dist` | 0.86 | T53 (after T31 and T58; before T06, the round arbiter's ruling on ask:417-T06-order) |
| 2 | homesteads (6.5M) | `rolling/gap_ways.py` `_way_for` -> `_first_admitted` -> `access.admitted` -> `tree_admits` -> `ways/tree.py` `judge` | up to `GAP_TRIES` exits a household, each traced back along the flood (`trace`), pulled taut (`route.taut`, 177) and judged by the ways tree, most refused | 40 households, 85 runs, 103 admissions, 56 tree judgments | 1.37 | T54 |
| 3 | homesteads | `homesteads/growth.py` `settled_seat` -> `household_reach` -> `rolling/bundle.py` `_bundle_envelope` | every candidate seat's whole homestead laid out on its four garden sides, fixtures included, to measure its reach | 416 reaches; 2,506 bundle geometries; 1,216 fixture layouts | 0.39 | T55 |
| 4 | homesteads | `settlement/houses.py` `try_place` -> `rolling/place.py` `_place_bundle_nucleated` -> `rolling/fit.py` `_parts_fit` | a seat's homestead placed and its parts' rules asked; most offers refused | 160 placements for 40 houses; 359 parts fits | 0.59 | T55 |
| 5 | homesteads | `homesteads/capacity.py` `free_seats` / `offer_seats` | the exhaustive pass's every free grid point offered to the placer in turn | 1 scan | 0.28 | T55 |
| 6 | lane_wells (2.2M) | `homesteads/wells.py` `seat_wells` -> `shrines_wells/wells.py` `well_at` -> `overlap/registry.py` `admits` | each ranked seat asked of the overlap registry and the ground, one at a time, until one stands | 1,746 `well_at`; 73,249 `_seat_ok` | 0.35 | T56 |
| 7 | appurtenances (1.0M) | `seat_wells` -> `well_at` -> `admits` (the cluster form's wells, seated before the lanes) | the same, one seat at a time | 824 | 0.19 | T56 |
| 8 | hinterland (3.4M) | `hinterland/parcels/patches.py` `_ok` -> `open_ground_region` | each lattice seat read from a region (by construction already), re-asked by the nudge, the row step and the size roll | 12,589 seats; 10,895 region reads | 0.40 | T56 (low: already a raster read) |
| 9 | hinterland | `homesteads/bamboo.py` `strip_refused` | each strip candidate asked the eight refusals one at a time | 833 strips | 0.17 | T56 |
| 10 | windbreak (1.3M) | `homestead_parts/stands.py` `_seat` | each grid seat through the rejection chain (a region read, by construction already) | 9,971 seats | 0.25 | T56 (low) |
| 11 | notice (0.95M) | `structures/fixtures/siting.py` `_route_seats` -> `houses._fits` | each seat along each route asked the placer's `_fits` | 42 routes; 1,561 fits | 0.26 | T56 |

## Beside them: place then repair (T03's, listed here for the ranking)

| stage | site | profiled s | task |
|---|---|---|---|
| web | `ways/settle/stage.py` `settle_the_web` (the settle's remaining steps) | 1.13 | T31, then T58 and T06 (after T55) |
| field (2.8M) | `waterfields/settle.py` `Fabric` judge, merge and neighbors (cells cut, then judged and merged) | 0.33 judge, 0.24 merge | T12 |

## What no task needs

`seat`, `woodland`, `crossings`, `labels`: none over 0.12 profiled seconds or 300,000 calls at 40 households.

Every site over 50,000 calls has its task: 1 (T53), 2-5 (T54, T55), 6 (T56).

## Converted

- **Row 1, `served_network` (T58, T53).** Seed 39 at 40 households, measured 2026-10-27 (`make perf-profile SEED=39 STAGE=web
  HOUSEHOLDS=40`; `make perf-fanout STAGES=web`): T58's one predicate, with each pair's box asked first and a pair already joined
  skipped, took the web stage 10,462,166 -> 8,101,851 calls and `served_network` 0.86 -> 0.24 profiled s; T53's `NetworkMemo` (each pair's
  answer kept by the two lanes' points) took `lanes_share_tread` 2,976 -> 91 calls, `served_network` 0.24 -> 0.02 profiled s, and
  the web stage 8,101,851 -> 7,208,472 calls (`dev/perf-log/20261027T040412Z-fanout-417-T58.txt`,
  `dev/perf-log/20261027T050246Z-fanout-417-T53b.txt`).
- **Row 2, the households' ways (T54).** Seed 39 at 40 households, measured 2026-10-27 (`make perf-profile SEED=39 STAGE=homesteads
  HOUSEHOLDS=40`, `make perf-fanout STAGES="homesteads web"`; the shares by a throwaway call counter in `gap_ways`): the trial's
  refused candidates are about a third of the chain (626,443 + 45,164 of about 2.05M calls), the admitted ways' judgment about
  1.2M. The judgment's scans asked box-first (`rejoined`, `house_hit`, `free_end`, `_seg_box_gap` written out), the same verdicts:
  homesteads 6,940,189 -> 6,172,193 calls, web 7,208,472 -> 6,942,717, `_way_for` 2.25 -> 1.11 profiled s
  (`dev/perf-log/20261027T052103Z-fanout-417-T54b.txt`). The rest - the admitted ways' lane-law judgment - is T06's (the round
  arbiter's accept on ask:417-T54-exit).
- **Rows 3-5, the homesteads' seating (T55, set down by the round arbiter's ruling on ask:417-T55-route).** Seed 39 at 40 households,
  measured 2026-10-27 (`make perf-profile SEED=39 STAGE=homesteads HOUSEHOLDS=40`, `make perf-fanout STAGES=homesteads`, throwaway
  counters): the stage's 6,171,552 calls sit in the settled seats' reach rolls (about 1.9M) and the admitted layouts (39 at 16,067),
  none of it trial; laid out and then refused, about 268k (`_parts_fit` 18 at 12,148, the envelope or the growth's distance 19 at
  2,587) - about 4% of the stage. The one refusal that needs no layout and is not already early, the house and yard over a reserved
  wood seat (126 of 157 wood refusals), asked by the growth before the placer saves 2.2% but forgoes the placer's move off a neighbor
  (Inashiro, Kuwabata and Sawada moved); asked exactly in the placer it saves nothing. Noted: 83 of 159 offered seats stood over a
  reserved wood seat - a high rate, for where the wood share's reservation is claimed.
