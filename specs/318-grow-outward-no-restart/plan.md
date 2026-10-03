# Implementation Plan: Grow outward, never restart

**Branch**: none (main, in the clone) | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

## Summary

The nucleated seating stops throwing seated houses away: one margin is seated, its cluster grows outward until every household
stands, and nothing refuses a seat for its distance from the field. The take-back machinery goes (the margin ladder's take-back,
the rescue, feature 317's withheld re-seat and early stop, the 12:1 refusal, the passage re-lay), the 700 ft field reach goes
with every use, and the growth tries the seat nearest the field first among each level's offers.

## Performance bookends (constitution VI)

`make perf LABEL=318-start` at main before the first engine edit, `LABEL=318-end` on the engine as it lands, alternated.
Expected: no thrown-away seating on seed 47 at 40 households (feature 317 R10: 8.2 s against main's 4.0 at 317's landing).

## Decisions

**D1 - No take-back (FR-001, FR-004, FR-005).** `stages.seat_every_household` seats the chosen margin once. The ladder is kept
only for a margin that seats NO house - `_seat_households` returns before seating any (no lawful exit bearing, no lawful field
corridor) - and only then is the next margin tried; with no house standing nothing is taken back. A margin that seats some but
not all is refused (`SiteRefused`, naming the households seated and the margin). Removed: `capacity.rescue_the_margin` and its
constants, `stages.seat_the_margin`, `_passage_withheld`, `passage.passages_spent` and growth's early stop before the widest
level, the 12:1 refusal (`drawn_in_band` asked as a refusal; the declared shape still recorded, `declare_cluster_shape`).

**D2 - The growth keeps widening (FR-002).** `growth.grow_the_margin` queues and offers seats with no radius test: the
`d <= bound` filter on queued seats and the `> bound` refusal of a settled seat go. Where `GROW_LEVELS` runs dry the growth keeps
widening: further levels at 16 directions with rings stepping out by half the least distance each, until a level queues no new
seat on the canvas (every ring point off it or already seen) - the termination. AMENDED with D4 (research R1): the table is one
level, every direction and ring of the old three offered at once. The old radius stays only where it sizes
something else (the exit strip's length, the front row's reach on the other forms, the seat lattice's band).

**D3 - The field reach removed (FR-003, SC-002).** `fit.FIELD_REACH_FT` and `within_field_reach` deleted, with their four
calls (`growth.seat_refused`, `place._place_bundle_nucleated`, `capacity.free_seats`, `fit._parts_fit`'s reach memo). The
growth's seat region window (`region.seat_window`), the free-ground grid's box (`boundary.free_ground_bounds`) and
`capacity.free_seats`' search box are the canvas; their docstrings already say the box bounds the cost, never the answer -
the grid's cost on the whole canvas measured at the bookends. `site_boundary.window` records the canvas box `(x0, y0, x1, y1)` - sized from the map's own extent, FR-003's words - and the
placement-stages plate draws it as a box (no radius, no reach);
the placement-stages legend and the tests pinning 700 updated. `ways/law.py`'s own `FIELD_REACH_FT` (a way reaching the field)
untouched.

**D4 - Nearest the field first (FR-003a, SC-002a), AMENDED 2026-10-03 on measurement (research R1).** The growth's heap is keyed
by the seat's distance to the field's facing chains (`chain_distance` against `s._site_chains`, the same chains the reach read),
ties broken by the distance from the margin's center; every seat offered is one adjacent to a standing house, and of those the
nearest the field is tried first. A unit test pins the order (SC-002a).

The level structure as first planned ("unchanged": 8 directions, then 12, then 16) was measured and FAILED FR-003a's own clause,
"the cluster stays as tight as its ground allows": with no radius a level never runs dry, so the eight sparse directions of the
first level served the whole seating, the near-field seats they missed were never offered, and the cluster crept away from the
field - mean house-to-field distance on the reference at 40 households (seeds 4, 25, 39, 47) 637, 400, 585, 442 ft against main's
443, 421, 429, 416. So `GROW_LEVELS` is ONE level, sixteen directions at rings 1.0, 1.5 and 2.0 of the least distance offered at
once - every adjacent option, the nearest the field taken: 384, 367, 394, 355 ft, every farthest house under 610 ft. Priced: every
ring in quarters 1.0-2.0 (405, 361, 386, 352 ft, homestead stage 44.6 s for the four), twelve directions (429, 362, 421, 374 ft,
29.6 s); chosen sixteen at three rings (31.2 s against main's 21.5; 32.7 s once the direction jitter is scaled with the step,
`grow_jitter`, so sixteen directions' neighbors never cross). The cost - near-field seats are more often hemmed in and refused
after the envelope and the corridor search - is a perf band the bookends measure (FR-010).

**D5 - The passage recheck without the re-lay (FR-001).** `passage.recheck_passages` keeps only its first arm: a household
reached across a yard whose drawn layout finds a straight or round-the-gable corridor on the finished seating is given it and
its passage ended, in place. `relay`, the stored layouts (`_passage_seats`' layouts, `_tight_of["layouts"]`) and
`meta.passage_unfit` go.

**D6 - The quarter-built figure reported (FR-007).** Page 0032's rule binds villages, not hamlets ("A hamlet is rightly loose
and is not held to it"), and no hamlet code enforces it; the seating records it for every nucleated map
(`meta.built_share`: the area of houses, yards, gardens and homestead groves inside the houses' outline - the convex hull of the
homestead boxes - over the outline's area), refusing nothing.

**D7 - The record (FR-008).** 0029's drawing page: of the seats the cluster offers at its edge the nearest the field is taken
first; no distance from the field is a limit (the GM's ruling, canon). 0032's: the 700 ft is no limit (its back-row sentence
kept as what the drawn villages showed), and the maps report the built share. 0081's: a passage the finished map makes
unnecessary (its drawn layout given a way of its own) is ended in place; no re-lay. 0004 already states the rule. Every claim
citing the reach goes with its code; claims of changed units re-checked by impl-drift.

**D8 - Occasions.** placement-changed: farmhouse on the pool's nucleated maps (Inashiro, Kuwabata, Sawada) - the seating's
order and limits change; village lane where the houses move.

## Verification

Unit tests for D1-D6 (the no-take-back test SC-001 counts houses during the seating; SC-002a's order; SC-003's constructed
refusal); `make done`; the cohort (`make cohort N=24`) and the pool against main; seed 18 and the 40-household bookend seeds on
their first margin (SC-002); the bookends (FR-010) with the spread (farthest house from the first and from the field, built
share) in research.md.

## Constitution Check

XII: every decision labeled (D2-D4 canon, the GM's rulings; D6 calibration reported). XIII/XIV: cohort and pool against main.
XVI: the literal request - every take-back removed, the reach removed with every use.
