# Research: no canopy tree in a yard's or bed's sun (feature 310)

## R0 Historical grounding (constitution XII, the opening bookend)

**What the reality was.** The record holds why a plot wants its sun and what a tree's shade reaches, and is silent on how far a
farm's plots stood from its trees:

- A drying yard dries the autumn harvest in the sun, and a kitchen bed's autumn crops want about six hours of it
  (`research/questions/0038-sunlight-and-shade-on-the-farm.html`, `.drawing.html`).
- A tree's shade: the Qimin Yaoshu reckons an elm's shade to reach on the east, west and north as far as the tree is tall, and
  sets elms on the garden's north edge, from which no noon shadow falls on it (0038, the Qimin Yaoshu notes). China-first, and
  the direct form of the rule this feature applies: no tree east, west or south of the ground it would shade.
- Where groves stood: Tohoku groves on the north and west of a house; Tonami's tall trees from the south round to the west,
  its east front open with flowering and fruit trees (0038). These are sides, not distances; the drawing page states "No source
  measures how far a farm's plots stood from its trees".
- Bamboo: madake is a tall culm in thickets "shading out almost everything else" (`research/questions/0075-bamboo-groves-chikurin.html`).

**Does the design match?** Partly, and the gap is the GM's ruling. The record supports keeping trees out of a plot's sun (the
Qimin Yaoshu's elm rule) and does not measure how close real groves stood; the Tonami south-side grove shows trees could stand
on a house's sunny flank. The design holds every canopy tree out of every plot's sun ground - the GM's rule over a silent record,
labeled a guess in the spec's Decisions table and on the sun page. Bamboo's exemption is the GM's tentative allowance against
the bamboo page's tall madake, labeled the same way and raised with the GM.

**What determines it in reality.** The sun's path in the drying season (season and latitude), and the household's choice of
where its plots and trees stood (tenure: its own lot). Neither is drawn from a source here beyond the shadow geometry.

## R1 The tree placers (scouted 2026-10-02; the plan review's D3 finding folded in)

**How the list was found.** Every writer of `tree_crowns` (a grep of the engine for the key: `_record_crowns` and its four
callers, and `land/cover.py`'s two direct writes), then every class the generator can draw - the interactive class registry,
`l7r/diagram/interactive/classes/*.py`, read class by class for the trees each draws (not only the five pool maps' classes,
which missed the fruit dike a mulberry-dike hamlet may roll). Trees: alder, copse, homestead grove, windbreak, woodland
commons, persimmon, scrub and rough grazing (its pines), perimeter dike (its willows), fruit dike. No trees: homestead bamboo
and the shared bamboo grove (bamboo, FR-003), mulberry dike and tea dike (coppiced and clipped bushes, below), burial ground,
field rock, grave island, and every field, water, way and building class.

| placer | site | trees | today's test before inking | recorded |
|---|---|---|---|---|
| `_belt_ranks` | `homestead_parts/groves.py` | the conifer-led belt's rank conifers | `_crown_covers` | `tree_crowns` |
| `_draw_grove` clumps | `homestead_parts/groves.py` | the farm grove's bands, the windbreak's, the copse's and the alder clumps | `_crown_covers` | `tree_crowns` |
| woods stand + fringe | `shrines_wells/woods.py` | woods and shrine groves (no scripted hamlet draws one today) | `_crown_covers` | `tree_crowns` |
| the woodland commons' throws and its `woodland_room` grid | `land/cover.py` | the coppice crowns | `_sparse` / the room grid - NOT `_crown_covers` | `tree_crowns` |
| the scrub's hill pines | `land/cover.py` | a few scraggly pines, trunk and branch lines | `_sparse`, `_in_soft` | NOT recorded |
| the perimeter dike's willow row | `land/dikes.py` | pollarded willows on the water face | none - drawn in the field stage, before any plot exists | NOT recorded |
| the fruit dike's trees | `fields/landuse.py` | standard fruit trees along a dike-pond's bank (lychee, longan, citrus) | none - drawn in the field stage, before any plot exists | NOT recorded |
| the persimmon | `homestead_parts/fixture_seats.py` | one tree a household | seats itself out of the sun ground | `tree_crowns` |

Not canopy: the bamboo culm marks and stands (FR-003); the perimeter dike's and the mulberry dikes' coppiced mulberry, "for the
most part trained as low bushes" (`research/questions/0026-mulberry-and-other-crops-on-pond-dikes-sangji-guoji.html`);
and the tea dike's hedge, clipped low (`fields/landuse.py`; its width a drawing guess) -
each a bush of the bank cut back as a crop, which the code calls "not canopy"
(`land/dikes.py`, `fields/landuse.py`).

A plot's sun ground is the box from `x0 - reach` to `x1 + reach` and `y0` to `y1 + reach` - a (center, half sizes) box - and
`_crown_covers`' disc-against-box test is exactly `tree_shade.crown_shades`. So one keep-out source serves every crown test.
## R2 Before figures (SC-004; one-shot, read from the shipped manifests 2026-10-02)

| map | household wood rolled / drawn (sq ft) | copse clumps | windbreak clumps | recorded crowns |
|---|---|---|---|---|
| Inashiro | 10,321 / 10,321 | 365 | 131 | 2,123 |
| Kashikawa | - (grove farms) | - | - | 2,685 |
| Kuwabata | 14,520 / 14,528 | 382 | 377 | 1,486 |
| Mizuguchi | - (grove farms) | - | - | 2,069 |
| Sawada | 11,486 / 11,493 | 460 | 228 | 1,624 |

Crowns in a plot's sun (spec Context): 95, 78, 98, 10, 143.

## R2a After figures (SC-004; read 2026-10-02 from main at the merge base 5d2562bb7 and the clone at 3845e432e, same moment)

Main moved after R2 was read (feature 308 re-grew the cluster), so the before column here is main as it stands, not R2.
Crowns in sun are `tree_shade.trees_shading_plots` at `CANOPY_SHADE_FT` - (plot, tree) pairs.

| map | household wood rolled / drawn (sq ft), main -> 310 | copse clumps | windbreak clumps | recorded crowns | crowns in sun |
|---|---|---|---|---|---|
| Inashiro | 15,699 / 15,709 -> 14,995 / 14,987 | 359 -> 321 | 387 -> 387 | 2,750 -> 2,651 | 145 -> 0 |
| Kashikawa | - (grove farms) | - | - | 2,685 -> 3,071 | 84 -> 0 |
| Kuwabata | 12,597 / 12,600 -> 11,960 / 11,968 | 395 -> 358 | 233 -> 233 | 1,319 -> 1,209 | 143 -> 0 |
| Mizuguchi | - (grove farms) | - | - | 2,069 -> 1,807 | 10 -> 0 |
| Sawada | 9,414 / 9,418 -> 8,791 / 8,791 | 460 -> 421 | 140 -> 140 | 1,354 -> 1,202 | 183 -> 0 |

The rolled wood falls 4.5 to 6.6% (one-shot, observed 2026-10-02; method: the table above, read from the five manifests) because the sun ground takes part of the ground the copse could hold (`wood_goal.attainable_band`);
drawn stays within 8 sq ft of rolled. Kashikawa draws more crowns because its east bands now run end to end.
