# Derivation - windbreak (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's oriented footprint; each farm's homestead wood, rolled in the register's range (`homestead_wood_ft2`); the belt and the groves already planted by the hinterland; the registry; the water courses (each farm's bank).
- Writes: the copse among the homes (`village_groves`, role `copse`): its clumps on a grid in the gaps between the houses, each clump's crowns; `meta.copse_clumps`.
- Keeps: over the cluster's own oriented footprint, in the gaps between the houses (0036, 0071); a clump within 90 ft of a house (`COPSE_HOUSE_REACH_FT`, a dooryard's reach, 0036); on its house's own bank (0035, a GUESS recorded there); sized by the homestead woods, each farm's share of 6,000 to 28,000 sq ft, the copse filled to what the belt and groves leave (0036); no copse without a belt or a reserved seat; seated after the woods and the ground cover, so the copse and the belt read as two stands; each clump asked before it is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); a clump 11 ft in radius on a grid of pitch 11 x root 2, 15.556 ft (the clumps' median nearest neighbor 15.5 ft at 10 and 20); the clumps 223 and 462 (x2.07: 462 at 20, 957 at 40, 1,980 at 80) and their crowns 296 and 624 (x2.11: 624 at 20, 1,317 at 40, 2,779 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 3 houses in 3 by 3 cells of 90 ft; at most 29 things in a 64 ft cell; at most 26 water segments in a 64 ft cell; the belt's ring 44 and 93 points (`belt_near_vertices`, x2.1: 93 at 20, 196 at 40, 411 at 80); 1 ft a pixel at the hamlet scale. The typical densities (rubric S8; `items.md`, measured 2026-10-28 on the same reference manifests at 10 and 20, each the mean over the cells occupied or crossed): things of every kind 3.4 and 3.3 an occupied 64 ft cell (4.5 and 5.5 within 3 cells of a house); homestead parts 2.8 and 2.6 an occupied 64 ft cell; water segments 4.1 and 3.7, ways' legs 1.3 and 1.9, the field's outline segments 2.1 and 1.8, and marsh segments 4.4 and 3.8 a crossed 64 ft cell; site-boundary segments 2.6 and 2.4 a crossed 32 ft cell; each held flat past 20, a mean over occupied cells not rising with the households as the densest cell does. The admission share (FR-014; the round arbiter's ruling ask:444-T09-rescore-batch; measured 2026-10-28 on the reference manifests): of the 15.556 ft grid's sites within 90 ft of a house, 0.49 and 0.47 at 10 and 20 are clear of the homestead parts, the ways and the water for a clump's 22 ft box (0.47 taken), so a clump is admitted at the 1 / 0.47 = 2.13th site tried; every belt point lies within 90 ft of a house (the belt 36 ft behind the fringe, 100 ft deep).

## The algorithm

    each farm's share: its rolled homestead wood, less what the belt already holds for it: the belt's ring walked once, each
        point's farm its nearest house from the 90 ft house index, its area apportioned (the fengshui groves are none on a
        hamlet: `groves` is empty on the reference at 10 and 20)
    for each house: the clump grid's sites within its 90 ft reach (a disk of the 15.556 ft grid, at most 133 sites at any offset), each
        site once over the run (a site two houses reach is taken by the first)
        each site, until its farm's share fills (the walk then ends): its farm's share (1); within 90 ft of its
            house by construction (no lookup); on its house's own bank - the segment from the site to its house walked
            through the water index's cells, no water segment crossing it; its clump's box against the registry's things in its
            cells (S4); admitted: the clump drawn and filed, its crowns written, the farm's share counted down

## Indexes

- house index: cells of 90 ft (the copse's reach), so a belt point's nearest house lies in its 3 by 3 cells; densest the houses' density x 9 x 90 squared, 3, from a smallest side of 90 ft
- registry: cells of 64 ft; densest 29 things a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against a clump's 22 ft box, in at most 2 by 2 cells
- water index: cells of 64 ft; densest 26 water segments a cell (measured at 10 and 20, the ceiling taken), from a smallest side of 64 ft against a site's segment to its house, at most 90 ft

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 462 at 20, 957 at 40, 1,980 at 80 | the clumps drawn (223 and 462 at 10 and 20, x2.07) | 80 households |
| the sites tried | per item | 2.13 | 1 / p, p = 0.47 the measured share of a reach's sites a clump's box finds clear (S8); a farm's walk ends once its share fills | the typical cluster |
| the site test (water index and registry cells examined) | per item | 20 | its farm's share (1); its bank, the typical 60 ft segment to its house in about 2.2 cells of 64 ft at a random angle, with the mean 4 water segments in the one it crosses (6.2); its clump's 22 ft box in about 1.8 cells (1 + 22/64 squared) with the mean 5.5 things near the houses and the cell (11.7); 19.9, rounded up | the typical cluster |
| slack | per item | 2 | what varies around the typical case (S8): the spread around the mean sites tried | a crowded farm |
| the shares (house index cells examined) | once | 1,322 at 20, 2,784 at 40, 5,834 at 80 | each farm's share set (1), and the belt's ring walked, each point its area term (2) and its farm, the nearest house in its 3 by 3 cells of 90 ft (12) | 80 households |
| the clumps (registry cells written) | over the run | 462 x 2.8 at 20, 957 x 2.8 at 40, 1,980 x 2.8 at 80 | each clump recorded (1) and filed in its about 1.8 cells (1.8) | 80 households |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 90 ft cell | 80 households |
| the crowns (written) | over the run | 624 at 20, 1,317 at 40, 2,779 at 80 | each crown written once | 80 households |

So: the clumps x 2.13 x 20 x 2, plus the shares, the clumps x 2.8, the house index and the crowns.

## Totals

- at 20: 462 x 2.13 x 20 x 2 + 1322 + 462 x 2.8 + 20 + 624 = 42622
- at 40: 957 x 2.13 x 20 x 2 + 2784 + 957 x 2.8 + 40 + 1317 = 88357
- at 80: 1980 x 2.13 x 20 x 2 + 5834 + 1980 x 2.8 + 80 + 2779 = 182933

## Earlier findings

- verdict-3, finding 1: fixed - the sites tried a clump are 1/p, p = 0.47 measured on the reference geometry; the items are the clumps, the candidates the sites tried (S7's form); a farm's walk ends when its share fills; the registry and the bank at their mean cells; every belt point within 90 ft of a house
- verdict-1, finding 1: fixed - the bank test walks the site's segment to its house through the water index's cells, no water segment crossing it, its own count (130)
- verdict-1, finding 2: fixed - no raster is built; the bank is read from the water index, and the 1 ft a pixel is the map's scale only
- verdict-1, finding 3: fixed - each farm's share is set once, less the belt's and the groves' hold, its own row
- verdict-1, finding 4: fixed - the candidates are the sites within each house's 90 ft reach, 106 a house, each once; the share check runs first
- verdict-1, finding 5: fixed - the items are the houses and the sites their candidates, the rubric's form; the clumps are written over the run
- verdict-1, finding 6: fixed - the grid's pitch is 11 x root 2, 15.556 ft
- verdict-2, finding 1: fixed - the sites are the grid's at the worst offset, every site's cell within 90 + 11 ft of the house, at most 133
- verdict-2, finding 2: fixed - the belt's ring apportioned to farms point by point by the nearest house (12 a point); the fengshui groves are none on a hamlet, measured empty at 10 and 20
- verdict-2, finding 3: fixed - the bank's segment meets at most 4 cells (its run and rise sum under 128 ft), 104
- verdict-2, finding 4: fixed - the house-index lookup per site is dropped: each site comes from its own house's reach
- FR-014 re-score: each factor at the typical case (rubric S8): the sites tested about twice the clumps drawn, the farms' shares filling well before a house's whole reach is tried; the mean densities of `items.md`; slack 2 (ask:444-budget-standard; the accept was ask:444-T05-windbreak-round-3)

## Cheaper algorithms considered

- sweep: not used - the candidates are the sites in each house's reach, not a sweep of the footprint
- grid or spatial index: used - the house index for the reach and the registry for each clump
- priority queue: not used - the sites are taken in grid order; the farms' shares bound the fill
- incremental update: used - each clump is filed as it is drawn, and its farm's share counted down
- memoizing what a scan does not change: used - the houses and the belt stand through the stage; the 90 ft house index is built once, each house filed
