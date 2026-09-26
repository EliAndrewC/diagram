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

`measure.py` on the shipped manifests:

| map | seed | households | seat | belt clumps | belt bearing | off NW | arc |
|---|---|---|---|---|---|---|---|
| Inashiro | 4 | 15/15 | wind-facing, clean | 309 | 345 | 30 | 113 |
| Kashikawa | 8 (was 3) | 20/20 | wind-facing, clean | 264 | 288 | 27 | 134 |
| Kuwabata | 21 | 16/16 | wind-facing, clean | 111 | 297 | 18 | 87 |
| Mizuguchi | 27 (was 23) | 12/12 | wind-facing, clean | 349 | 325 | 10 | 168 |
| Sawada | 24 (was 6) | 19/19 | wind-facing, clean | 154 | 317 | 2 | 157 |

The final cohort (`make cohort N=48`, this engine): **38/48**, failing 2, 8, 23, 25, 28, 31, 35, 36, 40, 46 - every one also failing on the baseline (R3), all `scatter_frame_breach`; seed 37 now passes; no `households_seated` failure. No regression.
