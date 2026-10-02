# Research - feature 300, reeds to the bank

## R1. The margin, and the bank band's figures (observed 2026-10-01, method: reading `land/wet.py`'s keep-out slots and the rendered Inashiro PNG)

The marsh files the watercourses in its keep-out grid at slot 3 with the query's extra `2 + pad` (pad = `MARSH_TUFT_R * bs`, 7 ft; observed 2026-10-01, method: reading `land/wet.py`):
the reed tile's bare ground is the drawn half-width plus 9 ft each side - the thrown tuft's reach, kept so no blade crossed the
water. Feature 298 carried the slot into the tile's bare ground unchanged. The bank band's target is about 6 ft each side (the
session's proposal); the as-built figure and the outline decision are recorded here once calibrated.

As built (observed 2026-10-01, method: `make map` of Inashiro, its PNG read at full size): the bank band 6 ft each side of the
drawn water, reeds at three times the marsh's density in a darker green; the stream reads clearly through the toe marsh with
it - a light line framed by darker reeds - so the conditional outline (FR-003) is not added.

## R2. Addendum - the drain at the paddy's foot (observed 2026-10-01, method: the Inashiro manifest - the toe marsh 9.9 ft from the field, the collector drain on the field's edge - and its PNG)

The GM, after the feature landed: "irrigated drainage ditches at the bottom of the rice paddy fields also appear to have a similar
clearance. which I think should probably be fixed in the same way." The cause was a second leftover margin (observed 2026-10-01, method: reading `land/wet.py`): the marsh was cut
10 ft off every paddy's outline (`drawn_ground`'s `field_pad`, and the reeds' keep-out ring), "the same 10 px pad as the old edge
test" - a thrown reed's, not a finding. The marsh is now cut at the paddy's edge; the collector drain along it is a watercourse,
so the bank band lines it. The scrub's own 6 ft margin off a field (research/contents.json#vegetation, the crop margin: bund grass kept cut)
is a finding and stays.
