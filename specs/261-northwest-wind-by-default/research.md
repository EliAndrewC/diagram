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
| Inashiro | 4 | 15/15 | wind-facing | 168 | 332 | 17 | 104 |
| Kashikawa | 3 | 20/20 | wind-facing, the brook crossed | 285 | 320 | 5 | 160 |
| Kuwabata | 21 | 16/16 | wind-facing | 141 | 283 | 32 | 88 |
| Mizuguchi | 23 | 12/12 | wind-facing, astride the brook (8 and 4) | 132 | 305 | 10 | 91 |
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

