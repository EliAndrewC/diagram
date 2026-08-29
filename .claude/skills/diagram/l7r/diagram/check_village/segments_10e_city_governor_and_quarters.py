"""Gate segments (city governor and quarters; keys 0563_195-0563_251) - bodies verbatim, registry order preserved."""


# the government compounds (governor's mansion + ministry offices) sit inside, clear of the
# barriers. (The governor's YAMEN is legitimately a large walled compound - a whole city block,
# dozens of buildings inside, drawn here as walls-only - so its size is fine; it must just not
# cross the rampart.)


# the governor's mansion is the GRANDEST compound - a city-block yamen, at least as large
# as any samurai estate and several times any single ministry office


# a planned city's government offices FRONT its streets - the yamen sits where the main
# streets cross and the bureaus line the avenues around it (Chinese official street /
# jokamachi grid), so every ministry must sit on a street, not float mid-block


# a walled city SEALS its samurai/government quarter off the commoner streets with kido
# (wooden ward gates), not internal ramparts: full walled wards are a great-capital / Tang
# feature, over-scaled here, so a provincial city gates the quarter's street entries instead


# CAPITAL-INVERTED (021): the capital adopts the ward MESH (kido at machi mouths;
# yashiki walls seal the samurai streets). Either form is the interior-gate doctrine,
# which meta(ward_gates=False) turns off for a city that does not use it - there is
# then nothing to seal with (GM 2026-08-10).


# ...and that ward must be SEALED: a continuous fence whose ends abut the city wall, that
# a street pierces ONLY at a kido gate. Otherwise the gates can just be walked around, and
# the road network connects samurai to commoner with no gate between them.


# ...same mesh doctrine, same knob


# ...and the fence ends must actually TOUCH the wall - a gap (even a small one, which the
# coarse 45px seal tolerance lets slide) means commoners can simply walk AROUND the end of
# the fence. The end must abut the rampart within ~10px (about the wall's own half-width).


# THE FENCE SEALS COMMONERS OUT - so nobody it seals out may LIVE inside it (GM
# 2026-08-02, on Minami: 2 laborer houses in the middle of the samurai neighborhood
# and a merchant row hugging the inside of the west fence, leaked in by whole-interior
# top-up sweeps whose rectangles overlap the ward). Historical grounding: an Edo-era
# jokamachi zoned samurai and chonin ground apart as a matter of LAW (bukechi vs
# chonin-chi), and a Chinese provincial seat likewise kept commerce off the yamen
# quarter - a laborer terrace between two samurai houses inside the palisade is not
# variety, it contradicts the fence around it. Only samurai dwellings, their live-in
# domestics (servant - the gens interleave them deliberately) and government ground
# belong inside. monk_house is deliberately NOT barred: a temple may stand inside the
# ward (Tango's Bishamon precinct - the warrior fortune beside the garrison quarter)
# and its clergy row belongs with its temple, held there by the temple-neighborhood
# checks. Classification family: CENTER-tested on purpose (a building belongs to ONE
# ward; see "Centers, footprints, and aggregates" in the skill CLAUDE.md).


# ...and the residents who ARE admitted must be housed the way the ward houses them.
# A samurai household's domestics lived in the perimeter nagaya that forms the plot's
# street boundary, in the nagayamon gate rooms, or in nando off the kitchen - never in
# a freestanding house in the buke-chi; a Chinese elite compound puts them in the
# daozuofang, the south row whose blank back IS the street wall. Ranks of small uniform
# dwellings are real, but they are ashigaru kumi-yashiki on the town FRINGE. So every
# servant inside the fence must carry `of` (its master's house), ABUT that house, and
# be a RANGE rather than a cottage. GM 2026-08-02, after the barred kinds were evicted
# and the packs refilled the same ground with servants: "I swear I'm seeing way MORE
# commoner houses in the samurai neighborhood now!" - the servant glyph is a laborer
# glyph with a 4 ft trim, so detached-and-ranked reads as exactly what the fence
# excludes. The COUNT is canon and is not what this polices (budgets.md: 72 of a
# provincial city's 120 servant families are attached to its 60 samurai households);
# the ARRANGEMENT is. Research: research/cities/government.md.


# the ward FENCE runs in OPEN ground - it must not pass THROUGH a building, a mausoleum, or
# another ward's fence (GM, 2026-07). The packs keep off the fence via s.ward's corridor, but
# a hand-placed compound (the mausoleum) or a diagonal fence segment can still cut through one.


# a KIDO is a gate THROUGH the fence, so it must sit ON the fence (overlap it), not beside it
# (GM, 2026-07: a gate next to rather than part of the wall does not work). Its crossing point
# must lie within ~8px of a fence segment so the gate visibly straddles the fence.


# ...and where the fence meets the wall, the city WALL must render ON TOP (the fence runs
# UNDER the rampart). The fence is drawn late (high z), so without a wall cap on top of the
# junction it paints over the wall stroke. s.ward records the fence z and the wall cap it
# lays over each end; the cap's z must be above the fence's.


# the extramural samurai estates all lie TOWARD OTOSAN UCHI (the Imperial capital) - a
# samurai builds his country seat on the capital-facing side, so the direction is
# per-city: meta(capital_dir=<cardinal>) (Tango SE, Nagahara NE). Each estate must sit in
# the correct half-plane(s) for that direction (a diagonal requires BOTH axes).


# ... and clear of the ROADS leaving the city (an estate straddling the highway blocks it -
# GM, 2026-07: a Nagahara estate sat on the bridge road). Test each outside estate footprint
# against every recorded road.


# the ground circulation (streets + alleys; NOT the Imperial road, which exits at the
# gates) must stay INSIDE the wall and clear of the moat - separate checks, since a lane
# can poke through the rampart, the moat, or both (the elliptical wall curves in, so a
# lane run to the block edge can spill outside even with its vertices nominally interior)


# a way WHOLLY outside the rampart is the SUBURB's own circulation (021: the kashi
# belt and guan-xiang wards keep streets and roji like any machi) - only a way that
# CROSSES the wall, or an inside way poking out, is the defect


# farm fields (in-wall plots OR the surrounding farmland) must not cut across the wall stroke
# or the moat - the moat sits between the wall and the close-in fields, so they abut, not overlap


# the in-wall pond is a water source, not a moat - it must not touch the wall or moat
