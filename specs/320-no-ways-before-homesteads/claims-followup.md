# Feature 320: pre-existing drifts its record edits surfaced

Load this file when: picking up the pre-existing drifts feature 320's record edits surfaced.

Each was found by impl-drift once page 0081 changed (and the claims of the units this feature touched were judged); feature
320 did not change the value or the behavior. Settling any of them means recording a figure on a record page (0081 sits at
its size cap) or changing the code, so each is left for its own feature, beside feature 318's list
(`specs/318-grow-outward-no-restart/claims-followup.md`). The claims gate counts them as introduced; they land with
CLAIMS_OK naming this file.

- `l7r/diagram/hamletgen/ways/clearance.py::_clear_touch#junction link margin` (MISLABELED): the 4 ft link margin departs
  from the page's "A lane keeps 7 ft clear of a garden fence"; a DEVIATION to record on 0081's drawing page
- `l7r/diagram/hamletgen/ways/clearance.py::may_write#no nearer the fabric` (MISLABELED): half the width + 2 ft, at least
  4 ft - the same departure; a DEVIATION to record on 0081
- `l7r/diagram/hamletgen/ways/law.py::fouls_fabric#foul margin` (MISLABELED): the law's 4 ft (`_TOUCH_GAP`) off another
  household's yard or bed; a DEVIATION to record on 0081
- `l7r/diagram/hamletgen/ways/settle.py::fouled_segment#off another household's yard or garden` (MISLABELED): the same 4 ft
- `l7r/diagram/hamletgen/homesteads/stages.py::stage_homesteads#the declared cluster shape` (MISLABELED): the cluster's
  shape is rolled as a knob, where 0031's drawing page says a hamlet "leaves none of these to chance"; record the roll on
  0031 as a DEVIATION, or derive the shape from the dry ground
- `l7r/diagram/hamletgen/ways/track.py::stage_track#polder has no spur` (MISLABELED): 0014's drawing page runs the field
  path to the outer bund; the polder's dropped spur is a DEVIATION to record there
- `l7r/diagram/settlement/rolling/access.py::exit_bearing#track out leaves away from the field` (MISLABELED): 0081 says
  the track out leaves downslope past the wet foot, on the cluster's flank; cite it, and check "away from the field"
  agrees with "downslope"
- `l7r/diagram/hamletgen/homesteads/growth.py::grow_the_margin#nearer the field breaking ties` (MISLABELED): the GM's
  ruling (2026-10-03); the claim vocabulary has no label for a ruling the record does not carry - record the ruling on
  0004's drawing page, or add the label
