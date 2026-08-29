"""Gate segments (walls gates and housing; keys 0124-0133_030) - bodies verbatim, registry order preserved."""


# PADDY FANS ARE GAPLESS inside their command area: bare parchment inside a comb fan is
# ground the water commands that nobody planted - the "white spots" bug. The carve's minimum
# plot/sector/closer thresholds are REAL-FEET quantities (build_comb's `grain` scales them:
# tuned at 2 ft/px, a 3 ft/px city passes grain=2/3); left unscaled they silently drop
# sectors, head plots and gap-closers a village would plant (Tango/Nagahara re-exposed
# exactly this at the city grain, 2026-07-21 - the frozen fixture). Only fields that record
# their drawn "plot_polys" are gated (the city gens do; a village gen can opt in by recording
# them). The rim is inset away (canal berms / drain set-backs legitimately live there) and
# the tolerance covers bunds and the delivery-ditch strips between plot columns.


# the plot tolerance is BUND-scale (6 real ft): anything wider than a bund must be planted
# or be WATER - the field's recorded ditches count as covered ground (they draw over the
# fan), so the delivery-ditch strips between plot columns never read as bare


# ALMOST all shops front a street (commerce wants the street); POOR housing (laborer/burakumin)
# mostly packs the block INTERIOR, reached by alleys, not the paved street frontage. (The towns
# set the template: businesses on the frontage via s.frontage, dwellings interior via s.pack.)


# surrounding farmland must be WORKED: the part of each outside field that SHOWS on the map
# carries farmhouses at roughly the village/hamlet linear density (~12 per 1000px of field edge,
# min ~4). Off-map field portions have their farmhouses off-screen (fine, expected), but a field
# presenting a real on-map edge with almost no farmhouses beside it is wrong - farmers build
# close to the fields they work. We count only IN-VIEW houses against the on-map field edge, so
# a partially-rendered field is held to its SHOWN extent (the gap the old per-field >=2 missed).


# the IN-WALL agricultural district (the unusual city that farms inside its walls) is REAL
# farmland too. Unlike the SURROUNDING fields above - mostly off the cropped map, so only a
# FLOOR (7) is enforceable on their shown sliver - an in-wall field sits ENTIRELY in view, so
# its WHOLE perimeter must read as worked: ring it DENSELY all the way round, not a sparse few
# on one side leaving long bare edges. Held to a much higher density (the dense end of village
# ringing). Only bites when meta(agricultural_district=True) - most cities have no in-wall fields.


# housing packs DEEP, but no GIANT cluster may be cut off from circulation: a big block of
# dwellings with no street OR alley anywhere near it has no way in or out. Deep blocks must
# be laced with gravel alleys (s.alley) so every dwelling is reachable.


# an alley must EARN its length by UNIQUELY serving dwellings. A building is credited to its
# NEAREST lane only (the one it actually fronts), exactly as empty_street_runs scores streets -
# so a lane counts only what no other lane already reaches. This catches BOTH a lane running off
# into a half-empty corner (a "lane to nowhere") AND a redundant lane laid beside or across one
# that already serves the same block (a perpendicular arm the block's spine already reaches, or a
# second lane shadowing a parallel street). Scaled to the buildings (~1 dwelling per 30px of its
# own length), so it holds at the city's dense small-footprint grain, not a fixed town pixel gap.

# `paddy_fan_gapless` RETIRED WITH ITS WHOLE DERIVATION (feature 141's cut; the residue removed here in
# 146). It walked a grid over each paddy's outline - stepping `_g_step`, inset `_g_inset` from the rim -
# and counted the sample points that fell in no plot polygon AND near no field ditch, failing the map when
# more than max(2, 2%) of them came out bare: unplanted holes inside the comb's command area mean the
# carve dropped sectors, head plots or closers there, and the usual cause was `build_comb` being passed a
# grain whose real-feet minimum-size thresholds did not match the map's scale. Feature 141 cut it, and this
# feature removes the seven segments that stayed behind - a full grid scan of every paddy on every gate,
# the single most expensive derivation in the battery, feeding a list nothing read. The `_hq_*` chain went
# with it (its own check had already gone), including `_seg_0123___hq_ftpx` over in 02b.
