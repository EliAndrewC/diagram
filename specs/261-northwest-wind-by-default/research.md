# Research - feature 261, the wind is northwest unless a map declares otherwise

All figures from the pool manifests via [`measure.py`](measure.py) (compass bearings: 0 = north, 315 = northwest;
`off-wind` is the belt center's angle off the windward bearing, `arc` the belt's arc around its cluster), or from
the named run's own output.

## R0 - The defect, at HEAD before the feature

The shipped manifests recorded windward N (Inashiro), SE (Kashikawa), NW (Kuwabata), S (Mizuguchi), NE (Sawada).
The wind was `windward_for(down_deg, seed)` - the upslope bearing turned by a rolled 45 degrees - and
`ways/track.py` renamed it after the seat's back whenever the two were more than ~70 degrees apart. Kashikawa
(falls NE) could only roll S, SW or W from the slope; its `SE` is the rename.

## R1 - The trial: the wind alone moved, the seat unchanged

Default `NW`, the rename removed, `seat_cluster` untouched. The belts went where the seats let them:

| map | households | windbreak clumps | note |
|---|---|---|---|
| Inashiro | 15/15 | 72 | |
| Kashikawa | 20/20 | **0** | the belt was planted in the crop and thinned away (194 before) |
| Kuwabata | 16/16 | 111 | |
| Mizuguchi | 12/12 | 7 | |
| Sawada | 19/19 | 27 | |

So the seat has to bend to the wind (plan D2). With the 45-degree bar added:

| map | households | offwind | clumps | belt bearing | off-wind |
|---|---|---|---|---|---|
| Inashiro | 15/15 | no | 169 | 331 | 16 |
| Kashikawa | 20/20 | no | 293 | 301 | 14 |
| Kuwabata | 16/16 | no | 111 | 297 | 18 |
| Mizuguchi (seed 23) | **8/12** | no | 154 | 356 | 41 |
| Sawada (seed 6) | 19/19 | **yes** | 27 | 300 | 15 |

Mizuguchi's seat was a wind-facing margin the brook divides (`seat_divided`), and the brook-ignoring re-roll
(feature 230) was no better. Sawada falls northwest: its northwest margin is the wet foot below the drain, and
no wind-facing margin was open at seed 6.

## R2 - The seed search (the spec's owed per-map measurement)

Seeds 1-30 of each map under its own declared fall and sink, through `make hamlet` (`--no-render`; Sawada's
`intake="open"` is not a CLI flag, so seed 24 was re-rolled through its real generator before it was taken).

- **Sawada**: 29 of 30 seeds fall back off the wind; seed 24 alone seats on a wind-facing margin - 19/19, 154
  clumps at 317 degrees, confirmed through the real generator with `intake="open"`. The off-wind seeds still drew
  northwest belts of 65-303 clumps (median about 250) - the evidence for plan D3's order.
- **Mizuguchi**: 21 of 30 seats 12/12; the short ones (seeds 2, 6, 9, 14, 17, 20, 21, 23, 25, 26) are all `round`
  clusters. Five candidates were re-rolled through the real generator: 8, 12, 16 seat on divided margins; 24 and 27
  on clean ones. Seed 27 - 12/12, undivided, 349 clumps at 325 degrees - was taken.

Neither map needed anything from the spec's "When no seed works" list.

## R3 - The cohort, both ways (constitution XIII)

`make cohort N=48` in a detached worktree at HEAD (the unmodified engine) and in the clone.

- Baseline: **37/48**; failing seeds 2, 8, 23, 25, 28, 31, 35, 36, 37, 40, 46 (all `scatter_frame_breach` but one
  `farmhouses_reach_a_way`). These are pre-existing and ledgered here, not this feature's.
- An intermediate cut of the seat order (a wind-facing divided margin ahead of a clean off-wind one): **41/48**,
  failing 2, 8, 23, 35, 36, 40, 46, every one also failing on the baseline. Superseded - see R4.
- The final engine: see R5.

## R4 - The divided test was wrong, and the order the exception check refused

**The defect.** `seat_cluster`'s divided test recorded each brook-near band point's LATERAL half of the band, with a
reach of twice the band's depth - so a brook running behind the band, parallel to the margin, read as dividing it.
On the pool (the intermediate cut) Kashikawa and Inashiro were both flagged divided with every house on one bank:
20 | 0 and 15 | 0. Fixed as `brook_banks()` - the side of the nearest brook segment for each band point - with a
unit test. With it and feature 230's order unchanged, Inashiro seats wind-facing at its reference seed 4.

**The order.** Putting a wind-facing divided margin ahead of a clean off-wind one was put to `spec-fidelity` twice
and refused twice. The second time with the 48 cohort specs rolled under both orders on the fixed engine
(manifests kept in `wip/_261c`, not committed):

| | feature 230's order | wind-first |
|---|---|---|
| off-wind seats | 22 | 11 |
| divided seats | 1 | 12 |
| belts under 50 clumps (with none) | 10 (4) | 4 (0) |
| households short | 0 | 0 |
| houses on both banks | 0 | 0 |
| a structure across the brook from every house | 0 | 3 of the 12 divided (the reviewer's count) |

The reviewer counted every house, yard, garden, byre, well and fixture per bank: in Audit-8, -12 and -38 a byre, a
well, a garden or fixtures stood across the brook from their houses - feature 230's own failure. So the order
stands, and a map whose clean seats all face off the wind is re-seeded.

**Kashikawa** (declared fall 315, offmap, `brook_side=-1`), seeds 1-30 on the fixed engine: five seeds (7, 8, 14,
21, 23) seat all 20 households on a clean wind-facing margin; at seed 3 the wind-facing margins were refused by the
dry hem behind the west ones, the wet toe under the northwest ones, and the brook the declared flank runs along
(a logged run). Belt arcs round the cluster: 7 182, 8 134, 14 **333**, 21 113, 23 103 degrees. Seed 14's belt, the
fullest, stood in the middle of the cluster's north edge with houses on three sides - the wrap the record rules out -
so seed 8 (264 clumps at 288 degrees, 134-degree arc) was taken, and the pool test now holds the arc to 200 degrees.
Every candidate's drain ends as near the brook as seed 3's did (54-94 px against 83; observed 2026-09-26, method: the distance from the drain polyline's ends to the nearest brook segment, on each candidate's manifest), so the confluence stands.

## R5 - The shipped maps, and the final cohort

`measure.py` on the shipped manifests (observed 2026-09-27, method: `measure.py` over the five pool manifests after
the amendment's last re-roll):

| map | seed | households | seat | belt clumps | belt bearing | off NW | arc |
|---|---|---|---|---|---|---|---|
| Inashiro | 4 | 15/15 | wind-facing, across the brook from its rice | 180 | 320 | 5 | 109 |
| Kashikawa | 3 | 20/20 | wind-facing, across the brook from its rice | 281 | 319 | 4 | 161 |
| Kuwabata | 21 | 16/16 | wind-facing | 151 | 285 | 30 | 83 |
| Mizuguchi | 23 | 12/12 | wind-facing, astride the brook (7 and 5) | 89 | 313 | 2 | 122 |
| Sawada | 24 (was 6) | 19/19 | wind-facing | 179 | 319 | 4 | 161 |

Every rule still holds on every map (the two pool test files).

The final cohort (observed 2026-09-27, method: `make cohort N=48` on this engine, merged with main at 2e6f46e6):
**38/48**, failing 2, 8, 23, 25, 28, 31, 35, 36, 40, 46 - every one also failing on the baseline (R3), all
`scatter_frame_breach`; seed 37 now passes; no `households_seated` failure. No regression.

## R6 - What the re-seeds took from the pool, and how it was put back

The gate's coverage floor caught it before anything else did: 19 lines in four files went unreached once the pool
re-rolled, and every one sat behind a knob VALUE no pool map showed any more. Compared against main, per knob, the
values the five maps exhibited: bamboo `both` (was Kashikawa), byre form `courtyard` (was Mizuguchi and Sawada),
copse `against_the_belt` (was Mizuguchi), lane web `alleys` (was Sawada) were gone. (`water_source` `head_left` also
went, but it is derived from where gravity puts the head sluice, not a knob.) A knob owes one map per value on the
sheet, so each value is now DECLARED on the map that showed it before - Kashikawa `bamboo="both"`, Mizuguchi
`byre_form="courtyard"` and `copse_siting="against_the_belt"`, Sawada `lane_web="alleys"` - which needed one new spec
field, `HamletSpec.byre_form`, pinned onto the settlement engine's knob. Re-rolled, every wind rule still holds on
all five maps (R5).

## R7 - The brook made crossable, and the seeds it gave back

The GM's ruling (2026-09-27): *"if we find instead that our placement algorithm ends up not making it possible to lay
out a known-to-be-valid settlement configuration then we should fix the placement algorithm instead."* The record
attests a hamlet astride its own small channel (`research/water/270`, Harie), so the refusals R4 measured were the
engine's, not the record's. Built (plan D9): fords every 160 ft (`m:ford-spacing`) where the brook bends under 20 degrees, a 30 ft gap
in its no-route corridor at each, the spur routed through one when its line would cross the water, every crossing
decked by `bridges()`; the strike-out, its re-roll and the far-bank refusal deleted.

Measured at the original seeds (observed 2026-09-27, method: `make map` on each generator, then the session's
manifest reader for households per bank and bridges within their span of a brook crossing):

| map | seed | households | per bank | bridges on the brook | fords |
|---|---|---|---|---|---|
| Inashiro | 4 | 15/15 | 15 / 0 | 1 | 19 |
| Kashikawa | 3 | 20/20 | 0 / 20 | 3 | 28 |
| Mizuguchi | 23 | 12/12 | 4 / 8 | 2 | 19 |
| Sawada | 24 | 19/19 | 0 / 19 | 0 | 20 |

Kashikawa and Mizuguchi therefore return to seeds 3 and 23 (the spec's Edge Case: no research-supported refusal was
recorded at either). Sawada's seed 6 stays refused: its refusal was the drain and the wet toe, which the record
supports (R2).

## R8 - What the settlement-reviews found, and what each fix measured

Five reviews on the re-rolled maps (the ledger rows of 2026-09-27) returned NEEDS-WORK. Each finding became an FR
(FR-013 - FR-018) and each fix was measured on the pool (observed 2026-09-27, method: the manifest measures now held
by `tests/hamletgen/test_pool_261.py` and `test_pool_wind.py`, run before and after each fix):

| finding | before | after |
|---|---|---|
| farmstead parts across the brook from their house (FR-013) | Inashiro 4, Mizuguchi 2 | 0 on every map |
| copse crowns beyond reach (FR-014; 90 ft of a house, `m:copse-house-reach`, or 60 ft of the belt) | Kashikawa 393 crowns, median 167 ft from a house; after the first fix, 4 on Kashikawa and 4 on Mizuguchi through the re-seat nudge | 0 on every map; medians 63-72 ft |
| entrance board distance from its anchor (FR-015) | Sawada 669 ft | 65-139 ft on the four entrance maps, each within 100 ft of a house |
| belt depth along the wind (FR-016; 30 ft minimum per 40 ft bin not cut by a way, the brook or the page edge) | Kashikawa at seed 8: an arm 12-21 ft deep | at least 51 ft on every judged bin of every map |
| the brook's sharpest turn (FR-017; 100 degrees) | Sawada 123 | Inashiro 41, Kashikawa 53, Mizuguchi 53, Sawada 95 |
| pop-up naming a side the belt does not occupy | Kuwabata ("north and west" on a west strip) | the pop-up names the northwest as the wind's direction |

The one-bank rule's research pass (2026-09-27, `research/homesteads/250`) found nothing that places a farmstead's own
parts across a channel from its house or says they never stood there; it is a guess with an absence note, and the
one on-topic paper that could not be read is on the GM's download list.

## R9 - The second round of reviews, on the amended maps, and what each fix measured

The five reviews of the amended maps (2026-09-27) were recorded NOT-REVIEWABLE - engine edits landed while they ran - but
each judged its snapshot and kept its findings on the record. Every finding was answered in the engine and measured on
the re-rolled pool (observed 2026-09-27, method: the manifest measures of `tests/hamletgen/test_pool_261.py`, and the
session's reading of each crossing, spur and caption, before and after):

| finding | before | after |
|---|---|---|
| households whose way out misses the entrance board (FR-015) | Inashiro 1, Kashikawa 2, Sawada 1 | 0 on all four entrance maps |
| a lane crossing the brook and back to a house on its own bank | Kashikawa 1 | 0 (a crossing is priced) |
| brook crossings more than 10 degrees off square | Kashikawa 1 at 52 degrees | 0 |
| hamlets whose field lies across the brook with no way to it (FR-012) | Inashiro, Kashikawa, Mizuguchi, once crossings were honest | 0; each spur crosses at a ford |
| brook ruled level along the frame (the GM's 2026-08-26 ruling) | Sawada 457 ft (`m:sawada-brook-ruled`) | 66 ft; no map over 150 ft |
| cluster declared a shape its drawing does not read as | Inashiro, crescent at a drawn 1.97 | recorded unhonored |
| scrub inside the farmsteads' own outline | Kuwabata 138 bases (20 within 15 ft of a part) | the keep-out takes in every part |
| board caption past the page's edge | Kashikawa, 31 ft | all five inside the view |
| a rejected roll readable in the pool mid-sweep | Sawada's first attempt read by the census | every attempt staged, the kept one promoted |
| a farmhouse standing on the brook (FR-013) | Mizuguchi, a wall on the centerline | every house corner at least 26 ft from the course |
| a household whose nearest way is across the brook, undecked | Mizuguchi 1 | 0 on every map |
| the entrance board under a drawn crown | Mizuguchi, 0.6 ft inside | 32 ft clear, every departure still passing it |
| a through-running connector with no handover found | Mizuguchi (both ends off the sheet) | the junction where a lane's end meets it |

Found on the way (constitution XIV): three sites used `seg_intersect` - which answers for the lines - as a crossing test,
so every spur detoured to a ford and every connector bearing scored a brook violation per segment; with the test fixed the
connector scorer chose different tracks on four maps, and their district directions were re-read from the drawing.

## R10 - The next review round, and what each fix measured

The reviews of engine 4d1f0170 (2026-09-27) found the caption and the ways still wrong in places; each fix was measured
on the re-rolled pool (observed 2026-09-27, method: the manifest measures of `tests/hamletgen/test_pool_261.py` and the
records `m:kashikawa-r4-caption`, `m:kuwabata-r4-tail`, `m:kuwabata-r4-caption-lane`, `m:mizuguchi-r4-over-and-back`):

| finding | before | after |
|---|---|---|
| the board caption drawn on a farmhouse roof | Kashikawa, its center inside the roof | 11.2 ft clear (`m:kashikawa-r4-caption`); no caption within 0 ft of a roof on any map |
| a board caption across a lane's tread, on the drawn quad | Kuwabata, -1.5 ft | every map at least 2 ft (Kuwabata 3.4) |
| a lane running back along another | Kuwabata, 122 ft beside its connector | 0 on every map |
| a lane crossing the brook and straight back | Mizuguchi, two planks 35 ft apart | 0; every crossing within 45 ft of a ford |
| lane records that draw nothing | Kashikawa 3, Kuwabata 2 | 0 |
| a farmhouse 402 ft from its nearest neighbor | Kuwabata | not on the kept roll; the farthest is 151 ft |
| a doubled-tail cut that drew a hook, and necked the route out | Sawada, a 9.8 ft leg back 116 degrees; 69.7 ft of 3 ft path | no hook on any map (`m:sawada-r5-hook`); the 6 ft track runs to the hub (`m:sawada-r5-route-wide`) |
| a way out over the brook and back | Mizuguchi, 2 of 12 households | at most 1 crossing on every route (`m:mizuguchi-r4-over-and-back`) |
| a caption nearer another footprint than its board | Kuwabata, byre 4.9 ft and board 24.6 ft | nearest its board on every map; Kuwabata 6.8 against 11.2 (`m:kuwabata-r5-caption-pair`) |
| a caption level beside a tilted board | Kuwabata, level beside a board at 38.7 degrees | every caption at its board's angle (`m:kuwabata-r6-caption-angle`) |
| a lane over a drawn channel off square | Mizuguchi's head-race plank, 44 degrees | every such crossing square (`m:mizuguchi-r6-headrace`) |
| a caption's halo notching crowns | Kuwabata, 3 crowns, 24% of the caption box on canopy | no caption on a crown on any map (`m:kuwabata-r7-caption-canopy`) |
| woodland parcels in a ruled row | Inashiro, 5 ft off one line over 1,104 ft | no row on any map; Inashiro keeps 2 parcels (`m:inashiro-r7-parcel-row`) |
| copse clumps in the marsh | Kashikawa, 6 clumps 3-21 ft in | none on any map (`m:kashikawa-r7-copse-marsh`) |
| copse clumps across the brook from their houses | Kashikawa, 3 clumps | none on any map (`m:kashikawa-r8-copse-bank`) |
| the belt's north arm cut by the frame behind a house | Inashiro, a 97 ft opening; view top 121 | the belt wraps the house; view top 38, 180 to 239 clumps (`m:inashiro-r9-belt-frame`) |
| a lane hollowing the belt | Kuwabata, drawn crowns 58 ft deep at the median, 53% of the outline (main 93, 80%) | 88 ft, 75% (`m:kuwabata-r10-belt-depth`) |

Kuwabata's first two rolls under the changed ways each left a farmhouse off the way network, so it keeps its third: 4
of 16 farmsteads re-seated, the farthest 134 ft (`m:kuwabata-r4-notes`).

## R11 - The round of engine 0ae309f0, and what each fix measured

The reviews of engine 0ae309f0 (2026-09-27) passed Kashikawa and found one error each on the other four maps, plus a
questionable finding on Inashiro. Each fix was measured on the re-rolled pool (observed 2026-09-27, method: the manifest
measures of `tests/hamletgen/test_pool_261.py` and the records named in each row):

| finding | before | after |
|---|---|---|
| Kuwabata: a bare wedge inside the cluster, straight-edged | the largest ink-free disc in the wedge's box 72 ft in radius, 24,600 sq ft more than 20 ft from any mark | 29.4 ft and 2,000 sq ft: the scrub keeps off each farmstead and each near pair only (`m:kuwabata-r11-wedge`) |
| Sawada: the brook straight for most of its course on the page | 872 ft within 3.1 ft of a line, 70% | 380 of 1,240 ft, 31%; the other brook maps 17-23% (`m:sawada-r11-brook-straight`) |
| Mizuguchi: the belt's footprint holding the front rank, houses 34-47 ft from the west edge | the seat scored its belt room and still won | a seat without belt room is a fallback; the westernmost house 1,236 ft from the edge (`m:mizuguchi-r11-belt-room`) |
| Mizuguchi, after the re-seat: the board 202 ft from its handover | 2 of 12 ways out missed it | 16 ft from the handover, 0 missed (`m:mizuguchi-r11-board`) |
| Inashiro: the dry plots across the rice from every house | median 658 ft | 72 ft: a homestead field against ten of fifteen steadings, the canal hem kept (`m:inashiro-r11-dry`) |
| Inashiro: the rolled crescent drawn as a blob after the seat moved to the brook flank (a regression against main, found by the escalation-check) | 1.62, unhonored (main 4.07) | 2.0, honored; Kuwabata 1.73 and Mizuguchi 1.93 honored, Kashikawa and Sawada unhonored as on main (`m:inashiro-r11-shape`) |
| Inashiro (questionable): the woodland across the rice | 3 of 3 parcels across the field | 2 of 3 - no seat on the houses' side qualifies inside the predicted frame; the preference is in place and falls back (`m:inashiro-r11-woods`) |
| Sawada (nitpick): an axis-aligned S-jog below the tap | the segment leaving the tap run 0.1 degrees off vertical | 0 segments within 1.6 degrees of an axis below any tap run; an approach leg on Inashiro (1.2 degrees, on main too) nudged as well (`m:sawada-r11-tap-axis`) |
| Mizuguchi (nitpick): both wells on the north bank | a hamlet astride the brook | all 12 houses and both wells on one bank (`m:mizuguchi-r11-wells`) |
| Sawada (from the round before): the belt on the toe's reed edge | 70 of 201 belt clumps in the marsh, drawn as cedar and broadleaf | the same 70 drawn as alder, the record's woody stage at a reed edge (`m:sawada-r11-alder`) |

The research for two of these was run first. Where dry fields lie: the old settlements of an alluvial lowland stand
on the natural levee, which is also their dry field, with the paddy in the back marsh (`shizen-teibo-jawiki`,
`kohai-shicchi-jawiki`, both already read for the record); the household's own-consumption plot of `kateisaien-jawiki`
is the dooryard bed the map already draws, and that page puts it as often in odd corners by the paddy or on a riverbank.
What stands at a reed edge: alder grows tallest at a wetland's fertile periphery (ja.wikipedia ハンノキ, read by the
research pass, not cited); cutting the reed stops litter building soil on which willow grows (`opal-biwa-yoshi-hara`,
new, APPLICABLE-WITH-LIMITS). No readable page says whether a village's windbreak grove ever ran onto marsh ground
(searched 2026-09-27: ja.wikipedia 屋敷林 and 防風林, the Kushiro alder-zonation page, the Tonami dispersed-settlement
pages).

The round of engine 03cf6a84 (observed 2026-09-27) stopped four reviews at their first stage on dispositions, and found
one error on Kashikawa. What each fix measured:

| finding | before | after |
|---|---|---|
| Kashikawa: a plank 44 degrees off square, the lane bent 3 ft inside the brook | 44 degrees | 1.0 degree at the worst crossing on the map (`m:kashikawa-r12-plank`) |
| Kashikawa (nitpicks): the notes' connector bearing, the drain junction, four stale records | 11 degrees; 476 ft and 655 ft; greps on 360 clumps, aspect 1.03 | 14 degrees (`m:kashikawa-r12-bearing`); 584 ft inside the view, 778 ft of brook below (`m:kashikawa-r12-junction`); the belt's 277 clumps and every other record re-measured (`m:kashikawa-r12-records`) |

The same round's cohort ran 37/48 against main's 38/48 (observed 2026-09-27, method: `make cohort`): seed 45's view reached 41 ft past the predicted scatter frame (observed 2026-09-27, method: the roll's `scatter_frame_breach`),
its title pocket placed below the content because every seat above it was off the canvas. The prediction now takes in
that band when the content reaches the canvas top, and the seed passes (observed 2026-09-27, `make hamlet` on Audit-45).

The round of engine 0c0ac524 (observed 2026-09-27) passed Kashikawa, Kuwabata and Sawada and found two maps needing work:

| finding | before | after |
|---|---|---|
| Inashiro: the entrance board bypassed | 2 of 15 ways out missed it | 0 of 15, each walked from its door to the outer end (`m:inashiro-r13-board`) |
| Inashiro: every route passed the board by construction | routes walked to the handover and back | a board at the old inner end misses 1 route in the test fixture (`m:inashiro-r13-routes`) |
| Mizuguchi: the bamboo thicket on the brook | 13 culms on the water ribbon | 144 ft from the centerline (`m:mizuguchi-r13-bamboo`) |
| Mizuguchi: the notes said the hamlet stands astride the brook | seven and five | all 12 on one bank (`m:mizuguchi-r13-notes`) |
| Mizuguchi: a lane off the top of the map past the connector | 52 ft past the junction | 0 lane ends off the frame (`m:mizuguchi-r13-lane`) |
| Mizuguchi, Kuwabata: two bearings for one connector | 34 and 57; 274 and 271 | 59 (`m:mizuguchi-r13-bearing`); 274 (`m:kuwabata-r13-bearing`) |
| Kuwabata: seat distances written as moves | "67 to 149 ft from main's" | stated as distances to main's nearest seats, 4 farmsteads (`m:kuwabata-r13-moves`) |
| Sawada: stale history inside the census block | 1 section | moved above it, pointing at the current caption (`m:sawada-r13-census`) |

The cohort after round 03cf6a84's fixes ran 48/48 (observed 2026-09-27, method: `make cohort`), against main's 38/48.

The round of engine 176042d3 (observed 2026-09-27) passed Kashikawa, Kuwabata and Sawada; both errors it found were made by
the previous round's own lane cut and entrance rule:

| finding | before | after |
|---|---|---|
| Inashiro: a farmstead's only lane cut to a 4 ft stub | its nearest way 100.5 ft | 39.7 ft (`m:inashiro-r14-lane`) |
| Inashiro: the entrance sited on that stub | notes said 15 ft to a stub | 17 ft from the restored lane's join, as the notes say (`m:inashiro-r14-board`) |
| Mizuguchi: a lane 61 ft past its house into the grass | 1 end reaching only the way it left | 0 on every map (`m:mizuguchi-r14-nowhere`) |
