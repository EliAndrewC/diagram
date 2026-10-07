"""The hamlet's water constants: the brook, its intake and weir, the fords, the delivery ditches and the runoff.

Split from consts.py by feature 316 (the 1,000-line bar); bodies verbatim, and every name here is re-exported from consts.py,
so callers keep importing them from there.
Research: water plumbing - NONE: every constant here with no claim of its own
"""

from __future__ import annotations

# How far below the drain outfall a tameike may stand before the map is better off without one.
# Calibrated against the drawn ponds: an ordinary set-back lands well under 200 px, and the case
# that motivated the limit was 575. See `stage_sink`.
POND_SETBACK_LIMIT = 300.0
"""Research: tameike set-back limit - UNRESEARCHED: 300 ft below the outfall"""

# THE INTAKE, AND THE BROOK THAT RUNS ON PAST IT (feature 230, GM 2026-09-12; researched -
# research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html). A brook does not
# turn into a ditch: it is TAPPED at an intake on one bank and keeps its own course below it, so the
# hamlet's brook now passes the fan's head and runs on down one flank to the frame.
#
# THE INTAKE'S FORM IS A KNOB (research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.html) because the record
# attests two and prefers neither: in old Japan "in many cases no intake weir was built at all - water was taken naturally", and where the level would not serve
# a weir was built, of timber frames packed with stone, gabions and brushwood. The record gives no
# proportion between them, so the roll is EVEN and that evenness is a GUESS (labeled in the entry).
INTAKE_FORMS = ("weir", "open")
"""Research: intake form - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: weir or open mouth, even odds"""
# WHICH FLANK the brook passes the fan on - DERIVED from the wind, not rolled. The cluster is seated on the
# margin whose outward normal points into the wind (背山面水, back to the hill and face to the water), so the
# brook takes the other flank and the settlement stands on one side of its own stream. Rolling it was the
# first cut and `settlement-review` measured what it costs when the roll agrees with the seat: two
# homesteads, their byre, two threshing yards and their gardens stranded across the water, every lane, both
# wells and the notice board on the far bank, and a lane drawn walking into the stream. A hamlet's brook runs
# past it, not through it. The roll survives only as the tie-break where the wind runs along the fall and
# neither flank is the windward one.
BROOK_FLANKS = (1, -1)
"""Research: brook's flank - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the flank away from the seat, rolled only on a tie"""
# HOW FAR THE HEAD RACE RUNS from the intake to the division point, in feet, rolled per map. No source
# read gives a distance - the Japanese standards treat it as a site variable in the head-loss computation
# and Tabayashi says only that the small canals run "for short distances" - so the BAND is a guess; what
# is derived is the shape, a race that leaves the bank at the intake and reaches the fork.
HEAD_RACE_LEAD = (80.0, 105.0, 130.0)
"""Research: head race length - GUESS: 80 to 130 ft, rolled"""
# THE ANGLE THE HEAD RACE LEAVES THE BROOK AT, degrees off the brook's own downstream heading. An offtake
# leaves its parent pointing downstream at an acute angle - the record's own canal-junction rule, "30 or
# 45 instead of 90" - and clean mountain water is the case the angled offtake is allowed for (a
# silt-laden river takes the right angle instead).
OFFTAKE_DEG = 35.0
"""Research: offtake angle - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: 35 degrees, leaning downstream"""
# HOW FAR OUTSIDE THE CROP the continuing brook runs as it passes the fan's flank, px - the FLOOR of the
# offset, wide enough that neither the paddy's own bund nor the brook's no-build corridor touches the
# planted ground. `BROOK_WANDER` is how far outside that floor the course strays, a seeded walk rather than
# a held offset: a brook that asymptotes onto a fixed offset draws a ruled line, which is a thing the GM has
# already rejected on this very map ("appears to run exactly east to west parallel to the edge of the map.
# that makes it look like a mistake", 2026-08-26) - and a held offset also runs PARALLEL to whatever supply
# canal hems that margin, which is the two-overlapping-water-lines catch in a new place. The walk's step is
# what breaks both; its amplitude is a drawing judgment, not a researched figure.
BROOK_SKIRT = 34.0
"""Research: brook outside the crop - UNRESEARCHED: 34 ft floor"""
# ...and how far outside THAT floor the course may stray. Small, and bounded by the frame rather than by
# taste: the sheet is cropped to its hard content and a watercourse is deliberately not content (it "clips at
# the edge, trailing off as more map this way" - `crop_to_content`), so a brook that strays more than the
# crop's own margin runs outside the picture. It did: `settlement-review` measured a course drawn just beyond
# the left edge for its whole length, reappearing at the bottom, which reads as two unrelated bits of water.
# The course's variety comes from the field's own outline, which it now follows at this distance, and the walk
# only keeps it off a ruled line.
BROOK_WANDER = 10.0
"""Research: brook's stray - UNRESEARCHED: up to 10 ft past the floor"""
BROOK_WANDER_STEP = 10.0
"""Research: brook's meander step - UNRESEARCHED: 10 ft"""
# HOW FAR PAST THE FIELD's own bounds a station may sit, px - the belt to the skirt's braces, and sized to the
# crop margin (`CROP_MARGIN`, 48) so that a station inside this box is inside the picture. On a map whose land
# falls on a diagonal the first cut bounded the offset in the FALL's frame, which is not the frame the sheet is
# cropped in, and 77% of the brook came out beyond the view in two pieces a reader cannot join.
# WIDENED TO THE SKIRT PLUS THE WANDER (feature 230, settlement-review pass 10). At 8 px the margin was narrower than the
# skirt the crop floor demands (34), so wherever the brook passed the crop that also bounds the box the two rules fought:
# a station was floored 26 px past the box, the cut points between stations were clamped back into it, and the course
# drew a V at every station - 68.7 degrees on Mizuguchi, a ruler-straight sawtooth 30 ft inside Kashikawa's frame. At
# skirt + wander a station the floor puts outside the crop is always inside the box. What kept the course on the sheet
# at 8 px is kept instead by the frame, which now reserves the brook's reach beside the field (`brook_beside_the_field`).
# Two levers were measured first and refused: this margin alone (Kashikawa's brook left the view in two pieces, 2,435 ->
# 1,520 px in view), and letting a cut point sit as far out as its nearer station (four pieces, 70 degree turns).
BROOK_FRAME_MARGIN = 44.0
# THE MOST A STATION MAY STEP ACROSS THE FALL before the step is led into over two, px. The clearance profile
# jumps when a hem plot enters it, and an un-led jump draws a mitred elbow - 67 degrees on the reference
# hamlet, against 0.3 to 18 degrees everywhere else on the same course. A stream bends; it does not turn a
# corner to get round a barley plot.
BROOK_SLEW = 22.0
"""Research: brook bends, never corners - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a step over 22 ft led in over two"""
# HOW MUCH SHORTER the fan's supply canal is on the brook's flank. The field is cut AROUND the stream, not the
# stream around the field - and a comb built symmetrically about its own intake cannot leave room for the water
# it is fed by: the fan's edge diverges from the tap at 42 and 58 degrees, so a brook keeping outside it has to
# diverge faster still, which is not a course a stream takes. Trimming the canal on the brook's side leaves the
# margin the brook runs in; the acreage solve makes it up on the other flank and down the fall, so the field is
# the size the households need either way. The figure is a drawing judgment, not a researched one.
BROOK_FAN_TRIM = 0.72
"""Research: fan cut back from the brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: brook-side canal at 0.72"""
# THE TAP'S OWN FIRST STRIDE, px: the brook runs on along the fall before it bends away to its flank, so
# that the head race really does leave it at `OFFTAKE_DEG` - the record's rule is an angle off the parent's
# DOWNSTREAM HEADING, and a brook already turning at the tap is not heading down the fall there.
BROOK_TAP_RUN = 70.0
"""Research: brook straight at the tap - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: 70 ft down the fall"""
# THE WEIR GLYPH at a `weir` hamlet's intake: an oblique bar across the brook, running diagonally upstream from the
# intake mouth as the old ones did. Half-length in feet. The full closure is a MAP DRAWING CONVENTION - half-river
# closures were the common old form and at a 7 ft brook a half-bar is a pixel or two.
WEIR_HALF_FT = 7.0
"""Research: weir across the whole brook - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: 7 ft half-length"""
# WHAT THE WEIR IS BUILT OF, AND SO HOW THICK IT IS DRAWN, in feet, by form (269 B22; research/water/300, "What was a
# village weir built of, and how thick was it?"). The weir on small water was built of what lay to hand, and four forms
# are read, so the form is a knob (`WEIR_FORM`, water/brook.py) rolled per weir hamlet, each at its own thickness:
# - `fence`, stakes with reed woven between them (the grass weir): a fence is as thick as its row of stakes; 1.5 ft is
#   WIDER than that so it can be seen at all - a MAP DRAWING CONVENTION;
# - `gabion`, a course of stone-filled baskets: one basket "about 40-60 cm in diameter", read as about 2 ft - the
#   basket's read size; the gabion course as a BROOK weir at all is a GUESS (the source gives gabions on rivers);
# - `frame`, stakes and logs packed with clay (the Kodera site) and `crib`, timber frames weighted with stone: 5 ft,
#   a GUESS - the only dimensions read are river works', and a crib at village scale is not recorded. 5 ft is the
#   thickness the one crib glyph was drawn at before the knob.
WEIR_THICK_FT = {"fence": 1.5, "gabion": 2.0, "frame": 5.0, "crib": 5.0}
"""Research: weir forms and thickness - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: four forms, 1.5 to 5 ft"""
WEIR_SKEW_DEG = 30.0
"""Research: weir runs diagonally upstream - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: 30 degrees"""

# DELIVERY-DITCH DENSITY by household count. A comb's offtakes are how many delivery ditches drop
# off the supply canal; too many on a small fan waters the same ground twice (build_comb drops the
# redundant near-pairs itself, so an over-dense request is silently thinned - which is worse than
# asking for the right number, because the drawn net then no longer matches the declared one).
# Ikegami's 15 households run a deliberately SPARSE two-offtake net.
# ...and the LAST offtake sits near the canal's end for a reason of its own. Whatever length of
# supply canal runs on past its last delivery ditch is a TAIL, and a tail that ends outside the
# planted extent is runoff dying in bare ground (`watercourse_ends_reach_water`; the gate allows a
# tail that dies at the crop edge, which is what a real canal does - it peters out where the last
# plot it waters ends). Ikegami's authored (0.30, 0.66) leaves a third of the canal as tail and gets
# away with it because its fan happens to be wide there; across a cohort of twenty that came back as
# one dangling collector. A last offtake at ~0.88 - which is also `build_comb`'s own default - keeps
# the tail short and inside the rice.
# ...AND EVERY ROW DRAWS CANAL B (GM caught Inashiro's bare west margin 2026-08-16; researched -
# research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html). A gravity canal commands
# only the ground BELOW it, and the carve plants paddy on BOTH sides of the bunsuiguchi fork - so
# the hamlet rows' old offtakes_b=() (copied from Ikegami's authored choice, now a frozen exhibit)
# left the whole canal-B flank carved as watered ground with no drawn water: the modeled net and
# the inked net disagreed, exactly the failure the paragraph above warns about. One offtake at
# ~0.55 inks the second arm partway down its margin, tapering to a thread (Minuma-dai divides its
# head into TWO margin canals; the Isawa fan's canals radiate from the fan head). Gated by
# comb_supply_commands_both_flanks.
OFFTAKE_LADDER: tuple[tuple[int, tuple[float, ...], tuple[float, ...]], ...] = (
    (11, (0.36, 0.93), (0.55,)),
    (21, (0.30, 0.62, 0.93), (0.55,)),
    (99, (0.26, 0.52, 0.78, 0.93), (0.6,)),
)
"""The delivery-ditch fractions along canals A and B, by household band.

Research:
    delivery ditches by size - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: canal B always feeds one
    canal B's single delivery ditch at 0.55-0.6 (0053 drawing: the second canal feeds at least one) - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the second canal feeds at least one delivery ditch; its position is UNRESEARCHED
    delivery-ditch count and positions - UNRESEARCHED: 2, 3 or 4 offtakes under 11, 21 and 99 households, the last at 0.93
"""

# THE BROOK IS CROSSED WHERE A WAY NEEDS TO CROSS IT (feature 261, the GM 2026-09-27: "fix the placement algorithm
# instead"). The record puts a settlement's own small channel through the middle of the place (the Harie finding,
# feature 230), and the engine refused every seat the brook ran through or ran between the houses and their rice
# only because no way could cross it. Now the routing corridor round the brook has a gap at a ford every
# `FORD_SPACING` along its course, on a straight reach, and `bridges()` decks whatever crosses there.
#   FORD_HALF: half the gap, px. The router keeps 14 px off water and plans on a 10-14 px lattice, so a lane
#     threads a gap only when its half-length clears the corridor by a cell (14 + 14); and a gap no longer than
#     the corridor is deep lets a way through only near square - about 40 deg from square at most, the same
#     bound `shallow_crossing` holds every other crossing to. A map drawing convention, not a finding.
#   FORD_SPACING: px along the brook between fords. A guess: often enough that a field path never walks far to
#     one (the record gives no spacing for field-path crossings; searched 2026-09-27, see research/contents.json#ways).
#   FORD_BEND_DEG: a site where the brook turns more than this across the gap is skipped - a deck across a bend
#     is not square to both reaches.
FORD_HALF = 30.0
"""Research: crossing place's length - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: 60 ft gap, crossed near square"""
FORD_SPACING = 160.0
"""Research: crossing places along the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: every 160 ft"""
FORD_BEND_DEG = 20.0
"""Research: crossing on a straight reach - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: none where the brook turns over 20 degrees"""

# A NATURAL BROOK DOES NOT DOUBLE BACK (feature 261, settlement-review of Sawada): no vertex of the drawn course turns it
# more than this. The pool's brooks turn at most 41-53 deg anywhere on their meandered courses; 100 deg is well above that
# and well below the 113-131 deg folds the exit has produced at the frame edge. A map drawing convention.
BROOK_MAX_TURN_DEG = 100.0
"""Research: brook never doubles back - UNRESEARCHED: no turn over 100 degrees"""

# A BROOK TURNS ON A CURVE (feature 261, settlement-review of Sawada): every corner of the drawn course is filleted at this
# many widths of its drawn bed, the ratio the ditches have been drawn at since 2026-07-25 (`fillet_polyline`,
# research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: sharp corners belong to stone-lined channels, and nothing
# on these maps shows one) - Sawada's brook drew mitred corners of 27-47 degrees. Rounded at the end of the water stages
# (`round_the_brooks` in `stage_sink`, feature 287; the crossings stage until then) by `finished_course`, and held at
# the tap the head race leaves from. A map drawing convention on an accurate rule.
BROOK_BEND_WIDTHS = 2.5
"""Research: brook's bend radius - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: 2.5 bed widths"""

# WHAT A WAY PAYS TO CROSS THE BROOK (feature 261, settlement-review of Kashikawa). Fords made the brook passable, and
# at no cost the router took any ford that was a few feet shorter: a lane crossed the brook and came straight back to
# reach a house on its own bank - two planks built to save a short walk. A crossing is one more thing to build and keep,
# so the router charges it as this much extra walking; a way that has to reach the far bank still crosses. 150 ft is a
# GUESS (no page read prices a plank against a detour), about the length of a house row, recorded in research/questions/0035-villages-beside-their-stream-one-bank-or-both.html.
BROOK_CROSSING_COST_FT = 150.0
"""Research: cost of crossing the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: 150 ft of walking"""

# WHERE THE FIELD'S RUNOFF GOES. Both are ordinary; the GM's brief names both in one breath ("the
# drainage ditch feeds into a pond, though it could just as easily have run off the edge of the map
# with the understanding that that would have somewhere off map fed into a stream"). `pond` is the
# tameike reservoir at the low foot - the Ikegami case, and the one that gives the map a named
# feature; `offmap` lets the drain brook leave the frame, which is what most real valleys do.
SINKS = ("pond", "pond", "offmap")
"""Where the field's runoff goes.

Research:
    where the runoff goes - research/questions/0060-field-drains-akusuiro.drawing.html: a pond at the foot (a GUESS there) or off the map
    sink odds - UNRESEARCHED: pond two in three, off the map one
"""
