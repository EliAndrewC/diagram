"""The lane and web clearances, the track's and the footpath's, and a farmhouse's reach - split from consts.py by feature 405
T130 (T112's claims took consts.py past the 1,000-line bar, as feature 316 split consts_water.py); bodies verbatim, and every name
here is re-exported from consts.py, so callers keep importing them from there.

Research: way constants plumbing - NONE"""

from __future__ import annotations

# THE NO-BUILD CORRIDOR OF A WEB LANE, in feet - deliberately much tighter than LANE_CLEARANCE.
#
# LANE_CLEARANCE (40) is derived for a lane the homesteads FRONT: it is the drawn minka's
# half-diagonal plus the lane's own half-tread, so the steading clears the way it faces. A web lane
# is the other kind: the research describes the lateral ones as "colonized as semi private space by
# the adjoining house", which is a way people build right up against. Holding 40 ft off both verges
# of every web lane reserved the middle of the cluster and pushed the houses out - measured on the
# four pool hamlets, the long axis grew 51%, 58%, 15% and 97%. This is the lane's own half-tread
# plus a hand's breadth: enough that a wall is not drawn ON the tread, and no more. Since feature 328 it is the lane page's
# own room between two homesteads, 18 ft - 7 ft at each garden fence and a 4 ft tread (it was 28, on no page) - and since
# feature 374 wave 142 read as what it is, a HALF-width (`lane()`'s `clearance`): 9 ft from the lane's middle, the 18 ft room
# whole; at 18.0 it held 36 ft clear.
WEB_CLEARANCE = 9.0
"""Research: web lane's no-build corridor - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's room of 18 ft, 7 ft at each garden fence and a 4 ft tread between - 9 ft each side of the middle"""

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
#
# 7 SINCE FEATURE 328: the 16 ft was on no page, and the check it was set off (`houses_off_corridors`) is retired; the lane
# page keeps a lane's middle at least 7 ft from a garden fence, and a track is held to that figure like every other way.
TRACK_FABRIC_GAP = WEB_FABRIC_GAP
"""Research: track off a steading - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: 7 ft from the track's middle to a garden fence, as every lane"""

# A FOOTPATH'S CLEARANCE: the path from an outlying steading's door to the nearest way, the residual room between two plots ("colonized as semi private space by the adjoining house").
# 0246's 7 ft SINCE feature 385 T96 (the round arbiter's hour-28 ruling: room first). Held at 4 ft from feature 328 wave 4 because at 7 the linear form's farms went unreached - measured 2026-10-19,
# that was never the footpath's room: a row farm's DOOR read this constant (`front_door` at it + 4, `door_off_fixtures` at it + 1), so the door could not stand clear of its own fixtures (seeds 3, 4,
# 903, 904); the door's numbers are its own now (`DOOR_STEP_FT`, `DOOR_FIXTURE_CLEAR_FT`). Likely the cause of wave 96's failed try too (m:wave96-footpath-7ft in specs/328), not measured on its maps.
FOOTPATH_FABRIC_GAP = 7.0
"""Research: footpath off a plot - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle, a 3 ft footpath's included, keeps at least 7 ft clear of a garden fence"""

GROVE_WORKING_ROOM_FT = 9.5
"""How far a door path's tread keeps off the trees of a grove band (feature 374 wave 119; moved here from `ways/serve.py` by feature 385 T98, so the track reads it too): 0036 lays a lane through a band
"with a footpath's clearance and some working room kept off the trees on each side, about 22 ft of the opening" - a 3 ft
tread and 9.5 ft each side. A band's rect bounds its trunks (crowns are thrown inside it less 2 px), so the room is off them.

Research: working room off the trees - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: about 22 ft of the opening, a 3 ft tread and 9.5 ft each side"""

DOOR_STEP_FT = 8.0
"""How far past the far edge of its yard a grove farm's front door point stands (`ways/serve.front_door`'s `clear`) - the
household's own dooryard, not a fence gap: 0246 lets a household's own way run beside its own fence. The value the door held
as `FOOTPATH_FABRIC_GAP` + 4 before feature 385 T96.

Research: door step - UNRESEARCHED: 8 ft past the yard, in the household's own dooryard"""

DOOR_FIXTURE_CLEAR_FT = 5.0
"""How far the door point is kept off the farm's own fixtures and the grove bands round it (`ways/serve.door_off_fixtures`)
- the point a door path starts from; the path from it keeps `FOOTPATH_FABRIC_GAP` off every garden fence. The value it held
as `FOOTPATH_FABRIC_GAP` + 1 before feature 385 T96.

Research: door point off the fixtures - UNRESEARCHED: 5 ft clear of the fixtures and grove bands, in the household's own dooryard"""

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
#
# ...AND SINCE FEATURE 374 WAVE 143 IT HOLDS OFF THE TOE AND THE MARSH ONLY: against the crop a web lane runs on the bund, its edge
# at most on the plot's boundary (`WEB_CROP_GAP`, half the widest tread laid on this ground - at a 3 ft lane's half-tread the
# 6 ft streets and joins routed on the same ground stood 1.5 ft on the crop, impl-drift), as 0081's drawing page lets it; the crop polygons carry that gap themselves
# (`clearance.Gapped`), so every reader handed the hard ground keeps each part at its own.
WEB_HARD_GAP = 8.0
"""Research: web lane off the toe and marsh - UNRESEARCHED: 8 ft; the record says only that a lane keeps off wet ground"""
WEB_CROP_GAP = 3.0
"""Research: web lane against the crop - research/questions/0081-village-lanes.drawing.html: a lane may touch a plot's boundary - its middle half the widest tread laid on this ground (a row street's or a join's 6 ft) off the field and the dry plots, so no tread's edge passes the boundary"""

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
# (`farmhouses_reach_a_way`). It is 0246's own figure, "every farmhouse within 100 ft of one" - NOT the row pitch.
# The two were one number because the pitch is 100; feature 328 found them distinct figures (0038 sets the row
# pitch at 92, which waits for the lane-law wave - its geometry Z'd a Kuwabata joint), so they are two constants now.
# The same number sets the web's lane spacing, so the requirement and the geometry that satisfies it cannot drift
# apart.
#
# Grounding: research/questions/0081-village-lanes.html, and research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html - a house
# in a nucleated cluster is reached by a way, but for the few reached across a neighbor's land (feature 317), which
# `ways/checks.py` `unreached_houses` counts reached through their neighbor. The previous 90 ft in
# `lanes_reach_something` was flagged in the backlog as a number nobody had justified; this one is
# derived from a researched constant instead of chosen to make today's maps pass.
WEB_REACH_FT = 100.0  # 0246's "within 100 ft"; the gate's copy is asserted equal in tests
"""Research: every farmhouse reached by a way - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft, how close counts as serving a house; but the few reached across a neighbor's land"""

WAY_END_REACH_FT = 60.0
"""How near a lane's END must come to another way or a farmhouse before the path is one somebody wore (the field's reach
is `ways.law.FIELD_REACH_FT`, 0014's).

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

12 ft is DERIVED from the clip, not chosen. A tread is cut `WEB_FABRIC_GAP` (7 ft) clear of a plot it runs beside -
`FOOTPATH_FABRIC_GAP`, the same 7 ft, for a footpath - and `clear_runs` walks its candidate in 4 ft steps - so a path that genuinely
reaches a boundary records its last point 7-11 ft off it and cannot record it nearer. Measured: the two straggler ends
at 7.8 and 6.9 ft from the garden they stop at, Inashiro's byre arm at 8.4, against the next-nearest built ground on any
of those three maps at 24 ft. Anything past 12 is a tread that stopped somewhere else.

Research: a lane end arrives at a steading - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 12 ft of its built ground"""


# How close two drawn treads must come to count as ONE network (feature 166, lifted out of the retired
# `farmhouses_reach_a_way` check, which held it as `_LANE_JOIN`). Its recorded why, carried verbatim from
# the check because it is the reason the number is 40 and not something else: it is the same figure
# `lanes_reach_something` used for "this end has met another way", deliberately - the two rules are about
# the same fact from opposite ends, and letting them disagree would let a lane be connected for one and
# isolated for the other. 25 SINCE FEATURE 328: the lane page's own join reach, "ends within 25 ft of one another are
# joined at a single point" (40 was on no page).
LANE_JOIN_FT = 25.0
"""Research: two lanes as one network - research/questions/0081-village-lanes.drawing.html: treads within 25 ft count as one network, the page's join reach"""

# A TAIL PAST A MEETING (feature 417 T05, D13): the one figure for a lane's run beyond the crossing or junction it overran -
# cut when shorter. It was written six times (`sweeps._PAST_CONNECTOR_FT`, `bund._PAST_JUNCTION_FT`,
# `settle.shapes._CROSSING_TAIL_FT`, `knots._TAIL_CUT_FT`, and a bare 40.0 in `serve` and `touch`), all 40.
TAIL_CUT_FT = 40.0
"""Research: a tail past a crossing - research/questions/0081-village-lanes.drawing.html: a tail of under 40 ft beyond a crossing is cut"""

# A WAY JOINING THE BUND (feature 417 T05, D16): an end this near the paddy's edge reaches the field - `thread.SPUR_REACH_FT`
# and `law.FIELD_REACH_FT` both read it (they were two 6.0s a test held equal).
FIELD_REACH_FT = 6.0
"""Research: reaching the field - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: an end within 6 ft of the paddy's edge joins it"""

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
    field spur's tip - research/questions/0081-village-lanes.drawing.html: a lane never crosses row crops, so the connector starts off the crop (the bund join is `ways/bund.py`'s claim); the 17 ft setback is UNRESEARCHED, the cohort's smallest clear value
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
