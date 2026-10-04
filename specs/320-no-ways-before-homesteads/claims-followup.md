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
- `l7r/diagram/hamletgen/ways/fabric.py::_homestead_polys#a path leaves its own yard` (MISLABELED): 0081 lets a way leave its
  dooryard round its own beds and fixtures; the exemption of the owner's gardens and sheds as walls to its own path departs from
  it - keep only the yard's exemption, or record a DEVIATION; and the village groves and the commons kept off are unclaimed
- `l7r/diagram/hamletgen/ways/track.py::stage_track#spur bow` (DRIFTED): the field spur's 14 ft bow along the seat axis; 0081
  pulls every lane taut - drop the bow or record it

## Open from the village-lane glyph check (round 4 PASS; questionable, no norm broken)

- Jogs where a household's way meets another at a T (Inashiro: lane 4 onto lane 2's corner by the notice board, and three
  more): page 0081's zigzag rule ("two turns of more than 50 degrees within 40 ft ... pulled straight") names only lanes met
  end to end. Either the page extends it across a T and the gap pass pulls a way's last legs taut through the T, or it is
  left as drawn.
- The route from the field to the track changes width (field way, households' ways, track): with the 5 ft strip gone, the
  through-route page 0081 calls one route is drawn at the households' footpath width between them.
