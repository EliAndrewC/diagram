I ruled all 64 numbers in `t38_N4-ways.txt`. None turned out to be an unresearched question about the world, so I ran no web pass, fetched no page and added nothing to the ledger. Nothing was edited. I checked the record (the pages under `/diagram/research/questions/` and the units' own and neighbouring `Research:` claims), and three findings need action:

- **The 14 ft gap off water contradicts its own cited page.** `clearance.py` lines 27 and 334 keep a path 14 ft off water, but 0055 puts a path on the bank of every channel. The code's own claims already call this "a departure the code keeps until feature 417 T32".
- **The 8 ft stream-width fallback in `squaring.py:74` disagrees with the record.** The record gives the brook as 7 ft everywhere. The fallback never runs, because every stream record carries `w` (written by `settlement/water_ways/water.py:132`).
- **`OVER_THE_WATER_FT` (`bund.py:425`) cites a page that does not give its figure.** Its claim cites 0014 for "3.5 ft past the centerline", but 0014 has no 3.5: the only 3.5 in its notes is a soybean height. The code comment says the figure was "measured on Mizuguchi by the landing's round-3 review", so the citation needs fixing.

## Sources

**0055-where-a-field-meets-its-ditch-…-mizuguchi.html** (the Rites of Zhou with a Tang sub-commentary; premodern China). It contradicts the 14 ft:
- "It puts a path on the bank of every grade of field channel, from the smallest up, and a Tang-dynasty sub-commentary says the path on the smallest takes no cart, but oxen, horses and people on foot."

**0055 ….notes.html** records a search already run and found silent, which covers the 3.5 ft far-bank figure:
- The note reads "no publicly readable source", with this search recorded: "searched 2026-09-29: for the width of the bank along a village supply canal before 1868 in Japan or 1912 in China - in Japanese, 用水路 土手 馬踏 幅 江戸時代 地方凡例録 堤 and 用水堀 両側 土手 幅 間 村明細帳 用水路 敷 江戸 … in Chinese, the Rites of Zhou with its commentaries on Wikisource".

**0014-bunds-between-the-paddies-aze.drawing.html** records the bund width as its own guess:
- "Between 2 and 5 ft, a GUESS: no page we read gives its width, so it is held between the two-shaku (about 2 ft) dividing bund and the one-ken (about 6 ft) farm road of a field replanned in 1869."

**0035-villages-beside-their-stream-one-bank-or-both.drawing.html**, against the 8 ft fallback:
- "A brook 7 ft wide, which the hamlet draws its water from, is in between, the size of a stream, where the record shows both forms and prefers neither."
- The code agrees with the page elsewhere: `water.py:129`, `brook_rules.py` (`BROOK_DRAWN_W = 7.0`, citing 0068) and `city/bridges.py` (`DEFAULT_W` 7, citing 0035).

**0081-village-lanes.drawing.html**:
- On the footpath: "At the hamlet's scale of one foot to the pixel, a footpath is drawn 3 ft wide, the cluster's spine and its spur to the fields 5 ft, and the track out to the wider world 6 ft."
- On the shadowing rule, which uses an angle where the code uses a share: "A lane whose end runs back along another way at less than 20 degrees, or that wanders over another way at such an angle, would be walked into one path with it, so the maps cut it where it comes alongside and let it meet the other as a T."

**0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html**:
- "the maps lay a lane with a footpath's clearance and some working room kept off the trees on each side, about 22 ft of the opening". 22 ft is 3 ft + 2 x 9.5 ft, and `consts_ways.py:87` sets `GROVE_WORKING_ROOM_FT = 9.5`.

**0196-communal-wells-ido.drawing.html** makes the well's radius a sheet size:
- "A well is drawn as a marker larger than life. At one foot per pixel its curb is drawn at a radius of 9.36 ft, about 19 ft across, so the well is visible at map scale: the marker shows where the well stands, not how much ground it takes."

**Searched-silent claims already in the code** (this month's T29 passes):
- `route.py::_route`: "clear of the toe and marsh - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 8 ft (`WEB_HARD_GAP`)".
- `track.py::connector_dry_exit`: "pond berth - GUESS: searched, the record silent (feature 417 T29 pass D, 2026-10-25); 80 ft past the pond's larger half-axis". The same claim says of the wet ground: "a convention there, no distance given; the 8 ft is ours".

## Reading

**SILENT** on the one world distance that has no page value: how far past a crossed water's centerline the square leg reaches (bund.py:390, 3.5 ft). The 2026-09-29 search for a supply canal's bank width found no source, and 0014 gives the bund's width only as its own guess. The 3.5 is consistent with half the 7 ft brook (0035), or half a 4.5 ft canal (0068) plus a step onto a bund of 2 ft or more, but no page states it. Every other world number either quotes a page or carries a searched-silent claim from this month, and the rest are plumbing.

## Rulings

| file::unit | line | value | ruling | what the number does |
|---|---|---|---|---|
| bund.py::squared_step | 390 | 3.5 | SEARCHED-SILENT 0055.notes (bank width, 2026-09-29) / GUESS 0014 (2-5 ft bund); the neighbouring `OVER_THE_WATER_FT` cite of 0014 does not hold | the least the square leg runs past the water's centerline |
| checks.py::brook_boxes | 109 | 64 | NONE | memo size |
| checks.py::ford_leg | 117 | 256 | NONE | memo size |
| clearance.py::link_index | 27 | 14 | CONTRADICTED 0055 (departure recorded, deferred to T32) | link held 14 ft off water lines |
| clearance.py::clear_runs | 260 | 8 | NOT-ABOUT-THE-WORLD | sampling step along a run |
| clearance.py::clip_to_clear | 334 | 8 | NOT-ABOUT-THE-WORLD | sampling step |
| clearance.py::clip_to_clear | 334 | 14 | CONTRADICTED 0055 (departure recorded, T32) | lane arm held 14 ft off a water line |
| corridors.py::__init__ | 158 | 64 | NONE | spatial-index cell (water) |
| corridors.py::__init__ | 160 | 64 | NONE | spatial-index cell (edges) |
| corridors.py::__init__ | 165 | 64 | NONE | spatial-index cell (parts) |
| corridors.py::_shortest_runs | 283 | 64 | NOT-ABOUT-THE-WORLD | first query band, grown until enough runs |
| corridors.py::field_router | 436 | 1.5 | NONE | point-match tolerance (owner is this house) |
| dry_exit.py::_blocked_memo | 116 | 8 | NONE | memo size |
| fabric.py::__init__ | 70 | 12 | NOT-ABOUT-THE-WORLD | look-ahead vertex count on the envelope walk |
| fabric.py::_homestead_polys | 235 | 8 | CONVENTION 0196 (marker larger than life); `vr` overrides it | well obstacle radius fallback |
| fabric.py::_homestead_polys | 240 | 8 | NONE | octagon standing in for the circle |
| fabric.py::_homestead_polys | 265 | 8 | CONVENTION 0196; `vr` overrides it | held-well radius fallback |
| fabric.py::_homestead_polys | 266 | 8 | NONE | octagon |
| geom.py::push_clear_of_fabric | 130 | 24 | NOT-ABOUT-THE-WORLD | step count walking out until clear |
| geom.py::push_clear_of_fabric | 134 | 6 | NOT-ABOUT-THE-WORLD | step length of that walk |
| geom.py::_seg_cross | 138 | 0.02 | NONE | float tolerance |
| geom.py::_seg_cross | 149 | 0.02 | NONE | float tolerance |
| last_resort.py::foul_part | 128 | 0.4 | NONE | widening for a diagnostic matrix query (names the reason) |
| law.py::field_unreached | 800 | 128 | NONE | spatial-index cell |
| law_water.py::crossing_points | 66 | 64 | NONE | spatial-index cell |
| route.py::set_crossing | 43 | 20 | NONE | spatial-index cell floor |
| route.py::set_crossing | 46 | 5 | NOT-ABOUT-THE-WORLD | brook sampling step |
| route.py::_new_crossing | 71 | 5 | NOT-ABOUT-THE-WORLD | sampling step of the straight pull |
| route.py::lattice_search | 120 | 1e18 | NONE | sentinel |
| route.py::lattice_search | 155 | 1e18 | NONE | sentinel |
| route.py::_route | 162 | 0.75 | NOT-ABOUT-THE-WORLD | search-box pad as a share of span |
| route.py::_route | 199 | 80 | NOT-ABOUT-THE-WORLD | least search-box pad |
| route.py::_route | 210 | 90000 | NOT-ABOUT-THE-WORLD | lattice cell budget |
| route.py::_route | 224 | 0.71 | NONE | half a cell's diagonal (geometry) |
| serve.py::_lay_web_lane | 209 | 0.6 | GUESS 0081 (page rule is under 20 degrees; share recorded as a departure, T32) | a run refused when over 60% shadowed |
| serve.py::band_grow | 418 | 1.5 | CITED 0036 ("about 22 ft of the opening") + 0081 (3 ft footpath) | half the footpath's tread |
| serve.py::flank_doors | 585 | 0.7 | NOT-ABOUT-THE-WORLD | cosine (about 45 deg) for "faces a grove band"; 0036 gives the rule, not the angle |
| serve.py::route_from_door | 614 | 8 | NONE | eight compass directions (the step itself already GUESS T29 A2) |
| squaring.py::square_waters | 74 | 8 | CONTRADICTED 0035 / 0068 (brook 7 ft); never runs, every stream records `w` | stream width fallback |
| street.py::street_run_out | 67 | 60 | CONVENTION | run carried past the sheet's edge |
| street.py::run_to_edge | 78 | 60 | CONVENTION | same |
| street.py::street_runs_out | 91 | 60 | CONVENTION | same |
| sweeps.py::_join_orphan_ways | 73 | 6 | NOT-ABOUT-THE-WORLD | rounds of the orphan sweep |
| sweeps.py::_join_orphan_ways | 117 | 14 | NOT-ABOUT-THE-WORLD | lattice cell for the retry route |
| sweeps.py::farm_bands | 165 | 8 | NONE | octagon for a copse clump |
| track.py::connector_track | 558 | 20, 21, 9 | NOT-ABOUT-THE-WORLD | 41 bearings at 9 deg steps |
| track.py::wet_grown_by_the_lane | 648 | 8 | SEARCHED-SILENT route.py::_route claim (T29 pass A1; 0081 gives no distance) | wet ground grown 8 ft (`WEB_HARD_GAP` written as a literal) |
| track.py::connector_dry_exit | 767 | 16 | NONE | 16-gon for the pond disc |
| track.py::connector_dry_exit | 767 | 80 | SEARCHED-SILENT connector_dry_exit claim (T29 pass D) | pond berth |
| track.py::connector_dry_exit | 780 | 0.71 | NONE | half a cell's diagonal |
| tree.py::left_to_the_tree | 406 | 1.5 | NONE | point-match tolerance |
| tree.py::rejoined | 746 | 0.2 | NONE | floor on sin, a divide-by-zero guard |
| tree_base.py::nearest | 72 | 64 | NONE | first search radius, grown until a house is found |
| web/skeleton.py::water_along_side | 55 | 8, 9 | NOT-ABOUT-THE-WORLD | nine sample points along a flank |
| web/skeleton.py::_web_cut_lines | 327 | 12, 13 | NOT-ABOUT-THE-WORLD | 13 vertices per lateral |
| web/skeleton.py::_web_cut_lines | 335 | 40 | NOT-ABOUT-THE-WORLD | vertex spacing to follow the curve |
| web/skeleton.py::_web_cut_lines | 355 | 8, 9 | NOT-ABOUT-THE-WORLD | nine vertices per tie |
| web/stage.py::seat_wall_reach | 301 | 1.5 | CITED 0081 ("a footpath is drawn 3 ft wide") | half the footpath's tread |
| web/stage.py::_reachable_runs | 334 | 8 | NOT-ABOUT-THE-WORLD | sample stride ("the stride is the resolution") |

## Leads not followed

- `cluster_edge.py:129` has the same `f.get("w", 8.0)` stream fallback, outside this list.
- `track.py:648` writes 8.0 as a literal instead of `WEB_HARD_GAP`, so the two could drift apart.