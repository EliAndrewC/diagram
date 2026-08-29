"""Gate segments (city castes and dojos; keys 0563_000-0563_044) - bodies verbatim, registry order preserved."""


# every provincial city's interior carries the provincial government:


# a provincial city is ~10% samurai (~300 of ~3,000, budgets.md) - about pop/50 households.
# Most are housed in the samurai neighborhood as individual houses; the governor's compound
# and the extramural estates hold the rest. Require the neighborhood to depict at least ~65%
# of that expected household count, so it is a real quarter, not a token cluster of a few.


# samurai (unlike the poor, who sit in the deep block cores) LINE their streets - many houses
# front a street even if deeper lots sit behind. Require at least a third near a street/road.


# SAMURAI HOUSING varies in size by rank, UNLIKE a uniform cluster. budgets.md's provincial-city
# rank table puts ~25% of resident samurai in the senior ranks (R5-7) and the rest in R1-4; so the
# in-city neighborhood mixes a MINORITY of large houses (senior) among many small ones (junior).
# Crucially, samurai walled ESTATES are OUTSIDE the walls (rural goshi) - the only walled samurai
# compound inside the city is the governor's mansion - so NO manor may sit inside the wall ring.


# MARTIAL TRAINING (GM 2026-07-25; settlements.md "Historical grounding: martial training in
# a provincial city"). The provincial city is the FIRST tier that supports a dojo at all -
# a county town's ~20 resident samurai are no student body and no living for a sensei, which
# is why the county magistracy draws a practice ground and no dojo (buildings.md). It
# supports two kinds, and both are required here:
#   - EXACTLY ONE state PROVINCIAL MARTIAL HALL, inside the walls. Historically the hanko's
#     bugeijo, and hanko were built in castle towns for the domain's own retainers - the
#     tier that seats a governor and ~225 working samurai is the tier that seats the hall.
#     It is its OWN compound, not a wing of the governor's yamen.
#   - PRIVATE dojos, count rolled from the samurai cohort (s.dojos): 1 per full 200 samurai
#     plus a remainder-fraction chance of one extra, floored at 1. A ~3,000 city is ~10%
#     samurai = ~300, so 1 + a 50% roll. Total martial establishments therefore land at 2-3,
#     matching the ~1 per ~100 resident samurai the research put a provincial city at.
# The ARCHERY LANE is the state hall's alone and sits INSIDE its compound wall: 90 ft is the
# kyudo standard 28 m shot (the same clear lane the Mode A azuchi uses), and a private lot
# has no room for it. A recorded roll must match the drawn count, so a stale hand count
# cannot ship - the bathhouse ratchet, applied to a samurai-driven institution.


# the HANKO's court is deliberately BLANK (synced doctrine, GM 2026-08-09: a real
# hanko is building-dense, so its faithful interior - bugeijo and archery lane
# included - lives on its Mode A sheet); only provincially-drawn halls owe the lane


# LABORER HOUSING VARIES BY WEALTH, like the samurai and merchant tiers: budgets.md's provincial-city
# laborer cohort is ~12.5% "master" (rich) laborers, the rest standard - so a MINORITY of larger homes
# (kind "laborer_large", the wealthier hinin who line the prime back-street frontage, with room around
# them) among the overwhelming majority of small standard dwellings. The exact share is room-limited
# (the big homes need street frontage), so the band is generous around the 12.5% target; the point is
# that the variety is PRESENT and a clear minority, not that every laborer dwelling is identical.


# the city's CASTE MIX must match budgets.md, not just the total head-count: a provincial city is
# ~40% laborer / 20% servant / 25% merchant / 10% samurai / 5% burakumin of its ~600 households.
# The total-population check alone lets the mix DRIFT (e.g. laborers absorbing everyone else's
# slots, servants starved to near-zero because they were appended to the END of a pack list), so
# each caste is held within +/-30% of its target. Servants live among the merchants/samurai they
# serve - INTERLEAVE them into those packs rather than tacking them on the end.


# MERCHANT HOUSING is varied and roomy, UNLIKE the uniform, jammed laborer warren. Behind the
# storefronts the homes mix sizes by wealth band (budgets.md: very rich -> walled ESTATES, rich
# -> LARGE houses, the rest -> small houses) and are SPREAD OUT - more room between them than the
# densely-packed laborers (a few denser merchant blocks are fine; the median is robust to those).
# ROW-PACKING doctrine (GM, 2026-07): city commoner housing is CONTIGUOUS - the
# machiya/nagaya fabric of party walls and touching eaves, not detached-with-yard.
# Real urban commoners packed into terraces (street frontage was taxed and precious;
# a back-lot nagaya was one roof over a row of family units; Chinese county-seat
# courtyard housing shared party walls in continuous street walls). Measured on the
# pre-doctrine Tango: median nearest-neighbor gap was 12px (~31 ft) with ZERO
# touching pairs - a suburb, not a city quarter. Gaps allowed: a hairline seam
# (<=1.2px, touching), the ~3-6 ft eave gap between back-to-back rows, courts,
# and street/roji breaks - but the QUARTER-WIDE stats must read as terraces.


# DRAWN COMPOUND COUNT MATCHES THE ROLL (GM 2026-07-23, mirroring torii_match_roll): a
# walled/gated compound is a PRIVILEGE explicitly granted to a merchant family - most very
# rich merchants can afford one but lack the legal standing to build it (the Edo pattern of
# individually granted merchant rights: a New Year's audience with the daimyo, a hereditary
# surname, etc. - see MERCHANT_ESTATE_WEIGHTS in settlement.py and settlements.md). The gen
# rolls 1-3 grants per city (30/40/30, seeded on the map seed), records the target in
# meta['merchant_estate_roll'], and this gates drawn == target - so the pre-roll state
# (both cities hand-coding exactly 1, a copied pattern) can never silently return.


# CAPITAL-INVERTED (021): a capital is fed BY THE RIVER, not its outskirts - the whole
# wharf/granary doctrine (stipend rice arrives from the six provinces by boat, and the
# frame shows that supply chain: wharf, granaries, towpath), and its sheet frames only
# the walled city and its suburbs. A provincial city's identity IS its farm country, so
# the comb stays mandatory there. (capitals.md; audit 2026-08-10)
