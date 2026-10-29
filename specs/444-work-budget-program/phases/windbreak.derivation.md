# Derivation - windbreak (feature 444)

## Contract

- Reads: the placed homesteads and the cluster's oriented footprint; each farm's homestead wood, rolled in the register's range (`homestead_wood_ft2`); the belt and the groves already planted by the hinterland; the registry; the water courses (each farm's bank).
- Writes: the copse among the homes (`village_groves`, role `copse`): its clumps on a grid in the gaps between the houses, each clump's crowns; `meta.copse_clumps`.
- Keeps: over the cluster's own oriented footprint, in the gaps between the houses (0036, 0071); a clump within 90 ft of a house (`COPSE_HOUSE_REACH_FT`, a dooryard's reach, 0036); on its house's own bank (0035, a GUESS recorded there); sized by the homestead woods, each farm's share of 6,000 to 28,000 sq ft, the copse filled to what the belt and groves leave (0036); no copse without a belt or a reserved seat; seated after the woods and the ground cover, so the copse and the belt read as two stands; each clump asked before it is drawn (S4).
- Bounds (measured 2026-10-28, `phases/items.md`, the reference manifests at 10 and 20 households; past 20 at each figure's measured rate a doubling): the cluster's extent 477 by 721 ft and 750 by 1,085 ft (x1.57 and x1.5: 750 by 1,085 ft at 20, 1,178 by 1,628 ft at 40, 1,849 by 2,442 ft at 80); a clump 11 ft in radius on a grid of pitch 11 x root 2, 15.556 ft (the clumps' median nearest neighbor 15.5 ft at 10 and 20); the clumps 223 and 462 (x2.07: 462 at 20, 957 at 40, 1,980 at 80) and their crowns 296 and 624 (x2.11: 624 at 20, 1,317 at 40, 2,779 at 80); the houses' density at most 2.9e-5 a sq ft, so at most 3 houses in 3 by 3 cells of 90 ft; at most 29 things in a 64 ft cell; at most 26 water segments in a 64 ft cell; the belt's ring 44 and 93 points (`belt_near_vertices`, x2.1: 93 at 20, 196 at 40, 411 at 80); 1 ft a pixel at the hamlet scale.

## The algorithm

    each farm's share: its rolled homestead wood, less what the belt already holds for it: the belt's ring walked once, each
        point's farm its nearest house from the 90 ft house index, its area apportioned (the fengshui groves are none on a
        hamlet: `groves` is empty on the reference at 10 and 20)
    for each house: the clump grid's sites within its 90 ft reach (a disk of the 15.556 ft grid, at most 133 sites at any offset), each
        site once over the run (a site two houses reach is taken by the first)
        each site: its farm's share not yet filled (1, first, so a filled farm's sites cost one test); within 90 ft of its
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
| items | per item | 924 at 20, 1,914 at 40, 3,960 at 80 | the sites tested: about twice the clumps drawn (S8: the sites the search order reaches before each farm's share fills - a site in a house's reach admitted about one time in two; the clumps 223 and 462 at 10 and 20, x2.07: 462 at 20, 957 at 40, 1,980 at 80) | 80 households |
| the site test (water index and registry cells examined) | per item | 35 | its farm's share (1); its bank, the segment to its house in at most 4 cells of 64 ft, each read, with the mean 4 water segments in the one a segment typically crosses (8); its clump's 2 by 2 cells with the mean 5.5 things a cell near the houses and the cell (26) | the typical cluster |
| slack | per item | 2 | what varies around the typical case (S8): a crowded farm testing more of its reach | a crowded cluster |
| the shares (house index cells examined) | once | 1,322 at 20, 2,784 at 40, 5,834 at 80 | each farm's share set (1), and the belt's ring walked, each point its area term (2) and its farm, the nearest house in its 3 by 3 cells of 90 ft (12) | 80 households |
| the clumps (registry cells written) | over the run | 462 x 5 at 20, 957 x 5 at 40, 1,980 x 5 at 80 | each clump drawn, recorded (1) and filed in at most 4 cells (4) | 80 households |
| the house index (cells written) | once | 20 at 20, 40 at 40, 80 at 80 | each house filed once in its 90 ft cell | 80 households |
| the crowns (written) | over the run | 624 at 20, 1,317 at 40, 2,779 at 80 | each crown written once | 80 households |

So: the sites tested x 35 x 2, plus the shares, the clumps x 5, the house index and the crowns.

## Totals

- at 20: 924 x 35 x 2 + 1322 + 462 x 5 + 20 + 624 = 68956
- at 40: 1914 x 35 x 2 + 2784 + 957 x 5 + 40 + 1317 = 142906
- at 80: 3960 x 35 x 2 + 5834 + 1980 x 5 + 80 + 2779 = 295793

## Earlier findings

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
