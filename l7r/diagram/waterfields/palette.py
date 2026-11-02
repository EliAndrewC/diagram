"""Layer-0 palette: paddy and crop colors, the bund (aze) width, and the dry crops' names.

Research: palette plumbing - NONE: unit conversion and polygon sampling
"""

# A rice field is ONE crop at ONE transplant/growth stage, so its body is a UNIFORM green - the plot-to-plot
# shade jitter denoted nothing (it was only anti-flatness texture), and the GM asked for it uniform. The bund
# network + footpaths carry the structure, not color. Kept as a 3-element list of the SAME value so R.choice
# consumes the RNG stream IDENTICALLY to the old 3-shade version - the field geometry + the meaningful FLOODED
# drain-plots stay byte-for-byte unchanged; only the body color goes uniform. (The MEANINGFUL colors remain:
# FLOODED blue-green for the low plots that sit on the drain, and RIPE_GOLD, when a map uses it.)
_RICE_GREEN = '#A6C398'
"""Research: rice green - CONVENTION: the hue of a growing paddy"""
RICE_GREENS = [_RICE_GREEN, _RICE_GREEN, _RICE_GREEN]
"""Research: one green - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: every rice basin drawn one green"""
FLOODED = '#93B7AC'
"""Research: wet-paddy tint - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a blue-green marking wetter ground"""
RIPE_GOLD = '#C9BA79'
"""Research: early-ripening plot - research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: gold for the odd plot ripening early"""
BUND = '#C2A772'
"""Research: bare-earth tan - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: kept for earthworks of real width, dikes and pads"""
# AZE: the paddy plot-boundary stroke, split from BUND (GM 2026-07-24). BUND stays the broad
# exposed-earth AREA fill (perimeter dikes, dike-top house pads - true-width earthworks); AZE is
# the LINE between paddies: the puddled-mud ridge (aze / tiangeng) re-plastered each spring
# (azenuri) to seal the basin. A plain aze ran ~1-2 ft wide and ~1 ft high (walking bunds,
# azemichi, 2-5 ft), so AZE_FT below draws it near TRUE scale instead of the old 1.7-2.6 px
# tan (~3-5 ft at village grain) - a dark line stays legible at half the width where the light
# tan needed inflation. The hue is the GM's pick from a 5-color ladder rendered on Hoshigaoka
# (2026-07-24): red-leaning dark mud, chosen over the lighter chestnut #7A5230 that reads more
# nameably "brown" at hairline width - at map view this dark a line blends toward black against
# the rice green, and the GM preferred that weight. Accuracy
# is deliberately mixed: the color is honest for SPRING (fresh azenuri mud); by high summer -
# the season the paddy surfaces depict - real bunds green over with grass and azemame and all
# but vanish, so a dark visible bund network is a stylization that keeps the field structure
# readable. See research/questions/0005-rice-paddies-and-their-plots-suiden.html.
AZE = '#6E4520'
"""Research: bund color - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a dark red-leaning mud brown, shown in summer by convention"""
AZE_FT = 1.5  # drawn aze width in real feet; convert at the map's ftpx, floored for raster visibility
"""Research: dividing bund width - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: about 1.5 ft, its real width"""


def aze_w(ftpx: float) -> float:
    """Paddy bund stroke width in px at this map's scale: AZE_FT real feet, floored at 0.5 px
    so the city scale (3 ft/px) keeps a faint-but-present line instead of vanishing.

    Research: bund stroke - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: AZE_FT at the map's scale, never thinner than half a pixel
    """
    return max(AZE_FT / ftpx, 0.5)


BEAN_GREEN = '#2F6B35'  # azemame (bund soybeans) - the beaded-bund accent. Deep PINE green
# (GM 2026-08-15): the old olive #7C9A4E sat between the rice green and the bund brown and read as
# neither - the beads were nearly invisible at map zoom. A glyph rendering convention, not botany
# (real soybean foliage is lighter): dark enough to punch against the pale rice, green enough to
# still read as a plant against the near-black bund stroke. Picked from a 3-color ladder rendered
# on Inashiro (hunter #355E3B grayed out, forest #1F4A28 read as black).
"""Research: bean bead color - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a deep pine green, darker than the plant"""


# DRY-FIELD (hatake) crops on ground the irrigation cannot command - the upslope margin
# above the supply canal. Each: fill + furrow-line color (dry crops are ridge-cultivated).
DRY_CROPS = {
    "barley": ("#CDB86A", "#B49E52"),  # mugi - tan-gold
    "millet": ("#C6A64A", "#AD8C36"),  # awa/kibi - ochre
    "buckwheat": ("#D3C2A6", "#C69C86"),  # soba - pale, reddish stems
    "soy": ("#A9B36A", "#8E9A50"),  # daizu as a field crop - soybean green
}
"""Research: four dry crops at their ripest color - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: barley, millet, buckwheat and soybean, each with a furrow color"""
