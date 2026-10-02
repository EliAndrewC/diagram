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

## R1 The crown placers (scouted 2026-10-02)

Every drawn canopy crown passes `Settlement._crown_covers(x, y, r, rects, circles, pad)` against keep-out boxes as
(center, half-width, half-height) before it is drawn:

| placer | site | trees |
|---|---|---|
| `_belt_ranks` | `homestead_parts/groves.py` | the conifer-led belt's rank conifers |
| `_draw_grove` clumps | `homestead_parts/groves.py` | the farm grove's bands, the windbreak's and the copse's clumps |
| woods stand + fringe | `shrines_wells/woods.py` | woods, the woodland commons, shrine groves |
| the persimmon | `homestead_parts/fixture_seats.py` | seats itself out of the sun ground (pushed 2026-10-02) |

The bamboo culm marks in a clump use the same keep-out list (`groves.py`, the marks pass) - the one site the new boxes must not
reach (FR-003).

A plot's sun ground is the box from `x0 - reach` to `x1 + reach` and `y0` to `y1 + reach` - a (center, half sizes) box - and
`_crown_covers`' disc-against-box test is exactly `tree_shade.crown_shades`. So one keep-out source serves every crown site.

## R2 Before figures (SC-004; one-shot, read from the shipped manifests 2026-10-02)

| map | household wood rolled / drawn (sq ft) | copse clumps | windbreak clumps | recorded crowns |
|---|---|---|---|---|
| Inashiro | 10,321 / 10,321 | 365 | 131 | 2,123 |
| Kashikawa | - (grove farms) | - | - | 2,685 |
| Kuwabata | 14,520 / 14,528 | 382 | 377 | 1,486 |
| Mizuguchi | - (grove farms) | - | - | 2,069 |
| Sawada | 11,486 / 11,493 | 460 | 228 | 1,624 |

Crowns in a plot's sun (spec Context): 95, 78, 98, 10, 143.
