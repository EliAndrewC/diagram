# Research: Grow the cluster (feature 308)

Every figure here was observed 2026-10-02, method: `specs/308-grow-the-cluster/prototype.py` on the reference spec
(Inashiro, nucleated) beyond the band, the homesteads stage timed alone, one process per method, unless a round says otherwise.
"Per margin" is (offers, houses seated) on each margin the ladder tried, in order.

## R1 - Round 1: grow from the houses at the footprint's minimum distance

**Method.** The first house is offered the margin's free ground nearest the seat, in order, until one stands. Then every
standing house offers eight seats around it, jittered by ±12 degrees in direction and up to +12% in distance, positional from
the map's seed. Each seat sits at the distance where the two homesteads' footprints part. A footprint is the envelope plus the
reserved woodlot seats, and to the south the yard's far edge plus `SUN_CORRIDOR_FT` (FR-003). Seats are offered nearest the
cluster's center first, and the placer's `try_place` judges each one.

**Result (seeds 4, 25 at 40 households).** No margin seats 40. Each margin seats 3-15 households (seed 25: 8-28) for 5-8 offers
per house kept.

**What refused, seed 4.** The tracer (`TRACE=1`) names the last predicate that refused each failed offer:

| refused by | offers |
|---|---|
| envelope | 1,056 |
| no straight corridor candidate (`seat_reaches_tree`) | 532 |
| corridor | 523 |
| house box | 509 |
| field reach | 368 |
| sun corridor | 11 |

The sun term of the footprint did its job: only 11 offers broke a sun rule.

**Why it stalls** (`PICTURE=` plates). A house grown north of a standing house has no straight run from its dooryard to the
access tree, because the standing house, and the woodlot seats it reserved north of itself, stand across every run. Growth
reaches one row along the exit strip and stops.

## R2 - Round 2: the path first, seats beside every corridor

**Method.** Seats are offered along every reserved corridor and the exit strip, on both sides. Each seat stands half a footpath
plus `GAP` off the path, one envelope width apart.

**Result.** The row along the exit strip seats cleanly: short corridors, a refusal mix of reach and envelope. Then the margin
stops at 3-7. The ground beyond the field's reach (700 ft) ends the row inland, and a second row has no way through the first.

## R3 - Round 2b/3: both proposers, more directions and rings, gaps in the row

| variant | seed 4 per margin | seed 25 per margin | seed 47 per margin |
|---|---|---|---|
| both proposers | 7-14 | 11-17 | 8-16 |
| 12 directions, rings 1/1.4/1.8 | 11-40 (14.5 s, 10 margins) | 13-36 | 11-19 |
| a footpath gap every seat along the row (`ROWGAP` 1 or 2) | no gain | no gain | no gain |

None fills a margin reliably. The limit is still a straight run from the door.

## R4 - The engine's layout at 40 households (seed 25)

The base seats 40 on margin 1 with 1,682 offers in 3.4 s. Its plate shows a BRANCHING path tree. Trunks run parallel to the
field, from far houses back to the exit strip, and later houses hang off them with short diagonal legs. The exhaustive pass finds
these by offering every grid point: a far house's long corridor becomes the trunk the next houses reach.

## R5 - Round 5: the path laid round what stands (routed corridors)

**Method.** Where no straight or round-the-gable corridor clears (`_house_candidates`), a corridor is ROUTED.
- The route starts from a dooryard door.
- It is found by A* (weight 1.5, aimed at the tree's nearest points) on a 12 px grid of the open ground: off the site's taken
  ground, off every placed box by the corridor's half-width, off reserved wood seats, and off the house's own box.
- It ends at the nearest point of the tree.
- It is then pulled taut. Each leg reaches the farthest node the engine's own leg tests admit: `house_clear`, `fixtures_clear`,
  `parts_clear`, `standing_ground` and `lawful_leg`. A route has at most 5 legs and no hairpin (`doubles_back`).
- The corridor so found still passes `tree_admits` (the lane law over the whole tree) before it is reserved, like any other.

This is FR-005 literally: each house's path is laid back to a neighbor's path or the tree as the house is placed.

**Capacity.** Seed 25, 8 directions, 10 px grid: 26 margins, but each seats 29-36 at about 6 offers a house kept. Growth now
fills nearly a whole margin, and the plate draws a branching tree like the base's. The margin still falls 4-11 short and is
thrown away.

**Widening the growth when it runs dry.** When the heap is empty with households unseated, every standing house offers again at
the next level: 8 directions at ring 1, then 12 directions at rings 1 and 1.5, then 16 directions at rings 1.25, 1.75 and 2.0.
It is still growth from the standing houses, never the free grid.

| seed | margins | seconds | offers |
|---|---|---|---|
| 4 | 1 | 3.9 | 1,425 |
| 25 | 1 | 2.0 | 567 |
| 47 | 1 | 2.4 | 506 |
| 2 | 1 | 1.6 | 254 |
| 6 | 1 | 2.3 | 479 |
| 7 | 1 | 4.2 | 773 |
| 12 | 1 | 3.2 | 826 |
| 39 | 1 | 2.9 | 762 |

Seeds 2, 6, 7, 12 and 39 took 5-13 s on the base, because 3-6 margins were seated and thrown away. Every stage after the
homesteads also ran on all eight seeds (`FULL=1`) without a refusal.

The back-to-back legs over the sixteen seeds at 10, 15, 20 and 40 households are R6.

## R6 - Round 5 against the engine, sixteen seeds (observed 2026-10-02, method: prototype.py, `ROUTE_STEP=12 GROW=house`, base then grow per household size, one process each, sequential)

At 40 households, homesteads stage seconds (margins):

| seed | base | grow |
|---|---|---|
| 1 | 2.39 (1) | 2.77 (1) |
| 2 | 8.67 (3) | 1.58 (1) |
| 3 | 3.74 (1) | 5.32 (1) |
| 4 | 3.16 (1) | 4.14 (1) |
| 5 | 2.52 (1) | 2.91 (1) |
| 6 | 13.61 (4) | 2.03 (1) |
| 7 | 6.40 (2) | 4.10 (1) |
| 8 | 6.61 (1) | 10.01 (2) |
| 9 | 3.80 (1) | 2.20 (1) |
| 10 | 3.69 (1) | 3.33 (1) |
| 11 | 2.67 (1) | 2.79 (1) |
| 12 | 17.62 (6) | 3.07 (1) |
| 13 | 3.83 (1) | 2.01 (1) |
| 25 | 4.14 (1) | 2.02 (1) |
| 39 | 9.91 (3) | 2.79 (1) |
| 47 | 3.64 (1) | 2.33 (1) |
| **sum** | **96.4** | **53.4** |

- At 40 households every seed seats every household under both methods. The grower uses the first margin on 15 of 16 seeds;
  the base uses it on 11.
- At 20 households the sums are 17.8 s for the base and 16.6 s for the grower.
- The legs at 10 and 15 households ran under uneven load: seed 13 at 10 households measured 1.91 s in the leg and 0.58 s alone.
  Those two sizes are re-measured alternating (R7).
