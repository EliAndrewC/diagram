# Implementation Plan: the pool sweep's recorded findings

**Feature**: 152-pool-sweep-findings | **Spec**: [spec.md](spec.md) (FAITHFUL, round 3) | **Date**: 2026-08-29

## Constitution Check

- **VI (verify before done)**: every item carries a before-number already; each gets an after-number by
  the same measurement. The pool is re-rolled and a `settlement-review` pass runs over the changed maps.
- **X (files at human scale)**: no file here approaches 1,000 lines from this work.
- **XII (two supportable answers become a knob)**: two items ARE knobs (copse siting, kosatsuba siting),
  specified as such rather than picked. Cost sized below.
- **XIV (fix defects where you find them)**: this feature IS that principle being paid off.
- **XVIII (a guard owes a test companion)**: no new guard here.

## The order of work, and why

Not the spec's priority order. Two constraints reorder it:

1. **The windbreak first**, because it is the only item whose fix moves canopy on every map, and every
   later re-roll then rides on the corrected belt rather than being measured twice.
2. **The knobs last**, because each owes a map per value and the pool should be settled first.

## Mechanisms - what has already been traced, so the implementer does not re-derive it

**FR-003 windbreak.** `belt_polygon` (`hamletgen/hinterland.py`) already samples ACROSS the wind and
follows the cluster's windward profile - the "offset from the centroid" diagnosis in the sweep was wrong
about the polygon. The defect is downstream, in `homestead_parts.py` around line 881: after seating, a
clump is kept only if `_sign * (pos[_axis] - _inner) >= -(face_margin + clump * 0.9)`. That is a ONE-AXIS
proxy for "off the page" - deeper than the belt's inner face by more than the margin - and it drops
clumps that are demonstrably on the page. Sawada records 83 off-page of which the reviewer measured 38
wholly inside the frame, and `make sun-audit` independently reports only 2 truly off-page. The three maps
that fail SC-002 are exactly the three discarding most of their canopy (Kuwabata 45 undrawn against 47
drawn, Sawada 84/95, Kashikawa 61/99). **Fix**: test the clump against the actual crop box rather than
the single-axis proxy.

**FR-002 privy wind.** `_PRIVY_SEATS = (("back", 0.60), ("gate", 0.25), ("naya", 0.15))` in
`hamletgen/homesteads.py`, rolled by `_roll` and expressed in the HOUSE's local frame. Houses draw at rot
0-4 degrees, so "back" is north on every map, and nothing consults `plan.windward`. **Fix**: after the
roll, reorder the seat preference so a seat whose bearing from the house is within 90 degrees of the
windward vector loses to one that is not. The three seats and their weights stay - the spec forbids
inventing a fourth.

**FR-001 marsh modal.** `interactive/classes.py`, the `_c(key="marsh", ...)` record - its `why`,
`sources` and `entry` fields are what the modal shows. The finding and its seven sources are already in
`research/water.md` and `research/SOURCES.md` from feature 150.

**FR-006 caption.** `pick_caption_seat` (`settlement/structures/fixtures.py`) filters on `_hug` and
`_box_clearance`; `_hug` already computes the ROTATED quad, `_box_clearance` measures only drawn ways.
**Fix**: add a fabric term and a way-side term to the legality filter, keeping satisfice-then-nearest.

**FR-014 jogs.** `make jogs` red on Sawada: 3 sideways steps in 776 rings, largest 12.5 ft, one on the
flooded plot's own edge. Diagnose before fixing - it may be `close_seams` residue rather than a placer.

## Knob cost, which the spec does not size (raised by the review)

`FR-005` (copse: embedded in the belt / threading the houses) and `FR-016` (kosatsuba: busiest frontage /
drawing-water place) are two knobs of two values each. Constitution VI: **a feature adding a knob owes one
map per knob VALUE - four maps, not a cohort.** These ride on existing pool maps by setting the knob on a
map that already rolls each value, so the cost is 4 rolls plus the reading, not 4 new settlements.

## Verification

- Each FR measured before/after by the measurement its finding already used.
- `make maps` to the same standard as before (the pre-existing seed 37 tripwire failure excluded, per the
  spec's Assumptions, which does NOT excuse FR-014).
- A `settlement-review` pass over the changed maps, paired with the gate.
- `make done` green; the push takes the LOCAL-GATED route.
