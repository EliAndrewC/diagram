# Implementation Plan: the head race's mouth does not read as the river (355)

**Spec**: `spec.md`

## Summary

The sketch's order: first the judgment (FR-000), then - only if the race reads as the river - the taper (FR-001), the race's
width untouched (FR-002), nothing else moved (FR-003), 358's copy marked done (FR-004, already in 358's spec).

## Decisions

- **D1 - the judgment (FR-000)**: a `glyph-check` of the head race at its mouth on Sawada, on the map as main draws it today
  (the pool SVG rendered at 9 px per map unit, 260 x 220 units round the tap at (4575, 3455)), dispatched with that crop and
  the SVG; its verdict is the gate. If it reads the race as the river (or as liable to be confused with it), D2 is built; if not,
  355 closes with the verdict recorded and no code lands.
- **D2 - the taper (FR-001, FR-002)**: `hamletgen/water/brook.py` `open_race_mouth`, after it carries the race's first stroke back
  to the tap, appends to the race's bed `race_taper`: the race's own polyline cut at `s.px(RACE_TAPER_FT)` (30 ft, the entry's
  figure), stroked at the race's own width with a `linearGradient` (userSpaceOnUse, from the tap to the cut) from the brook's bed
  hue `#9CB4C8` to `SUPPLY_HUE`. It paints with the race's bed, so the brook (moved to paint after the race by the same function)
  still covers the mouth; it ends in the race's own color, so it joins the bed beneath without a seam. The gradient id is the
  entry's index in `s.late_water` (deterministic). A `CONVENTION` research claim beside it.
- **D3 - tests and verification**: unit tests of `race_taper` (cut inside a segment, a race shorter than the taper, a single
  point) and of `open_race_mouth` appending it; the pool hamlets re-rolled by the gate; a `glyph-check` of the redrawn mouth
  (`glyph-redrawn: head race on sawada`) after the gate.
