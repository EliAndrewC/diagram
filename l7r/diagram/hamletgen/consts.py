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
from l7r.diagram.sitegen.types import SQ_FT_PER_ACRE as SQ_FT_PER_ACRE  # noqa: F401
from l7r.diagram.sitegen.types import Poly as Poly  # noqa: F401
from l7r.diagram.sitegen.types import Pt as Pt  # noqa: F401

from .consts_fields import COPSE_SITINGS as COPSE_SITINGS
from .consts_fields import DEFAULT_HARVEST_WEATHER as DEFAULT_HARVEST_WEATHER
from .consts_fields import DIKE_CROPS as DIKE_CROPS
from .consts_fields import DIKEPOND_CONVERSION as DIKEPOND_CONVERSION

# The field archetypes and knobs live in consts_fields.py (feature 405, the 1,000-line bar) and are re-exported here by name.
from .consts_fields import FIELD_ARCHETYPES as FIELD_ARCHETYPES
from .consts_fields import FRY_FORMS as FRY_FORMS
from .consts_fields import HARVEST_WEATHERS as HARVEST_WEATHERS
from .consts_fields import KOSATSUBA_SITINGS as KOSATSUBA_SITINGS
from .consts_fields import LEFTOVER_FORMS as LEFTOVER_FORMS
from .consts_fields import MANURE_FORMS as MANURE_FORMS
from .consts_fields import POLDER_ARCHETYPES as POLDER_ARCHETYPES
from .consts_fields import POLDER_FABRIC as POLDER_FABRIC
from .consts_fields import POND_BANK_CROWN_FT as POND_BANK_CROWN_FT
from .consts_fields import POND_BANK_FT as POND_BANK_FT
from .consts_fields import POND_BANK_PITCH_FT as POND_BANK_PITCH_FT
from .consts_fields import POND_BANKS as POND_BANKS
from .consts_fields import POND_LAYOUT_MOSAIC as POND_LAYOUT_MOSAIC
from .consts_fields import POND_LAYOUTS as POND_LAYOUTS
from .consts_fields import ROLLED_ARCHETYPES as ROLLED_ARCHETYPES
from .consts_fields import WATERWARD_DEPTH as WATERWARD_DEPTH

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
from .consts_ways import DOOR_FIXTURE_CLEAR_FT as DOOR_FIXTURE_CLEAR_FT
from .consts_ways import DOOR_STEP_FT as DOOR_STEP_FT
from .consts_ways import FIELD_REACH_FT as FIELD_REACH_FT
from .consts_ways import FOOTPATH_FABRIC_GAP as FOOTPATH_FABRIC_GAP
from .consts_ways import GROVE_WORKING_ROOM_FT as GROVE_WORKING_ROOM_FT
from .consts_ways import LANE_FRONTAGE_STANDOFF as LANE_FRONTAGE_STANDOFF
from .consts_ways import LANE_JOIN_FT as LANE_JOIN_FT
from .consts_ways import MIN_WEB_GAP as MIN_WEB_GAP
from .consts_ways import SPUR_SETBACK as SPUR_SETBACK
from .consts_ways import STEADING_ARRIVAL_FT as STEADING_ARRIVAL_FT
from .consts_ways import SUN_CORRIDOR_FT as SUN_CORRIDOR_FT
from .consts_ways import TAIL_CUT_FT as TAIL_CUT_FT
from .consts_ways import TRACK_FABRIC_GAP as TRACK_FABRIC_GAP
from .consts_ways import WAY_END_REACH_FT as WAY_END_REACH_FT

# The lane and web clearances live in consts_ways.py (feature 405 T130, the 1,000-line bar) and are re-exported here by name.
from .consts_ways import WEB_CLEARANCE as WEB_CLEARANCE
from .consts_ways import WEB_CROP_GAP as WEB_CROP_GAP
from .consts_ways import WEB_FABRIC_GAP as WEB_FABRIC_GAP
from .consts_ways import WEB_HARD_GAP as WEB_HARD_GAP
from .consts_ways import WEB_REACH_FT as WEB_REACH_FT
from .consts_ways import WEB_SHADOW_FT as WEB_SHADOW_FT
from .consts_ways import WEST_SUN_FT as WEST_SUN_FT

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
# 0246's 7 FT AS IT STANDS (feature 328 wave 48). Held at 40 from wave 7: the corridor is a CENTER test (`_near_corridor`), so 7 ft
# would have let a building's body stand on the tread, and 40 carried the 7 ft to a center by the minka's half-diagonal. The
# FOOTPRINT is now held there exactly - every corner `LANE_MIDDLE_CLEAR_FT` off a lane's middle (`houses._on_a_tread`) - so the
# corridor carries the page's figure. Measured before the change: no pool hamlet moved with the corridor at 7 ft, the houses
# being seated before the lanes are drawn.
LANE_CLEARANCE = 7.0
"""Research: fronting lane's corridor - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle 7 ft clear of a garden fence, the footprint held to it at its corners (`houses._on_a_tread`)"""

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
"""Research: cluster's reach along the field edge - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 1.6 of the band's half-extent"""

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
# THE SPACING BETWEEN ROWS IS SET BY THE THRESHING YARD'S SUN - and since feature 385 T09 that spacing is
# `homesteads.stages._rank_step` (0038's house, yard and 39 ft of sun), not this number, which once stood for it. The spacing of
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
# So THIS number is a planning span along the rows and nothing else: nothing pays 100 ft east-west. See
# specs/126-derived-lanes-and-form/research.md R8.
#
# RAISED 92 -> 100 when the SUN CORRIDOR landed (2026-08-13), when it was still taken for the row pitch. The pitch was calibrated before the
# rule existed, and a row now needs house depth (28) + yard (~26) + 39 ft of sun + the gaps between
# them, which comes to about 100 rather than 92. Asking the band for less than a row needs does not
# make the cluster tighter - it makes the placer spill the overflow OUTSIDE the band, which is how
# seed 18 grew a two-farm satellite 500 px off the nucleus, 777 px from the nearest water against a
# 760 px reach, with every legal well seat around it already taken by its own two courtyards.
BUNDLE_PITCH = 100.0
"""The along-row span: the step between homesteads along a row, and the grids' and the web's spans that borrow it. It is NOT the
distance between rows: the ranks stand `homesteads.stages._rank_step` apart - a homestead's depth and the yard's 39 ft of sun
(`SUN_CORRIDOR_FT`), 0038's "rows set 92 ft apart" (feature 385 T09: this claim once called 100 ft the row pitch, on 0038).

Research: the along-row span - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 100 ft, the step along a row and the grids' spacing; the rows themselves stand `_rank_step` apart, 0038's house, yard and 39 ft of sun"""

# THE GROUND ONE HOMESTEAD TAKES, as the side of a square (feature 280 M16 merged into feature 287, 2026-09-29): the seat
# band's AREA (`plan.band_extent`, `households x HOMESTEAD_GROUND_FT^2`, which also sizes the canvas's room for the seat).
# It was `BUNDLE_PITCH`, and grows with the yard: 280 moved the rice hamlet's yard median from 18 to 25 tsubo, and at the
# apron's 1.45 aspect the median yard is sqrt(18 x 35.583 / 1.45) = 21.0 ft deep before and sqrt(25 x 35.583 / 1.45) =
# 24.8 ft after - 3.8 ft more yard, added to the along-row span as the band's margin, so 104. The along-row span stays 100: it plans offers the placer
# staggers from (and the web's reach is tied to it, `WEB_REACH_FT`). MEASURED (`make cohort N=1 SEED=<n>`; a detached
# worktree at 287's HEAD passes seed 18): with the band at 100 the merge held 13 of seed 18's 15 households on its best
# margin and refused the site; with the band at 104 all 15 seat. Raising the along-row span to 104 as well seated seed 18 but
# left one farmhouse off the way network on seeds 11 and 43 - measured and not taken.
HOMESTEAD_GROUND_FT = 104.0
"""The ground one homestead takes, the pitch the cluster band is sized on.

Research:
    the yard within it - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: 25 tsubo
    ground per homestead - research/questions/0285-how-big-was-a-farmhouses-lot-in-a-clustered-village.drawing.html: 104 ft square (about 305 tsubo), a map drawing convention sized by
        what the seating needs, above the typical attested lot (157 tsubo, the 1698 register's median); the attested sizes do not fit
        (75 ft: 49/54, 90 ft: 51/54 of the cohort, 405 T112)
"""

# THE GROUND THE SEATING SPREADS ITS HOUSEHOLDS OVER, as the side of a square (feature 306, FR-010; a map drawing
# convention, recorded on 0285's drawing page by 405 T112 - no lot holds the wood floor it counts): `HOMESTEAD_GROUND_FT` counts the house, its yard and the row, and NOT the household's
# wood floor, which 269 B26 added after it (`HOMESTEAD_WOOD_FT2`, 6,000 sq ft at least, within the copse's reach of the house).
# Seated over a band of that size a village sat at the edge of its capacity and whether a margin filled was near chance - seed
# 47 at 40 households seated sixteen margins before one held everyone (specs/306-seat-by-packing/research.md R2, R6). The band's
# AREA is the households' SUM, so this is the side of a square holding the MEAN homestead: the pool's 82 envelopes' mean
# (`geom.bbox`, 20,366 sq ft) and the least wood floor, sqrt(26,366) = 162. It sizes only the band the SEATING spreads its offers
# over (`homesteads.stages._seat_households`: the lattice and the seat bound); the margin's choice, the canvas's room and the belt
# keep `HOMESTEAD_GROUND_FT`'s band - growing those as well re-fitted every field and refused sites the base seated (R11, R12).
SEATING_GROUND_FT = 162.0
"""Research: seating ground per homestead - research/questions/0285-how-big-was-a-farmhouses-lot-in-a-clustered-village.drawing.html: 162 ft square, the mean envelope plus the least wood floor - a
map drawing convention, holding the wood floor a lot need not (405 T112)"""

# `carve_comb`'s GRAIN, and why this tier passes the PRINCIPLED value rather than the pool's.
#
# `grain` scales the carve's real-feet thresholds AND the channel widths. `carve_comb`'s docstring
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
# settlement-review) rather than an oversight - `carve_comb`'s docstring carries the same account.
GRAIN = 2.0

# THE HAMLET BAND (research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.html): 10-20 households, 50-100 inhabitants. Below
# 10 the place is an outlying farmstead or two rather than a hamlet; above ~20 it is a small village
# and grows the features a hamlet must not have (a headman, a shrine, tax-free plots).
HOUSEHOLD_BAND = (10, 20)
"""Research: hamlet household band - research/questions/0001-the-five-sizes-of-settlement-hamlet-village-town-provincial-city-and-capital.drawing.html: 10 to 20"""

# The reference fan, at Ikegami's 15 households: the comb builder's lengths that produced it. Every
# other size is this fan scaled by a single multiplier (see `fit_field`), so the fan's ASPECT - the
# thing that makes a comb read as a comb - is a constant of the tier and only its area varies.
REF_HOUSEHOLDS = 15
REF_FIELD_FALL = 1150.0
"""Research: reference fan's fall - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 1,150 ft, Ikegami's hand-drawn fan"""
REF_CANAL_A = (1250.0, 1450.0)
"""Research: reference fan's canal A - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 1,250 to 1,450 ft, Ikegami's hand-drawn fan"""
REF_CANAL_B = (680.0, 800.0)
"""Research: reference fan's canal B - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 680 to 800 ft, Ikegami's hand-drawn fan"""

# ...and its ASPECT is rolled, which matters more than it sounds. `fit_field` scales the reference
# fan by one multiplier, so without this every hamlet of a given household count and fall direction
# gets the SAME fan silhouette - the review of the first draft found Inashiro's field outline was a
# byte-for-byte translation of Ikegami's, vertex for vertex, because the reference lengths ARE
# Ikegami's and its multiplier came out at 1.0. A cohort of maps that share their largest object is
# a cohort of re-skins. Trading fall length against canal length leaves the AREA alone (so the
# acreage solve is untouched) and changes the shape: a long narrow valley fan against a broad
# shallow one.
FAN_ASPECTS = (0.88, 0.95, 1.0, 1.08, 1.16)
"""Research: fan aspect - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); 0.88 to 1.16 fall against canal, rolled"""

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
# convention on the record's words, not a finding.
COPSE_HOUSE_REACH_FT = 90.0
"""Research: copse among the houses - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: within 90 ft of a house"""

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
    lane skeleton - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: spine, T, Y or cross wherever no water runs along the cluster
    lane along the water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the fifth lane shape, a lane along the water, joins the roll where a brook runs along the cluster's flank (LANE_SKELETONS_BY_WATER)
"""
# THE LANE ALONG THE WATER (feature 374 wave 138, plan W138-1): 0031's drawing page gives a village's lanes five shapes,
# the fifth "a lane along the water in a village by a stream", needing "water running along the cluster". The seat is
# fixed before the brook's place against the houses is known, so the fifth shape is offered where the skeleton is laid,
# after the houses (`ways/web.py`): a brook runs ALONG the cluster when it passes within WATER_ALONG_FT of one flank of
# the houses' extent over WATER_ALONG_SHARE of its depth. Both numbers are a GUESS - the page names no band - set so a
# brook skirting the houses' side qualifies and one crossing the field below them does not. The village tier asks the
# same question of its declared site (`settlement/_knobs.py` `_lane_skeleton_ok`: a stream-fed or waterside site); the
# hamlet measures its drawn brook instead, since a hamlet declares no such site.
LANE_SKELETONS_BY_WATER = (*LANE_SKELETONS, "waterside")
"""Research: lane along the water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: five shapes where water runs along the cluster, each even odds"""
WATER_ALONG_FT = 120.0
"""Research: water along the cluster - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a brook within 120 ft of a flank of the houses"""
WATER_ALONG_SHARE = 0.6
"""Research: water along the cluster's depth - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: over three fifths of the flank"""
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
# ...and its SHELTER (feature 374 wave 153): every farm's own grove on its windward sides whichever side its street runs, or
# the leeward row sheltered by the grove row across the street, its bamboo set south - the two forms 0033 records (the
# Musashino farms). No page gives shares between them: even odds, a GUESS. Drawn only where farms stand on BOTH sides.
ROW_SHELTERS = ("own_grove", "sheltered")
"""Research:
    row village's shelter - research/questions/0033-row-villages-resson.drawing.html: the grove kept windward whichever side the road runs, or the bamboo set south where a row of grove farms across the road already broke the wind
    even odds - GUESS: no page gives shares between the two forms"""
# ...and a clustered hamlet's WELLS (feature 374 wave 154): by the lane, on its verge, or in the open ground among five to
# ten houses - the two forms 0196 records as a knob. No page gives shares between them: even odds, a GUESS.
WELL_SITINGS = ("lane", "cluster")
"""Research:
    the wells' siting - research/questions/0196-communal-wells-ido.drawing.html: by the lane or among the houses, a knob
    even odds - GUESS: no page gives shares between the two forms"""

WELL_VERGE_FT = 8.0
"""How far past a lane's tread a lane-side wellhead's curb may stand, and how far a cluster-form well keeps the lanes laid
after it: a lane's verge, clear of the tread (0196; feature 374 wave 154).

Research: on the lane's verge - GUESS research/questions/0196-communal-wells-ido.drawing.html: the curb within about 8 ft of the tread, a GUESS the page names"""
# A DISPERSED farm's own water (feature 291 amendment 5; homesteads/200): a small channel led off the irrigation water into
# its grounds - the Tonami museum: "in many areas a small channel was led into the house's grounds", the fan's water table
# too deep for a well (ACCURATE) - or its own well, the other areas as this record reads them (a GUESS). Even odds, a GUESS.
FARM_WATERS = ("channel", "well")
"""Research: scattered farm's water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a channel or a well, even odds"""

# Where the hamlet's bamboo stands (feature 133 T47; the `bamboo` knob's roll table). Weighted so a
# temperate lowland hamlet usually has one - the research puts bamboo below the frost line as a
# matter of course - and "none" is the cold-upland minority. Read the knob's note in `_knobs.py`.
BAMBOO_FORMS = ("homestead", "homestead", "thicket", "both", "none")
"""Research:
    where the bamboo stands - research/questions/0075-bamboo-groves-chikurin.drawing.html: farmsteads, a thicket, both or none
    the forms' odds - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P7, 2026-10-25); homestead 2 in 5 and the others 1 in 5, where the registry's knob rolls the four evenly; no page gives odds"""
PLOT_SIZES = ("small_irregular", "medium", "medium", "large_block")
"""Research: paddy plot size - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a hamlet basin about 48 ft across its canal and 26 to 36 ft along it, some 40 to 60 ft across, larger (about 0.07 acre) only on a valley hamlet's map - the medium size is the page's; the small (34 ft across) and the large block (70 ft) fall outside 40 to 60 ft, the large block on any hamlet, a departure the code keeps until feature 417 T34; the odds, small 1, medium 2, large block 1, are a GUESS"""
GRAIN_DRIFTS = (-8, -4, 0, 0, 4, 8)
"""Research: furrow drift - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: -8 to 8 degrees off the contour, turning
    only the dry fields' furrow rows (carve.py theta0); the paddy grain never drifts, and the registry's grain_drift runs -12 to 12"""
