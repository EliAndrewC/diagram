"""Gate segments (city streets and docks; keys 0563_309-0563_333) - bodies verbatim, registry order preserved."""


# the Imperial-road label must sit OUTSIDE the walls (inside, the roadway is a city street)


# ROADSIDE LAND on a larger city street is PRIME real estate: a paved through-street in a
# commercial/residential quarter must be LINED with buildings (houses, shops, civic halls)
# close to it, not left with a long bare margin. This is stricter than city_streets_have_buildings
# (which tolerates a building up to ~105px away): here a building must sit WITHIN ~58px of the
# street, the way storefronts and house-fronts actually line a road. Only the narrow gravel
# ALLEYS that thread the block interiors are exempt (those are the "small streets" that need no
# frontage), and so is the GOVERNMENT avenue - its frontage is the spaced ministry compounds,
# governed by city_ministries_front_a_street, not shops/houses. (The merchant avenue once read
# bare because its storefront frontage was silently blocked by the avenue's own corridor.)


# INTRAMURAL groves OFF: a farm inside the wall carries NO windbreak grove - an in-wall plot is not
# an isolated farmstead (the urban fabric already breaks the wind) and sits on land too precious for
# a tree belt. So the in-wall agricultural district stays grove-free. WHY: settlements.md "Homestead groves".


# RIVER-CITY WATERWORKS (a cargo canal + wharf; only where they are drawn):


# (1) THE CANAL CONNECTS THE DOCK TO THE WATER, like a street reaching the road: one end
# taps the river OR hands off to the moat (the Suzhou shared-mouth pattern - the city's
# canals communicate with the MOAT, and the moat's own downstream river junction is the
# navigation entrance), the other feeds the in-city dock basin - a canal that stops short
# of the dock is a ditch to nowhere (GM, 2026-07: Nagahara's canal left a visible gap to
# the dock). "Reaches" = the end's bed physically meets the target (within the target's
# half-extent + the canal half-width + a small tolerance).


# (2) THE WHARF JETTIES REACH THE BANK: a jetty is a finger running out from the river's
# near bank into the water - its landward end must TOUCH the bank, not float mid-stream
# (GM, 2026-07: Nagahara's jetties floated in the middle of the river). The near bank is
# the river centerline offset by half its width toward the city; a jetty's nearest end
# must sit within ~14px of it.


# (3) THE LOG BOOM IS A SHORE-FAST PEN, NOT STICKS IN THE STREAM (GM 2026-08-02, "it
# just looks like a bunch of logs in the middle of the river"; the research is in
# research/urban-features.md "The log boom"). A boom is a floating fence - anchored to
# nothing it holds nothing. Attested booms anchor to the bank and run ALONG a navigated
# river, the pen between chain and shore (Susquehanna: seven miles along one side;
# St. Croix: log channels beside a navigation channel kept clear by statute); only a
# loose-log CATCH boom on an unnavigated reach ever spans the water (the Kiso tsunaba
# at the gorge mouth), never a port's holding pen. GAP-VERDICT family: both rules below
# measure the pen's DERIVED CORNERS (x/y/rot/len/pen_w, the same local frame the glyph
# draws - bank on local +y) against the river's stroked centerline; a center measure
# would condemn the good bank-hugging pen and pass the mid-stream chain (see the test
# pair). pen_w defaults to the ~14px the pre-2026-08 chain glyph drew.
