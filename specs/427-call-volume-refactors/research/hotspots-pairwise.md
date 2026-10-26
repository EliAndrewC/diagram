# Hotspots: each candidate checked against its neighbors one Python call at a time

**Load this file when:** you work on the lane web and the lane law, the gap ways, the wood share, the tread test, the
overlap registry's admission, the brook rules, the yards, or the hinterland's belt, bamboo and groves.

These checks are usually already prefiltered by a grid (`settlement/_geom/indexes.py`). The cost is that every surviving
pair is measured by a scalar pure-Python primitive (`seg_dist`, `segments_cross`, `box_gap`). In total there are about
2.2M `seg_dist` calls at 40 households, nearly all inside the chains below.

`settlement/_geom/primitives.py:59 seg_dists` is the in-repo vectorized precedent. Its docstring records that it cut "a third
of Kashikawa's lane stage" (2026-10-01).

Counts are seed 39, 20 households -> 40 (`fanout-2026-10-26.txt`); exponent n^k is the growth from 20 to 40. Paths are under
`l7r/diagram/`.

## The lane web (stage `web`) and the lane law

| chain | @20 | @40 | growth |
|---|---|---|---|
| `hamletgen/ways/checks.py:376 served_network` (29 -> 45) -> `lanes_share_tread` (`:365`) | 7.3k | 27k | n^1.9 |
| ... -> genexpr `:373` -> `seg_dist` | 448k | 955k | |
| `hamletgen/ways/tree.py:711 rejoined` (60 -> 120) -> `primitives.segments_cross` | 67k | 154k | |
| ... -> `ccw` | 140k | 317k | |
| the same `rejoined` in the homesteads stage (44 -> 95) -> `segments_cross` | 42k | 120k | |
| `hamletgen/ways/law.py:512 near_misses` (42 -> 83) -> `free_end` (`:449`) -> `box_gap` (`:459`) | 8.4k | 62k | n^2.9 |
| `hamletgen/ways/law.py:833 over_a_fixture` (53 -> 82) -> `fabric._crosses_fabric` -> `poly_box` genexpr | 29k | 73k | |
| `hamletgen/ways/geom.py:351 _trim_to_service` (21 -> 27) -> `end_serves` -> `ring_within` (`:209`) -> `indexes.edge_within` -> `near` | 35k | 88k | |
| `hamletgen/ways/law.py:438 doubled_tails` -> `tails.tail_doubled` -> `keeper.keyed` / `pts_key` | 12.8k keys | 41k keys | see `hotspots-cheap-wins.md` C2 |

**Direction:**
- Hold each lane as a numpy segment array plus one segment STRtree for the web.
- Ask the pair questions in bulk: `STRtree.query(segs, predicate="dwithin", distance=...)`, then a vectorized segment-segment
  distance or crossing over the candidate pairs.
- In the settle rounds, re-check only lanes an edit touched.
- The 40-household refusal (seed 4, `WebRefused` after 20.3 s in the web, `measurements.md`) belongs to this stage. Judge
  any change here on that seed as well.

## Homestead seating (stage `homesteads`)

| chain | @20 | @40 | growth |
|---|---|---|---|
| `settlement/homestead_parts/yards.py:166 _filled_lattice` (20 -> 40) -> `fits` (`:114`) -> `primitives.edge_dist` (`:167`) | 6.3k | 12.7k | |
| ... -> `seg_dist` | 59k | 174k | |
| `settlement/rolling/gap_ways.py:265 way_out` (20 -> 40) -> `ok` (`:275`) | 42k | 90k | |
| ... -> `rolling/access.py:258 fixtures_clear` -> `seg_box_within` (`:64`) | 29k | 76k | |
| `settlement/rolling/gap_ways.py:309 trace` (90 -> 243) -> lambda / genexpr at `:323` | 9.4k | 56k | n^2.6 |
| `settlement/homestead_parts/wood_share.py:408` genexpr | 3.8k | 39k | **n^3.4** |

## Wells' tread and admission tests (stage `lane_wells`, also `appurtenances`)

| chain | @20 | @40 | growth |
|---|---|---|---|
| `seat_wells` -> `shrines_wells/wells.py:107 well_at` -> `settlement/houses.py:265 _fits` -> `_on_a_tread` (`:200`) -> genexprs `:235`/`:237` | 22k | 167k | **n^2.9** |
| `_tread_skipped` (`:241`) | 6.8k | 54k | **n^3.0** |
| `well_at` -> `core.admits` -> `overlap/registry.py:321 admits` -> `conflicts` (`:271`) -> `overlap/reserved.py:134 conflicts` -> `_seats_near` (`:121`, a binned lookup, about 24 seats per call), lane_wells | 69k | 299k | n^2.1 |
| the same chain in appurtenances | 3.1k | 23.5k | n^2.9 |
| ... -> `registry._center` (`:408`) genexpr | 41k | 199k | |
| ... -> `reserved.poly_seg_gap` (`:54`) -> `seg_dist` (appurtenances) | 37k | 108k | |

The registry's admission is a correct, binned test, but it is asked one candidate at a time. It is cheap to batch once the
well seats are scored together (`hotspots-recompute.md` R1): admit only the winner.

## Water (stage `field`)

| chain | @20 | @40 | growth |
|---|---|---|---|
| `hamletgen/water/brook_rules.py:190 crosses_mid_run` (24 -> 26) -> `_proper_cross` (`:170`) | 37k | 56k | |
| ... -> `side` (`:173`) | 75k | 112k | |
| `waterfields/partition.py:329 keep_rows` (6 -> 8) -> shapely `length` | 912 | 15.5k | |
| ... -> `decorators.wrapped` | 24k | 63k | |

## Ground cover (stages `hinterland`, `windbreak`)

| chain | @20 | @40 | growth |
|---|---|---|---|
| `homestead_parts/grove_fill.py:354 close_belt_gaps` (1 call) -> `grove_blocks.inside` (`:123`) -> `indexes.inside` (`:455`) | 56k | 97k | |
| ... -> `too_near` (`:228`) genexpr | 57k | 65k | |
| ... -> `Region.taken` -> PIL `getpixel` | 26.5k | 36k | see `hotspots-cheap-wins.md` C3 |
| `hamletgen/homesteads/bamboo.py:73 household_bamboo` -> `strip_refused` (`:277`, 573 -> 833) -> `homestead_parts/bamboo_keepout.py:36 stand_spares_seats` -> genexpr `:45` | 74k | 213k | |
| `hamletgen/hinterland/belt.py:368 fouled` (2 -> 4 calls) -> genexpr `:369` -> `indexes.inside` / `edge_within` | 12.7k | 65k | |
| `primitives.py:171 convex_hull` (46 -> 96) -> `cross` | 41k | 90k | |
| `homestead_parts/belt_law.py:158-169` `uv` / `bin` / `_near` | 3.5k | 25.5k | n^2.8 |
| `math.atan2` / `degrees` (hinterland) | 1.2k | 27k | n^4.5, small |
| `shrines_wells/woods.py:110 _crown_seat_clear` (windbreak) -> genexpr `:123` | 26k | 56k | |
| `homestead_parts/groves.py:590` genexpr | 9.5k | 37.5k | n^2.0 |
| `hamletgen/hinterland/stages.py:493` genexpr | 9.5k | 37.5k | n^2.0 |

## Direction for the whole family

The general move is from one Python call per pair to one call per candidate set:

- obstacles held as numpy arrays or shapely geometry arrays, built once per stage;
- candidates batched;
- `STRtree.query(..., predicate=...)` or a numpy broadcast for the measure.

This is the change agents estimated at 2-3.5 s of 6.8 s at 20 households (`estimate-exercise.md`). It touches many call
sites, so do it by family: lanes, then homestead parts, then cover. Re-run the survey after each family to see the chain's
count fall.
