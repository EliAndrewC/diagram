# Feature 318: pre-existing drifts its record edits surfaced

Load this file when: picking up the pre-existing drifts feature 318's record edits surfaced.

Each was found by impl-drift once pages 0081, 0029 and 0032 changed; feature 318 did not change the value or behavior. Fixing
any of them changes code or the record's values, so each is left for its own feature. The claims gate counts them as
introduced (their question changed under them); they land with CLAIMS_OK naming this file.

- `l7r/diagram/hamletgen/consts.py::MIN_WEB_GAP#least gap a lane threads` (DRIFTED): `2*7+4` takes a 4 ft tread, which matches none of the page's drawn widths (3, 5 or 6 ft); with a real tread the sum is 17 ft (3 ft footpath) or 19 ft (5 ft lane)
- `l7r/diagram/hamletgen/ways/law.py::needle_ends#a lane meets another as a T` (DRIFTED): NEEDLE_DEG 20 lets a meeting that turns 140-160 degrees through, but the page says "A turn of more than 140 degrees is a hairpin"; the 20 ft leg floor is not on the page either
- `l7r/diagram/hamletgen/ways/smooth.py::_smooth_web#lane pulled taut` (DRIFTED): `if (ln.get("connector") or ln.get("street"))` skips the connector and the streets, where the page says "Every lane is pulled taut like a string"; either pull them taut, or record the exemption on the page
- `l7r/diagram/hamletgen/ways/sweeps.py::_join_orphan_ways#orphan joined to the network` (DRIFTED): `_net_reach(...) <= _LANE_JOIN_FT` counts any way within 30 ft as on the network, but the page has lanes "joined where their treads meet"
- `l7r/diagram/hamletgen/ways/web.py::stage_web#a cut's room` (DRIFTED): MIN_WEB_GAP = 2*7+4 takes a 4 ft tread, and no lane is drawn 4 ft (3 ft footpath, 5 ft spine); the page's room is "7 ft clear of each garden fence, the tread between". Use a drawn tread width
- `l7r/diagram/settlement/_knobs.py::web_cuts#every house within reach of a way` (DRIFTED): lays the fewest cuts that put each house within reach, but the page now lays "each household's way ... out of its dooryard into the gap beside its homestead"
- `l7r/diagram/settlement/rolling/access.py::ACCESS_HALF_FT#corridor room` (DRIFTED): the page says "7 ft clear of each garden fence, the tread between", which is 8.5 ft from the line for a 3 ft tread; the code reserves 7 ft from the line
- `l7r/diagram/settlement/rolling/access.py::parts_clear#path off its own beds and outbuildings` (DRIFTED): the code keeps the tread 0.5 ft off garden beds, but the page says "A lane keeps 7 ft clear of a garden fence"; the code should keep 7 ft, or the page should record an exception for the household's own beds
- `l7r/diagram/settlement/water_ways/lanes.py::LanesMixin.lane#a worn earth track` (DRIFTED): the default worn=False draws "the legacy wide dashed lane", but the page says "never a wide, two-lane road" and "no line down its middle"
