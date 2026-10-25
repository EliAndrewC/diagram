# T106's knots, measured 2026-10-24

All probes ran in detached worktrees, with `settle_knots`' judge instrumented to log every refused gather near the knot and the reason.

## Seed 7 (cohort): mended by D133

Two households' ways (lanes 1 and 10) tee onto the connector 2.2 ft apart, about 20 degrees apart.

What refused each gather:

- the moves: `needle_joins`;
- the 3 ft pass: `households_only` (the connector is at both nodes);
- the tee of lane 1 onto lane 10: it stranded lane 6, a third household's way that met lane 10 and ran 34 ft on to end on the leg the tee cut away;
- the reverse tee: `needle_loops`.

D133 cuts that tail back to its meeting with lane 10 (0081: "a tail of under 40 ft beyond a crossing is cut"). With it, seed 7 is clean and the cohort is 54/54 (`make cohort N=48`).

## Sawada (pool): NOT mended

Lane 11 (a household's way) tees onto lane 6 22.9 ft from where lane 6 tees onto lane 4: two junctions on one lane within the 25 ft reach (`test_pool_261::test_no_lane_ends_knot_short_of_a_join[sawada]`). This is batch 11's Sawada knot of 2026-10-21, the same 22.9 ft.

What refused each gather (`make map GEN=pool/hamlets/sawada/sawada.gen.py` in a worktree):

- lane 11's end moved onto lane 6's end: `fabric` (its last leg crosses a homestead);
- lane 6's end moved onto lane 11's tee: the web loses four households' ways that hang off lane 6's corners;
- a probe bent lane 11's new leg round what stands, 12 offsets either side (`bent_round`'s, applied to a lane-law refusal): every bend `fabric`.

The other forms (`teed_onto`, `teed_back`, `onto_cut_back`, `joiner_first_meeting`) produce nothing for it.

Room (T107's grow_gap +5 and +10 ft, 2026-10-22) was measured on the fence-gap knot, not this one.

## The room sweep (the round arbiter's ruling on ask:t106-sawada-knot), 2026-10-24

Each step ran in a detached worktree with T106's seat turn, D132's flank fix and D133 applied. The checks at each step were `make map GEN=pool/hamlets/sawada/sawada.gen.py`, then `test_pool_261`, then `make cohort N=48`.

| step | Sawada | cohort |
|---|---|---|
| `SEATING_GROUND_FT` and `grow_gap` +5 ft | clean | 53/54 (seed 36: a knot at 22.5 ft) |
| +10 ft | clean | 53/54 (a knot at 18.5 ft) |
| +15 ft | clean | 51/54 (three knots) |
| `HOMESTEAD_GROUND_FT` 117 ft | clean | the reference (Inashiro) refused: `needle_loops` |
| `HOMESTEAD_GROUND_FT` 130 ft | clean | 47/54 (WebRefused, knots, `row_rules`) |

No step within the bounds was clean, so the ruling's route (b) applies:

- **the seat turn: reverted.**
- **the flank fix alone: reverted.** It also re-deals the seats, to 52/54 (seeds 2 and 13 WebRefused, seed 18 knots).
- **D133: lands alone as T138.**
- **T106: set down again.**
