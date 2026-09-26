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
  `farmhouses_reach_a_way`).
- New (the D3 intermediate cut): **41/48**; failing 2, 8, 23, 35, 36, 40, 46 - every one also failing on the
  baseline, all `scatter_frame_breach`. No `households_seated` failure anywhere. Four baseline failures now pass.
- The seven `scatter_frame_breach` seeds are pre-existing and ledgered here, not this feature's.
- New (final D3): see R4.

## R4 - The shipped maps

Filled from the final re-roll.
