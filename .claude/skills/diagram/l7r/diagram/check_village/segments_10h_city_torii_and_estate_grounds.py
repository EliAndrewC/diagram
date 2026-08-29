"""Gate segments (city torii and estate grounds; keys 0563_334-0563_376) - bodies verbatim, registry order preserved."""


# the street network must be CONNECTED - one coherent grid wired to the Imperial
# road, not isolated stubs (ported from the town "no street to nowhere" thinking).


# a temple a city street runs UP TO (a street that terminates at its front) marks a
# sacred approach - it needs torii arches on that street, just in front of the temple


# (RETIRED 2026-07-24: city_temple_torii_fill_approach - "an avenue with open room takes
# another arch" - is superseded by the per-temple seeded ROLL: shrine_hall now rolls each
# hall's count on the tier's TORII_WEIGHTS column and records the target on the religious
# rec, so avenue completeness is defined by the roll, not by remaining street room. A
# rolled 1 beside an open street is a hall with one patron gate, not an unfinished avenue.
# torii_match_roll (with torii_count_canonical) now carries the teeth. Same precedent as
# torii_full_avenue_is_seven's retirement when the numerology rule landed.)
# a torii arch stands OVER the street it spans - the street passes beneath it - so a
# torii sitting on a street must be drawn after (higher z than) that street, not under it


# no LARGE empty swath inside the walls (ported from wall_hugs_the_town; REBUILT
# footprint-aware, GM 2026-07-23, after Tango shipped a ~230x95px bare pocket just
# inside its north gate that read fully green). The old detector sampled an 80px grid
# and called a cell "used" within 120px of any building CENTER - a single house
# sanitized a 240px-wide disc, so only vast voids could ever fire. Now every claiming
# feature counts with its real FOOTPRINT: building/compound/grove rects, field and
# ground polys, well / stable-yard / torii discs, the road / street / alley / ring-road
# / water rights-of-way, ward fences, the rampart + its patrol strip, and the pond. A
# 32px grid marks cells >= 20px clear of ALL of them as dead ground; any contiguous
# dead cluster >= 4,000 px2 of core fails. Calibration (2026-07-23, pool-wide dry-run,
# settlements.md): Tango's north-gate pocket measures 6,144 px2 of core; the largest
# LEGITIMATE opens anywhere else measure 2,048 (Tango) / 1,024 (Nagahara), so the
# threshold sits between with ~2x headroom both ways. A city keeps SOME open ground,
# but every deliberate open is CLAIMED by a feature record (a working stable yard /
# animal ground, a right-of-way, a field); ground claimed by nothing, at
# wall-protected premium, would not have been left bare.


# the CITADEL claims its ground (021): a castle court is deliberately BLANK (the
# sync doctrine) - blank is not unclaimed, and its moat band goes with it
