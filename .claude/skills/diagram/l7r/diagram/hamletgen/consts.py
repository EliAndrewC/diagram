"""The researched constants that size a hamlet, each with the reasoning that fixed it.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
Research: aliases and plumbing - NONE: type aliases, re-exports, unit tables, and every constant here with no claim of its own
"""

from __future__ import annotations

# Pt, Poly and SQ_FT_PER_ACRE moved to the shared sitegen package (feature 119) - they were
# never about hamlets. Re-exported here so `from .consts import Poly, Pt` keeps working inside
# this package and hamletgen's public surface is unchanged.
# The `X as X` form is not stylistic: mypy --strict turns on --no-implicit-reexport, so a
# plain `from ... import X` would NOT re-export X and every `from .consts import Poly, Pt`
# in this package would fail to type-check.
from typing import Any

from l7r.diagram.sitegen.types import SQ_FT_PER_ACRE as SQ_FT_PER_ACRE  # noqa: F401
from l7r.diagram.sitegen.types import Poly as Poly  # noqa: F401
from l7r.diagram.sitegen.types import Pt as Pt  # noqa: F401

# The water constants live in consts_water.py (feature 316, the 1,000-line bar) and are re-exported here by name.
from .consts_water import BROOK_BEND_WIDTHS as BROOK_BEND_WIDTHS
from .consts_water import BROOK_CROSSING_COST_FT as BROOK_CROSSING_COST_FT
from .consts_water import BROOK_FAN_TRIM as BROOK_FAN_TRIM
from .consts_water import BROOK_FLANKS as BROOK_FLANKS
from .consts_water import BROOK_FRAME_MARGIN as BROOK_FRAME_MARGIN
from .consts_water import BROOK_MAX_TURN_DEG as BROOK_MAX_TURN_DEG
from .consts_water import BROOK_SKIRT as BROOK_SKIRT
from .consts_water import BROOK_SLEW as BROOK_SLEW
from .consts_water import BROOK_TAP_RUN as BROOK_TAP_RUN
from .consts_water import BROOK_WANDER as BROOK_WANDER
from .consts_water import BROOK_WANDER_STEP as BROOK_WANDER_STEP
from .consts_water import FORD_BEND_DEG as FORD_BEND_DEG
from .consts_water import FORD_HALF as FORD_HALF
from .consts_water import FORD_SPACING as FORD_SPACING
from .consts_water import HEAD_RACE_LEAD as HEAD_RACE_LEAD
from .consts_water import INTAKE_FORMS as INTAKE_FORMS
from .consts_water import OFFTAKE_DEG as OFFTAKE_DEG
from .consts_water import OFFTAKE_LADDER as OFFTAKE_LADDER
from .consts_water import POND_SETBACK_LIMIT as POND_SETBACK_LIMIT
from .consts_water import SINKS as SINKS
from .consts_water import WEIR_HALF_FT as WEIR_HALF_FT
from .consts_water import WEIR_SKEW_DEG as WEIR_SKEW_DEG
from .consts_water import WEIR_THICK_FT as WEIR_THICK_FT

# ---- researched constants, each with the reasoning that fixed it -------------------------------

# GROSS PADDY PER HOUSEHOLD. Ikegami's generator states the tier's own figure: "~15 households x
# ~1.3 acres gross = ~20 acres of paddy". It is GROSS (the household's whole holding, bunds and
# access included), not the net planted area, which is why it sits above a bare subsistence ration.
# Recorded here because this is the one number that sizes the entire map: the field area sets the
# canvas, the canvas sets the crop, and the crop sets how the place reads.
#
# WORTH KNOWING, and the reason this module SOLVES for the figure instead of passing a fall length:
# Ikegami aims at ~20 acres in its docstring and its own closing line reports 15.3 - a 24% miss, and
# nothing catches it, because `field_fall` is a PIXEL length hand-tuned until the fan looked right
# and no check reads acreage. A script can close that loop (see `fit_field`), which is the clearest
# single case in this experiment of scripted beating authored on PRECISION rather than speed.
GROSS_ACRES_PER_HOUSEHOLD = 1.3
"""Research: paddy per household - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html: 1.3 acres gross"""


# LANE CLEARANCE - the no-build corridor a lane reserves, in px.
#
# This used to be 48 rather than the authored maps' 32, as a WORKAROUND: `_near_corridor` tests a
# candidate's CENTER against the corridor and the placer passed the farmhouse's BASE rect (46 x 28
# ft), while a homestead's wealth variation renders the house up to ~1.33x that - so at 32 a
# well-off farmhouse's drawn corner ended 2.4 px from a connector track's centerline with its center
# a legal 34 px off, and `houses_clear_of_lanes` measures the DRAWN corners.
#
# THE WORKAROUND IS OVER (feature 121, 2026-08-17), and this is no longer what keeps a house off a
# lane. The bundle path now tests the rect it will DRAW against the lane's drawn tread
# (`_house_on_a_tread`), and the gate reads the same raked corners (`rect_corners`), so a seat that
# would put a wall on the trodden surface is refused on its own geometry whatever this number says.
# CORRECTNESS LIVES IN THE TREAD TEST; this constant is now only a PLACEMENT preference - how far
# out seats are offered, so houses FRONT the lane instead of crowding it.
#
# THE OLD DIAGNOSIS WAS WRONG, so do not restore it from an old copy of this comment. It said the
# drawn house "is offset from the seed point AND scaled by the wealth/length jitter - so the rect
# the placer clears is neither the size nor the position of the rect the map draws." Measured across
# pool/hamlets/inashiro/inashiro.json: position and size match the drawn record to 0.0000 px. The divergence
# was the RAKE (`_house_rot`, +/-5 deg, up to 2.56 px of corner bulge) - and separately, 32 was the
# PLAIN house's arithmetic while the nucleated path jitters a minka's length to 1.35x, because a
# minka grew by adding bays along the ridge.
#
# DERIVED, at 1 ft/px: longest drawn minka 62.1 x 30.8 ft -> half-diagonal 34.7, plus the lane's own
# half-tread (a ~10 ft tread -> 5), = 39.7 -> 40. Measured on the 24-seed cohort: 22/24 at 40, with
# the same two pre-existing failures on the same two seeds as the 48 baseline - so the 8 ft this
# returns to the cluster costs nothing. (At 32 the cohort drops to 21/24: the lane checks stay
# green, but a corridor that tight re-packs the cluster into gardens and crops.)
LANE_CLEARANCE = 40.0
"""Research: fronting lane's corridor - UNRESEARCHED: a 40 ft no-build corridor about a fronting lane, where the page says only that farmsteads front a lane and nothing is built on it"""

# HOW FAR ALONG THE FIELD OUTLINE THE CLUSTER ACTUALLY REACHES, as a multiple of the seat band's own
# lateral half-extent. ONE definition, read by `front_row` (which samples outline vertices out to
# this reach) and by `stage_seat` (which sizes the seat band). The lane skeleton is no longer sized
# over it at all - feature 128 moved every lane after the houses, so the skeleton is fitted to where
# they actually landed rather than to this predicted band.
#
# It is one definition because the two being separate numbers WAS the defect. `front_row` had 1.6
# inline and the skeleton was sized on the bare `lat`, so the lanes huddled in the middle of a
# cluster 1.6x longer than they were, and the houses at the ends had nothing near them. Measured on
# the four pool hamlets before the fix: every one of the 25 unserved farmhouses sat at a large
# offset along the cluster's LONG axis (up to 478 ft), and none at a large offset across it - a
# lateral coverage failure, not the depth failure the ledger had assumed. See
# specs/123-lane-web-and-cluster-shape/research.md R2.
CLUSTER_SPAN_FACTOR = 1.6
"""Research: cluster's reach along the field edge - UNRESEARCHED: 1.6 of the band's half-extent"""

CLUSTER_ROW_SPAN = {"round": 1.2, "crescent": 1.6, "elongated": 2.6, "split": 1.6}
"""How far the FRONT ROW wraps along the field outline, per rolled `cluster_shape`, as a multiple of
the seat band's own half-length.

The band aspect (`CLUSTER_BAND_ASPECT`) was not enough on its own, and the measurement says why:
with the band alone, Kashikawa declared `elongated` and DREW 1.2:1, because the row wraps 1.6x past
the band in every direction and the lane-frontage pass then fills behind it. A declaration that does
not describe the drawing is the exact failure the old stamping guard existed to prevent, so binding
the shape at the band and declaring it unconditionally without this would have reintroduced it in a
worse form - the knob would read as honored on every map while changing almost nothing.

So the shape governs the ROW's reach too: a round hamlet keeps its row short and packs depth behind
it, an elongated one strings along the margin. Crescent keeps 1.6, the value every map used before,
so a crescent map is unchanged. `ways.py` keeps reading the plain `CLUSTER_SPAN_FACTOR` for the lane
frame - that frame spans the houses that actually landed, which is a different question.

Research: front row's reach per shape - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: 1.2 round to 2.6 elongated"""

# THE NO-BUILD CORRIDOR OF A WEB LANE, in feet - deliberately much tighter than LANE_CLEARANCE.
#
# LANE_CLEARANCE (40) is derived for a lane the homesteads FRONT: it is the drawn minka's
# half-diagonal plus the lane's own half-tread, so the steading clears the way it faces. A web lane
# is the other kind: the research describes the lateral ones as "colonized as semi private space by
# the adjoining house", which is a way people build right up against. Holding 40 ft off both verges
# of every web lane reserved the middle of the cluster and pushed the houses out - measured on the
# four pool hamlets, the long axis grew 51%, 58%, 15% and 97%. This is the lane's own half-tread
# plus a hand's breadth: enough that a wall is not drawn ON the tread, and no more.
WEB_CLEARANCE = 28.0
"""Research: web lane's no-build corridor - UNRESEARCHED: 28 ft, byres and sheds kept off the tread; 0081 gives no corridor"""

# THE LEAST ROOM BETWEEN TWO STEADINGS A WEB LANE WILL THREAD, in feet. `web_cuts` only cuts where a
# gap is at least this wide, so a lane is placed where one can actually be walked rather than driven
# through a wall and left to the clipper to sort out. Three feet of tread plus a hand's breadth on
# each side, doubled for the two neighbors: a person with a carrying pole, which is the traffic these
# lanes were for (see research/contents.json#ways - the vehicle to picture is the wheelbarrow and the
# shoulder-pole porter, never a cart).
#
# NOTE ON WEB_CLEARANCE ABOVE, because the number moved twice and the reason changed with it. While
# the web was laid BEFORE the houses, a wide corridor was ruinous - it reserved the middle of the
# cluster and the placer shoved the houses out, growing the four pool hamlets' long axes by 15-97%.
# Laid AFTER them (see `stage_web`) the corridor no longer competes with a single farmhouse, because
# every farmhouse is already seated; all it still governs is what `stage_appurtenances` puts down
# NEXT - byres, sheds, wells. At 12 those were landing on the tread and `features_do_not_overlap`
# fired on 7 of 24 cohort seeds. 28 holds a byre off the way while staying well under the 40 ft a
# fronting lane reserves, which is the distinction the two constants exist to keep.

# HOW FAR A WEB LANE'S CENTERLINE STAYS OFF THE SETTLEMENT'S OWN FABRIC, in feet.
#
# It has to clear the overlap MATRIX, not just the drawing, and the matrix is less forgiving than it
# looks: it sizes EVERY lane at 6 ft wide whatever the record says (`_MX_LINE_W`), so a 3 px web
# tread is judged as a 3 ft half-width; and a dooryard garden records both a `poly` and a rect, with
# the rect running up to ~2.3 ft proud of the poly. At 6 ft of margin that leaves well under a foot
# of true clearance, and `features_do_not_overlap` fired on `lanes` vs `gardens` across the cohort.
# It was 9 while the fabric list carried only a garden's `poly`. Now that `_homestead_polys` records
# the RECT as well, the discrepancy is covered by the geometry instead of by the margin, and 9 was
# doing a second job it should not have been: `MIN_WEB_GAP` says a 16 ft gap between two steadings is
# walkable, while a 9 ft margin needs 18 - so the cut solver offered gaps the router could not
# thread, and a house sat 296 ft from any way with no route found at all. The two are now derived
# from each other and cannot contradict again.
WEB_FABRIC_GAP = 7.0
"""Research: web lane off a plot - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from the lane's line, so a tread's edge may pass 5.5 ft off a fence"""

# HOW FAR A TRACK KEEPS OFF A STEADING, as opposed to how far the WEB does (feature 128).
#
# `WEB_FABRIC_GAP` is 7 px because an alley IS the residual gap between two plots - it threads
# between them and is barely wider than the space it occupies. A connector or a field spur is a
# different animal: it runs PAST the settlement rather than through it, and it has no business
# hugging a wall.
#
# 16 px is derived, not chosen. The gate counts a house-on-corridor hit at
# `seg_dist(house_center, lane) < 14` (`houses_off_corridors`), and a clip measures to the FOOTPRINT
# rather than the center - so a 7 px clip left the center 14-17 px out and 3 of the reference
# hamlet's 15 houses failed. 16 px to the footprint puts the center comfortably past 14 with the
# margin coming from the house's own half-extent.
#
# NOT LARGER, and feature 126 recorded why: it clipped its skeleton arms at 20 px, which demands a
# 40 px clear corridor between two steadings that a packed cluster does not have, so arms were
# clipped out of existence entirely. A track only needs to reach the cluster's edge, not thread it.
TRACK_FABRIC_GAP = 16.0
"""Research: track off a steading - UNRESEARCHED: 16 ft to the footprint, set off the houses_off_corridors check's 14"""

# A FOOTPATH IS NOT A LANE, and it may squeeze where a lane may not. This is the clearance for the
# path from an outlying steading's door to the nearest way - the thing the sources describe as
# "colonized as semi private space by the adjoining house", i.e. the residual room between two
# plots, walked in single file. It still clears the overlap matrix's 3 ft half-tread with room over,
# but it lets a path thread a gap a back lane could not, which is the difference between a house
# being reached and a house being 296 ft from anything with no route at all.
# 4 ft, and the number is doing real work at the margin. The overlap matrix sizes every lane at 6 ft
# wide whatever its record says, so 3 ft is the hard floor and this is 3 plus a hand's breadth; the
# drawn tread is 3 px, so the ink clears a wall by better than two of its own widths. At 5 a hemmed-in
# farmstead on cohort seed 41 had no route to the network at all, at any target - the gaps between
# its neighbors' plots were simply narrower than a lane-and-two-margins. A footpath is the one way on
# the map that is walked in single file, and this is the width that says so.
FOOTPATH_FABRIC_GAP = 4.0
"""Research: footpath off a plot - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 4 ft, single file"""

# HOW FAR A WEB LANE STAYS OFF THE CROP, THE TOE AND THE MARSH, in feet.
#
# The skeleton's arms are clipped at 20, which is right for them: they are 5-6 px cart ways and they
# are laid before anything else, so there is no cost to being generous. A web lane is 3 px and is
# threading ground that is already full, and 20 was not a rule, it was a copied default - the gate's
# own bar is `fields_clear_of_road`, which allows w/2 + 2, i.e. about 3.5 ft for a tread this narrow.
# Measured cost of the copied 20: a farmstead 251 ft from its nearest neighbor had NO route to the
# network at all, not because any single obstacle blocked it but because the crop, the toe and the
# marsh each took 20 ft off the same corridor and closed it between them. 8 keeps better than double
# the gate's bar while leaving a path somewhere to go. It also matches the doctrine: a real farm
# track runs on the baulk between plots, not twenty feet clear of the rice.
WEB_HARD_GAP = 8.0
"""Research: web lane off crop, toe and marsh - research/questions/0081-village-lanes.drawing.html: 8 ft, the lane on the bund"""

# HOW CLOSE TWO WAYS MAY RUN BEFORE A READER SEES ONE WAY DRAWN TWICE, in feet.
#
# This is a LEGIBILITY number, not a clearance: `MIN_WEB_GAP` says what a lane can squeeze through,
# and using it here was a category error that let a back lane share a corridor with the connector -
# median 14.6 ft apart, 91% of its length within 30 ft - without the shadow test firing once. A
# review read the pair as "a long thin scissors with a drafting overlap". 30 ft is a third of a
# bundle pitch: far enough apart that the eye separates them at fit zoom.
WEB_SHADOW_FT = 30.0
"""Research: two ways read apart - CONVENTION: 30 ft at fit zoom"""

MIN_WEB_GAP = 2.0 * WEB_FABRIC_GAP + 4.0  # 18 ft: both neighbors' clearance, plus the tread between them
"""Research: least gap a lane threads - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft clear of each garden fence and a 4 ft tread between, within the page's 3 ft footpath to 5 ft spine; the 2 ft parting is added by `growth.grow_gap`"""

# THE REACH A FARMHOUSE IS ENTITLED TO: every house center must be within this of some drawn way
# (`farmhouses_reach_a_way`). It is BUNDLE_PITCH, deliberately and by reference rather than by
# repetition - the ground one homestead occupies is exactly the distance at which a lane passes your
# own plot or your neighbor's, which is what the sources mean by a lateral "colonized as semi-private
# space by the adjoining house". The same number sets the web's lane spacing, so the requirement and
# the geometry that satisfies it cannot drift apart.
#
# Grounding: research/questions/0081-village-lanes.html, and research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html - a house
# in a nucleated cluster is reached by a way, but for the few reached across a neighbor's land (feature 317), which
# `ways/checks.py` `unreached_houses` counts reached through their neighbor. The previous 90 ft in
# `lanes_reach_something` was flagged in future-work/ as a number nobody had justified; this one is
# derived from a researched constant instead of chosen to make today's maps pass.
WEB_REACH_FT = 100.0  # == BUNDLE_PITCH; asserted in tests rather than imported, since BUNDLE_PITCH is defined below
"""Research: every farmhouse reached by a way - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft, how close counts as serving a house; but the few reached across a neighbor's land"""

WAY_END_REACH_FT = 60.0
"""How near a lane's END must come to another way, a farmhouse or the field before the path is one somebody wore.

ONE NUMBER FOR THE PLACER AND THE CHECK, which is the whole reason it is a constant (feature 227). `_trim_to_service`
pulled a run's ends back to the last point that reached a way within 40 ft or a HOUSE within 90, while
`test_every_lane_end_reaches_something_worth_walking_to` asks 60 of all three - so a lane whose end fell in the 60-90
band was trimmed to a position the gate then failed, and nothing said so until a re-packed cluster put one there
(Inashiro's two skeleton arms, ends 81-97 ft from the nearest house). The trim's own docstring still quoted the older
pair of numbers, which is how the drift survived: the check had been tightened and the placer had not. The bar itself
is the check's - a path exists because somebody had a reason to walk to its end.

Research: a lane end reaches something - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 60 ft"""

STEADING_ARRIVAL_FT = 12.0
"""How near a lane end must stand to a steading's own built ground - house, byre, shed, threshing yard or garden -
to count as having ARRIVED there rather than as stopping in the open (feature 227 D11, 2026-09-12).

WHY A SECOND, MUCH TIGHTER FIGURE rather than measuring the footprint at `WAY_END_REACH_FT`. The end rule asks that
a path reach something worth walking to, and it measures a farmhouse by its CENTER - which is where the house is, not
where a walker arrives. A 46x28 ft farmhouse carries 27 ft of itself between its center and its front corner, so two
straggler footpaths that stop AT a steading's garden fence measured 63 and 76 ft to a center they never go to and read
as treads ending in grass (Kashikawa, Kuwabata). Reading the footprint at 60 ft instead fixes those two and loosens the
rule everywhere else by most of a house: measured the same afternoon, it let three of Inashiro's skeleton arms keep ends
56-60 ft from the nearest wall, which IS a tread stopping in open ground. So arrival is its own clause at its own
distance, and the three 60 ft clauses are untouched.

12 ft is DERIVED from the clip, not chosen. A tread is cut `WEB_FABRIC_GAP` (7 ft) clear of a plot it runs beside, or
`FOOTPATH_FABRIC_GAP` (4) for a footpath, and `clear_runs` walks its candidate in 4 ft steps - so a path that genuinely
reaches a boundary records its last point 7-11 ft off it and cannot record it nearer. Measured: the two straggler ends
at 7.8 and 6.9 ft from the garden they stop at, Inashiro's byre arm at 8.4, against the next-nearest built ground on any
of those three maps at 24 ft. Anything past 12 is a tread that stopped somewhere else.

Research: a lane end arrives at a steading - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of its built ground"""


# How close two drawn treads must come to count as ONE network (feature 166, lifted out of the retired
# `farmhouses_reach_a_way` check, which held it as `_LANE_JOIN`). Its recorded why, carried verbatim from
# the check because it is the reason the number is 40 and not something else: it is the same figure
# `lanes_reach_something` used for "this end has met another way", deliberately - the two rules are about
# the same fact from opposite ends, and letting them disagree would let a lane be connected for one and
# isolated for the other.
LANE_JOIN_FT = 40.0
"""Research: two lanes as one network - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: treads within 40 ft count as one network (the page joins ends within 25 ft)"""

# How far off a lane's centerline a frontage seat is offered. This is a PLACEMENT decision and is
# deliberately not derived from LANE_CLEARANCE, which is the corridor rule: fronting a lane excuses
# a seat from the corridor's setback (that is what `skip` means to `_near_corridor`), so the row's
# own offset is the only thing holding the DRAWN steading off the tread. A wealthy minka renders to
# ~61 x 37 ft, a half-diagonal of ~36 px; add the lane's own half-tread and a dooryard's working
# margin. Tying this to the clearance is what made the clearance look like it had to be 48.
LANE_FRONTAGE_STANDOFF = 70.0
"""How far off a lane's centerline a frontage seat is offered.

Research:
    farmsteads front a lane - UNRESEARCHED: a seat offered off a lane, which the page gives no figure for
    frontage seat off the lane - UNRESEARCHED: 70 ft off the centerline, with a dooryard's working margin the page does not give
"""

# How far outside the paddy's outline a field spur's tip stops. The lane is drawn 5 px wide and
# `fields_clear_of_road` allows w/2 + 2, so 8 px would clear it on paper - but the outline is a
# rolled, ragged polygon and the tip is placed against a VERTEX, whose two edges may fall away on
# either side. This is the smallest set-back that keeps every cohort map's tip out of the standing
# water, and it is still under a farmhouse's width, so the track visibly reaches the field.
#
# RE-CALIBRATED 14 -> 17 when the comb net went to TRUE SIZE (2026-08-17). Narrower channels let the
# carve plant closer to the water and `close_seams` recover more scraps, so a field's DRAWN extent
# (`vis_bbox`, which is what `fields_clear_of_road` intersects with the outline) grew - and ground a
# spur tip had legitimately occupied became rice. Seed 11 of the 24-map cohort was the one that
# tipped: its tip stood 2.7 px from an outline vertex against the check's 4.5 px allowance. Swept
# 14/16/17/18/20/22 against that seed - 14 and 16 fail, 17 is the first that clears - and 17 returns
# the whole cohort to its pre-change residue (22/24, the same two maps).
#
# THE LESSON, since this is the second knob this ladder has moved: a constant calibrated as "the
# smallest value that passes the cohort" is calibrated against a GEOMETRY, not against a principle,
# so anything that changes what the fan draws can invalidate it silently. Re-run the cohort after
# any change to channel widths, carve thresholds or the seam pass, and expect this number to move.
SPUR_SETBACK = 17.0
"""How far outside the paddy's outline a field spur's tip stops.

Research:
    path joins the outer bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html
    field spur's tip - UNRESEARCHED: stops 17 ft outside the paddy outline, the cohort's smallest clear value
"""

# How much open ground a threshing yard needs to its SOUTH, in feet. A thatched roof is pitched 45
# degrees or steeper, so the 46 x 28 ft minka's ridge stands ~20 ft up; at 38N in the threshing
# month that is 21 ft of shadow at noon and 39 ft by 9am. 39 protects the 9-to-3 drying day, which
# is the one that matters - and it costs nothing in row pitch, since house depth (28) + yard depth
# (~26) + 39 already comes to about the 92 ft the cluster band was independently sized at.
SUN_CORRIDOR_FT = 39.0
"""Research: clear ground south of a yard - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 39 ft"""

# How much open ground a threshing yard or a garden bed needs to its WEST and SOUTHWEST of the
# communal windbreak, in feet - the AFTERNOON sun (feature 133 T10, GM 2026-08-25). The belt is the
# tallest thing on the map. Its height is taken at 10 m = 33 ft: the one MEASURED igune in the
# record (Osaki, drone survey) is "about 10 m", Tonami's kainyo "over 10 m", Izumo's clipped pines
# 8-12 m - a WORKING belt, limb-pruned and kept. At 3pm in the shoulder month at 38N the sun stands
# 28 deg high at azimuth ~232, so the shadow runs 1.9 x height to the NORTHEAST: ~63 ft, of which
# ~50 ft is EASTWARD reach. 50 ft is the rule - the same 9-to-3 window the yard's south corridor
# protects, now for the afternoon half; the growing-season figure is smaller (~35 ft in the 7th
# month), so the shoulder month binds, as it does for the yard.
#
# 75 ft WAS TRIED FIRST AND DECLINED (2026-08-25), and the reason is a ruling, not a taste: 75 is
# the same geometry at 15 m, the floor of the Sendai "tall tree" class an untended mature
# sugi/keyaki stand reaches (15-28 m). At 75 the belt has to stand so far off the west rank that it
# falls outside the frame the hard features set, and the frame does NOT open for the belt (GM
# 2026-07-20: the communal windbreak clips at the view edge; `crop_hugs_content`). Measured on
# Inashiro: 131 clumps -> 38, `village_windbreak_is_continuous` red. At 50 the belt stands whole
# (81 clumps, continuous) inside today's frame. So 10 m is the calibrated value - a DEGREE along
# the attested band, not a choice between forms. THE FRAME QUESTION WAS THEN SETTLED SEPARATELY
# (GM 2026-08-26): the belt's inner face now sets the frame (`windbreak_face`), so a taller belt
# would no longer be cropped away - 10 m stays because it is the record's measured working height,
# not because the frame forces it. research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html.
WEST_SUN_FT = 50.0
"""Research: clear ground west of a yard or bed - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 50 ft from the belt"""

# THE FIELD ARCHETYPES this generator can draw, and why there are two rather than five. The pool's
# hamlets span five (`valley_paddy`, `polder_grid`, `mulberry_dike_fishpond`, `contour_terraces`,
# `ribbon_valley`) and they are not variations on one shape - a comb fan is grown around a head-race
# on sloping ground, a polder is a surveyed orthogonal grid diked out of standing water on flat
# ground. They share `draw_comb_field` (build_polder deliberately returns build_comb-compatible
# keys) and almost nothing else: different water entry, different drainage, a perimeter dike, and a
# village that must sit on the LANDWARD side rather than the upslope one.
#
# `mulberry_dike_fishpond` IS declared as a third archetype (feature 150, Kuwabata) because a pool
# entry names it and the gate reads it (`dikepond_is_ponds_in_a_block` keys off
# `meta.field_archetype`) - but it is BUILT as the polder carried to the wholesale-conversion
# overlay, which is what it is historically too (research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html:
# the wall-to-wall dike-pond landscape is the rare END STATE of the scattered overlay, ~300 years
# of 挖塘培基 plot by plot). So `POLDER_ARCHETYPES` is the set the polder stage serves, and the
# dike-pond differs from the rice polder only in its PARCEL FABRIC (`POLDER_FABRIC`), the overlay
# applied after the grid is drawn, and the ring-canal crossing caps.
FIELD_ARCHETYPES = ("valley_paddy", "polder_grid", "mulberry_dike_fishpond")
"""The field forms a hamlet may roll.

Research:
    field forms drawn - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html, research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: valley fan, rice polder, dike-pond
    no jori grid rolled - DEVIATION research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: no plain ruled on the jori grid, so that form is never rolled
"""
POLDER_ARCHETYPES = ("polder_grid", "mulberry_dike_fishpond")
"""Research: dike-pond built as a polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html"""

# THE PARCEL FABRIC PER POLDER ARCHETYPE - every number is `build_polder`'s TRUE-SCALE SIZING note
# (researched 2026-07-21, source-verified the same day; 1 px = 1 ft, no legibility inflation):
# - a RICE polder's module is ~190 ft (feature 280 M54, research/questions/0022-parcels-and-bunds-inside-a-polder-aze.html: a polder parcel before modernity ran about
#   three mu - the 1897 fish-scale register of nineteen Taipingqiao polders outside Suzhou, 3,700 parcels on 11,000 mu -
#   so the bay/half/third mix of the old ~110 ft module, whose ~1 mu mean was Buck's 1929-33 survey, is carried to
#   110 x sqrt 3 ~ 190 ft), most bays split into strips ((0.52, 0.16, 0.12)), with 3 ft walking
#   bunds between rows and 8 ft ditch corridors on the module lines ((1.5, 4.0));
# - a DIKE-POND's ponds were 0.4-0.6 ha oblongs (Ruddle & Zhong / FAO; CAVEAT in the note: the
#   sizes are Republican-to-1980s surveys of the traditional landscape, not Ming/Qing documents),
#   so a ~160 ft module with a merge-heavy mix ((0.10, 0.0, 0.60): mostly 160x320 ft ~0.48 ha 1:2
#   ponds, a square ~2.4-mu minority), the grid's ~22 ft gaps ((11, 11)), and each pond's water inset 23 ft inside its
#   parcel (`settlement/fields/landuse.py` `DIKEPOND_WATER_INSET`). THE WATER SHARE (feature 280 M58,
#   research/archetypes/610): every page that writes the water-to-dike split as a number (6:4, 7:3, 4:6) is modern, and
#   the oldest figures are Qu Dajun's for Jiujiang in 1678 - read together (a GUESS, this record's arithmetic) water to
#   dike about 5:3 - so a parcel is calibrated to about 6 parts water in 10 (0.62 measured on Kuwabata, 2026-09-29);
#   the 11 ft inset it replaced left 80% water per parcel, wetter than any figure read in any period. The dike's
#   width itself has no premodern figure (the 6-10 m once cited is a modern manual's): it follows from the share.
# `fit_polder` scales the GRID to the acreage and never the cell, so these calibrations hold
# whatever the household count asks for.
POLDER_FABRIC: dict[str, dict[str, Any]] = {
    "polder_grid": {"cell": 190.0, "parcel_mix": (0.52, 0.16, 0.12), "gap": (1.5, 4.0)},
    "mulberry_dike_fishpond": {"cell": 160.0, "parcel_mix": (0.10, 0.0, 0.60), "gap": (11.0, 11.0)},
}
"""Research: polder parcel fabric - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html, research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html: rice 190 ft modules, dike-pond 160 ft"""

# THE POND LAYOUT - ONE ATTESTED FORM AT POND SCALE (feature 280 M56, research/archetypes/130): the grid is attested for
# the Song tangpu CANALS, the mosaic for the PONDS, while a uniform chessboard of ponds is found only as today's aerial view
# of Digang - so a dike-pond block is drawn as the mosaic and the pond grid is no longer rolled. The GM ruled the knob in on
# 2026-08-18 on the reading that both were attested ponds; that reading is withdrawn at pond scale and the reversal
# reported. What follows is the knob's original note (constitution XII,
# GM 2026-08-18). research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: the lower-Yangtze wei-tian was a SURVEYED
# rectilinear grid (the Song tangpu lattice) while the Pearl-delta dike-pond accreted household by
# household into a MOSAIC - rectangles of varied size at varied local orientation around winding
# creeks. Both systems carried dike-ponds (Lake Tai mulberry sat on the tang banks inside the
# grid), so a dike-pond hamlet rolls between them; a RICE polder is the surveyed grid by definition
# and does not roll (`plan_site` pins it to "grid", which keeps every polder_grid map byte-identical
# to before this knob existed). The uniform chessboard is also the MODERN consolidated look, which
# is why the mosaic is the more common roll. `build_polder(mosaic=)` is the engine's dial: 0.0 is
# the grid, 0.5 the mosaic Kuwabata was drawn with (the GM saw and accepted that map's ponds).
POND_LAYOUTS = ("mosaic",)
"""Research: dike-pond layout - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0024-fish-fry-and-nursery-ponds-yumiao.html: the mosaic only; the chessboard grid is never rolled"""

# THE FRY FORM - which nursery a dike-pond hamlet keeps (feature 280 M60, research/archetypes/200 and 172): the ordinary
# delta hamlet raised grown fish and BOUGHT its fry, with no nursery ponds; the fry village of Jiujiang raised fry in seven
# parts of ten of its pond water (Qu Dajun, 1678). The "one parcel in ten" once drawn is on no page read, premodern or
# modern. Two attested forms, so a knob; the fry village rare (Qu Dajun: fry ponds only in Jiujiang) - the odds a GUESS.
# The third form read, a small fry pit beside each big pond (Nongzheng quanshu, 1639), is OFF the delta, and the block
# drawn is the delta's mosaic.
FRY_FORMS = ("none", "none", "none", "fry_village")
"""Research: fry form - research/questions/0024-fish-fry-and-nursery-ponds-yumiao.drawing.html: one hamlet in four a fry village"""

# THE MANURE FIXTURE'S FORM - heap or pit, two attested forms so a knob (constitution XII; feature 150, GM
# 2026-08-28 choosing audit A2). Sugiura 1973 counts the manure shed/heap on Tohoku farmsteads; Fei 1939 has
# the Lake Tai silk village keeping its manure "in the pits made of earthenware, half buried in the ground at
# the back of the building", lined along the road. Neither source gives a share of villages using each, so
# the roll is even. research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html.
MANURE_FORMS = ("heap", "pit")
"""Research: manure fixture form - research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.drawing.html: heap or sunk jar, even odds"""

# THE HARVEST WEATHER - an ENVIRONMENT FACT the spec declares, never a roll (feature 282, FR-005). Racks gathered by
# the house are named for the changeable-weather San'in coast, "so that it is convenient to do the threshing work within
# the homestead" (Nishimura and Makino 1959), and the drying method followed the weather and the ground over whole
# regions, not a village's choice - so a free roll per hamlet would let two neighbors in one climate differ, which is
# what the GM asked us not to do (2026-09-28). `changeable` draws a rack by every house; `settled` (the default: the
# gathered racks are one region's form - this project's decision, as the regional wind is) draws none at the house.
# research/questions/0016-rice-drying-racks-hasa-hasagi.html; the rule at research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html.
HARVEST_WEATHERS = ("settled", "changeable")
"""Research: harvest weather - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: declared, never rolled; racks by the house where changeable
standing rack forms - research/questions/0016-rice-drying-racks-hasa-hasagi.html, research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: no map draws Niigata's living alder rack posts on the bunds or Ehime's permanent roofed racks"""
DEFAULT_HARVEST_WEATHER = "settled"
"""Research: harvest weather when undeclared - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: settled"""
# TWO SUPPORTABLE ANSWERS BECOME A KNOB (constitution XII), not a picked one. Both were named by a
# settlement-review as knob candidates and the GM approved working them (feature 152, FR-005/FR-016).
COPSE_SITINGS = ("among_the_houses", "against_the_belt")  # a village copse threading the homesteads, or
"""Research: village copse siting - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: among the houses or against the belt"""
# tucked against the back grove - both are what a back-village planting is, and they make a settlement
# read differently at a glance, which is the whole point of a knob rather than a house style.
KOSATSUBA_SITINGS = ("frontage", "waterside")  # the notice board on the busiest built frontage, or at the
"""Research: notice board siting - research/questions/0190-notice-boards-kosatsuba.drawing.html: busiest frontage or the drawing-water place"""
# drawing-water place. The takafuda stood at crossroads and bridgeheads AND at the village well; a
# settlement-review measured Mizuguchi's at the wellhead (7 of 12 households within 250 ft) against 11 of
# 12 at the frontage optimum and called it defensible-but-off-optimum, which is exactly the shape of a
# genuine two-answer question rather than a defect.

# THE DIKE CROP - which dike-pond planting a hamlet is (feature 150, GM 2026-08-28 choosing audit A6; the
# options re-read by 269 B34). research/archetypes/230: Qu Dajun (late 17th c.) has the villages' pond dikes
# planted with fruit - lychee most, tea and mulberry next - and a modern history dates the fruit dike first
# (mid-Ming) and the mulberry dike dominant through the Qing. So three premodern plantings: mulberry, fruit and
# tea. The cane, banana and vegetable dikes are attested only in modern sources (one undated modern listing
# for cane, nothing earlier than the modern surveys for banana and vegetable), and by the GM's ruling of
# 2026-09-28 a form attested only in modern sources is not drawn - they are no longer options. The weighting
# is a GUESS, a degree (constitution XII): mulberry the Qing norm at 3 in 6, fruit the oldest form at 2, tea,
# named after lychee and never as a district's type, at 1.
DIKE_CROPS = ("mulberry", "mulberry", "mulberry", "fruit", "fruit", "tea")
"""Research: dike crop - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: mulberry half, fruit a third, tea a sixth"""

# WHAT THE LEFTOVER PARCELS OF A WHOLESALE CONVERSION READ AS (feature 150 B2): standing rice, or no leftover
# at all (every parcel a pond); the roll is even. A third state, tilled vegetable ground, rested on Fei's 1930s
# silk village and the modern vegetable dike, and is retired by the GM's ruling of 2026-09-28 that a form
# attested only in modern sources is not drawn (269 E9; research/archetypes/230).
WATERWARD_DEPTH = 280.0  # px of wild water drawn outside a polder's dike face (feature 150 T55). Not "to the canvas edge": the crop keeps ~120 px past the content at most on this tier, so everything beyond was scattered, keep-out tested and thrown away - 18.4 s of a 40 s gen. 280 outlasts any hamlet crop measured (the tightest flank keeps 245 px of headroom), and `waterward_strips_run_off_the_frame` holds the line.
"""Research: wild water outside the dike - CONVENTION: 280 ft drawn, outlasting any crop"""
LEFTOVER_FORMS = ("rice", "pond")
"""What the leftover parcels of a wholesale conversion read as.

Research:
    dike-ponds throughout - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: a wholesale village
    dike-pond leftover parcels - UNRESEARCHED: rice or pond, even odds
"""
POND_LAYOUT_MOSAIC = 0.5
"""Research: mosaic strength - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: 0.5, the lattice bent out of line"""

# THE SHARE OF THE BLOCK THAT CONVERTED in the end state. `apply_land_use(fraction=)` is the ECONOMIC
# term over the ELIGIBLE set, and the archetype opts out of the topographic filter by name
# (`eligible="all"`); 0.9 is the hand-authored Kuwabata's figure - "(almost) every former paddy cell"
# - so a few leftover parcels still read as standing rice among the ponds (research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: leftovers of a wholesale conversion are repainted as paddy, not left as outlines).
# The exact share is a DEGREE along the attested continuum (Shunde: rice under one-tenth of the land
# by c. 1900), a calibrated liberty rather than a measured number - recorded as such.
DIKEPOND_CONVERSION = 0.9
"""Research: share of the block converted - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: 0.9, leftovers in rice"""

# ...but only the proven one is ROLLED, and `polder_grid` is opt-in until it survives a COHORT.
#
# It was promoted on 2026-08-15 after sweeping 48 of 48 (8 seeds x 4 cardinal bearings, plus the
# household band's ends) and demoted the same day, because the cohort is a harder test than that
# sweep: `cohort_audit` varies HOUSEHOLDS per seed and rolls water_sink, cluster_shape and
# lane_skeleton, where the sweep pinned households at 16 and took the default rolls. Under those
# conditions the fitted cohort fell to 19 of 24. That is the cohort earning its keep exactly as it
# did three times for the valley tier - a fixed-parameter sweep is not evidence of consistency.
#
# THE BAR FOR PROMOTION is therefore a green COHORT, not a green sweep: 24/24 and 12/12 with polders
# in the mix. Rolling an archetype with open failures mixes them into the valley tier's own numbers
# and destroys the one measurement that says this process is consistent.
ROLLED_ARCHETYPES = ("valley_paddy",)
"""Research: field forms rolled - DEVIATION research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html: only the valley fan is rolled, the attested polder opt-in until its cohort is green"""

# HOW MUCH GROUND ONE HOMESTEAD TAKES, in px at 1 ft/px - the pitch the cluster band is sized on.
# A bundle's reserved rects come to ~71 x 57 ft. 92 px per household leaves the cluster dense enough
# to read as a nucleus and open enough for its courtyards, its wells and its byres. See
# `seat_cluster` for what the wrong number does.
#
# ASKED vs ACHIEVED - do NOT lower this to "recover" the difference (feature 121, 2026-08-17). This
# comment used to run the two together: the placer keeps bundles apart by circumscribed circles
# rather than real footprints, "so the effective pitch is larger again". True, and it is the
# ACHIEVED pitch that the circle inflates, not this number. Retiring the circle closes that gap by
# itself - the cluster lands at the pitch it asks for instead of overshooting it.
#
# THIS NUMBER IS HISTORICALLY GROUNDED, which is why it survives the fix unchanged: the spacing of
# farmsteads in a nucleated wet-rice village is set by the THRESHING YARD'S SUN, not by how tightly
# buildings can be packed. Rice dries on the niwa, so a yard needs clear ground to its south; a
# kayabuki thatch must be pitched 45 deg or steeper to shed rain, putting the ridge ~20 ft up, and
# at 38N in the 10th month that throws 39 ft of shadow by 9am. Lowering the asked pitch would put
# houses inside each other's drying shadow - a defect against the rule, arriving disguised as a
# density win. (research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html; specs/121 research.md D2.)
#
# THE HONEST WAY TO GET MORE DENSITY HERE is what real yashiki lots did: STAGGER east-west rather
# than space rows further apart.
#
# THAT IS NOW DONE, and this comment used to end "the placer is free to; nothing asks it to yet",
# which was stale and cost feature 126 a user story before anyone read the placer instead of the
# comment. Three mechanisms already deliver it, and re-deriving a fourth would be a second
# implementation of a rule the checker owns:
#   - `_sun_corridor_ok` keeps SUN_CORRIDOR_FT (39) of open ground SOUTH of every threshing yard,
#     in BOTH directions between neighbors, and `yards_unshaded_by_neighbors` gates it;
#   - `_yard_sun_conflict` and `_garden_shaded` prefer seats that keep groves and houses off the plots' sun, and every
#     canopy crown is held out of every plot's sun ground where it is drawn (`_sun_keepouts`, feature 310);
#   - feature 121 retired the circumscribed-circle spacing for real rotated footprints, and
#     `_house_too_near_a_neighbor` is an eave-drip rule of a couple of feet, not a sun rule.
# So THIS number is a ROW-PLANNING pitch and nothing else: nothing pays 100 ft east-west. See
# specs/126-derived-lanes-and-form/research.md R8.
#
# RAISED 92 -> 100 when the SUN CORRIDOR landed (2026-08-13). The pitch was calibrated before the
# rule existed, and a row now needs house depth (28) + yard (~26) + 39 ft of sun + the gaps between
# them, which comes to about 100 rather than 92. Asking the band for less than a row needs does not
# make the cluster tighter - it makes the placer spill the overflow OUTSIDE the band, which is how
# seed 18 grew a two-farm satellite 500 px off the nucleus, 777 px from the nearest water against a
# 760 px reach, with every legal well seat around it already taken by its own two courtyards.
BUNDLE_PITCH = 100.0
"""Research: row pitch - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: 100 ft, house, yard and the yard's 39 ft of sun"""

# THE GROUND ONE HOMESTEAD TAKES, as the side of a square (feature 280 M16 merged into feature 287, 2026-09-29): the seat
# band's AREA (`plan.band_extent`, `households x HOMESTEAD_GROUND_FT^2`, which also sizes the canvas's room for the seat).
# It was `BUNDLE_PITCH`, and grows with the yard: 280 moved the rice hamlet's yard median from 18 to 25 tsubo, and at the
# apron's 1.45 aspect the median yard is sqrt(18 x 35.583 / 1.45) = 21.0 ft deep before and sqrt(25 x 35.583 / 1.45) =
# 24.8 ft after - 3.8 ft more ground in the row's sum above, so 104. The ROW pitch stays 100: it plans offers the placer
# staggers from (and the web's reach is tied to it, `WEB_REACH_FT`). MEASURED (`make cohort N=1 SEED=<n>`; a detached
# worktree at 287's HEAD passes seed 18): with the band at 100 the merge held 13 of seed 18's 15 households on its best
# margin and refused the site; with the band at 104 all 15 seat. Raising the row pitch to 104 as well seated seed 18 but
# left one farmhouse off the way network on seeds 11 and 43 - measured and not taken.
HOMESTEAD_GROUND_FT = 104.0
"""The ground one homestead takes, the pitch the cluster band is sized on.

Research:
    the yard within it - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: 25 tsubo
    ground per homestead - UNRESEARCHED: 104 ft square, the 100 ft row pitch plus 3.8 ft of yard, cohort-measured
"""

# THE GROUND THE SEATING SPREADS ITS HOUSEHOLDS OVER, as the side of a square (feature 306, FR-010; a GUESS with its reasoning -
# the record gives no figure for it): `HOMESTEAD_GROUND_FT` counts the house, its yard and the row, and NOT the household's
# wood floor, which 269 B26 added after it (`HOMESTEAD_WOOD_FT2`, 6,000 sq ft at least, within the copse's reach of the house).
# Seated over a band of that size a village sat at the edge of its capacity and whether a margin filled was near chance - seed
# 47 at 40 households seated sixteen margins before one held everyone (specs/306-seat-by-packing/research.md R2, R6). The band's
# AREA is the households' SUM, so this is the side of a square holding the MEAN homestead: the pool's 82 envelopes' mean
# (`geom.bbox`, 20,366 sq ft) and the least wood floor, sqrt(26,366) = 162. It sizes only the band the SEATING spreads its offers
# over (`homesteads.stages._seat_households`: the lattice and the seat bound); the margin's choice, the canvas's room and the belt
# keep `HOMESTEAD_GROUND_FT`'s band - growing those as well re-fitted every field and refused sites the base seated (R11, R12).
SEATING_GROUND_FT = 162.0
"""Research: seating ground per homestead - GUESS: 162 ft square, the mean envelope plus the least wood floor"""

# `build_comb`'s GRAIN, and why this tier passes the PRINCIPLED value rather than the pool's.
#
# `grain` scales the carve's real-feet thresholds AND the channel widths. `build_comb`'s docstring
# prescribes `2 / ftpx` so "too narrow to plant" means the same real size at every map scale - 2.0
# for a 1 ft/px hamlet - while every hand-authored hamlet in the pool passes the default 1.0, which
# at this scale means half the real size and half the ditch width. That gap was recorded as an open
# question the first time round. It is now settled by measurement.
#
# WHAT USED TO BLOCK 2.0, AND WHAT FIXED IT (2026-08-12). First the bridge arithmetic: wider
# ditches produced planks and carried-way decks whose abutments stood in the channel, because both
# paths sized a deck from a nominal width rather than from the water actually beneath them. Both
# now measure the crossed water. Second the communal WINDBREAK: at the coarser grain the crop
# shifts enough that a belt derived from the house cloud's EXTREMES lands off a tall narrow cluster
# entirely (measured: 9 clumps, 350 px from the nearest farmhouse). `belt_polygon` samples the
# windward fringe as a PROFILE in columns across the wind instead, so the belt follows the shape of
# the cluster rather than a box around it, and the failure mode is gone.
#
# So this module runs at 2.0 and its cohorts gate clean there. The POOL's hamlets stay at 1.0 until
# someone re-rolls them, which is a real job (every comb map re-rolls, each wants a
# settlement-review) rather than an oversight - `build_comb`'s docstring carries the same account.
GRAIN = 2.0

# THE HAMLET BAND (research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html): 10-20 households, 50-100 inhabitants. Below
# 10 the place is an outlying farmstead or two rather than a hamlet; above ~20 it is a small village
# and grows the features a hamlet must not have (a headman, a shrine, tax-free plots).
HOUSEHOLD_BAND = (10, 20)
"""Research: hamlet household band - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html: 10 to 20"""

# The reference fan, at Ikegami's 15 households: the `build_comb` lengths that produced it. Every
# other size is this fan scaled by a single multiplier (see `fit_field`), so the fan's ASPECT - the
# thing that makes a comb read as a comb - is a constant of the tier and only its area varies.
REF_HOUSEHOLDS = 15
REF_FIELD_FALL = 1150.0
"""Research: reference fan's fall - UNRESEARCHED: 1,150 ft, Ikegami's hand-drawn fan"""
REF_CANAL_A = (1250.0, 1450.0)
"""Research: reference fan's canal A - UNRESEARCHED: 1,250 to 1,450 ft, Ikegami's hand-drawn fan"""
REF_CANAL_B = (680.0, 800.0)
"""Research: reference fan's canal B - UNRESEARCHED: 680 to 800 ft, Ikegami's hand-drawn fan"""

# ...and its ASPECT is rolled, which matters more than it sounds. `fit_field` scales the reference
# fan by one multiplier, so without this every hamlet of a given household count and fall direction
# gets the SAME fan silhouette - the review of the first draft found Inashiro's field outline was a
# byte-for-byte translation of Ikegami's, vertex for vertex, because the reference lengths ARE
# Ikegami's and its multiplier came out at 1.0. A cohort of maps that share their largest object is
# a cohort of re-skins. Trading fall length against canal length leaves the AREA alone (so the
# acreage solve is untouched) and changes the shape: a long narrow valley fan against a broad
# shallow one.
FAN_ASPECTS = (0.88, 0.95, 1.0, 1.08, 1.16)
"""Research: fan aspect - UNRESEARCHED: 0.88 to 1.16 fall against canal, rolled"""

# The fall bearings a rolled hamlet may sit on: the eight compass points, in the engine's screen
# convention (0 = east, 90 = south). The GM's water-flow doctrine says the bearing is a fact about
# the REGIONAL terrain and should be reasoned from the range the settlement sits under - a script
# cannot know that, so an unpinned bearing is ROLLED and the spec always lets the GM pin the real
# one. The roll exists so a cohort varies, not because a rolled bearing is as good as a known one.
FALL_BEARINGS = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0)
"""Research: land's fall - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: declared, else rolled among eight points"""
CARDINAL_BEARINGS = (0.0, 90.0, 180.0, 270.0)  # the survey grid a polder is laid to; see plan_site
"""Research: polder grid's orientation - DEVIATION research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: laid to the four cardinal bearings, never tilted"""

# WHICH WAY THE COLD WIND COMES FROM: THE NORTHWEST, UNLESS THE MAP DECLARES A LOCAL WIND (feature 261).
#
# The East Asian winter monsoon blows out of the Siberian high from the northwest across China and Japan, and
# the GM ruled (2026-08-29) that it does across Rokugan too "in most places when the local geography does not
# override the regional geography" - which is why shelter belts stand on the north and west, and why a reader
# who sees them there is being told a real fact about the regional wind (research/contents.json#vegetation, 'Does a shelter
# belt wrap the settlement?'). A local wind that departs from it - a valley whose cold air drains off its own
# high side, say - is a DECLARATION on the spec (`HamletSpec.windward`), and nothing else (GM 2026-09-26:
# "only when declared"). No pool map declares one.
#
# WHAT THIS RETIRED, and why. Until feature 261 every map's wind was its UPSLOPE bearing turned by a rolled 45
# degrees (`WIND_TURNS`, the katabatic reading: cold air pools on the high ground and drains downhill), and
# `stage_ways` then RENAMED it after whatever the seat's back faced when the two disagreed by more than ~70
# degrees. Between them the regional northwest never reached a map: the five scripted hamlets came out W/N,
# SE, NW, S and NE, and Kashikawa's belt stood on the south and east with no explanation on the page. The GM
# asked whether that was a bug; it was. The katabatic finding stays in the record as the reason a map MAY
# declare a local wind.
DEFAULT_WINDWARD = "NW"
"""Research: regional wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the northwest unless declared"""

# THE SEAT TURNS ITS BACK TO THE WIND, and the wind is never renamed to fit the seat (feature 261). A field
# margin is a candidate seat only if its outward normal - the direction the settlement's back faces - lies
# within 45 degrees of the windward bearing: cos 45 deg = 0.7071. 45 degrees is half the spacing of the
# compass quarters a wind is named in, so a seat inside the bar is one whose back faces the windward quarter
# itself rather than a neighboring one. A map convention, not a finding: nothing read gives a tolerance for
# how squarely a settlement faces away from its wind. A margin outside the bar is kept only as the last
# fallback, and a map that falls back to it records `meta.seat_offwind`, which the gate refuses on the pool.
WIND_BACK_MIN_DOT = 0.7071
"""Research: seat's back to the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: within 45 degrees"""

# THE COPSE STANDS AMONG WHAT IT IS NAMED FOR (feature 261). The record gives the dooryard copse as "a loose copse of
# bamboo and fruit trees in the gaps between the houses" and no distance (research/contents.json#vegetation, 'How our maps draw a
# village's groves'); 90 ft is the bar the feature-230 settlement-review itself used to call a copse a wood (86% of clumps
# more than 90 ft from any house), and the pool's copses before the reseats sat at a median 77-81 ft. A map drawing
# convention on the record's words, not a finding. The against-the-belt copse reads as one wood with the belt when its
# crowns stand within a crown or two of the belt's: 60 ft, the same kind of convention.
COPSE_HOUSE_REACH_FT = 90.0
"""Research: copse among the houses - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: within 90 ft of a house"""
COPSE_BELT_REACH_FT = 60.0
"""Research: copse against the belt - CONVENTION: within 60 ft of the belt, a crown or two; the 0071 drawing page has no belt-side copse"""

WIND_VECTORS: dict[str, Pt] = {
    "N": (0.0, -1.0),
    "NE": (0.7071, -0.7071),
    "E": (1.0, 0.0),
    "SE": (0.7071, 0.7071),
    "S": (0.0, 1.0),
    "SW": (-0.7071, 0.7071),
    "W": (-1.0, 0.0),
    "NW": (-0.7071, -0.7071),
}

CLUSTER_SHAPES = ("round", "round", "elongated", "crescent")
"""Research: cluster shape - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: round 2, elongated 1, crescent 1"""

CLUSTER_BAND_ASPECT = {"round": 2.2, "crescent": 3.0, "elongated": 5.0, "split": 3.0}
"""How long the cluster BAND is against how deep, per rolled `cluster_shape`.

THE KNOB WAS DEAD UNTIL THIS TABLE EXISTED (2026-08-19). `cluster_shape` is rolled per settlement
and printed in every cohort-audit header, and it fed exactly one thing: `cluster_seeds`, the CLOUD
pass, which runs only for households the front rows do not seat. Census: on all 48 cohort seeds and
all four pool hamlets the rows plus lane frontage seat EVERY house, the cloud never runs, and
`meta.cluster_shape` is stamped on none of them - so round, elongated and crescent all drew the
same 3:1 band. (History, as of 2026-08-19. The front row was capped to one rank that same week, and
since then the cloud seats the ranks behind on four of the five pool hamlets - `meta.cluster_seeding` reads
"cloud" there; since feature 226 it proposes a pitch lattice over the band rather than random throws.) A peer session found it while retracting a result that had blamed the knob for a
placement failure; the knob could not have caused anything, because nothing read it.

The band is where the shape has to bind, because the band is what the front rows are seated along.
Area is HELD (`households * BUNDLE_PITCH^2`, the ground a homestead actually takes), so only the
ratio moves and no settlement gains or loses room by its shape. The 3.0 that was hardcoded here is
kept as the crescent/split value, so a crescent map is byte-identical to what it drew before and the
change is visible only where it should be.

Depth floors at 112 px, so a small round hamlet reads well under its band figure and a small
elongated one is pushed toward 2.5:1 rather than 5:1 - the floor is a real minimum (a band shallower
than that cannot hold a homestead bundle and its yard), and letting it compress the extremes is
honester than pretending a 10-household string can be five times longer than it is deep.

ROUND'S BAND IS 2.2/1.2, AND WHAT IT BUYS IS HONESTY RATHER THAN ROUNDNESS. Say the limit plainly: on
the rotation-aware measure, round rolls draw a MEAN 2.48 aspect against a 2.0 ceiling, so `round` is
declared on 5 of 21 cohort rolls and recorded `cluster_shape_unhonored` on the rest. The knob does not
make a round hamlet round; it reports truthfully that most of them are not.

That is a smaller claim than an earlier version of this docstring made, and the earlier one was wrong
for an instructive reason: it rested on the AXIS-ALIGNED aspect, which cannot see a diagonal band (see
`cluster_aspect`). Measured on the honest metric across the full 48, the trade is:

    2.2/1.2 -> 43/48, ZERO regressions, round honored  5/21, mean 2.48   <- shipped
    1.5/0.9 -> 42/48, ONE regression (seed 34), honored 12/21, mean 1.86
    1.2/0.8 -> 38/48, four regressions,          honored 20/21, mean 1.50

**THE WALL IS `lane_ends_front_different_houses` (0611), AND IT IS CORRECT.** The session that owns it
ruled on this exact question: two lane ends within 60 ft pointing within 25 degrees are a fork serving
one steading, so a cluster tight enough to produce that is too tight. Do not weaken 0611 to buy a
rounder cluster; Principle XIII forbids shipping the regression anyway.

WHAT THIS MEANS ARCHITECTURALLY, and it is the finding worth more than the number: at hamlet scale the
LANE SKELETON AND FRONTAGE dominate cluster shape, and the band aspect is a weak lever pulling against
them. The front rows and `lane_frontage` seat every household on 47 of 48 seeds, along a margin whose
bearing the field chose - so the cluster's proportion is mostly a consequence of the field edge, not of
this table. A genuinely round hamlet needs the SKELETON to be shape-aware (a T laid compactly rather
than spread), which is untried for SHAPE - note that it was tried and falsified for REACH, which is a
different question. That, not a smaller number here, is the next real lever.

Research: seat band's aspect per shape - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: 2.2 round to 5.0 elongated"""

CLUSTER_DRAWN_ASPECT = {"round": (1.0, 2.0), "crescent": (1.9, 4.2), "elongated": (2.8, 12.0), "split": (1.9, 4.2)}
"""What the FINISHED cluster's long:short ratio must fall inside for a rolled shape to be declared.

THIS IS NOT `CLUSTER_BAND_ASPECT`, AND CONFLATING THE TWO WAS A BUG (caught 2026-08-19, in the sweep
that chose the round value). The band aspect is a MECHANISM parameter - the proportions of the seat
band the front rows are laid along. The drawn aspect is an OBSERVABLE - the bounding box of where the
houses actually ended up. They are not the same quantity and they do not even track each other
closely: at `CLUSTER_BAND_ASPECT["round"] = 2.2` the five swept seeds drew 1.01, 1.07, 1.17, 1.76 and
2.21, because the front row wraps and the rows stack, so a 2.2:1 band routinely yields a ~1:1 cluster.

The first honesty guard compared the drawn aspect directly against the band parameter and passed only
because its tolerance was wide enough to swallow the mismatch - one seed sat 1.19 outside a 1.2
tolerance and was declared honored on what was effectively a rounding accident. That is this
project's most-repeated defect wearing yet another hat: A CHECK AND THE THING IT CHECKS MEASURING
DIFFERENT QUANTITIES. So the guard now tests the observable against these ranges, which are stated in
the observable's own units and can be read off a finished map with a ruler.

ROUND'S CEILING IS 2.0, AND IT COMES FROM THE HAND-AUTHORED MAPS rather than from taste. Those 19 are
frozen exhibits drawn by eye before any of this machinery existed, so they are the only visual ground
truth the project has for what a word means. Measured on the rotation-aware aspect, the ones a reviewer
reads as a round clump sit at **1.24 / 1.29 / 1.38 / 1.80** (moritono, honda, ikegami, shimizu) and the
ones read as a string sit at **2.42 / 3.52 / 3.72 / 4.26** (tanada, kuwabata, enokida, yatsuda). The gap
between 1.80 and 2.42 is where the word changes, so 2.0 sits in it.

The first cut of this table said 2.4, which was calibrated against the AXIS-ALIGNED measure and is
inside the string band on the honest one - so it would have honored `round` on clusters that plainly
read as ribbons. The ceiling and the measure had to be fixed together; fixing either alone leaves the
rule wrong.

The ranges are wide on purpose. They are not a target the generator aims at; they are the band inside
which a reader looking at the sheet would agree with the word. `round` tops out at 2.4 because past
that a clump reads as a string; `crescent` starts at 1.9 and `elongated` at 2.8, overlapping
deliberately, because the difference between those two at the margin is the CURVE of the band and not
its ratio, and this rule is not the place to adjudicate curvature. The upper bound of 12.0 on
`elongated` is a sanity rail, not a shape statement.

Kept in step with the gate's own copy in `check_village/segments_04c_groves_and_shading.py` by
`tests/hamletgen/test_cluster_shape.py` - the gate may not import the generator, so the table is
duplicated, and a duplicated table with no pin is a table that drifts.

Research: drawn aspect a shape is declared at - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: round up to 2.0"""
LANE_SKELETONS = ("spine", "T", "Y", "cross")
"""Research:
    lane skeleton - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: spine, T, Y or cross
    lane along the water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the fifth lane shape, a lane along the water, is never rolled; only spine, T, Y or cross
"""
# The two attested forms of making every house reachable. NOT weighted: the research supports both
# equally, so an even roll is the honest one, and the two read differently enough at a glance
# (a laid-out double row vs. a grown spine-and-alleys) to be worth a full half of the cohort each.
LANE_WEBS = ("alleys", "back_lane")
"""Research: lane web form - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: side lanes or a back lane, even odds"""
# THE SETTLEMENT FORM - which KIND of settlement this is, not merely what shape its cluster takes.
# Three forms, and the roll is DELIBERATELY flatter than real-world frequency would be. Read that
# sentence twice before re-weighting this tuple, because the departure is the decision.
#
# What the research supports (research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html):
#   - nucleated  - the default across wet-rice East Asia, because paddy is too valuable to build on,
#                  so households cluster on whatever ground will not grow rice. The access rule
#                  (`farmhouses_reach_a_way`) is decisive for THIS form and no other.
#   - dispersed  - the Tonami plain's 7,000 farmhouses over 220 km2, each in its own kainyo grove.
#                  Arises where an alluvial fan drains too well for paddy, so water control is
#                  per-holding and the farmer lives on the holding. Our comb field IS such a fan.
#   - linear     - the row village: farmsteads either side of a through-track, each holding behind
#                  its own house. Weakest-attested of the three in the English-language record, so
#                  it draws least - but not so rarely that the cohort stops exercising it.
#
# THE DEPARTURE, recorded per the project's calibrated-liberty rule: in the real world nucleated
# would dominate far more heavily than 50% - Tonami is famous precisely BECAUSE dispersal is
# regionally unusual. These maps exist to be told apart at a glance ("settlements which are within
# historical norms while being as different from one another as is justifiable"), and each form here
# is individually inside the norms; it is the FREQUENCY that is flattened, which is the liberty a
# DEGREE-along-a-continuum may take. Weighting to true frequency would make two of the three forms
# vanishingly rare, untested by the cohort, and pointless to have built.
# HOW FAR A NON-NUCLEATED FARMHOUSE MAY STAND FROM ITS FIELD - A RETIRED FIGURE, KEPT AS A RECORD.
#
# `FIELD_ADJ_PX = 165.0` stood here with twelve lines of rationale and ZERO consumers (found 2026-09-12
# by an escalation-check pass over a writeup that cited it). It mirrored `all_houses_field_adjacent` (retired, feature 166)
# (segment 0232), which died with the check battery in feature 166, and its sibling `field_ringed` (retired, feature 141) went
# in feature 141 on the GM's own cut. A live constant nothing reads is worse than no constant: a reader
# calibrates against it believing a check enforces it, which is what five comments in the placers had
# done. The figure is deleted; what was worth keeping is the MEASUREMENT and the research behind it.
#
# THE RESEARCH, which is still the operative thing: a Tonami farmstead stands in the MIDDLE of its own
# holding and a row village's fields lie directly behind each house, so neither form has a back rank to
# excuse - where a nucleated cluster legitimately does (`research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html`, which gives a 6 ft MINIMUM and no maximum at all).
#
# THE MEASUREMENT, for whoever switches the non-nucleated forms on: left to the cloud pass, dispersed
# and linear maps put houses a median 164 and 208 px from the field against a nucleated baseline's 144
# and 145. That is the generator being wrong about the FORM, not a map being too far from its crop, and
# it is the number to re-derive a standoff from rather than a bar to re-impose.

# THE THREE FORMS, ROLLED AGAIN (feature 291) - at feature 126's weights, nucleated 5 : dispersed 3 : linear 2.
#
# Feature 126 rolled nucleated only, because switching the other two on surfaced four latent defects in the
# per-house grove, measured on the in-gate ratchet seeds then:
#
#   seed 42 (linear):    groves_clear_of_lanes, groves_on_windward_side, gardens_unshaded_from_east
#   seed 43 (dispersed): groves_clear_of_structures, structures_clear_of_trees (groves over byres),
#                        gardens_unshaded_from_east, and 12 of 14 households seated
#
# Two fixes were tried then and MEASURED NOT TO HELP, and are not to be repeated as fixes: adding `groves` to the
# lane fabric in `_homestead_polys`, and giving the grove rects the house's own `_house_on_a_tread` test (both kept,
# being correct in themselves). What changed since is the seating: the houses come first and the lanes last (126),
# the free-ground and placed-box indexes judge the whole bundle (276), and the matrix owns the overlaps (166).
# Feature 291 measured the restored weights on cohort seeds 1-24 (dispersed 7, linear 6, nucleated 11) with the
# matrix and the grove predicates (`homestead_parts/grove_rules.py`) run on every roll by `tools/cohort_audit` -
# the battery that had caught 126's defects was retired by 166, so the cohort's own verdict no longer saw them.
_SETTLEMENT_FORMS_WHEN_GROVES_WORK = ("nucleated", "nucleated", "nucleated", "nucleated", "nucleated", "dispersed", "dispersed", "dispersed", "linear", "linear")
"""Research: settlement-form weights - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: nucleated 5, dispersed 3, linear 2"""
SETTLEMENT_FORMS = _SETTLEMENT_FORMS_WHEN_GROVES_WORK
"""Research: settlement form - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: nucleated 5, dispersed 3, linear 2"""

# HOW MANY SIDES A FARMSTEAD GROVE TAKES (feature 291): the roll tables live with the engine that draws the grove
# (`settlement/homestead_parts/grove_sides.py`, where their reasoning is), so the city path rolls the same ones.
from l7r.diagram.settlement.homestead_parts.grove_sides import GROVE_FLANKS as GROVE_FLANKS  # noqa: E402,F401
from l7r.diagram.settlement.homestead_parts.grove_sides import GROVE_SIDES as GROVE_SIDES  # noqa: E402,F401
from l7r.diagram.settlement.homestead_parts.grove_sides import GROVE_SIDES_FLOOD as GROVE_SIDES_FLOOD  # noqa: E402,F401

# THE ROW VILLAGE (feature 291 amendment 3; research/questions/0033-row-villages-resson.html). A linear hamlet's farms stand in a row
# along ONE LINE - a street laid first (the planned row's form, which a paddy row may borrow; drawn straight, as a
# surveyed road is) or the dry edge the ground gives (a levee, a dike, a fan's foot; the field's margin stands for it,
# this project's reading; the row curves with it). Flood-prone ground takes the dike, the edge; otherwise the two at
# even odds - a GUESS, no page counts them.
ROW_LINES = ("street", "edge")
"""Research: row village's line - research/questions/0033-row-villages-resson.drawing.html: street or dry edge, even odds"""
# ...on ONE side of its street (the field across it, Shimotome) or BOTH (each farm's holding behind it, Santome and
# Nobidome): both attested, no count - even odds, a GUESS.
ROW_SIDES = ("one", "both")
"""Research: row village's sides - research/questions/0033-row-villages-resson.drawing.html: one side or both, even odds"""
# ...and its WATER: each farm its own well, or wells shared along the street. The record rules only on the dispersed
# farm (homesteads/200: its own water); the one row it knows (Santome, few deep shared wells on a water-poor upland)
# does not transfer to a paddy row - even odds, a GUESS.
ROW_WATERS = ("own", "shared")
"""Research: row village's water - research/questions/0033-row-villages-resson.drawing.html: own wells or shared, even odds"""
# A DISPERSED farm's own water (feature 291 amendment 5; homesteads/200): a small channel led off the irrigation water into
# its grounds - the Tonami museum: "in many areas a small channel was led into the house's grounds", the fan's water table
# too deep for a well (ACCURATE) - or its own well, the other areas as this record reads them (a GUESS). Even odds, a GUESS.
FARM_WATERS = ("channel", "well")
"""Research: scattered farm's water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a channel or a well, even odds"""

# Where the hamlet's bamboo stands (feature 133 T47; the `bamboo` knob's roll table). Weighted so a
# temperate lowland hamlet usually has one - the research puts bamboo below the frost line as a
# matter of course - and "none" is the cold-upland minority. Read the knob's note in `_knobs.py`.
BAMBOO_FORMS = ("homestead", "homestead", "thicket", "both", "none")
"""Research: where the bamboo stands - research/questions/0075-bamboo-groves-chikurin.drawing.html: farmsteads, a thicket, both or none, weighted homestead 2 in 5 and
    the others 1 in 5, where the registry's knob rolls the four evenly"""
PLOT_SIZES = ("small_irregular", "medium", "medium", "large_block")
"""Research: paddy plot size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: small 1, medium 2, large block 1"""
GRAIN_DRIFTS = (-8, -4, 0, 0, 4, 8)
"""Research: furrow drift - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: -8 to 8 degrees off the contour, turning
    only the dry fields' furrow rows (carve.py theta0); the paddy grain never drifts, and the registry's grain_drift runs -12 to 12"""
