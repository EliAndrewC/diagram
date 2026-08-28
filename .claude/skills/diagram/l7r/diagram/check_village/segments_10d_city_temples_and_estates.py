"""Gate segments (city temples and estates; keys 0563_126-0563_194) - bodies verbatim, registry order preserved."""


# ... and clear of the HOUSING: the kido + its guard box occupy a fixed crossing that the
# packs cannot see (s.ward draws long after the quarters are built), so the gen must
# RESERVE each gate's ground (block_polys) before any pack runs - else a row house lands
# under the guard box (GM, 2026-07: caught twice, on both fence-end gates)


# a walled city has a RING ROAD (順城街) just inside the rampart - the wall-clear patrol zone a
# fortified city keeps for moving troops along the wall; the quarters pack INSIDE it (s.ring_road
# returns the loop to use as s.bound).


# a street running toward a THROUGH-LANE (the Imperial road or the ring road) must MEET it
# cleanly at a T-junction: its bed reaches the lane's bed and ENDS there - neither a sliver
# SHORT of it (an undershoot, the street appears to dead-end in open ground) nor a sliver
# PAST it (an overshoot, the street pokes through to the far side instead of stopping at the
# junction). A genuine crossroads, where the street truly continues well past the lane, is
# fine - only a short stub poking through is wrong. (The ring road is gated where it crosses
# the ward fence, so even the government quarter's lanes may give onto it without un-sealing.)


# streets AND alleys: a gravel alley that runs straight at a through-lane and stops a sliver
# short of it (the laborer warren's east lane stopping just shy of the east ring road) should
# reach it too, just like a paved street


# the RING ROAD is a CLEAR patrol road: it must run clear of EVERY solid footprint and of
# fields. The gate guard houses / inspection stations / towers DO sit along it (wall
# furniture - `gate_structs` and `wall_towers` are overlap TARGETS and EXEMPT respectively,
# so the registry leaves them out), and a ward fence may cross it - but only at a gated kido
# (enforced by city_samurai_ward_sealed, which has the ring road in its netlines). Overlap =
# the ring's BED passes through a footprint.
#
# READS THE REGISTRY, NOT A HAND LIST (GM 2026-07-25). This check used to name its own eight
# keys, so every new feature had to be remembered into it - and the martial hall, correctly
# classified and correctly cleared of all thirteen no_structure_on_* hazards, sat squarely on
# Tango's ring road with the gate green because nobody had. See solid_structs' docstring.


# WHY (a walled city cannot do without burakumin labor during a siege, so some live inside): settlements.md "Historical grounding"


# ... and the shown estates are DISPERSED, not a tight cluster: each is its own walled compound
# on its own landholding with fields between, so no two sit adjacent. A packed clump at one
# stretch of wall is the COMMERCIAL SUBURB's density, not the genteel country-estate pattern -
# gentry estates scatter by land/scenery, they do not ring the moat (GM 2026-07-22, researched:
# China-first absentee-landlord + dispersed-fortified-manor pattern, Japan agreeing). See settlements.md.


# WHY (the extramural samurai residence is the walled, defensible country ESTATE; a lone
# UNWALLED samurai house beyond the rampart is defenseless and belongs in the sealed ward
# inside): settlements.md "Historical grounding". Hard-zero - the estates rule above is
# exactly why the commoner inside-walls check exempts samurai, so this closes that gap
# (validated instance: Tango's SE top_up sweep leaked 14 houses into the moat berm, 2026-07-20).


# scattered country estates each front their OWN approach lane (not drawn at this scale), so
# their depicted (formal) gates do NOT all open the same way - a uniform direction is the
# unconsidered default. The formal gate favors the auspicious south; others face the cityward
# approach (the cityward service gate, like the governor's, is omitted at this scale).


# all city temples INSIDE the walls, and clear of the wall stroke and the moat


# THE LABELED (major) CITY TEMPLES ARE DEDICATED TO THE CLAN'S TWO PATRON FORTUNES. Hantei
# X codified that every city holds a temple to each of its clan's patron fortunes (l7r.md);
# the two GREAT temples honor those, and a smattering of small wayside shrines fills the
# rest. Declare meta(clan=...); the labeled temples (kind="temple", not "small_shrine")
# must be exactly the clan's two fortunes. Override with meta(temple_fortunes=[...]) for a
# city that changed hands. GM, 2026-07: Nagahara (Crab) had a large Temple of Suitengu -
# a thematic pick, not a Crab patron (Crab = Bishamon + Ebisu). Named after "Temple of X".


# MORE THAN TWO MAJOR TEMPLES IS THE MARKED EXCEPTION, AND IT MUST BE DECLARED (feature
# 016). settlements/religion-and-death.md has enumerated the recognized justifications
# since it was written, but nothing enforced them - so a city could quietly draw six
# temples and ship green, which is the "a check that never RUNS looks exactly like a
# check that passes" shape one level up: the RULE existed and the check did not. The
# declaration is meta(temple_exception=...), from the fixed TEMPLE_EXCEPTIONS vocabulary.


# a TEMPLE NEIGHBORHOOD (>= 2 temples clustered together) should be dotted with a smattering of
# small wayside SHRINES (s.small_shrine - non-residential, kind 'small_shrine'). A lone temple
# among houses (e.g. the warrior-fortune temple in the samurai quarter) is not a neighborhood.


# ADEPT-MONK HOUSING (GM 2026-07-24). A city temple is a blank-court COMPLEX like the
# governor's yamen - the subject of its own Mode A diagram, a big walled rectangle on the
# city map - and its celibate resident monks live INSIDE the precinct, implied. But a
# share of each complex's 15-30 monks are married ADEPTS (adepts marry and raise
# children), and those households keep ordinary homes in the temple's neighborhood. So
# every major temple needs >= 2 dwellings of kind "monk_house" within ~170px - drawn
# deliberately identical to a laborer house (no label, no glyph of its own; the manifest
# kind exists so this check, the budget, and the population math can see households the
# caste bands must NOT count - clergy are not a lay caste).


# the outside samurai estates: no overlapping each other, none over the wall or moat


# the WALLED MERCHANT ESTATES (their court, not just the house inside) must likewise sit clear
# of the rampart, the moat, and any other building. (The estate's OWN inner house, centered in
# the court, is fine; everything else - temples, compounds, other homes, other estates - is not.)


# registry-driven (GM 2026-07-25): an estate court may not swallow ANY solid footprint


# a walled estate's GATE may not open INTO a building. The walls may ABUT a neighbor (very
# common historically), but the threshold just outside the gate must front OPEN ground, not
# a COMPOUND (temple, ministry, the yamen, or another estate court) - point the gate elsewhere.
