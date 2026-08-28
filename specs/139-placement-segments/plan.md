# Implementation Plan: Placement Measures Against a Few Segments

**Branch**: none (`SPECIFY_FEATURE=139-placement-segments`) | **Date**: 2026-08-28 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 3)

## Summary

`_geom/primitives.py` gains `simplify_ring` (Douglas-Peucker on a closed ring), `ring_offset` (a mitered
offset ring), `keepout_ring` (chords pushed out by the covered shape's MEASURED reach) and `facing_chains`
+ `chain_violated` (the open chains on the house side, each chord carrying its outward normal; a seat is
judged by sign and by the rule's gap). The dike's placement keep-out becomes the crest's chords pushed
out to the band's reach (`land/dikes.py`, recorded as `dikes[].keepout`); the field tests in placement
(`rolling/fit.py::_field_chains`, `_field_blocks_point/_rect`, `_field_within`; `houses.py`) measure the
chains when `Settlement.field_face` is set (hamletgen's `stage_seat` sets it) and a simplified ring when
not; `finish()` records `fields[].keepout_chains` (or `keepout`); `houses_clear_of_paddies` and
`structures_clear_of_dike` measure the recorded chords. Maps move; the reference and the live pool are
regenerated and reviewed.

## Constitution Check

- I/II/III/IV/V/VII/VIII/IX: N/A. VI: tests per change, `make done`, `settlement-review` on every changed
  map. X: ruff/mypy/100% on the touched modules; red-green containment tests. XII: a DEVIATION - the
  setback is measured from the chords (up to the tolerance farther than the outline) - recorded in
  `research.md` and at the point of change; nothing historical changes. XIII: baseline = feature 138's
  manifests; byte identity is NOT the bar here (the GM's ruling); the bar is every regenerated map green
  at the gate and reviewed. XIV: defects found are tasks (the mypy crash on a dynamic attribute; the
  chord tolerance's effect on the lane web).

## Design decisions

1. Tolerance 3 px for fields (research R3: at 4-8 px the reference's re-seated houses broke its lane web -
   `lanes_bend_like_paths` / `lanes_form_one_network` - which is a lane-web fragility, recorded for
   feature 140's audit, not a chord problem; 3 px passes and still gives under ten vertices).
2. The dike keeps a closed ring (round-2 adjudication: a ring dike's houses stand inside it).
3. The far sides of a field are carried by `_hard_clear` (crop plots), as the spec says.
