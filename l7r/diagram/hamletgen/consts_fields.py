"""The field archetypes and the hamlet's field and pond knobs - split from consts.py by feature 405 (T112's claims took consts.py
past the 1,000-line bar, as feature 316 split consts_water.py); bodies verbatim, and every name here is re-exported from
consts.py, so callers keep importing them from there.

Research: field constants plumbing - NONE"""

from __future__ import annotations

from typing import Any

# THE FIELD ARCHETYPES this generator can draw, and why there are two rather than five. The pool's
# hamlets span five (`valley_paddy`, `polder_grid`, `mulberry_dike_fishpond`, `contour_terraces`,
# `ribbon_valley`) and they are not variations on one shape - a comb fan is grown around a head-race
# on sloping ground, a polder is a surveyed orthogonal grid diked out of standing water on flat
# ground. They share `draw_comb_field` (build_polder deliberately returns comb-compatible
# keys) and almost nothing else: different water entry, different drainage, a perimeter dike, and a
# village that must sit on the LANDWARD side rather than the upslope one.
#
# `mulberry_dike_fishpond` IS declared as a third archetype (feature 150, Kuwabata) because a pool
# entry names it and the gate reads it (`dikepond_is_ponds_in_a_block` keys off
# `meta.field_archetype`) - but it is BUILT as the polder carried to the wholesale-conversion
# overlay, which is what it is historically too (research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html:
# the wall-to-wall dike-pond landscape is the rare END STATE of the scattered overlay, ~300 years
# of 挖塘培基 plot by plot). So `POLDER_ARCHETYPES` is the set the polder stage serves, and the
# dike-pond differs from the rice polder only in its PARCEL FABRIC (`POLDER_FABRIC`), the overlay
# applied after the grid is drawn, and the ring-canal crossing caps.
FIELD_ARCHETYPES = ("valley_paddy", "polder_grid", "mulberry_dike_fishpond")
"""The field forms a hamlet's map may name; only `ROLLED_ARCHETYPES` are dealt at random.

Research:
    field forms drawn - research/questions/0017-how-much-farmland-a-settlement-works-and-in-what-tracts.drawing.html, research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: valley fan, rice polder, dike-pond
    no jori grid rolled - DEVIATION research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html, research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: no plain ruled on the jori grid, so that form is never rolled
"""
POLDER_ARCHETYPES = ("polder_grid", "mulberry_dike_fishpond")
"""Research: dike-pond built as a polder - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html, research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html"""

# THE PARCEL FABRIC PER POLDER ARCHETYPE - every number is `build_polder`'s TRUE-SCALE SIZING note
# (researched 2026-07-21, source-verified the same day; 1 px = 1 ft, no legibility inflation):
# - a RICE polder's module is ~190 ft (feature 280 M54, research/questions/0022-parcels-and-bunds-inside-a-polder-aze.html: a polder parcel before modernity ran about
#   three mu - the 1897 fish-scale register of nineteen Taipingqiao polders outside Suzhou, 3,700 parcels on 11,000 mu -
#   so the bay/half/third mix of the old ~110 ft module, whose ~1 mu mean was Buck's 1929-33 survey, is carried to
#   110 x sqrt 3 ~ 190 ft), most bays split into strips ((0.52, 0.16, 0.12)), with 3 ft walking
#   bunds between rows and 8 ft ditch corridors on the module lines ((1.5, 4.0));
# - a DIKE-POND's ponds were 0.4-0.6 ha oblongs (Ruddle & Zhong / FAO; CAVEAT in the note: the
#   sizes are Republican-to-1980s surveys of the traditional landscape, not Ming/Qing documents),
#   so a ~160 ft module with a merge-heavy mix ((0.10, 0.0, 0.60): mostly 160x320 ft ~0.48 ha 1:2
#   ponds, a square ~2.4-mu minority), the grid's ~22 ft gaps ((11, 11)), and each pond's water inset 23 ft inside its
#   parcel (`settlement/fields/landuse.py` `DIKEPOND_WATER_INSET`). THE WATER SHARE (feature 280 M58,
#   research/archetypes/610): every page that writes the water-to-dike split as a number (6:4, 7:3, 4:6) is modern, and
#   the oldest figures are Qu Dajun's for Jiujiang in 1678 - read together (a GUESS, this record's arithmetic) water to
#   dike about 5:3 - so a parcel is calibrated to about 6 parts water in 10 (0.62 measured on Kuwabata, 2026-09-29);
#   the 11 ft inset it replaced left 80% water per parcel, wetter than any figure read in any period. The dike's
#   width itself has no premodern figure (the 6-10 m once cited is a modern manual's): it follows from the share.
# `fit_polder` scales the GRID to the acreage and never the cell, so these calibrations hold
# whatever the household count asks for.
POLDER_FABRIC: dict[str, dict[str, Any]] = {
    "polder_grid": {"cell": 190.0, "parcel_mix": (0.52, 0.16, 0.12), "gap": (1.5, 4.0)},
    "mulberry_dike_fishpond": {"cell": 160.0, "parcel_mix": (0.10, 0.0, 0.60), "gap": (11.0, 11.0)},
}
"""Research: polder parcel fabric - research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html, research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html: rice 190 ft modules, dike-pond 160 ft"""

# THE POND LAYOUT - ONE ATTESTED FORM AT POND SCALE (feature 280 M56, research/archetypes/130): the grid is attested for
# the Song tangpu CANALS, the mosaic for the PONDS, while a uniform chessboard of ponds is found only as today's aerial view
# of Digang - so a dike-pond block is drawn as the mosaic and the pond grid is no longer rolled. The GM ruled the knob in on
# 2026-08-18 on the reading that both were attested ponds; that reading is withdrawn at pond scale and the reversal
# reported. What follows is the knob's original note (constitution XII,
# GM 2026-08-18). research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: the lower-Yangtze wei-tian was a SURVEYED
# rectilinear grid (the Song tangpu lattice) while the Pearl-delta dike-pond accreted household by
# household into a MOSAIC - rectangles of varied size at varied local orientation around winding
# creeks. Both systems carried dike-ponds (Lake Tai mulberry sat on the tang banks inside the
# grid), so a dike-pond hamlet rolls between them; a RICE polder is the surveyed grid by definition
# and does not roll (`plan_site` pins it to "grid", which keeps every polder_grid map byte-identical
# to before this knob existed). The uniform chessboard is also the MODERN consolidated look, which
# is why the mosaic is the more common roll. `build_polder(mosaic=)` is the engine's dial: 0.0 is
# the grid, 0.5 the mosaic Kuwabata was drawn with (the GM saw and accepted that map's ponds).
# Feature 374 wave 139 (plan W139-1): the chessboard of ponds IS attested before modern times - Qu Dajun's Guangdong
# xinyu (1678), quoted in 0019's drawing notes: "The land of Jiujiang is like a chessboard ... its black lines are the
# dikes, and the squares are the ponds". So both forms are attested at pond scale and a dike-pond block rolls between
# them again; the mosaic stays the commoner (two in three), the delta's accreted form - the odds a GUESS.
POND_LAYOUTS = ("mosaic", "mosaic", "grid")
"""Research: dike-pond layout - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: the mosaic or the chessboard (Qu Dajun 1678), the mosaic two in three (a GUESS)"""

# THE FRY FORM - which nursery a dike-pond hamlet keeps (feature 280 M60, research/archetypes/200 and 172): the ordinary
# delta hamlet raised grown fish and BOUGHT its fry, with no nursery ponds; the fry village of Jiujiang raised fry in seven
# parts of ten of its pond water (Qu Dajun, 1678). The "one parcel in ten" once drawn is on no page read, premodern or
# modern. Two attested forms, so a knob; the fry village rare (Qu Dajun: fry ponds only in Jiujiang) - the odds a GUESS.
# The third form read, a small fry pit beside each big pond (Nongzheng quanshu, 1639), is OFF the delta, and the block
# drawn is the delta's mosaic.
FRY_FORMS = ("none", "none", "none", "fry_village")
"""Research: fry form - research/questions/0024-fish-fry-and-nursery-ponds-yumiao.drawing.html: one hamlet in four a fry village"""

# THE MANURE FIXTURE'S FORM - heap or pit, two attested forms so a knob (constitution XII; feature 150, GM
# 2026-08-28 choosing audit A2). Sugiura 1973 counts the manure shed/heap on Tohoku farmsteads; Fei 1939 has
# the Lake Tai silk village keeping its manure "in the pits made of earthenware, half buried in the ground at
# the back of the building", lined along the road. Neither source gives a share of villages using each, so
# the roll is even. research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html.
MANURE_FORMS = ("heap", "pit")
"""Research: manure fixture form - research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.drawing.html: heap or sunk jar, even odds"""

# THE HARVEST WEATHER - an ENVIRONMENT FACT the spec declares, never a roll (feature 282, FR-005). Racks gathered by
# the house are named for the changeable-weather San'in coast, "so that it is convenient to do the threshing work within
# the homestead" (Nishimura and Makino 1959), and the drying method followed the weather and the ground over whole
# regions, not a village's choice - so a free roll per hamlet would let two neighbors in one climate differ, which is
# what the GM asked us not to do (2026-09-28). `changeable` draws a rack by every house; `settled` (the default: the
# gathered racks are one region's form - this project's decision, as the regional wind is) draws none at the house.
# research/questions/0016-rice-drying-racks-hasa-hasagi.html; the rule at research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html.
HARVEST_WEATHERS = ("settled", "changeable")
"""Research: harvest weather - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: declared, never rolled; racks by the house where changeable
standing rack forms - research/questions/0016-rice-drying-racks-hasa-hasagi.html, research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: neither Niigata's living alder rack posts nor Ehime's racks standing all year is drawn - both attested only by undated modern records, no premodern record found (feature 374 wave 137, 280's D1)"""
DEFAULT_HARVEST_WEATHER = "settled"
"""Research: harvest weather when undeclared - research/questions/0016-rice-drying-racks-hasa-hasagi.drawing.html: settled"""
# THE COPSE STANDS AMONG THE HOUSES (feature 328): 0071's drawing page draws the dooryard copse only in the gaps between
# the houses; the against-the-belt form (feature 152, a settlement-review's knob candidate) has no page behind it and is
# retired. Kept as the knob's one form so a spec that declares it still reads.
COPSE_SITINGS = ("among_the_houses",)
"""Research: village copse siting - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: among the houses, in the gaps between them"""
# THE NOTICE BOARD ON THE BUSIEST FRONTAGE (feature 328): 0190's drawing page seats it beside the busiest main road, else
# where the most buildings stand; the drawing-water siting (feature 152, a settlement-review's knob candidate) has no page
# behind it and is retired. Kept as the knob's one form so a spec that declares it still reads.
KOSATSUBA_SITINGS = ("frontage",)
"""Research: notice board siting - research/questions/0190-notice-boards-kosatsuba.drawing.html: the busiest frontage"""

# THE DIKE CROP - which dike-pond planting a hamlet is (feature 150, GM 2026-08-28 choosing audit A6; the
# options re-read by 269 B34). research/archetypes/230: Qu Dajun (late 17th c.) has the villages' pond dikes
# planted with fruit - lychee most, tea and mulberry next - and a modern history dates the fruit dike first
# (mid-Ming) and the mulberry dike dominant through the Qing. So three premodern plantings: mulberry, fruit and
# tea. The cane, banana and vegetable dikes are attested only in modern sources (one undated modern listing
# for cane, nothing earlier than the modern surveys for banana and vegetable), and by the GM's ruling of
# 2026-09-28 a form attested only in modern sources is not drawn - they are no longer options. The weighting
# is a GUESS, a degree (constitution XII): mulberry the Qing norm at 3 in 6, fruit the oldest form at 2, tea,
# named after lychee and never as a district's type, at 1.
# A TAIL POND'S BANK (feature 385 T08): bare, or planted sparsely with mulberry and cudrania (0061, Chen Fu's Nongshu), rolled
# per hamlet whose sink is a pond.
POND_BANKS = ("bare", "planted")
"""Research: pond bank form - research/questions/0061-reservoir-ponds-tameike.drawing.html: a bare bank, or one planted sparsely with mulberry and cudrania; even odds a GUESS (no share given)"""

POND_BANK_PITCH_FT = 30.0
"""Research: one tree about every 30 ft of bank - GUESS: 0061's "sparsely" gives no figure"""

POND_BANK_FT = 18.0
"""Research: a tail pond's bank beyond its reeds - GUESS: 18 ft, room for a crown and a little play (no crest width recorded)"""

POND_BANK_CROWN_FT = 6.0
"""Research: a bank tree's crown radius - GUESS research/questions/0061-reservoir-ponds-tameike.drawing.html: a tree whose shade the tethered cattle take (the manual), about 12 ft across - not research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html's field mulberry trained as low bushes"""

DIKE_CROPS = ("mulberry", "mulberry", "mulberry", "fruit", "fruit", "tea")
"""Research: dike crop - research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.drawing.html: mulberry half, fruit a third, tea a sixth"""

# WHAT THE LEFTOVER PARCELS OF A WHOLESALE CONVERSION READ AS (feature 150 B2): standing rice, or no leftover
# at all (every parcel a pond); the roll is even. A third state, tilled vegetable ground, rested on Fei's 1930s
# silk village and the modern vegetable dike, and is retired by the GM's ruling of 2026-09-28 that a form
# attested only in modern sources is not drawn (269 E9; research/archetypes/230).
WATERWARD_DEPTH = 280.0  # px of wild water drawn outside a polder's dike face (feature 150 T55). Not "to the canvas edge": the crop keeps ~120 px past the content at most on this tier, so everything beyond was scattered, keep-out tested and thrown away - 18.4 s of a 40 s gen. 280 outlasts any hamlet crop measured (the tightest flank keeps 245 px of headroom), and `waterward_strips_run_off_the_frame` holds the line.
"""Research: wild water outside the dike - CONVENTION: 280 ft drawn, outlasting any crop"""
LEFTOVER_FORMS = ("rice", "pond")
"""What the leftover parcels of a wholesale conversion read as.

Research:
    dike-ponds throughout - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: a wholesale village
    dike-pond leftover parcels - GUESS research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: every parcel a pond, or about one parcel in ten left in standing rice, at even odds; rice or pond, even odds
"""
POND_LAYOUT_MOSAIC = 0.5
"""Research: mosaic strength - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: 0.5, the lattice bent out of line"""

# THE SHARE OF THE BLOCK THAT CONVERTED in the end state. `apply_land_use(fraction=)` is the ECONOMIC
# term over the ELIGIBLE set, and the archetype opts out of the topographic filter by name
# (`eligible="all"`); 0.9 is the hand-authored Kuwabata's figure - "(almost) every former paddy cell"
# - so a few leftover parcels still read as standing rice among the ponds (research/questions/0022-parcels-and-bunds-inside-a-polder-aze.drawing.html: leftovers of a wholesale conversion are repainted as paddy, not left as outlines).
# The exact share is a DEGREE along the attested continuum (Shunde: rice under one-tenth of the land
# by c. 1900), a calibrated liberty rather than a measured number - recorded as such.
DIKEPOND_CONVERSION = 0.9
"""Research: share of the block converted - research/questions/0020-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.drawing.html: 0.9, leftovers in rice"""

# ...but only the proven one is ROLLED, and `polder_grid` is opt-in until it survives a COHORT.
#
# It was promoted on 2026-08-15 after sweeping 48 of 48 (8 seeds x 4 cardinal bearings, plus the
# household band's ends) and demoted the same day, because the cohort is a harder test than that
# sweep: `cohort_audit` varies HOUSEHOLDS per seed and rolls water_sink, cluster_shape and
# lane_skeleton, where the sweep pinned households at 16 and took the default rolls. Under those
# conditions the fitted cohort fell to 19 of 24. That is the cohort earning its keep exactly as it
# did three times for the valley tier - a fixed-parameter sweep is not evidence of consistency.
#
# THE BAR FOR PROMOTION is therefore a green COHORT, not a green sweep: 24/24 and 12/12 with polders
# in the mix. Rolling an archetype with open failures mixes them into the valley tier's own numbers
# and destroys the one measurement that says this process is consistent.
ROLLED_ARCHETYPES = ("valley_paddy",)
"""Research: field forms rolled - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html: only the valley fan is rolled; the attested polder and dike-pond are opt-in until their cohort is green, the page's known gap"""
