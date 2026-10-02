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
- Offers under grow at 40 households, by seed: 1: 757; 2: 254; 3: 1,568; 4: 1,425; 5: 702; 6: 479; 7: 773; 8: 3,427; 9: 474;
  10: 764; 11: 1,223; 12: 826; 13: 224; 25: 567; 39: 762; 47: 506. That is 224-3,427 a seed, or 5.6-85.7 offers per house kept.
- At 20 households the sums are 17.8 s for the base and 16.6 s for the grower.
- The legs at 10 and 15 households ran under uneven load: seed 13 at 10 households measured 1.91 s in the leg and 0.58 s alone.
  Those two sizes are re-measured alternating (R7).

## R7 - 10 and 15 households, alternating (observed 2026-10-02, method: prototype.py, base and grow alternated per seed, two runs each, the faster kept)

| households | base sum | grow sum | seeds faster under grow | margins |
|---|---|---|---|---|
| 10 | 9.08 s | 7.54 s | 11 of 16 (seed 5: 1.08 -> 0.52 s) | the first on every seed, under both |
| 15 | 16.56 s | 13.73 s | 13 of 16 (seed 4: 2.35 -> 1.56 s) | the first on every seed, under both |

**The verdict, by US1's GO rule: GO at every size.** The grower is faster in sum at 10, 15, 20 and 40 households (R6, R7), and
it seats every household on every seed the engine seats.

**What it misses.**
- SC-003, at most 5 offers per house kept. Most seeds offer 5-35 per house at 40 households, and seed 8 takes two margins.
- SC-002, under 4 s on every seed at 40 households. Seeds 3, 4, 7 and 8 take 4.1-10.0 s.

Both misses are carried to the engine build, where the levels and the router's breadth can be tuned.

## R8 - The plan review's footprint (observed 2026-10-02, method: prototype.py, base and grow alternated per seed, one run each, under load 5-8)

The footprint the plan review asked for (plan D1):
- the PATH OUT: the gap between two footprints is a corridor's whole strip plus 2 px, where it was 6 px;
- the beds' sun as well as the yard's, the south reach being the farther of the yard's and the beds' south edges plus
  `SUN_CORRIDOR_FT` + 2 ft;
- the new household's reach taken from the LARGEST homestead the roll can take (`_bundle_envelope` at `_house_max`), where it
  was the first house's;
- every routed path held to `leaves_its_yard`.

| households | base sum | grow sum | margins under grow |
|---|---|---|---|
| 40 | 138.9 s | 93.9 s | the first on 15 of 16 seeds; seed 8 on the second |
| 15 | 25.2 s | 18.9 s | the first on every seed |

- Every seed seats every household under both methods. The load made both methods' times higher than in R6 and R7, but each
  pair ran back to back.
- **Still GO.** The wider spacing costs offers: seed 1 offers 1,394 for 40 houses, where it offered 757 in R6. So SC-003 is
  missed by more than before.

## R9 - Each seat settled on the household's own envelope (observed 2026-10-02, method: `reach_check.py`, the clone's engine, reference spec at 40 households, seeds 1, 3, 4, 8, 13 and 25)

**The check.** For each house the growth seated, the drawn homestead's reach is compared with the reach its seat was spaced
for. The spaced-for reach is `household_reach`, asked at the seat offered, before the placer ran.

**Three forms, compared.**

| reach the seat was spaced for | placements exceeding it | worst excess (w, e, n, s) |
|---|---|---|
| the largest house, no household parts (the plan review's round-3 harness) | 240 of 302 | 8.3, 7.3, 35.9, 26.3 px |
| the largest house, with the household's parts | 33 of 272 | -0.4, -0.4, 21.1, 14.9 px |
| the household's OWN lot: its house, kura and parts | 12 of 234 | 5.0, 0.0, 3.6, 5.5 px |
| ...settled when OFFERED, for the household seated next (R10) | 5 of 271, all moved | 0.7, 0.0, 2.5, 2.3 px |
| ...and the grown seat EXACT, no computed move (R10, the final engine) | **0 of 301** (none moved) | 0, 0, 0, 0 |

- **Why the largest house bounds nothing.** A homestead's fixtures (the manure heap, the privy, the woodpile, the persimmon)
  are sought round its own walls. A larger house moves them, so the largest house's layout does not bound a smaller
  household's layout.
- **On the final engine** (R10: settled when offered, the gap on the parting axis, the grown seat exact), no placement
  exceeds the reach its seat was spaced for. Measured by `separation_check.py` (the plan review's harness): no house's drawn
  envelope comes closer to its source's footprint than the gap. The closest is 19.4 px against the 16 px gap, over 301
  grown placements.
- **The 12 that exceeded under the earlier form.** All are among the 30 placements the placer MOVED: its one computed move off a single
  overlapping neighbor (feature 227), after which the homestead is turned at its new spot. None of the 204 unmoved placements
  exceeds its seat's reach. So every seat the growth offers clears the standing footprints by the household's own envelope
  there (FR-004). The placer's existing move then carries a few households up to 5.5 px, away from the neighbor they would
  overlap.

## R10 - The engine build, back to back (observed 2026-10-02, method: prototype.py's `base` mode, run with ROOT set to the base worktree (`/tmp/base308`, HEAD before the engine change) and then to the clone, alternated per seed, one run each, under load 4-8)

**The final engine's changes.** Each was measured on the way to the final engine. Earlier runs on half-changed engines are
discarded.
- **A seat is settled when it is offered** (`growth.py`), not when it is queued. On seed 8 at 15 households, 448 seats were
  queued and 194 offered; settling each as queued cost 1.27 s of a 2.6 s seating.
- **Each settle starts from where the last ended**: the union of the first guess and the reach the last settle found. It
  took 2.8 envelope rolls a seat before. Seeds 5, 7, 9 and 47 at 15 households went 1.06-1.32 s -> 0.63-0.64 s.
- **The route is asked last** (`access.ROUTE_LATER`). The seat's own question takes a route as possible, and the search runs
  only after the parts' cheap refusals.
- **The gap is on the axis that parts the two homesteads** (`seat_toward`). A unit test found that a gap added along a
  slanted bearing parted them by 15.45 of 16 px at 15 degrees.
- **The placer's one computed move may not carry a grown seat nearer its source than the gap** (`keeps_its_distance`, read
  by `_place_bundle_nucleated` as `_grown_keep`).
  - On the engine before it, the move carried one house 2.6 px from its source (`separation_check.py`, seed 8).
  - Making a grown seat exact instead, with no move at all, was measured and withdrawn: 101.4 / 79.0 s base against 80.4 s
    clone at 40 households, with seed 4 on its third margin. The move is needed for capacity, and only the moves toward the
    source are refused.

**The final engine** (`separation_check.py` and `reach_check.py`, seeds 1, 3, 4, 8, 13 and 25 at 40 households):
- 271 grown placements, 19 of them moved.
- None comes closer to its source's footprint than the gap: the closest unmoved one is 17.7 px, the closest moved one 23.6 px.

**Timing, homesteads stage seconds:**

| households | base sum | clone sum | first margin (base / clone) | every household seated |
|---|---|---|---|---|
| 15 | 17.5 | 15.6 | 16 / 16 | yes |
| 40 | 101.4 | 84.8 | 11 / 12 | yes |

**At 40 households, by seed (base -> clone, margins):** 1: 3.39 -> 2.65; 2: 12.90 (3) -> 2.21; 3: 4.68 -> 4.43; 4: 3.19 ->
3.48; 5: 2.49 -> 3.38; 6: 14.55 (4) -> 10.62 (2); 7: 6.60 (2) -> 4.38; 8: 4.53 -> 10.83 (2); 9: 5.07 -> 8.41 (2); 10: 3.34 ->
5.66; 11: 2.84 -> 3.47; 12: 16.42 (6) -> 8.34 (2); 13: 2.55 -> 6.09; 25: 4.23 -> 2.78; 39: 10.75 (3) -> 3.07; 47: 3.87 -> 4.97.

**Offers at 40 households:** 230-2,483 a seed under the clone, 5.8-62 per house kept, against 383-5,927 under the base.

**The session's goals.**
- SC-002 (under 4 s on every seed at 40 households) is missed on eight seeds: 3, 6, 7, 8, 9, 10, 13 and 47, at 4.38-10.83 s.
- SC-003 (at most 5 offers a house kept, at most two margins) is missed on offers (5.8-62). It is met on margins: no seed
  needs a third.
- Both misses are raised with the GM, with every round's numbers here (FR-002).
