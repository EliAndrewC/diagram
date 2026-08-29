"""Gate segments (city civic and commerce; keys 0563_045-0563_077) - bodies verbatim, registry order preserved."""


# civic amenities ported up from the town tier (a city is a bigger version of the same):


# a CITY theater stage is bigger than a town's (towns run a viewing ground ~150 wide) - a provincial
# city draws a larger crowd, so its viewing ground is wider (>= 185, the city baseline)


# FIRE DEFENSE: a city's dense quarters each need a fire-watch tower (hinomi-yagura). WHY:
# settlements.md "Fire towers". Opt out per-map with meta(fire_tower=False).


# A NAMED civic building's label must sit on ITS OWN building, never on a DIFFERENT one of the
# same kind. labels_clear_of_other_buildings lumps every ministry into one "ministry" GROUP, so
# it permits a ministry label to sit on a SIBLING ministry (the "Ministry of Justice" label
# drifted onto the "Ministry of Works" office). This catches that finer case: a label that names
# a civic building (a ministry by name, the governor's yamen, a named temple) must not overlap
# any OTHER named civic building.


# GOVERNMENT OFFICES stand in their own ground - a ministry or the governor's yamen is a large,
# important compound and must not ABUT another structure. Ordinary city houses may touch each
# other, but a government office keeps a clear gap from every other building/compound around it.


# every solid footprint, from the registry - an office must not abut a martial hall or a
# brewery any more than it may abut a house (GM 2026-07-25; see solid_structs). The FUNERARY
# compounds are the one deliberate exclusion: the ruling clan's walled crypt standing against
# the governor's yamen is a real adjacency (the house's dead beside the house's seat), not a
# packing error, and Nagahara has drawn it that way since long before this check read the
# registry. Burial ground siting has its own battery (funerary_clear_of_fields, the
# burial-ground checks); this rule is about a bureau not being crowded by ordinary premises.


# PUBLIC WELLS: ensuring every commoner could draw water was a defining civic concern of a
# premodern city. A communal well (the idobata) served a courtyard / cluster of ~10-20
# households, so the warren is dotted with them - one within a short walk of any home. The
# underground half of the system (aqueducts, cisterns, rain barrels feeding the shafts) is too
# small or literally subterranean and stays OFF the map; only the wellheads show.
# PRIVATE wells (private=True - e.g. the brewery's own courtyard well, GM 2026-07-24) are
# premises fixtures, not neighborhood infrastructure: they serve no commoner households, so
# they are excluded from ALL the public-well accounting below (reach, density, block-interior
# siting, the samurai-ward ban) - exactly as samurai compounds' implied private wells are.


# a city ON the Imperial road LINES that road with COMMERCE (shops + traveler inns): the
# through-road is the city's prime frontage, where caravans and travelers pass, so it must not
# run bare. This holds for ANY city with an Imperial road, WALLED OR NOT - a city WITHOUT a road
# has no such ribbon (its commerce stays in the market district). The road's portion running
# THROUGH the city is judged: bounded by the WALL if there is one, else by the URBAN FOOTPRINT
# (the bbox of the city's buildings). Scaled to that length at ~1 commercial frontage per 130px,
# a floor that catches a bare spine.


# two lanes (streets/alleys) heading STRAIGHT at each other and stopping just short, with nothing
# between them, should simply CONNECT - a near-miss reads as a mistake, not a deliberate dead-end.
# (Unlike city_streets_no_near_miss, which only compares street-vs-street segment proximity, this
# catches ALLEYS too and the aligned end-to-end / T case, and ignores gaps a building/fence/wall
# genuinely blocks.) Generic to any city with lanes, walled or not.
